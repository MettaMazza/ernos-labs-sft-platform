#!/usr/bin/env python3
"""Freeze value-free source identities for the complete MICRO-001--009 family."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_micro_001_009_target_registry_v1.json"


ROWS = (
    ("001", "SFT-MAT-MICRO-DEFECT-POPULATION-001", "defect population and site-fraction measurement", ("NIST-POINT-DEFECTS-2026",)),
    ("002", "SFT-MAT-MICRO-DEFECT-MIGRATION-002", "defect migration and retained-path record", ("NIST-POINT-DEFECTS-2026", "NIST-DISLOCATION-DYNAMICS-2021")),
    ("003", "SFT-MAT-MICRO-DISLOCATION-REACTION-003", "dislocation reaction, climb and cross-slip record", ("NIST-DISLOCATION-DYNAMICS-2021", "NIST-DISLOCATION-CLIMB-MONOGRAPH-59")),
    ("004", "SFT-MAT-MICRO-GRAIN-GROWTH-004", "curvature-driven grain-boundary motion record", ("NIST-SHARP-INTERFACE-GRAINS-2001",)),
    ("005", "SFT-MAT-MICRO-BOUNDARY-SEGREGATION-005", "grain-boundary segregation and composition record", ("NIST-SEGREGATION-PRECIPITATION-2021",)),
    ("006", "SFT-MAT-MICRO-PRECIPITATE-INCLUSION-006", "precipitation and coherent/incoherent interface record", ("NIST-STRUCTURES-PRECIPITATION-HANDBOOK", "NIST-SEGREGATION-PRECIPITATION-2021")),
    ("007", "SFT-MAT-MICRO-COARSENING-TRANSFER-007", "coarsening and conserved carrier-transfer record", ("NIST-STRUCTURES-PRECIPITATION-HANDBOOK",)),
    ("008", "SFT-MAT-MICRO-INTERFACE-MOBILITY-008", "interface migration, mobility and path record", ("NIST-SHARP-INTERFACE-GRAINS-2001", "NIST-UNIFIED-GRAIN-BOUNDARY-MOTION-2008")),
    ("009", "SFT-MAT-MICRO-MULTISCALE-CORRESPONDENCE-009", "microstructure-to-bulk multiscale property record", ("NIST-MULTISCALE-MATERIALS-2026", "NIST-MICROSTRUCTURE-PROPERTY-TOOLS-2026")),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main():
    payload = {
        "schema": "sft-v3-materials-micro-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "defects_microstructure_interfaces_multiscale",
        "selection_rule": "All nine obligations and official source identities are frozen before detailed source capture or outcome extraction.",
        "custody_disclosure": "Topic-level NIST search summaries were observed; no detailed target document, measurement row or outcome enters this registry.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-MICRO-{number}", "claim_id": claim_id, "target_class": target, "source_identities": list(sources)}
            for number, claim_id, target, sources in ROWS
        ],
        "target_count": 9,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"target_count": 9, "registry_identity": payload["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
