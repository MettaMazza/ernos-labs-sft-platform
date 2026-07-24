#!/usr/bin/env python3
"""Register every V1 theorem-manifest row as prior observational data."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/mettamazza/Desktop/SFTOM/pure/THEOREM_MANIFEST.md")
SOURCE_HASH = "1539c1a4cc576ed9a167e1225534788a24737fcb10f53e9c10370dfd7c82d3f6"
OUTPUT = ROOT / "audits/v1_theorem_manifest_observation_census.json"
ROW = re.compile(r"^\| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| (.*) \|$")


EXPLICIT_MAPPINGS: dict[str, tuple[str, ...]] = {
    "M15": ("SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",),
    "M16": (
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
    ),
    "M17": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",),
    "M20": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",),
    "M21": (
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
    ),
    "M22": (
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
    ),
    "N8b": ("SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",),
    "G11": ("SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",),
}


CLOSED_DISPOSITIONS: dict[str, dict[str, object]] = {
    "M15": {
        "status": "closed_by_exact_postseal_empirical_validation",
        "closed": True,
        "receipt_hash": "sha256:369a1e48d622bba0f3e4abc1e89fef8553b17097c3d8c4427afca26386f6cbf9",
    },
    "N8b": {
        "status": "closed_by_joint_structural_and_empirical_admission",
        "closed": True,
        "receipt_hash": "sha256:38b06863d5a59f8f8ea17fee7a0a1d5ff1fdcd0c6f7b9de3e9f635705d4f8cc2",
    },
    "G11": {
        "status": "closed_by_observational_reconstruction_and_joint_empirical_admission",
        "closed": True,
        "receipt_hash": "sha256:d4ce8d8568e94b5032fc65633d024aaa7cba6365e6d88217c61ec9a388153e88",
    },
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    raw = SOURCE.read_bytes()
    if sha256(raw) != SOURCE_HASH:
        raise SystemExit("bound V1 theorem manifest hash changed")
    admitted = {
        row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]
        if row.get("model_admitted")
    }
    rows = []
    for line in raw.decode("utf-8").splitlines():
        match = ROW.match(line)
        if match is None or match.group(1) in {"id", "----"}:
            continue
        claim_id, kind, proof, status, statement = (part.strip() for part in match.groups())
        mapped = EXPLICIT_MAPPINGS.get(claim_id, ())
        missing = tuple(value for value in mapped if value not in admitted)
        mapping_status = (
            "mapped_to_current_admitted_claims" if mapped and not missing
            else "mapped_claim_missing" if missing
            else "blocking_explicit_disposition_required"
        )
        if claim_id in CLOSED_DISPOSITIONS:
            disposition = CLOSED_DISPOSITIONS[claim_id]
        elif mapping_status == "mapped_to_current_admitted_claims":
            disposition = {
                "status": "mapped_same_strength_review_pending",
                "closed": False,
            }
        else:
            disposition = {"status": mapping_status, "closed": False}
        rows.append({
            "v1_claim_id": claim_id,
            "v1_kind": kind,
            "v1_proof_id": proof,
            "v1_recorded_status": status,
            "prior_result_observation": statement,
            "source_row_sha256": "sha256:" + sha256((line + "\n").encode("utf-8")),
            "explicit_v3_claim_ids": list(mapped),
            "explicit_mapping_status": mapping_status,
            "missing_mapped_claim_ids": list(missing),
            "same_strength_disposition": disposition,
        })
    if len(rows) != 356:
        raise SystemExit(f"expected 356 V1 manifest rows, found {len(rows)}")
    payload = {
        "schema": "sft-v3-v1-prior-observation-census/1",
        "status": "open_blocking_until_every_v1_result_has_explicit_v3_disposition",
        "source_path": str(SOURCE),
        "source_sha256": "sha256:" + SOURCE_HASH,
        "source_row_count": len(rows),
        "source_kind_counts": {
            kind: sum(row["v1_kind"] == kind for row in rows)
            for kind in sorted({row["v1_kind"] for row in rows})
        },
        "policy": {
            "prior_results_are_observational_data": True,
            "prior_results_define_reconstruction_obligations": True,
            "prior_answer_artifacts_may_enter_v3_derivation": False,
            "prior_observation_may_select_v3_candidate_or_survivor": False,
        },
        "mapped_row_count": sum(row["explicit_mapping_status"] == "mapped_to_current_admitted_claims" for row in rows),
        "unmapped_row_count": sum(row["explicit_mapping_status"] == "blocking_explicit_disposition_required" for row in rows),
        "same_strength_closed_row_count": sum(bool(row["same_strength_disposition"]["closed"]) for row in rows),
        "same_strength_open_row_count": sum(not bool(row["same_strength_disposition"]["closed"]) for row in rows),
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} rows={len(rows)}")


if __name__ == "__main__":
    main()
