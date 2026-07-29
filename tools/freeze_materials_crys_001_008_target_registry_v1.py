#!/usr/bin/env python3
"""Freeze the value-free external target identities for Materials CRYS-001--008."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_crys_001_008_target_registry_v1.json"


TARGETS = (
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-001",
        "claim_id": "SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001",
        "target_class": "complete measured diffraction-amplitude and intensity record",
        "source_identities": ("NIST-TOTAL-SCATTERING-PDF-2014", "IUCR-STACKING-DIFFUSE-2023"),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-002",
        "claim_id": "SFT-MAT-CRYS-STRUCTURE-FACTOR-002",
        "target_class": "finite constituent-position structure-factor composition record",
        "source_identities": ("NIST-SP846-POWDER-DIFFRACTION-1992", "NIST-TOTAL-SCATTERING-PDF-2014"),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-003",
        "claim_id": "SFT-MAT-CRYS-TEXTURE-ORIENTATION-003",
        "target_class": "polycrystal grain-orientation and phase-fraction measurement record",
        "source_identities": ("NIST-NCAL-TEXTURE-PHASE-FRACTION-2026",),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-004",
        "claim_id": "SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004",
        "target_class": "local correlation and measured diffuse-scattering record",
        "source_identities": ("IUCR-MODULATION-WAVE-DIFFUSE-2015", "IUCR-STACKING-DIFFUSE-2023"),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-005",
        "claim_id": "SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005",
        "target_class": "stacking-sequence and measured diffraction-consequence record",
        "source_identities": ("IUCR-STACKING-FAULT-LDH-2020", "IUCR-STACKING-DIFFUSE-2023"),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-006",
        "claim_id": "SFT-MAT-CRYS-TWIN-DOMAIN-006",
        "target_class": "crystal twin-operation, domain and diffraction record",
        "source_identities": ("IUCR-TWINNED-DIFFRACTION-DATA-2022", "IUCR-TWIN-DICTIONARY-2026"),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-007",
        "claim_id": "SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007",
        "target_class": "incommensurate modulation and satellite-reflection organization record",
        "source_identities": ("IUCR-MODULATED-STRUCTURES-2009", "IUCR-INCOMMENSURATE-DICTIONARY-2026"),
    },
    {
        "obligation_id": "SFT-MAT-OBL-CRYS-008",
        "claim_id": "SFT-MAT-CRYS-PAIR-DISTRIBUTION-008",
        "target_class": "total-scattering real-space pair-distribution reconstruction record",
        "source_identities": ("NIST-SP846-POWDER-DIFFRACTION-1992", "NIST-TOTAL-SCATTERING-PDF-2014"),
    },
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def main() -> None:
    body = {
        "schema": "sft-v3-materials-crys-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "quantitative_crystallography_diffraction_disorder",
        "selection_rule": (
            "The complete eight-obligation Materials CRYS family and official source identities are "
            "registered before detailed target documents, numerical rows, figures or outcomes are captured."
        ),
        "custody_disclosure": (
            "General scientific topics and official source landing identities were observed during development; "
            "specific target content, measurement rows and comparison outcomes were not opened into this registry."
        ),
        "targets": list(TARGETS),
        "target_count": len(TARGETS),
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    body["registry_identity"] = "sha256:" + sha256(canonical(body)).hexdigest()
    OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"path": OUT.relative_to(ROOT).as_posix(), "target_count": len(TARGETS), "registry_identity": body["registry_identity"]}, indent=2))


if __name__ == "__main__":
    main()
