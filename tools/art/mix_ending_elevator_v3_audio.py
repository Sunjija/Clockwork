"""Mix six temporary, offline cues for the two separate ending candidates.

Reuse existing game land/switch WAV samples and the read-only v2 PCM helpers.
No visual production, new audio synthesis, game mutation, player execution,
video encoding or AVFoundation call occurs. These are cue-placement previews,
not final sound design: there are no dedicated lift-hum or clock recordings.
Differing outputs are preserved and cause a preflight failure before writes.
"""
from pathlib import Path
import argparse
import importlib.util
import io
import sys
import wave

import numpy as np


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "art/return-ending-elevator-v3"
HELPER_PATH = REPO / "tools/art/mix_full_cinematics_v2_audio.py"
SPEC = importlib.util.spec_from_file_location("clockwork_v2_audio_read_only", HELPER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the established PCM helper module")
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)

SAMPLE_RATE = 48000
CHANNELS = 2
SAMPLE_WIDTH = 2
MAX_GLOBAL_GAIN = .9
MAX_PEAK = .9
ALLOWED_SOURCES = {"land", "switch", "success"}
USED_SOURCES = ("land", "switch")
CLIPS = {"guardian-collapse": 3.0, "elevator-homecoming": 7.0}
SCOPE_NOTE = (
    "Unapproved offline temporary sound-placement preview for two separate "
    "ending clips. Existing land samples stand in for guardian settling; "
    "existing switch samples stand in for lift contacts and quiet clock ticks. "
    "No dedicated elevator hum or clock recordings exist in this package. "
    "No new tone synthesis, audio download, visual change, game change, game "
    "execution, video encoding or AVFoundation retry. Technical validation "
    "does not constitute listening review or human final approval."
)


def cue_plan():
    cue = HELPER.cue
    return [
        cue("collapse-soft-settle", "guardian-collapse", "guardian-collapse",
            "land", .85, .14, "Quiet existing land effect at the final crouch contact"),
        cue("lift-boarding-confirm", "elevator-homecoming", "elevator-homecoming",
            "switch", .76, .14, "Existing switch as the boarding contact confirmation"),
        cue("lift-ascent-start", "elevator-homecoming", "elevator-homecoming",
            "switch", 1.2, .07, "Small temporary switch contact at ascent start; not lift hum"),
        cue("lift-arrival-contact", "elevator-homecoming", "elevator-homecoming",
            "switch", 3.8, .10, "Small temporary switch contact at lift arrival"),
        cue("workshop-temporary-tick-1", "elevator-homecoming", "elevator-homecoming",
            "switch", 5.5, .025, "Quiet trimmed switch as a temporary workshop clock tick",
            trim=.03, fade_in_ms=1.0, fade_out_ms=5.0),
        cue("workshop-temporary-tick-2", "elevator-homecoming", "elevator-homecoming",
            "switch", 6.5, .025, "Quiet trimmed switch as a temporary workshop clock tick",
            trim=.03, fade_in_ms=1.0, fade_out_ms=5.0),
    ]


def preserve_or_write(outputs, check_only):
    """Preflight all four output paths; never overwrite differing bytes."""
    for path, data in outputs.items():
        HELPER.require(path.resolve().is_relative_to(ROOT.resolve()), "Output escapes new candidate root")
        HELPER.require(not path.is_symlink(), "Refusing output symlink: " + str(path))
        if path.exists():
            HELPER.require(path.is_file() and path.read_bytes() == data,
                           "Preserving different existing output: " + str(path))
        else:
            HELPER.require(not check_only, "Required output missing: " + str(path))
    if check_only:
        return
    for path, data in outputs.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(data)


def replay_from_manifest(record, placed, sources, wav_data):
    """Reconstruct each PCM track from recorded cue edits and source WAVs."""
    replay = np.zeros((record["frames"], CHANNELS), dtype=np.float64)
    for row in placed:
        if row["sequence"] != record["sequence"]:
            continue
        samples, edits = HELPER.prepare_cue(row, sources[row["source"]])
        HELPER.require(edits["sourceSha256"] == row["sourceSha256"], "Replay source hash mismatch")
        HELPER.require(edits["startOutputFrame"] == row["startOutputFrame"], "Replay cue timing mismatch")
        first = edits["startOutputFrame"]
        replay[first:first + len(samples)] += samples
    replay *= record["globalGain"]
    with wave.open(io.BytesIO(wav_data), "rb") as reader:
        actual_pcm = reader.readframes(reader.getnframes())
    expected_pcm = np.rint(replay * 32767.0).astype("<i2").tobytes()
    HELPER.require(actual_pcm == expected_pcm, "Recorded cue replay differs from WAV PCM")
    return {"recordedCuePcmReplayExact": True, "replayPcmSha256": HELPER.sha(expected_pcm)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true",
                        help="Reconstruct and validate exact existing output bytes without writing")
    args = parser.parse_args()
    plan = cue_plan()
    HELPER.require(len(plan) == 6, "Unexpected cue count")
    HELPER.require({row["source"] for row in plan} <= ALLOWED_SOURCES, "Non-allowed audio source")
    for row in plan:
        HELPER.require(0 < row["gain"] <= MAX_GLOBAL_GAIN, "Cue gain exceeds .9")
    sources = {name: HELPER.read_source(name) for name in USED_SOURCES}
    prepared = [HELPER.prepare_cue(row, sources[row["source"]]) for row in plan]
    outputs, records, placed = {}, [], []
    for name, duration in CLIPS.items():
        mixed = np.zeros((round(duration * SAMPLE_RATE), CHANNELS), dtype=np.float64)
        clip_cues = []
        for samples, edits in prepared:
            if edits["sequence"] != name:
                continue
            first, last = edits["startOutputFrame"], edits["startOutputFrame"] + len(samples)
            HELPER.require(0 <= first < last <= len(mixed), "Cue extends outside clip: " + edits["id"])
            mixed[first:last] += samples
            clip_cues.append(edits)
        raw_peak = float(np.max(np.abs(mixed)))
        HELPER.require(raw_peak > 0, "Unexpected silent clip")
        global_gain = min(MAX_GLOBAL_GAIN, MAX_PEAK / raw_peak)
        mixed *= global_gain
        data = HELPER.wav_bytes(mixed)
        record = HELPER.validate_wav(name, data, duration, global_gain, raw_peak, mixed)
        record["path"] = f"Clips/{name}/sound.wav"
        record["cueIds"] = [row["id"] for row in clip_cues]
        records.append(record)
        outputs[ROOT / record["path"]] = data
        for edits in clip_cues:
            placed.append({**edits, "sequenceGlobalGain": global_gain,
                           "effectiveGain": edits["gain"] * global_gain})
    for record in records:
        record.update(replay_from_manifest(record, placed, sources, outputs[ROOT / record["path"]]))
    for source in sources.values():
        HELPER.require(HELPER.sha(source["path"].read_bytes()) == source["record"]["sha256"],
                       "Existing source changed during mix")
    script_hash = HELPER.sha(Path(__file__).read_bytes())
    helper_hash = HELPER.sha(HELPER_PATH.read_bytes())
    manifest = {
        "schemaVersion": 1, "status": "unapproved-offline-temporary-sfx-preview",
        "scopeNote": SCOPE_NOTE, "scriptPath": Path(__file__).relative_to(REPO).as_posix(),
        "scriptSha256": script_hash, "numpyVersion": np.__version__,
        "readOnlyHelper": {"path": HELPER_PATH.relative_to(REPO).as_posix(),
                           "sha256": helper_hash, "oldMainInvoked": False,
                           "oldPreserveOrWriteInvoked": False},
        "outputFormat": {"sampleRate": SAMPLE_RATE, "channels": CHANNELS,
                         "sampleWidthBytes": SAMPLE_WIDTH, "encoding": "PCM16 little-endian stereo WAV"},
        "mixPolicy": {"maximumCueGain": MAX_GLOBAL_GAIN, "maximumGlobalGain": MAX_GLOBAL_GAIN,
                      "maximumPeak": MAX_PEAK, "limiterOrClippingUsed": False,
                      "differentExistingFilesPreservedAndFail": True},
        "sources": [source["record"] for source in sources.values()],
        "allowedExistingSourceNames": sorted(ALLOWED_SOURCES), "cues": placed, "clips": records,
        "visualTimingContract": {"guardian-collapse": 3000, "elevator-homecoming": 7000,
                                 "boardingConfirmationMs": 760, "ascentStartMs": 1200,
                                 "arrivalMs": 3800, "clockTickMs": [5500, 6500]},
        "dedicatedHumRecordingAvailable": False, "dedicatedClockRecordingAvailable": False,
        "newAudioSynthesis": False, "audioDownloads": False, "gameChanged": False,
        "gameExecuted": False, "videoEncoded": False, "avFoundationCalled": False,
        "humanListeningReview": "pending", "humanFinalApproval": "pending",
    }
    manifest_data = HELPER.json_bytes(manifest)
    validation = {
        "schemaVersion": 1, "status": "passed-offline-technical-validation",
        "scopeNote": SCOPE_NOTE, "scriptSha256": script_hash, "helperSha256": helper_hash,
        "audioCuesPath": "Source/audio-cues.json", "audioCuesSha256": HELPER.sha(manifest_data),
        "clips": records, "sourceHashesUnchanged": True, "cueCount": len(placed),
        "expectedCueCount": 6, "allRecordedCuePcmReplayExact": True,
        "humanListeningReview": "not-performed", "humanFinalApproval": "pending",
        "newToneSynthesis": False, "audioDownloads": False, "gameExecuted": False,
        "gameFilesChanged": False, "visualFilesChanged": False, "videoEncoded": False,
        "avFoundationCalled": False,
    }
    HELPER.require(len(placed) == validation["expectedCueCount"], "Unexpected placed cue count")
    outputs[ROOT / "Source/audio-cues.json"] = manifest_data
    outputs[ROOT / "QA/audio-validation.json"] = HELPER.json_bytes(validation)
    preserve_or_write(outputs, args.check_only)
    print(HELPER.json_bytes({"status": "validated" if args.check_only else "written-or-identical",
                            "clips": records, "cueCount": len(placed), "scopeNote": SCOPE_NOTE}).decode("utf-8"))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, wave.Error) as error:
        print("Audio mix stopped without overwriting existing output: " + str(error), file=sys.stderr)
        raise SystemExit(1)
