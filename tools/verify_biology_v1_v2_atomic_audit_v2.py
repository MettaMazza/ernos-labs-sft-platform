#!/usr/bin/env python3
"""Biology atomic-audit verifier v2.

V1 is preserved with its ordering halt. V2 registers the immutable source
manifest order explicitly; it changes no scientific expectation or closure
condition.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audits/biology_v1_v2_atomic_ownership.json"
V1 = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2 = ROOT / "audits/v2_407_step_observation_census.json"
OBLIGATIONS = ROOT / "sft/biology/obligations.py"
EXPECTED_V1 = ("X-8", "X-7", "X-6", "X-5", "X-4", "X-3", "X-2", "X-1", "G17")
EXPECTED_V2 = (29, 37, 41, 84, 99, 144, 294, 295, 304)
EXPECTED_ATOMS = 30
EXPECTED_OBLIGATION_IDS = frozenset(
    line.split('"')[1]
    for line in OBLIGATIONS.read_text(encoding="utf-8").splitlines()
    if line.lstrip().startswith('row("')
)


def digest_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    doc = json.loads(AUDIT.read_text(encoding="utf-8"))
    identity = doc.pop("audit_identity")
    assert identity == digest_json(doc), "audit identity mismatch"
    assert doc["schema"] == "sft.biology.v1-v2-atomic-ownership-audit.v1"
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    rows = doc["source_rows"]
    assert len(rows) == v1["source_row_count"] + v2["source_step_count"] == 763
    assert doc["source_surface"]["total_source_rows_reviewed"] == 763
    assert tuple(doc["source_surface"]["biology_relevant_v1_rows"]) == EXPECTED_V1
    assert tuple(doc["source_surface"]["biology_relevant_v2_steps"]) == EXPECTED_V2
    assert sum(row["biology_owned"] for row in rows) == len(EXPECTED_V1) + len(EXPECTED_V2)
    atoms = [atom for row in rows for atom in row["biology_atoms"]]
    assert len(atoms) == EXPECTED_ATOMS
    atom_ids = [atom["atom_id"] for atom in atoms]
    assert len(atom_ids) == len(set(atom_ids))
    mapped = {claim_id for atom in atoms for claim_id in atom["current_v3_claim_ids"]}
    assert mapped <= EXPECTED_OBLIGATION_IDS, "audit maps outside the frozen Biology inventory"
    assert all(row["atomization_mode"] in {"explicit_atomic_decomposition", "explicit_nonbiology_disposition"} for row in rows)
    assert doc["authority_boundary"]["engine_modified"] is False
    assert doc["authority_boundary"]["engine_called_for_admission"] is False
    assert doc["authority_boundary"]["prior_answers_used_as_premises"] is False
    closed = sum(atom["same_strength_closed"] for atom in atoms)
    assert closed == doc["summary"]["same_strength_closed_atom_count"]
    assert len(atoms) - closed == doc["summary"]["same_strength_open_atom_count"]
    if doc["audit_status"] == "current_evidence_closed_extension_open":
        assert closed == len(atoms)
        assert not doc["missing_biology_atoms"]
        assert doc["summary"]["publication_blocked"] is False
    else:
        assert doc["audit_status"] == "open_missing_same_strength_biology_atoms"
        assert closed < len(atoms)
        assert doc["summary"]["publication_blocked"] is True
    print(f"biology atomic audit v2: PASS reviewed=763 atoms={len(atoms)} closed={closed} open={len(atoms)-closed}")


if __name__ == "__main__":
    main()
