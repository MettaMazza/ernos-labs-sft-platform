#!/usr/bin/env python3
"""Extract stable text companions for the two registered CRYS PDF snapshots."""

from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/crys_001_008_v3"


def main() -> None:
    for filename in ("nist-sp846-powder-diffraction.pdf", "nist-total-scattering-pdf-2014.pdf"):
        source = BASE / filename
        reader = PdfReader(source)
        pages = []
        for number, page in enumerate(reader.pages, 1):
            pages.append(f"\n\n--- page {number} ---\n\n{page.extract_text() or ''}")
        target = source.with_suffix(".txt")
        target.write_text("".join(pages), encoding="utf-8")
        print(f"{target.relative_to(ROOT)}: {len(reader.pages)} pages, {target.stat().st_size} bytes")


if __name__ == "__main__":
    main()
