#!/usr/bin/env python3
"""Create three original, gentle looping scores for the offline learning game."""

from __future__ import annotations

import math
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np


RATE = 24_000
BEATS = 32


def midi(note: int) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def envelope(length: int, attack: float, release: float) -> np.ndarray:
    result = np.ones(length, dtype=np.float32)
    attack_samples = min(length, max(1, int(attack * RATE)))
    release_samples = min(length, max(1, int(release * RATE)))
    result[:attack_samples] = np.linspace(0.0, 1.0, attack_samples, dtype=np.float32)
    result[-release_samples:] *= np.linspace(1.0, 0.0, release_samples, dtype=np.float32)
    return result


def tone(frequency: float, seconds: float, kind: str = "soft", phase: float = 0.0) -> np.ndarray:
    count = max(1, int(seconds * RATE))
    t = np.arange(count, dtype=np.float32) / RATE
    if kind == "bell":
        raw = (
            np.sin(2 * math.pi * frequency * t + phase)
            + 0.42 * np.sin(2 * math.pi * frequency * 2.01 * t + phase * 0.7)
            + 0.16 * np.sin(2 * math.pi * frequency * 3.98 * t)
        )
        raw *= np.exp(-3.2 * t / max(seconds, 0.01))
    elif kind == "pluck":
        raw = np.sin(2 * math.pi * frequency * t + phase) + 0.22 * np.sin(2 * math.pi * frequency * 2 * t)
        raw *= np.exp(-5.2 * t / max(seconds, 0.01))
    else:
        raw = (
            0.72 * np.sin(2 * math.pi * frequency * t + phase)
            + 0.20 * np.sin(2 * math.pi * frequency * 2 * t + 0.4)
            + 0.08 * np.sin(2 * math.pi * frequency * 0.5 * t)
        )
    return (raw * envelope(count, 0.08 if kind == "soft" else 0.008, 0.32)).astype(np.float32)


def add_note(track: np.ndarray, note: int, start: float, duration: float, gain: float, pan: float, kind: str) -> None:
    sound = tone(midi(note), duration, kind, phase=(note % 7) * 0.17)
    first = int(start * RATE)
    last = min(track.shape[1], first + len(sound))
    if first >= last:
        return
    sound = sound[: last - first] * gain
    left = math.sqrt((1.0 - pan) / 2.0)
    right = math.sqrt((1.0 + pan) / 2.0)
    track[0, first:last] += sound * left
    track[1, first:last] += sound * right


def make_track(bpm: int, chords: list[tuple[int, int, int]], melody: list[int], style: str) -> np.ndarray:
    beat = 60.0 / bpm
    duration = BEATS * beat
    track = np.zeros((2, int(duration * RATE)), dtype=np.float32)

    for bar in range(BEATS // 4):
        chord = chords[bar % len(chords)]
        start = bar * 4 * beat
        for index, note in enumerate(chord):
            add_note(track, note, start, 4.15 * beat, 0.058, -0.45 + index * 0.45, "soft")
        add_note(track, chord[0] - 12, start, 3.8 * beat, 0.042, 0.0, "soft")

    if style == "stars":
        for step in range(BEATS * 2):
            if step % 4 in (0, 3):
                note = melody[step % len(melody)]
                add_note(track, note, step * beat / 2, 0.72 * beat, 0.082, -0.6 if step % 2 else 0.6, "bell")
        for bar in range(BEATS // 4):
            add_note(track, melody[(bar * 3) % len(melody)] + 12, (bar * 4 + 3.5) * beat, 0.8 * beat, 0.036, 0.7, "bell")
    elif style == "workshop":
        for step in range(BEATS * 2):
            note = melody[step % len(melody)]
            add_note(track, note, step * beat / 2, 0.54 * beat, 0.070, (-0.35, 0.35)[step % 2], "pluck")
        for beat_index in range(BEATS):
            add_note(track, 50 if beat_index % 4 in (0, 2) else 57, beat_index * beat, 0.32 * beat, 0.032, 0.0, "pluck")
    else:
        pattern = [0, 1, 0, 2, 0, 1, 3, 2]
        for step in range(BEATS * 2):
            note = melody[pattern[step % len(pattern)] % len(melody)]
            add_note(track, note, step * beat / 2, 0.46 * beat, 0.066, -0.45 if step % 2 else 0.45, "pluck")
        for bar in range(BEATS // 4):
            add_note(track, melody[(bar + 1) % len(melody)] + 12, (bar * 4 + 1.75) * beat, 0.9 * beat, 0.032, 0.65, "bell")

    # A quiet two-tap echo gives each loop a soft room rather than a hard edge.
    for delay_seconds, amount in ((0.19, 0.12), (0.37, 0.07)):
        delay = int(delay_seconds * RATE)
        track[:, delay:] += track[:, :-delay] * amount

    fade = min(int(0.45 * RATE), track.shape[1] // 8)
    track[:, :fade] *= np.linspace(0.0, 1.0, fade, dtype=np.float32)
    track[:, -fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    peak = float(np.max(np.abs(track))) or 1.0
    return np.clip(track / peak * 0.82, -1.0, 1.0)


def write_wave(path: Path, track: np.ndarray) -> None:
    pcm = (track.T * 32767).astype("<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes(pcm.tobytes())


def main() -> None:
    output = Path(__file__).resolve().parents[1] / "public" / "audio" / "music"
    output.mkdir(parents=True, exist_ok=True)
    scores = {
        "level-one": (72, [(48, 55, 64), (45, 52, 60), (41, 48, 57), (43, 50, 59)], [72, 76, 79, 83, 79, 76], "stars"),
        "level-two": (84, [(50, 57, 66), (47, 54, 62), (43, 50, 59), (45, 52, 61)], [66, 69, 73, 69, 71, 74, 73, 69], "workshop"),
        "level-three": (96, [(40, 47, 55), (48, 55, 64), (43, 50, 59), (38, 45, 54)], [64, 67, 71, 74], "trail"),
    }
    with tempfile.TemporaryDirectory(prefix="sft-story-music-") as temporary:
        temporary_path = Path(temporary)
        for name, (bpm, chords, melody, style) in scores.items():
            wave_path = temporary_path / f"{name}.wav"
            write_wave(wave_path, make_track(bpm, chords, melody, style))
            subprocess.run([
                "ffmpeg", "-loglevel", "error", "-y", "-i", str(wave_path),
                "-codec:a", "libmp3lame", "-b:a", "112k", "-ar", str(RATE), str(output / f"{name}.mp3"),
            ], check=True)
    print(f"Created {len(scores)} original looping scores in {output}")


if __name__ == "__main__":
    main()
