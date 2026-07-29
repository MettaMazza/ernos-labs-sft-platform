#!/usr/bin/env python3
"""Register the first three C3H8O records exposed by the sealed formula route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMULA = ROOT / "experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1/pubchem-c3h8o-formula-census-capture-url.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/comp_004_formula_linked_source_identity_addendum_v1.json"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("linked identity addendum already exists")
    identifiers = tuple(json.loads(FORMULA.read_text())["IdentifierList"]["CID"][:3])
    rows = []
    for cid in identifiers:
        rows.append({
            "source_id": f"PUBCHEM-C3H8O-LINKED-CID-{cid}",
            "cid": cid,
            "json_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON?record_type=2d",
            "sdf_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=2d",
        })
    payload = {
        "schema": "sft-v3-postseal-linked-source-identity-addendum/1",
        "family": "COMP-001-014-COMPUTATIONAL-CHEMISTRY-AND-CHEMINFORMATICS",
        "claim_id": "SFT-CHEM-CONSTITUTIONAL-ISOMER-ENUMERATION-004",
        "parent_formula_source_path": str(FORMULA.relative_to(ROOT)),
        "parent_formula_source_hash": digest(FORMULA),
        "selection_rule": "Capture exactly the first three record identities returned by the preregistered complete C3H8O formula route; do not inspect or select their structures before this addendum is written.",
        "postseal_identity_exposure_disclosed": True,
        "linked_records_never_relabelled_blind": True,
        "linked_records_allowed_to_select_or_change_native_law": False,
        "records": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"registered linked CIDs {identifiers}; addendum {digest(OUTPUT)}")


if __name__ == "__main__":
    main()
