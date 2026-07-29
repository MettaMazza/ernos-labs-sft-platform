#!/usr/bin/env python3
"""Create deterministic text reconstructions for registered THERM PDFs."""
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/therm_001_007_v1"
MANIFEST = BASE / "source_custody_manifest.json"

def main():
    manifest = json.loads(MANIFEST.read_text())
    for row in manifest["documents"]:
        path = ROOT / row["snapshot_path"]
        if path.suffix.casefold() != ".pdf" or row["source_id"] == "NIST-PHONON-THERMAL-LIMITS":
            continue
        output = BASE / (path.stem + ".txt")
        if output.exists():
            raise SystemExit("refusing to overwrite THERM text reconstruction: " + str(output))
        pages = PdfReader(path).pages
        output.write_text("\n\f\n".join((page.extract_text() or "") for page in pages))
        print(output.relative_to(ROOT))

if __name__ == "__main__":
    main()
