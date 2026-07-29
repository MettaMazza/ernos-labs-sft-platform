#!/usr/bin/env python3
"""Extract stable text companions for registered MICRO PDF snapshots."""

from pathlib import Path
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/micro_001_009_v2"


def main():
    for filename in ("nist-dislocation-climb-monograph-59.pdf", "nist-segregation-precipitation-2021.pdf"):
        source = BASE / filename
        reader = PdfReader(source)
        target = source.with_suffix(".txt")
        target.write_text("".join(f"\n\n--- page {index} ---\n\n{page.extract_text() or ''}" for index, page in enumerate(reader.pages, 1)))
        print(f"{target.relative_to(ROOT)}: {len(reader.pages)} pages, {target.stat().st_size} bytes")


if __name__ == "__main__":
    main()
