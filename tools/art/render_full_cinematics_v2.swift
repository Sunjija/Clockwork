// Offline frame-edit preview, NOT AI video generation or game execution.
// PNG/APNG remain the exact timing/color/pixel authorities. H264/AAC MP4 is a
// lossy viewing copy; technical checks do not replace listening/user approval.
// Existing PNG/WAV/game files are read-only. Different outputs are preserved.
// Requires only the already installed macOS Swift/AVFoundation frameworks.
// EXPERIMENTAL: Swift type-check passes, but no validated final MP4 was
// exported on the current Mac. Separate AAC mux shortened audio by44ms;
// the direct-WAV composition attempt hit writer backpressure timeout.
// Rejected/partial intermediate candidates remain in QA; use exact PNG/APNG
// and standalone WAV outputs until this mux implementation is repaired.
import Foundation
import AVFoundation
import CoreVideo
import CoreGraphics
import ImageIO
import CryptoKit
import Darwin

struct PreviewError: Error, CustomStringConvertible {
    let description: String
}
func require(_ condition: Bool, _ message: String) throws {
    if !condition { throw PreviewError(description: message) }
}
func digest(_ data: Data) -> String {
    SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}
func sha(_ url: URL) throws -> String { digest(try Data(contentsOf: url)) }
func stamp(_ ms: Int) -> CMTime { CMTime(value: Int64(ms), timescale: 1000) }
func exact(_ time: CMTime, _ ms: Int) -> Bool { CMTimeCompare(time, stamp(ms)) == 0 }
func relative(_ url: URL, _ root: URL) -> String {
    String(url.path.dropFirst(root.path.count + 1))
}
func confined(_ root: URL, _ path: String) throws -> URL {
    try require(!path.hasPrefix("/") && !path.split(separator: "/").contains(".."), "Unconfined input path: \(path)")
    let url = root.appendingPathComponent(path).standardizedFileURL
    try require(url.resolvingSymlinksInPath().path.hasPrefix(root.resolvingSymlinksInPath().path + "/"), "Path escapes candidate root: \(path)")
    return url
}
func waitReady(_ input: AVAssetWriterInput, _ writer: AVAssetWriter) throws {
    let deadline = Date().addingTimeInterval(60)
    while !input.isReadyForMoreMediaData {
        try require(writer.status == .writing && Date() < deadline,
                    "Writer stalled: \(String(describing: writer.error))")
        Thread.sleep(forTimeInterval: 0.002)
    }
}
func finish(_ writer: AVAssetWriter, _ inputs: [AVAssetWriterInput], _ duration: Int) throws {
    writer.endSession(atSourceTime: stamp(duration))
    for input in inputs { input.markAsFinished() }
    let done = DispatchSemaphore(value: 0)
    writer.finishWriting { done.signal() }
    try require(done.wait(timeout: .now() + 90) == .success, "Writer finish timed out")
    try require(writer.status == .completed, "Writer failed: \(String(describing: writer.error))")
}

struct Clip: Decodable {
    let name: String
    let durationMs: Int
    let durations: [Int]
    let width: Int
    let height: Int
    let frames: [String]
}
struct Sequence: Decodable {
    let name: String
    let shots: [String]
    let durationMs: Int
}
struct Plan: Decodable {
    let clips: [Clip]
    let sequences: [Sequence]
}
struct Frame {
    let url: URL
    let shot: String
    let index: Int
    let startMs: Int
    let durationMs: Int
    let sourceSha: String
}
let nativeWidth = 640, nativeHeight = 360, scale = 2
let width = nativeWidth * scale, height = nativeHeight * scale

func nativeBGRA(_ url: URL) throws -> [UInt8] {
    guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw PreviewError(description: "Cannot decode source PNG: \(url.path)")
    }
    try require(image.width == nativeWidth && image.height == nativeHeight, "Source is not native640×360")
    var bytes = [UInt8](repeating: 0, count: nativeWidth * nativeHeight * 4)
    try bytes.withUnsafeMutableBytes { raw in
        guard let context = CGContext(data: raw.baseAddress, width: nativeWidth, height: nativeHeight,
            bitsPerComponent: 8, bytesPerRow: nativeWidth * 4,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue) else {
            throw PreviewError(description: "Cannot decode PNG into native BGRA buffer")
        }
        context.interpolationQuality = .none
        context.setShouldAntialias(false)
        context.draw(image, in: CGRect(x: 0, y: 0, width: CGFloat(nativeWidth), height: CGFloat(nativeHeight)))
    }
    try require(stride(from: 3, to: bytes.count, by: 4).allSatisfy { bytes[$0] == 255 }, "Source PNG must be fully opaque")
    return bytes
}

func pixelBuffer(_ native: [UInt8], _ pool: CVPixelBufferPool) throws -> CVPixelBuffer {
    var candidate: CVPixelBuffer?
    let status = CVPixelBufferPoolCreatePixelBuffer(kCFAllocatorDefault, pool, &candidate)
    guard status == kCVReturnSuccess, let buffer = candidate else {
        throw PreviewError(description: "Cannot allocate encoder pixel buffer")
    }
    CVPixelBufferLockBaseAddress(buffer, [])
    defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
    guard let base = CVPixelBufferGetBaseAddress(buffer) else {
        throw PreviewError(description: "Pixel buffer has no storage")
    }
    let output = base.assumingMemoryBound(to: UInt8.self)
    let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
    // Literal integer2× source-pixel replication: no filter, interpolation,
    // CG resizing, anti-aliasing, recoloring, image edits or animation changes.
    for y in 0..<height {
        for x in 0..<width {
            let from = ((y / scale) * nativeWidth + x / scale) * 4
            let to = y * rowBytes + x * 4
            for channel in 0..<4 { output[to + channel] = native[from + channel] }
        }
    }
    return buffer
}

func writeVideo(_ frames: [Frame], _ duration: Int, _ target: URL) throws {
    let writer = try AVAssetWriter(outputURL: target, fileType: .mp4)
    let settings: [String: Any] = [
        AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: width, AVVideoHeightKey: height,
        AVVideoCompressionPropertiesKey: [
            AVVideoAverageBitRateKey: 12_000_000,
            AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
            AVVideoAllowFrameReorderingKey: false, AVVideoMaxKeyFrameIntervalKey: 1
        ]
    ]
    let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
    input.expectsMediaDataInRealTime = false
    input.mediaTimeScale = 1000
    let attributes: [String: Any] = [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: width, kCVPixelBufferHeightKey as String: height,
        kCVPixelBufferCGImageCompatibilityKey as String: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey as String: true
    ]
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: attributes)
    try require(writer.canAdd(input), "Cannot add H264 video input")
    writer.add(input)
    try require(writer.startWriting(), "Cannot start H264 writer: \(String(describing: writer.error))")
    writer.startSession(atSourceTime: .zero)
    guard let pool = adaptor.pixelBufferPool else { throw PreviewError(description: "Writer has no pixel buffer pool") }
    var last: CVPixelBuffer?
    for frame in frames {
        try waitReady(input, writer)
        let buffer = try pixelBuffer(nativeBGRA(frame.url), pool)
        try require(adaptor.append(buffer, withPresentationTime: stamp(frame.startMs)),
                    "Cannot append \(frame.shot)/\(frame.index): \(String(describing: writer.error))")
        last = buffer
    }
    // A boundary repeat pins the final authored hold; the exact endSession
    // and composition range clip this guard frame at8/10seconds.
    if let buffer = last {
        try waitReady(input, writer)
        try require(adaptor.append(buffer, withPresentationTime: stamp(duration)), "Cannot append final hold boundary")
    }
    try finish(writer, [input], duration)
}

func mux(_ video: URL, _ audio: URL, _ duration: Int, _ target: URL) throws {
    // Insert the original PCM WAV into the same zero-start composition.
    // Encode AAC once in the final MP4. Separately encoded AAC + export
    // passthrough double-removes encoder priming on this macOS version.
    let movie = AVURLAsset(url: video), sound = AVURLAsset(url: audio)
    try require(exact(sound.duration, duration), "Source WAV duration differs from sequence")
    guard let sourceVideo = movie.tracks(withMediaType: .video).first,
          let sourceAudio = sound.tracks(withMediaType: .audio).first else {
        throw PreviewError(description: "Missing encoded preview track")
    }
    let composition = AVMutableComposition()
    guard let videoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
          let audioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else {
        throw PreviewError(description: "Cannot create composition tracks")
    }
    let range = CMTimeRange(start: .zero, duration: stamp(duration))
    try videoTrack.insertTimeRange(range, of: sourceVideo, at: .zero)
    try audioTrack.insertTimeRange(range, of: sourceAudio, at: .zero)
    guard let description = sourceVideo.formatDescriptions.first else {
        throw PreviewError(description: "H264 source has no format description")
    }
    let hint = description as! CMFormatDescription
    let reader = try AVAssetReader(asset: composition)
    reader.timeRange = range
    let videoOutput = AVAssetReaderTrackOutput(track: videoTrack, outputSettings: nil)
    let audioOutput = AVAssetReaderTrackOutput(track: audioTrack, outputSettings: [
        AVFormatIDKey: kAudioFormatLinearPCM, AVSampleRateKey: 48000,
        AVNumberOfChannelsKey: 2, AVLinearPCMBitDepthKey: 16,
        AVLinearPCMIsFloatKey: false, AVLinearPCMIsBigEndianKey: false,
        AVLinearPCMIsNonInterleaved: false])
    reader.add(videoOutput)
    reader.add(audioOutput)
    let writer = try AVAssetWriter(outputURL: target, fileType: .mp4)
    writer.shouldOptimizeForNetworkUse = true
    let videoInput = AVAssetWriterInput(mediaType: .video, outputSettings: nil, sourceFormatHint: hint)
    videoInput.mediaTimeScale = 1000
    let audioInput = AVAssetWriterInput(mediaType: .audio, outputSettings: [
        AVFormatIDKey: kAudioFormatMPEG4AAC, AVSampleRateKey: 48000,
        AVNumberOfChannelsKey: 2, AVEncoderBitRateKey: 192000])
    for input in [videoInput, audioInput] {
        input.expectsMediaDataInRealTime = false
        try require(writer.canAdd(input), "Cannot add final MP4 input")
        writer.add(input)
    }
    try require(writer.startWriting(), "Cannot start final MP4 writer")
    writer.startSession(atSourceTime: .zero)
    try require(reader.startReading(), "Cannot read zero-start composition")
    var nextVideo = videoOutput.copyNextSampleBuffer()
    var nextAudio = audioOutput.copyNextSampleBuffer()
    while nextVideo != nil || nextAudio != nil {
        let chooseVideo: Bool
        if let v = nextVideo, let a = nextAudio {
            chooseVideo = CMTimeCompare(CMSampleBufferGetPresentationTimeStamp(v), CMSampleBufferGetPresentationTimeStamp(a)) <= 0
        } else { chooseVideo = nextVideo != nil }
        if chooseVideo, let sample = nextVideo {
            try waitReady(videoInput, writer)
            try require(videoInput.append(sample), "Cannot copy H264 composition sample")
            nextVideo = videoOutput.copyNextSampleBuffer()
        } else if let sample = nextAudio {
            try waitReady(audioInput, writer)
            try require(audioInput.append(sample), "Cannot encode source WAV composition sample")
            nextAudio = audioOutput.copyNextSampleBuffer()
        }
    }
    try require(reader.status == .completed, "Composition reader failed: \(String(describing: reader.error))")
    try finish(writer, [videoInput, audioInput], duration)
}

func compareRGB(_ buffer: CVPixelBuffer, _ expected: [UInt8]) throws -> Double {
    try require(CVPixelBufferGetWidth(buffer) == width && CVPixelBufferGetHeight(buffer) == height, "Decoded preview size differs")
    CVPixelBufferLockBaseAddress(buffer, .readOnly)
    defer { CVPixelBufferUnlockBaseAddress(buffer, .readOnly) }
    guard let base = CVPixelBufferGetBaseAddress(buffer) else { throw PreviewError(description: "Decoded video buffer has no storage") }
    let actual = base.assumingMemoryBound(to: UInt8.self)
    let rowBytes = CVPixelBufferGetBytesPerRow(buffer)
    var total = 0, count = 0
    for y in stride(from: 0, to: height, by: 8) {
        for x in stride(from: 0, to: width, by: 8) {
            let from = ((y / scale) * nativeWidth + x / scale) * 4
            let to = y * rowBytes + x * 4
            for channel in 0..<3 { total += abs(Int(actual[to + channel]) - Int(expected[from + channel])); count += 1 }
        }
    }
    return Double(total) / Double(count)
}

func validate(_ url: URL, _ sequence: Sequence, _ frames: [Frame], _ audio: URL, _ root: URL) throws -> [String: Any] {
    let asset = AVURLAsset(url: url)
    let videoTracks = asset.tracks(withMediaType: .video), audioTracks = asset.tracks(withMediaType: .audio)
    try require(videoTracks.count == 1 && audioTracks.count == 1, "Expected exactly one video and one audio track")
    let video = videoTracks[0], sound = audioTracks[0]
    guard let description = sound.formatDescriptions.first else {
        throw PreviewError(description: "Encoded audio has no format description")
    }
    // AVAssetTrack.formatDescriptions is documented as CMFormatDescription
    // objects; conditional CF downcasts are rejected by the Swift compiler.
    let audioDescription = description as! CMAudioFormatDescription
    guard let audioFormat = CMAudioFormatDescriptionGetStreamBasicDescription(audioDescription) else {
        throw PreviewError(description: "Cannot inspect encoded audio format")
    }
    try require(audioFormat.pointee.mFormatID == kAudioFormatMPEG4AAC
                && audioFormat.pointee.mSampleRate == 48000
                && audioFormat.pointee.mChannelsPerFrame == 2, "Stored MP4 audio is not48kHz stereo AAC")
    try require(exact(asset.duration, sequence.durationMs), "MP4 container duration is not exact")
    try require(exact(video.timeRange.duration, sequence.durationMs), "MP4 video duration is not exact")
    try require(exact(sound.timeRange.duration, sequence.durationMs), "MP4 audio duration is not exact")
    try require(CMTimeCompare(video.timeRange.start, .zero) == 0 && CMTimeCompare(sound.timeRange.start, .zero) == 0, "Preview tracks are not synchronized at zero")
    try require(video.naturalSize == CGSize(width: CGFloat(width), height: CGFloat(height)), "MP4 dimensions changed")
    let reader = try AVAssetReader(asset: asset)
    reader.timeRange = CMTimeRange(start: .zero, duration: stamp(sequence.durationMs))
    let output = AVAssetReaderTrackOutput(track: video, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
    reader.add(output)
    try require(reader.startReading(), "Cannot decode preview video")
    var index = 0, records = [[String: Any]](), maxError = 0.0
    while let sample = output.copyNextSampleBuffer() {
        let pts = CMSampleBufferGetPresentationTimeStamp(sample)
        if CMTimeCompare(pts, stamp(sequence.durationMs)) >= 0 { continue }
        try require(index < frames.count, "Preview contains an unexpected in-range image")
        let frame = frames[index]
        try require(exact(pts, frame.startMs), "Decoded image order/PTS mismatch at \(index)")
        guard let image = CMSampleBufferGetImageBuffer(sample) else { throw PreviewError(description: "Decoded sample has no image") }
        let error = try compareRGB(image, nativeBGRA(frame.url))
        try require(error < 20, "Decoded image differs excessively from corresponding PNG at \(index)")
        maxError = max(maxError, error)
        records.append(["sequenceFrame": index, "shot": frame.shot, "shotFrame": frame.index,
            "sourcePath": relative(frame.url, root), "sourceSha256": frame.sourceSha,
            "startMs": frame.startMs, "durationMs": frame.durationMs,
            "decodedPresentationTimeExact": true, "sampledRgbMeanAbsoluteError": error])
        index += 1
    }
    try require(reader.status == .completed && index == frames.count, "Decoded source image count/order differs")
    let audioReader = try AVAssetReader(asset: asset)
    audioReader.timeRange = CMTimeRange(start: .zero, duration: stamp(sequence.durationMs))
    let audioOutput = AVAssetReaderTrackOutput(track: sound, outputSettings: [
        AVFormatIDKey: kAudioFormatLinearPCM, AVSampleRateKey: 48000, AVNumberOfChannelsKey: 2,
        AVLinearPCMBitDepthKey: 32, AVLinearPCMIsFloatKey: true,
        AVLinearPCMIsBigEndianKey: false, AVLinearPCMIsNonInterleaved: false])
    audioReader.add(audioOutput)
    try require(audioReader.startReading(), "Cannot decode preview audio")
    var audioPeak: Float = 0, sampleCount = 0
    while let sample = audioOutput.copyNextSampleBuffer() {
        guard let block = CMSampleBufferGetDataBuffer(sample) else { throw PreviewError(description: "Decoded audio has no PCM block") }
        let count = CMBlockBufferGetDataLength(block)
        try require(count % MemoryLayout<Float>.size == 0, "Incomplete float PCM samples")
        var floats = [Float](repeating: 0, count: count / MemoryLayout<Float>.size)
        let result = floats.withUnsafeMutableBytes { raw in
            CMBlockBufferCopyDataBytes(block, atOffset: 0, dataLength: count, destination: raw.baseAddress!)
        }
        try require(result == noErr && floats.allSatisfy { $0.isFinite }, "Cannot decode finite audio samples")
        for value in floats { audioPeak = max(audioPeak, abs(value)) }
        sampleCount += floats.count
    }
    try require(audioReader.status == .completed && sampleCount > 0 && audioPeak > 0 && audioPeak < 0.95, "AAC preview audio failed peak/silence checks")
    return ["sequence": sequence.name, "path": "Sequences/\(sequence.name)/preview.mp4",
        "sha256": try sha(url), "width": width, "height": height,
        "durationMs": sequence.durationMs, "containerDurationExact": true,
        "videoDurationExact": true, "audioDurationExact": true, "trackStartAtZero": true,
        "videoCodec": "H264 High,12Mbps target,no frame reordering",
        "audioCodec": "AAC192kbps,48kHz stereo,lossy viewing copy",
        "sourceWavPath": relative(audio, root), "sourceWavSha256": try sha(audio),
        "storedAudioSampleRate": audioFormat.pointee.mSampleRate,
        "storedAudioChannels": audioFormat.pointee.mChannelsPerFrame,
        "decodedAudioPeak": audioPeak, "decodedAudioSampleCount": sampleCount,
        "decodedFrameCount": index, "imageOrderAndMillisecondPtsExact": true,
        "maximumSampledRgbMeanAbsoluteError": maxError,
        "rgbCheckNote": "Sampled tolerance check only; H264 is lossy. PNG/APNG are the exact pixel/color authorities.",
        "frames": records]
}

func main() throws {
    let script = URL(fileURLWithPath: #filePath).standardizedFileURL
    let repo = script.deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    let root = repo.appendingPathComponent("art/return-pixel-cinematics-v2-full")
    let planURL = try confined(root, "Clips/clip-plan.json")
    let rawPlan = try Data(contentsOf: planURL)
    let plan = try JSONDecoder().decode(Plan.self, from: rawPlan)
    let expectations = ["awakening": (["A1", "A2", "A3", "A4"], 8000),
                        "homecoming": (["B1", "B2", "B3", "B4"], 10000)]
    try require(plan.clips.count == 8 && plan.sequences.count == 2, "Expected8shots and2sequences")
    try require(Set(plan.clips.map { $0.name }).count == 8, "Duplicate source shot names")
    try require(Set(plan.sequences.map { $0.name }).count == 2, "Duplicate source sequence names")
    let clips = Dictionary(uniqueKeysWithValues: plan.clips.map { ($0.name, $0) })
    var allFrames = [String: [Frame]]()
    for sequence in plan.sequences {
        guard let expected = expectations[sequence.name] else { throw PreviewError(description: "Unknown sequence") }
        try require(sequence.shots == expected.0 && sequence.durationMs == expected.1, "Sequence order/duration changed")
        var elapsed = 0, frames = [Frame]()
        for name in sequence.shots {
            guard let clip = clips[name] else { throw PreviewError(description: "Missing shot") }
            try require(clip.width == nativeWidth && clip.height == nativeHeight && !clip.frames.isEmpty,
                        "Invalid native shot dimensions")
            try require(clip.frames.count == clip.durations.count && clip.durations.allSatisfy { $0 > 0 }
                        && clip.durations.reduce(0, +) == clip.durationMs, "Invalid variable source timing")
            for (index, filename) in clip.frames.enumerated() {
                let url = try confined(root, "Clips/\(name)/\(filename)")
                frames.append(Frame(url: url, shot: name, index: index, startMs: elapsed,
                    durationMs: clip.durations[index], sourceSha: try sha(url)))
                elapsed += clip.durations[index]
            }
        }
        try require(elapsed == sequence.durationMs, "Sequence image durations do not sum exactly")
        allFrames[sequence.name] = frames
    }
    let qa = try confined(root, "QA")
    try FileManager.default.createDirectory(at: qa, withIntermediateDirectories: true)
    var template = Array(qa.appendingPathComponent("video-preview-build-XXXXXX").path.utf8CString)
    let temporaryPath = template.withUnsafeMutableBufferPointer { bytes -> String? in
        guard let pointer = mkdtemp(bytes.baseAddress!) else { return nil }
        return String(cString: pointer)
    }
    guard let path = temporaryPath else { throw PreviewError(description: "Cannot create confined mkdtemp candidate directory") }
    let temporary = URL(fileURLWithPath: path)
    var records = [[String: Any]](), outputs = [(URL, Data)]()
    for sequence in plan.sequences {
        print("Rendering offline \(sequence.name),\(sequence.durationMs)ms from unchanged PNG/WAV files...")
        fflush(stdout)
        let frames = allFrames[sequence.name]!
        let audio = try confined(root, "Sequences/\(sequence.name)/sound.wav")
        let audioHash = try sha(audio)
        let video = temporary.appendingPathComponent(sequence.name + "-silent.mp4")
        let candidate = temporary.appendingPathComponent(sequence.name + "-muxed.mp4")
        try writeVideo(frames, sequence.durationMs, video)
        try mux(video, audio, sequence.durationMs, candidate)
        let record = try validate(candidate, sequence, frames, audio, root)
        try require(sha(audio) == audioHash, "Source WAV changed during rendering")
        for frame in frames { try require(sha(frame.url) == frame.sourceSha, "Source PNG changed during rendering") }
        records.append(record)
        outputs.append((try confined(root, "Sequences/\(sequence.name)/preview.mp4"), try Data(contentsOf: candidate)))
        print("Validated \(sequence.name): exact duration,1280×720,ordered frames,and synchronized audio.")
        fflush(stdout)
    }
    try require(sha(planURL) == digest(rawPlan), "Source plan changed during rendering")
    let report: [String: Any] = [
        "schemaVersion": 1, "status": "passed-offline-lossy-preview-technical-validation",
        "scriptPath": relative(script, repo), "scriptSha256": try sha(script),
        "clipPlanPath": relative(planURL, root), "clipPlanSha256": digest(rawPlan),
        "scale": scale, "scaling": "CPU integer2× identical pixel replication; no interpolation/antialiasing",
        "timing": "source variable frame durations,CMTime timescale1000,final boundary hold,endSession exact",
        "mux": "AVMutableComposition existing WAV zero-start;compressed H264 copied;AAC encoded once in final MP4",
        "sequences": records, "workingCandidatesPreservedAt": relative(temporary, root),
        "sourcePngAndWavHashesUnchanged": true, "aiVideoGenerated": false,
        "gameChangedOrExecuted": false, "nativeImagesModified": false,
        "exactColorAndPixelAuthority": "source PNG and native APNG;MP4 H264/AAC is lossy",
        "audioScope": "Temporary existing SFX mix;no dedicated hum/clock recording",
        "humanListeningReview": "not-performed", "humanFinalApproval": "pending",
        "differentExistingFilesPreservedAndFail": true]
    let reportData = try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys]) + Data([10])
    outputs.append((try confined(root, "QA/video-preview-validation.json"), reportData))
    // Preflight ALL final outputs before creating any; no old output is removed.
    for (url, data) in outputs {
        if FileManager.default.fileExists(atPath: url.path) {
            let values = try url.resourceValues(forKeys: [.isSymbolicLinkKey])
            try require(!values.isSymbolicLink.orFalse, "Output is a symlink")
            try require(Data(contentsOf: url) == data, "Preserving different existing output: \(url.path)")
        } else {
            try require((try? FileManager.default.destinationOfSymbolicLink(atPath: url.path)) == nil,
                        "Preserving broken output symlink")
        }
    }
    for (url, data) in outputs where !FileManager.default.fileExists(atPath: url.path) {
        try data.write(to: url, options: .withoutOverwriting)
    }
    print("Finished offline MP4 candidates;PNG/APNG remain authoritative;human approval pending.")
    print("Temporary candidates preserved: \(temporary.path)")
}
extension Optional where Wrapped == Bool { var orFalse: Bool { self ?? false } }
do { try main() }
catch {
    fputs("Preview stopped;existing output preserved: \(error)\n", stderr)
    exit(1)
}
