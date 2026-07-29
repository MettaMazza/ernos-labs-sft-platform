#!/usr/bin/env python3
"""Reconstruct the captured NISTIR 7458 text without altering source custody."""
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/opt_001_010_v1"

def main():
    source = BASE / "nistir7458-fluorescence-quantum-yield.pdf"
    target = BASE / "nistir7458-fluorescence-quantum-yield.txt"
    if target.exists():
        raise SystemExit("refusing overwrite")
    pages = PdfReader(source).pages
    target.write_text("\n\f\n".join((page.extract_text() or "") for page in pages))
    print(len(pages), target.stat().st_size)

if __name__ == "__main__":
    main()
