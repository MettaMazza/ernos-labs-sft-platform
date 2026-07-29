#!/usr/bin/env python3
"""Freeze value-free authoritative target identities for PHASE-001--010."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_phase_001_010_target_registry_v1.json"


ROWS = (
    ("001", "SFT-MAT-PHASE-FRACTION-LEDGER-001", "complete measured multiphase composition and phase-fraction record", ("NIST-TEXTURE-PHASE-FRACTION", "NIST-LEVER-RULE-SOLIDIFICATION")),
    ("002", "SFT-MAT-PHASE-TIE-LINE-LEVER-002", "coexisting endpoint, bulk composition, tie-line and lever-partition record", ("NIST-LEVER-RULE-SOLIDIFICATION", "NIST-LLE-TERNARY-TIE-LINES")),
    ("003", "SFT-MAT-PHASE-COMPONENT-HANDOFF-003", "component activity and phase-coexistence handoff record", ("NIST-SAT-TMMC-COEXISTENCE",)),
    ("004", "SFT-MAT-PHASE-METASTABLE-RETENTION-004", "metastable state, condition and retained observation-path record", ("NIST-LIQUID-WATER-METASTABLE", "NIST-BINARY-HALIDE-TRANSFORMATIONS")),
    ("005", "SFT-MAT-PHASE-SPINODAL-INSTABILITY-005", "spinodal and separation-amplifying instability record", ("NIST-LIQUID-WATER-METASTABLE", "NIST-ORDER-DISORDER-SEPARATION")),
    ("006", "SFT-MAT-PHASE-MARTENSITIC-006", "displacive martensitic transformation, shape and retained-identity record", ("NIST-MARTENSITIC-MATERIALS-STUDY",)),
    ("007", "SFT-MAT-PHASE-RECONSTRUCTIVE-007", "reconstructive or irreversible topology-changing transformation record", ("NIST-BINARY-HALIDE-TRANSFORMATIONS",)),
    ("008", "SFT-MAT-PHASE-ORDER-DISORDER-008", "ordered and disordered state transition record", ("NIST-ORDER-DISORDER-SEPARATION", "NIST-BINARY-HALIDE-TRANSFORMATIONS")),
    ("009", "SFT-MAT-PHASE-GLASS-ARREST-009", "glass transition, kinetic arrest, measurement and physical-aging record", ("NIST-GLASS-TRANSITION",)),
    ("010", "SFT-MAT-PHASE-TIME-TEMPERATURE-010", "complete transformation kinetics and time-temperature path record", ("NIST-SOLIDIFICATION", "NIST-PHASE-TRANSITION-TEMPERATURES")),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("refusing to overwrite frozen PHASE target registry")
    payload = {
        "schema": "sft-v3-materials-phase-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "phase_equilibria_transformations_metastability",
        "selection_rule": "All ten obligations and authoritative source identities are frozen before source capture, fragment extraction or outcome comparison.",
        "custody_disclosure": "Source titles and topic-level summaries identify measurement classes only; no target value, detailed outcome, survivor or favourable fragment enters this registry.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-PHASE-{number}", "claim_id": claim_id, "target_class": target, "source_identities": list(sources)}
            for number, claim_id, target, sources in ROWS
        ],
        "target_count": 10,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"target_count": 10, "registry_identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
