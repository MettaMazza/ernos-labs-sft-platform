#!/usr/bin/env python3
"""Project the categorical Physics inventory from immutable admitted claims.

This utility is publication bookkeeping only.  It does not import V1/V2 rows,
execute a derivation, alter the admission engine, or change any claim receipt.
Exactly the live census rows whose registered branch is ``physics`` and whose
engine receipt is model-admitted enter the inventory.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402


CENSUS = ROOT / "census/claims.json"
OUTPUT = ROOT / "publications/inventories/physics.json"

SUBBRANCH_ORDER = (
    "measurement_metrology",
    "mechanics_dynamics",
    "fields_forces_waves_geometry",
    "thermodynamics_vacuum",
    "physical_quantum_relativistic",
    "constants_scales_precision",
    "matter_interactions_flavour",
    "atomic_molecular",
    "nuclear_hadronic",
    "spacetime_gravitation",
    "continua_collective_matter",
    "physical_cosmology_boundary",
    "post_seal_empirical_validation",
)

PREFIX_OWNER = {
    "MEAS": "measurement_metrology",
    "MECH": "mechanics_dynamics",
    "DYNAMICS": "mechanics_dynamics",
    "COUPLED": "mechanics_dynamics",
    "LYAPUNOV": "mechanics_dynamics",
    "ODD": "mechanics_dynamics",
    "ORBITAL": "mechanics_dynamics",
    "STRUCT": "fields_forces_waves_geometry",
    "SPACE": "fields_forces_waves_geometry",
    "FIELD": "fields_forces_waves_geometry",
    "FORCE": "fields_forces_waves_geometry",
    "WAVE": "fields_forces_waves_geometry",
    "THERMO": "thermodynamics_vacuum",
    "VACUUM": "thermodynamics_vacuum",
    "QUANTUM": "physical_quantum_relativistic",
    "QED": "physical_quantum_relativistic",
    "RELATIVITY": "physical_quantum_relativistic",
    "CONSTANT": "constants_scales_precision",
    "SCALE": "constants_scales_precision",
    "MATTER": "matter_interactions_flavour",
    "ELECTRON": "matter_interactions_flavour",
    "ELECTROWEAK": "matter_interactions_flavour",
    "WEAK": "matter_interactions_flavour",
    "STRONG": "matter_interactions_flavour",
    "NEUTRINO": "matter_interactions_flavour",
    "SCATTERING": "matter_interactions_flavour",
    "DECAY": "matter_interactions_flavour",
    "COUPLING": "matter_interactions_flavour",
    "ATOMIC": "atomic_molecular",
    "MOLECULAR": "atomic_molecular",
    "NUCLEAR": "nuclear_hadronic",
    "NUCLEON": "nuclear_hadronic",
    "HADRON": "nuclear_hadronic",
    "SPACETIME": "spacetime_gravitation",
    "GRAVITY": "spacetime_gravitation",
    "POST": "spacetime_gravitation",
    "SYMMETRIC": "spacetime_gravitation",
    "STATIC": "spacetime_gravitation",
    "QUADRUPOLE": "spacetime_gravitation",
    "CONTINUUM": "continua_collective_matter",
    "FLUID": "continua_collective_matter",
    "PLASMA": "continua_collective_matter",
    "CONDENSED": "continua_collective_matter",
    "COSMO": "physical_cosmology_boundary",
    "VALIDATION": "post_seal_empirical_validation",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    rows = [
        row for row in read(CENSUS)["claims"]
        if row.get("branch") == "physics" and row.get("model_admitted") is True
    ]
    if len({row["claim_id"] for row in rows}) != len(rows):
        raise SystemExit("duplicate model-admitted Physics claim")
    obligations = []
    for position, row in enumerate(rows, 1):
        prefix = row["claim_id"].split("-")[2]
        if prefix not in PREFIX_OWNER:
            raise SystemExit(f"unclassified Physics prefix: {prefix}")
        receipt = ROOT / row["receipt_path"]
        registration = ROOT / "claims" / row["claim_id"] / "registration.json"
        if not receipt.is_file() or not registration.is_file():
            raise SystemExit(f"missing receipt or registration: {row['claim_id']}")
        registered = read(registration)
        if registered.get("branch") != "physics":
            raise SystemExit(f"registration branch mismatch: {row['claim_id']}")
        receipt_payload = read(receipt)
        if receipt_payload.get("model_admitted") is not True or receipt_payload.get("receipt_hash") != row["receipt_hash"]:
            raise SystemExit(f"receipt mismatch: {row['claim_id']}")
        obligations.append({
            "position": position,
            "claim_id": row["claim_id"],
            "title": row["title"],
            "subbranch": PREFIX_OWNER[prefix],
            "status": "model_admitted",
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
        })
    counts = Counter(row["subbranch"] for row in obligations)
    payload = {
        "schema": "sft-v3-physics-branch-inventory/2",
        "branch_id": "physics",
        "inventory_status": "current_categorical_projection",
        "inventory_date": "2026-07-25",
        "scope": "Categorical reconstruction of measurement and metrology; mechanics and dynamics; physical geometry, forces, fields and waves; thermodynamics and vacuum; physical quantum and relativistic correspondence; constants, scales and precision; matter, interactions and flavour; atomic and molecular physics; nuclear and hadronic physics; spacetime and gravitation; fluids, plasmas and condensed collective matter; and only universal physical relations required at the Astronomy/Cosmology boundary.",
        "exclusions": [
            "astronomical object census, cosmic history and observed populations belong to Astronomy/Cosmology",
            "chemical species and chemical transformation belong to Chemistry",
            "materials properties and material processing belong to Materials",
            "biology, consciousness, social sciences and engineering translation remain their own branches",
            "Protein, Chess, Go and Unison application experiments remain excluded",
            "external equations, constants and measurements test only after a Fold relation is sealed",
        ],
        "ownership_rule": "A claim enters this inventory exactly when its claim registration and immutable model-admitted receipt both assign it to Physics. Cross-branch V1/V2 observations are never bulk-assigned to Physics.",
        "subbranch_order": list(SUBBRANCH_ORDER),
        "subbranch_counts": {name: counts[name] for name in SUBBRANCH_ORDER},
        "required_claim_count": len(obligations),
        "admitted_claim_count": len(obligations),
        "required_claim_ids": [row["claim_id"] for row in obligations],
        "unclassified_obligations": [],
        "obligations": obligations,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: {len(obligations)} Physics claims")


if __name__ == "__main__":
    main()
