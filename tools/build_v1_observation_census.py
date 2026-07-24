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


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def main() -> None:
    raw = SOURCE.read_bytes()
    if sha256(raw) != SOURCE_HASH:
        raise SystemExit("bound V1 theorem manifest hash changed")
    rows = []
    for line in raw.decode("utf-8").splitlines():
        match = ROW.match(line)
        if match is None or match.group(1) in {"id", "----"}:
            continue
        claim_id, kind, proof, status, statement = (part.strip() for part in match.groups())
        rows.append({
            "v1_claim_id": claim_id,
            "v1_kind": kind,
            "v1_proof_id": proof,
            "v1_recorded_status": status,
            "prior_result_observation": statement,
            "source_row_sha256": "sha256:" + sha256((line + "\n").encode("utf-8")),
            "explicit_v3_claim_ids": [],
            "explicit_mapping_status": "blocking_explicit_disposition_required",
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
        "mapped_row_count": 0,
        "unmapped_row_count": len(rows),
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)} rows={len(rows)}")


if __name__ == "__main__":
    main()
