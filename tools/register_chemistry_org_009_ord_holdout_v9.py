#!/usr/bin/env python3
"""Register the complete non-USPTO ORD parquet holdout without opening rows."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
METADATA_URI = "https://datasets-server.huggingface.co/parquet?dataset=open-reaction-database/ord-data"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-ord-metadata-v9"
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v9.json"
EXCLUDED_USPTO_CONFIGS = {
    "ord_dataset-5481550056a14935b76e031fb94b88be",
    "ord_dataset-47eaacc46c3a4487bbdf99adb1a15e41",
    "ord_dataset-488402f6ec0d441ca2f7d6fabea7c220",
    "ord_dataset-e7830cd6b11158b43994ccfb5ee9acb3",
    "ord_dataset-1158e351757f315b93cbcbe7bc55f38e",
}


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    metadata_path = OUTPUT / "huggingface-parquet-metadata-v9.json"
    if metadata_path.exists() or IDENTITY.exists():
        raise SystemExit("ORG-009 V9 metadata or identity already exists; regeneration prohibited")
    request = Request(METADATA_URI, headers={"User-Agent": "Ernos-Labs-SFT/3 (Maria.Smith.Sftoe@gmail.com)"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()
        status = response.status
    if status != 200:
        raise SystemExit(f"ORG-009 V9 metadata request failed with status {status}")
    metadata = json.loads(payload)
    rows = [
        row
        for row in metadata["parquet_files"]
        if row["config"].startswith("ord_dataset-") and row["config"] not in EXCLUDED_USPTO_CONFIGS
    ]
    rows.sort(key=lambda row: row["config"])
    if len(rows) != 48 or sum(row["size"] for row in rows) != 12993815:
        raise SystemExit("ORG-009 V9 official non-USPTO ORD identity census changed")
    metadata_path.write_bytes(payload)
    identity = {
        "schema": "sft-v3-chemistry-org-009-target-identities/9",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "obligation_id": "SFT-CHEM-OBL-ORG-009",
        "registered_date": "2026-07-27",
        "all_v1_through_v8_results_must_remain_preserved": True,
        "preserved_v8_complete_result": {
            "complete_selected_product_count": 93,
            "favorable_count": 91,
            "adverse_count": 2,
            "unresolved_count": 0,
            "adverse_rows_independently_inscribed_confident_false": 2,
            "favorable_rows_independently_inscribed_confident_true": 91,
            "status": "universal_prediction_failed_and_preserved_not_postfiltered",
        },
        "repository_identity": {
            "authority": "Open Reaction Database official data repository mirrored on Hugging Face",
            "github_repository": "https://github.com/open-reaction-database/ord-data",
            "huggingface_repository": "https://huggingface.co/datasets/open-reaction-database/ord-data",
            "huggingface_repository_commit": "16ce3beca278610b8b039201b445ee4a17f791b4",
            "parquet_metadata_uri": METADATA_URI,
            "parquet_metadata_snapshot_path": metadata_path.relative_to(ROOT).as_posix(),
            "parquet_metadata_snapshot_sha256": sha256(payload),
        },
        "outcome_unopened_non_uspto_parquet_rows": [
            {
                "target_id": f"SFT-CHEM-ORG-009-ORD-{index:03d}",
                "config": row["config"],
                "split": row["split"],
                "uri": row["url"],
                "registered_filename": row["filename"],
                "registered_bytes": row["size"],
                "custody_class": "complete_parquet_payload_outcome_unopened_before_v9_seal",
            }
            for index, row in enumerate(rows, start=1)
        ],
        "complete_registered_payload_count": len(rows),
        "complete_registered_payload_bytes": sum(row["size"] for row in rows),
        "excluded_prior_corpus_boundary": {
            "excluded_uspto_config_count": len(EXCLUDED_USPTO_CONFIGS),
            "excluded_uspto_configs": sorted(EXCLUDED_USPTO_CONFIGS),
            "reason": "These five configurations duplicate the already opened USPTO-MIT or USPTO-grants corpus and cannot provide an independent holdout.",
        },
        "blind_selection_and_comparison_rule": {
            "source_only_selection": "After the 48 payloads open, retain every reaction whose non-product input structures contain exactly one three-nitrogen azide path and exactly one carbon-carbon alkyne triple support across distinct participating input carriers.",
            "independent_family_label": "Retain the complete source/procedure label inscription for every selected row. The explicit case-insensitive tokens click, CuAAC, azide-alkyne, azide alkyne, cycloaddition or triazole establish an independently labeled target subset before product structures open; absence of every token remains explicit.",
            "product_withholding": "Dataset/product outputs and product identifiers remain unread until the complete source-only identity and independent-label census is written and hash-sealed.",
            "atom_correspondence": "Enumerate every element-preserving exact input-output atom bijection; no imported mapping or favorable-only survivor may choose the correspondence.",
            "predicted_target": "Every independently labeled selected reaction admits at least one exact correspondence retaining all participating atoms and all source adjacencies, forming exactly two outer-azide-nitrogen to alkyne-carbon cross adjacencies in one of the two generated orientations, and relocating a positive finite multiplicity layer.",
            "complete_retention": "Preserve every labeled, unlabeled, favorable, adverse, absent, malformed, unresolved and no-product selected row.",
        },
        "native_arithmetic_boundary": "No external numerical zero, signed, decimal, continuum or conventional structure inscription enters native forcing; structural absence is EmptyOne.",
        "parquet_payload_open_count_before_v9_seal": 0,
    }
    IDENTITY.write_text(json.dumps(identity, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"identity": IDENTITY.relative_to(ROOT).as_posix(), "identity_sha256": sha256(IDENTITY.read_bytes()), "payload_count": len(rows), "payload_bytes": sum(row["size"] for row in rows)}, indent=2))


if __name__ == "__main__":
    main()
