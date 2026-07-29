#!/usr/bin/env python3
"""Create a deterministic text reconstruction of the captured NANO-006 PDF."""

from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/external_sources/materials/nano_001_010_v1/nist-nanoconfined-fusion.pdf"
TARGET = ROOT / "experiments/external_sources/materials/nano_001_010_v1/nist-nanoconfined-fusion.txt"


def main():
    if TARGET.exists():
        raise SystemExit("refusing overwrite")
    pages = PdfReader(SOURCE).pages
    TARGET.write_text("\n\f\n".join((page.extract_text() or "") for page in pages))
    print(f"NANO-006: {len(pages)} pages, {TARGET.stat().st_size} text bytes")


if __name__ == "__main__":
    main()

