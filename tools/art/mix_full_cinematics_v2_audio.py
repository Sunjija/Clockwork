"""Mix temporary offline storyboard cues from existing game WAV files only.

No new tones, recordings, downloads, visual assets, Unity/player execution or
game-file changes. This is an unapproved sound-placement preview: dedicated
factory hum and clock recordings are not available. All edits, source hashes,
gains, timing and output validation are recorded beside the v2 candidates.
Different existing output bytes are preserved and cause failure before writes.
Requires NumPy; all WAV reading/writing uses the standard-library wave module.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import sys
import wave

import numpy as np


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "art/return-pixel-cinematics-v2-full"
SOURCE_ROOT = REPO / "unity/TiqueReturnPrototype/Assets/Resources/Return/Audio"
SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2
MAX_GLOBAL_GAIN = 0.9
MAX_PEAK = 0.9
SOURCE_NAMES = ("success", "switch", "warning", "land")
SEQUENCES = {"awakening": 8.0, "homecoming": 10.0}
SCOPE_NOTE = (
    "Temporary offline storyboard sound-placement preview using only existing "
    "game sound effects. No dedicated factory hum or clock recording exists. "
    "Land cuts stand in for footsteps and switch cuts stand in for clock ticks. "
    "No new tone synthesis, audio download, game change or game execution. "
    "Technical validation is separate from human listening and final approval."
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def decode_pcm(raw, width, channels):
    """Normalize integer PCM to float64 without limiting or tone generation."""
    require(width in (1, 2, 3, 4), "Unsupported PCM sample width")
    require(channels in (1, 2), "Only mono or stereo source WAVs are supported")
    require(len(raw) % (width * channels) == 0, "Incomplete PCM source frame")
    if width == 1:
        samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif width == 2:
        samples = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    elif width == 3:
        octets = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        integers = octets[:, 0] | (octets[:, 1] << 8) | (octets[:, 2] << 16)
        integers = np.where(integers & 0x800000, integers - 0x1000000, integers)
        samples = integers.astype(np.float64) / 8388608.0
    else:
        samples = np.frombuffer(raw, dtype="<i4").astype(np.float64) / 2147483648.0
    samples = samples.reshape(-1, channels)
    require(samples.size and np.isfinite(samples).all(), "Invalid or empty PCM source")
    return samples


def read_source(name):
    require(name in SOURCE_NAMES, "Unexpected source outside the four existing WAVs")
    path = SOURCE_ROOT / (name + ".wav")
    require(path.resolve().is_relative_to(SOURCE_ROOT.resolve()), "Source path escapes existing Audio folder")
    data = path.read_bytes()
    with wave.open(io.BytesIO(data), "rb") as reader:
        require(reader.getcomptype() == "NONE", "Only uncompressed integer PCM source WAVs are supported")
        channels, width = reader.getnchannels(), reader.getsampwidth()
        rate, frames = reader.getframerate(), reader.getnframes()
        require(rate > 0, "Invalid source sample rate")
        raw = reader.readframes(frames)
    samples = decode_pcm(raw, width, channels)
    require(len(samples) == frames, "Decoded source frame count mismatch")
    record = {
        "name": name, "path": path.relative_to(REPO).as_posix(),
        "absolutePath": str(path), "sha256": sha(data), "pcmSha256": sha(raw),
        "sampleRate": rate, "channels": channels, "sampleWidthBytes": width,
        "frames": frames, "durationSeconds": frames / rate,
        "peakNormalized": float(np.max(np.abs(samples))),
        "sourceUnchanged": True,
    }
    return {"samples": samples, "record": record, "path": path}


def cue(cue_id, sequence, shot, source, time, gain, purpose, trim=None,
        fade_in_ms=1.0, fade_out_ms=6.0):
    return {
        "id": cue_id, "sequence": sequence, "shot": shot, "source": source,
        "startSeconds": time, "gain": gain, "purpose": purpose,
        "trimStartSeconds": 0.0, "trimDurationSeconds": trim,
        "fadeInMs": fade_in_ms, "fadeOutMs": fade_out_ms,
    }


def cue_plan():
    result = [
        cue("A1-connect-success", "awakening", "A1", "success", .76, .40, "Temporary docking confirmation"),
        cue("A1-contact-switch", "awakening", "A1", "switch", .76, .28, "Existing docking contact effect"),
        cue("A2-relay-contact", "awakening", "A2", "switch", 2.15, .38, "Existing switch as relay contact"),
        cue("A3-core-warning", "awakening", "A3", "warning", 4.2, .22, "Existing warning as core boot cue"),
        cue("A3-core-contact", "awakening", "A3", "switch", 4.2, .22, "Existing switch as core contact"),
        cue("A4-low-warning", "awakening", "A4", "warning", 6.1, .10, "Low-volume temporary confrontation cue"),
        cue("B1-soft-settle", "homecoming", "B1", "land", .55, .14, "Low-volume existing landing as shutdown settle"),
        cue("B2-door-threshold", "homecoming", "B2", "switch", 3.52, .14, "Existing switch as doorway threshold contact"),
    ]
    for index, time in enumerate((2.3, 2.65, 3.0, 3.35)):
        result.append(cue(
            f"B2-temporary-step-{index + 1}", "homecoming", "B2", "land", time, .045,
            "Very quiet shortened existing land effect, temporary footstep placeholder",
            trim=.04, fade_in_ms=1.0, fade_out_ms=6.0))
    for index, time in enumerate((4.7, 5.7, 6.7, 7.7, 8.7, 9.7)):
        result.append(cue(
            f"B34-temporary-tick-{index + 1}", "homecoming", "B3" if time < 7 else "B4",
            "switch", time, .025,
            "Very quiet shortened existing switch effect, temporary clock tick placeholder",
            trim=.03, fade_in_ms=1.0, fade_out_ms=5.0))
    return sorted(result, key=lambda row: (row["sequence"], row["startSeconds"], row["id"]))


def prepare_cue(row, source):
    record = source["record"]
    rate, samples = record["sampleRate"], source["samples"]
    start = round(row["trimStartSeconds"] * rate)
    count = len(samples) - start if row["trimDurationSeconds"] is None else round(row["trimDurationSeconds"] * rate)
    end = min(len(samples), start + count)
    require(0 <= start < end <= len(samples), "Invalid source trim for " + row["id"])
    trimmed = samples[start:end]
    output_count = round(len(trimmed) * SAMPLE_RATE / rate)
    require(output_count > 0, "Empty resampled cue")
    positions = np.arange(output_count, dtype=np.float64) * rate / SAMPLE_RATE
    source_positions = np.arange(len(trimmed), dtype=np.float64)
    converted = np.stack([
        np.interp(positions, source_positions, trimmed[:, channel])
        for channel in range(record["channels"])
    ], axis=1)
    if record["channels"] == 1:
        converted = np.repeat(converted, CHANNELS, axis=1)
    fade_in = min(output_count, round(row["fadeInMs"] * SAMPLE_RATE / 1000))
    fade_out = min(output_count, round(row["fadeOutMs"] * SAMPLE_RATE / 1000))
    if fade_in:
        converted[:fade_in] *= np.linspace(0, 1, fade_in, dtype=np.float64)[:, None]
    if fade_out:
        converted[-fade_out:] *= np.linspace(1, 0, fade_out, dtype=np.float64)[:, None]
    converted *= row["gain"]
    edits = {
        **row, "sourceSha256": record["sha256"], "sourceStartFrame": start,
        "sourceEndFrameExclusive": end, "sourceFramesUsed": end - start,
        "actualSourceDurationSeconds": (end - start) / rate,
        "resampling": "linear interpolation; existing samples only; final endpoint held",
        "channelConversion": "mono duplicated to L/R" if record["channels"] == 1 else "stereo preserved",
        "outputFrames": output_count, "actualOutputDurationSeconds": output_count / SAMPLE_RATE,
        "startOutputFrame": round(row["startSeconds"] * SAMPLE_RATE),
        "fadeInOutputFrames": fade_in, "fadeOutOutputFrames": fade_out,
        "peakAfterCueGain": float(np.max(np.abs(converted))),
        "looped": False, "pitchShifted": False, "newToneSynthesized": False,
    }
    return converted, edits


def wav_bytes(samples):
    require(np.isfinite(samples).all(), "Non-finite mixed samples")
    require(float(np.max(np.abs(samples))) <= MAX_PEAK, "Mix exceeds the 0.9 peak ceiling")
    pcm = np.rint(samples * 32767.0).astype("<i2")
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(CHANNELS)
        writer.setsampwidth(SAMPLE_WIDTH)
        writer.setframerate(SAMPLE_RATE)
        writer.writeframes(pcm.tobytes())
    return stream.getvalue()


def validate_wav(name, data, duration, global_gain, raw_peak, expected):
    with wave.open(io.BytesIO(data), "rb") as reader:
        channels, width, rate = reader.getnchannels(), reader.getsampwidth(), reader.getframerate()
        frames = reader.getnframes()
        raw = reader.readframes(frames)
    require((channels, width, rate) == (CHANNELS, SAMPLE_WIDTH, SAMPLE_RATE), "Wrong WAV output format")
    require(frames == round(duration * SAMPLE_RATE), "Wrong output sequence duration")
    decoded = np.frombuffer(raw, dtype="<i2").reshape(-1, CHANNELS)
    expected_pcm = np.rint(expected * 32767.0).astype("<i2")
    require(np.array_equal(decoded, expected_pcm), "Encoded/decoded PCM replay mismatch")
    peak_integer = int(np.max(np.abs(decoded.astype(np.int32))))
    peak = peak_integer / 32768.0
    clipped = int(np.count_nonzero((decoded == -32768) | (decoded == 32767)))
    require(peak <= MAX_PEAK and clipped == 0, "Output clips or exceeds peak limit")
    require(0 < global_gain <= MAX_GLOBAL_GAIN, "Global gain exceeds 0.9")
    return {
        "sequence": name, "path": f"Sequences/{name}/sound.wav", "sha256": sha(data),
        "sampleRate": rate, "channels": channels, "sampleWidthBytes": width,
        "encoding": "PCM16 little-endian stereo WAV", "frames": frames,
        "durationSeconds": frames / rate, "expectedDurationSeconds": duration,
        "peakNormalized": peak, "peakInteger": peak_integer, "clippedSamples": clipped,
        "rmsNormalized": float(np.sqrt(np.mean((decoded.astype(np.float64) / 32768.0) ** 2))),
        "peakBeforeGlobalGain": raw_peak, "globalGain": global_gain,
        "encodedDecodedPcmExact": True, "durationExact": True, "peakLimitPassed": True,
    }


def preserve_or_write(expected, check_only):
    """Preflight every output, then create absent files without overwriting."""
    for path, data in expected.items():
        require(path.resolve().is_relative_to(ROOT.resolve()), "Output escapes candidate package")
        require(not path.is_symlink(), "Preserving output symlink; refusing to write: " + str(path))
        if path.exists():
            require(path.is_file() and path.read_bytes() == data,
                    "Preserving different existing output; use a new candidate name: " + str(path))
        else:
            require(not check_only, "Required output is absent: " + str(path))
    if check_only:
        return
    for path, data in expected.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Reconstruct and validate exact existing output bytes without writing")
    args = parser.parse_args()
    sources = {name: read_source(name) for name in SOURCE_NAMES}
    prepared = [prepare_cue(row, sources[row["source"]]) for row in cue_plan()]
    outputs, sequence_records, placed_records = {}, [], []
    for name, duration in SEQUENCES.items():
        mixed = np.zeros((round(duration * SAMPLE_RATE), CHANNELS), dtype=np.float64)
        sequence_cues = []
        for samples, edits in prepared:
            if edits["sequence"] != name:
                continue
            first, last = edits["startOutputFrame"], edits["startOutputFrame"] + len(samples)
            require(0 <= first < last <= len(mixed), "Cue extends beyond sequence: " + edits["id"])
            mixed[first:last] += samples
            sequence_cues.append(edits)
        raw_peak = float(np.max(np.abs(mixed)))
        require(raw_peak > 0, "Unexpected silent sequence")
        global_gain = min(MAX_GLOBAL_GAIN, MAX_PEAK / raw_peak)
        mixed *= global_gain
        data = wav_bytes(mixed)
        record = validate_wav(name, data, duration, global_gain, raw_peak, mixed)
        record["cueIds"] = [row["id"] for row in sequence_cues]
        sequence_records.append(record)
        outputs[ROOT / record["path"]] = data
        for edits in sequence_cues:
            placed_records.append({**edits, "sequenceGlobalGain": global_gain,
                                   "effectiveGain": edits["gain"] * global_gain})
    for source in sources.values():
        require(sha(source["path"].read_bytes()) == source["record"]["sha256"], "Source changed during mix")
    script_data = Path(__file__).read_bytes()
    manifest = {
        "schemaVersion": 1, "status": "unapproved-offline-temporary-sfx-preview",
        "scopeNote": SCOPE_NOTE, "scriptPath": Path(__file__).relative_to(REPO).as_posix(),
        "scriptSha256": sha(script_data), "numpyVersion": np.__version__,
        "outputFormat": {"sampleRate": SAMPLE_RATE, "channels": CHANNELS, "sampleWidthBytes": SAMPLE_WIDTH},
        "mixPolicy": {"maximumGlobalGain": MAX_GLOBAL_GAIN, "maximumPeak": MAX_PEAK,
                      "limiterOrClippingUsed": False, "differentExistingFilesPreservedAndFail": True},
        "sources": [source["record"] for source in sources.values()],
        "cues": placed_records, "sequences": sequence_records,
        "dedicatedHumRecordingAvailable": False, "dedicatedClockRecordingAvailable": False,
        "newAudioSynthesis": False, "audioDownloads": False, "gameChanged": False,
        "gameExecuted": False, "humanListeningReview": "pending", "humanFinalApproval": "pending",
    }
    manifest_data = json_bytes(manifest)
    validation = {
        "schemaVersion": 1, "status": "passed-offline-technical-validation",
        "scopeNote": SCOPE_NOTE, "scriptSha256": sha(script_data),
        "audioCuesPath": "Source/audio-cues.json", "audioCuesSha256": sha(manifest_data),
        "sequences": sequence_records, "sourceHashesUnchanged": True,
        "cueCount": len(placed_records), "expectedCueCount": 18,
        "humanListeningReview": "not-performed", "humanFinalApproval": "pending",
        "newToneSynthesis": False, "audioDownloads": False, "gameExecuted": False,
        "gameFilesChanged": False,
    }
    require(len(placed_records) == validation["expectedCueCount"], "Unexpected cue count")
    outputs[ROOT / "Source/audio-cues.json"] = manifest_data
    outputs[ROOT / "QA/audio-validation.json"] = json_bytes(validation)
    preserve_or_write(outputs, args.check_only)
    print(json.dumps({"status": "validated" if args.check_only else "written-or-identical",
                      "sequences": sequence_records, "cueCount": len(placed_records),
                      "scopeNote": SCOPE_NOTE}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, wave.Error) as error:
        print("Audio mix stopped without overwriting existing output: " + str(error), file=sys.stderr)
        raise SystemExit(1)
