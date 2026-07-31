#!/usr/bin/env python3
"""Render a checked narration manifest with local Kokoro ONNX weights."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import soundfile as sf
from kokoro_onnx import Kokoro


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--voices", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    kokoro = Kokoro(str(args.model), str(args.voices))

    with tempfile.TemporaryDirectory(prefix="sft-kokoro-") as temporary:
        temp = Path(temporary)
        for filename, speaker, text in manifest["lines"]:
            samples, rate = kokoro.create(text, voice=manifest["voices"][speaker], speed=0.94, lang="en-gb")
            wave = temp / f"{filename}.wav"
            target = args.output / f"{filename}.mp3"
            sf.write(wave, samples, rate)
            subprocess.run([
                args.ffmpeg, "-loglevel", "error", "-y", "-i", str(wave),
                "-codec:a", "libmp3lame", "-b:a", "80k", "-ar", "24000", str(target),
            ], check=True)

    generated = sorted(args.output.glob("*.mp3"))
    receipt = {
        "schema": "sft-education-tts-receipt/1",
        "model": {"path_used": str(args.model), "sha256": sha256(args.model)},
        "voices": {"path_used": str(args.voices), "sha256": sha256(args.voices)},
        "manifest_sha256": sha256(args.manifest),
        "files": [{"name": path.name, "sha256": sha256(path)} for path in generated],
    }
    (args.output / "generation-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"Rendered {len(generated)} narrated lines to {args.output}")


if __name__ == "__main__":
    main()
