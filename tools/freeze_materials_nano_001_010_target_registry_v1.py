#!/usr/bin/env python3
"""Freeze all NANO target identities before source capture or outcome extraction."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_nano_001_010_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-NANO-SIZE-SHAPE-DISTRIBUTION-001", "nanoparticle size and shape distribution", ("NIST-NANOPARTICLE-SIZE-SHAPE",)),
    ("002", "SFT-MAT-NANO-NANOWIRE-CONFINEMENT-002", "nanowire and one-dimensional confinement", ("NIST-GAN-NANOWIRE-GROWTH",)),
    ("003", "SFT-MAT-NANO-LAYER-STACKING-003", "two-dimensional layer and stacking organization", ("NIST-QUANTUM-TRANSPORT-2D-STACKING",)),
    ("004", "SFT-MAT-NANO-QUANTUM-DOT-CONFINEMENT-004", "quantum-dot finite confinement", ("NIST-NANOWORLD-QUANTUM-DOTS",)),
    ("005", "SFT-MAT-NANO-SURFACE-VOLUME-DOMINANCE-005", "surface-to-volume dominance relation", ("NIST-NANOPARTICLE-SURFACE-AREA",)),
    ("006", "SFT-MAT-NANO-PHASE-MELTING-BOUNDARY-006", "nanoscale phase and melting boundary", ("NIST-NANOCONFINED-FUSION",)),
    ("007", "SFT-MAT-NANO-QUANTUM-COLLECTIVE-STATE-007", "quantum-material collective-state classification", ("NIST-MOIRE-QUANTUM-PHASES",)),
    ("008", "SFT-MAT-NANO-MOIRE-SUPERSTRUCTURE-008", "moire and twisted-layer superstructure", ("NIST-MOIRE-EXCITONS",)),
    ("009", "SFT-MAT-NANO-NANOCOMPOSITE-INTERFACE-DENSITY-009", "nanocomposite interface density", ("NIST-NANOCOMPOSITE-INTERFACIAL-LAYER",)),
    ("010", "SFT-MAT-NANO-AGGREGATION-DISPERSION-CUSTODY-010", "nanomaterial aggregation and dispersion custody", ("NIST-NANOPARTICLE-AGGREGATION-DISPERSION",)),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    value = {
        "schema": "sft-v3-materials-nano-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "nanomaterials_two_dimensional_quantum_materials",
        "selection_rule": "All ten obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-NANO-{number}", "claim_id": claim_id, "target_class": target_class, "source_identities": list(source_ids)}
            for number, claim_id, target_class, source_ids in ROWS
        ],
        "target_count": 10,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    value["registry_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(value["registry_identity"])


if __name__ == "__main__":
    main()

