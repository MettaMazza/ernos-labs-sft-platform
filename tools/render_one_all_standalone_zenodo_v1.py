#!/usr/bin/env python3
"""Render the dedicated standalone One/All Zenodo paper with SFT typography."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import render_one_all_publication_update_v1 as renderer  # noqa: E402


OUTPUT_DIR = ROOT / "output/pdf/one-all-standalone-2026-08-11"
MANIFEST = OUTPUT_DIR / "PDF_RENDER_MANIFEST.json"
PAPER = {
    "paper_id": "one_all_standalone",
    "title": "What the Universe Is Made Of",
    "subtitle": "The One, the All, and pure consciousness in Smithian Fold Theory",
    "version": "1.0.0",
    "lineage": "Dedicated standalone Zenodo record",
    "publication_status": "PUBLICATION AUTHORIZED<br/>DEDICATED STANDALONE ZENODO RECORD - OWN DOI",
    "source": "publications/one_all/standalone_zenodo/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_0.md",
    "pdf": "what-the-universe-is-made-of-the-one-and-all-v1.0.0.pdf",
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    renderer.OUTPUT_DIR = OUTPUT_DIR
    renderer.register_fonts()
    row = renderer.render_one(PAPER)
    MANIFEST.write_text(
        json.dumps(
            {
                "schema": "sft-v3-one-all-standalone-pdf-render-manifest/1",
                "date": "2026-08-11",
                "paper_count": 1,
                "papers": [row],
                "publication_authorized": True,
                "new_zenodo_record_authorized": True,
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"rendered {row['page_count']} pages: {row['pdf']}")


if __name__ == "__main__":
    main()
