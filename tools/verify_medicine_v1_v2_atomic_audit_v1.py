#!/usr/bin/env python3
"""Fail-closed verifier for the Medicine V1/V2 atomic ownership audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    audit = json.loads((ROOT / "audits/medicine_v1_v2_atomic_ownership.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "census/medicine_prior_obligations.json").read_text(encoding="utf-8"))
    rows = audit["source_rows"]
    errors = []
    if len(rows) != 763:
        errors.append("audit does not contain all 763 prior source entries")
    if len({(row["source"], row["source_entry"]) for row in rows}) != 763:
        errors.append("prior source identities repeat")
    if audit["source_surface"]["v1_row_count"] != 356 or audit["source_surface"]["v2_step_count"] != 407:
        errors.append("prior source cardinalities changed")
    atoms = [atom for row in rows for atom in row["medicine_atoms"]]
    if len(atoms) != 5 or len({atom["atom_id"] for atom in atoms}) != 5:
        errors.append("frozen Medicine prior atom set changed")
    if audit["source_surface"]["medicine_relevant_v1_rows"] != ["XIV-3"]:
        errors.append("Medicine V1 ownership surface changed")
    if audit["source_surface"]["medicine_relevant_v2_steps"] != [166, 176, 295]:
        errors.append("Medicine V2 ownership surface changed")
    if any(row["atomization_mode"] not in {"explicit_atomic_decomposition", "explicit_nonmedicine_disposition"} for row in rows):
        errors.append("a source row lacks explicit disposition")
    if ledger["reviewed_source_surface"]["reviewed_entry_count"] != 763:
        errors.append("ledger does not cover the full source surface")
    if audit["summary"]["same_strength_closed_atom_count"] + audit["summary"]["same_strength_open_atom_count"] != 5:
        errors.append("atom disposition count is incomplete")
    if errors:
        raise SystemExit("MEDICINE ATOMIC AUDIT HALTED:\n- " + "\n- ".join(errors))
    print(f"Medicine atomic audit structurally valid: 763 rows; 5 atoms; {audit['summary']['same_strength_closed_atom_count']} closed; {audit['summary']['same_strength_open_atom_count']} open")


if __name__ == "__main__":
    main()
