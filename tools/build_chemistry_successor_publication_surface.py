#!/usr/bin/env python3
"""Build the Chemistry v1.2 publication surface from admitted evidence only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "publications/current/chemistry"
SUCCESSOR = ROOT / "publications/successors/chemistry"
INVENTORY = ROOT / "publications/inventories/successors/chemistry.json"
PAPER = CURRENT / "FROM_FOLD_TO_CHEMISTRY.md"
PDF = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.2.pdf"


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    live_ids = [row["claim_id"] for row in census if row["claim_id"].startswith("SFT-CHEM-")]
    evidence_path = CURRENT / "evidence_map_v1.2.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    rows = evidence["claims"]
    evidence_ids = [row["claim_id"] for row in rows]
    if len(live_ids) != 176 or len(evidence_ids) != 176 or set(live_ids) != set(evidence_ids):
        raise SystemExit("Chemistry successor inventory does not equal the 176-claim live census")

    paper_text = PAPER.read_text(encoding="utf-8")
    for row in rows:
        claim_id = row["claim_id"]
        if row["survivor_count"] != 1 or row["control_count"] != 4:
            raise SystemExit(f"invalid survivor/control cardinality: {claim_id}")
        if claim_id not in paper_text:
            raise SystemExit(f"paper omits live Chemistry claim: {claim_id}")
        receipt = ROOT / row["engine_receipt"]["path"]
        if not receipt.is_file() or sha(receipt) != row["engine_receipt"]["file_sha256"]:
            raise SystemExit(f"receipt file mismatch: {claim_id}")
        for item in row["evidence_files"].values():
            path = ROOT / item["path"]
            if not path.is_file() or sha(path) != item["sha256"]:
                raise SystemExit(f"evidence file mismatch: {claim_id}: {item['path']}")

    evidence["paper"] = {"path": PAPER.relative_to(ROOT).as_posix(), "sha256": sha(PAPER)}
    evidence["rendered_paper"] = {"path": PDF.relative_to(ROOT).as_posix(), "sha256": sha(PDF)}
    evidence["publication_authorized"] = True
    write_json(evidence_path, evidence)

    inventory = {
        "branch_id": "chemistry",
        "closure_boundary": "secure_foundation_plus_90_admitted_extensions_through_ORG-011",
        "extension_policy": "current_evidence_complete_at_each_registered_claim__open_to_lawful_extensions",
        "full_discipline_status": "active__97_declared_operations_remaining_after_ORG-011",
        "required_claim_count": len(live_ids),
        "required_claim_ids": live_ids,
        "schema": "sft-v3-chemistry-successor-inventory/1",
        "version": "1.2.0",
    }
    write_json(INVENTORY, inventory)

    manifest_path = CURRENT / "manifest_v1.2.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "comprehensive_derivation_coverage": True,
            "controls_passed": True,
            "evidence_map_sha256": sha(evidence_path),
            "paper_sha256": sha(PAPER),
            "publication_authorized": True,
            "ready_to_publish": True,
            "remote_action_permitted": True,
            "rendered_page_count": len(PdfReader(str(PDF)).pages),
            "rendered_paper_sha256": sha(PDF),
            "successor_inventory_path": INVENTORY.relative_to(ROOT).as_posix(),
            "successor_inventory_sha256": sha(INVENTORY),
        }
    )
    write_json(manifest_path, manifest)

    SUCCESSOR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PAPER, SUCCESSOR / "FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_2.md")
    shutil.copyfile(evidence_path, SUCCESSOR / "evidence_map.json")
    shutil.copyfile(manifest_path, SUCCESSOR / "manifest.json")
    shutil.copyfile(ROOT / "publication/chemistry_zenodo_metadata.json", SUCCESSOR / "zenodo_metadata.json")
    print(
        "CHEMISTRY_SUCCESSOR_SURFACE "
        f"claims={len(live_ids)} controls={sum(row['control_count'] for row in rows)} "
        f"paper_pages={manifest['rendered_page_count']}"
    )


if __name__ == "__main__":
    main()
