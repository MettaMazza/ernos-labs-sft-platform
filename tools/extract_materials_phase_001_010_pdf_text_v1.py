#!/usr/bin/env python3
"""Produce deterministic text reconstructions of the captured PHASE PDFs."""

from pathlib import Path
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/phase_001_010_v1"
NAMES = (
    "nist-binary-halide-transformations",
    "nist-martensitic-materials-study",
    "nist-phase-transition-temperatures-2025",
)


def main():
    for name in NAMES:
        source = BASE / f"{name}.pdf"
        target = BASE / f"{name}.txt"
        if target.exists():
            raise SystemExit("refusing to overwrite " + target.relative_to(ROOT).as_posix())
        pages = PdfReader(source).pages
        target.write_text("\n\f\n".join((page.extract_text() or "") for page in pages))
        print(f"{name}: {len(pages)} pages, {target.stat().st_size} bytes")


if __name__ == "__main__":
    main()
