#!/usr/bin/env python3
"""Freeze the complete CLASS-001--012 target surface before outcome capture."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_class_001_012_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-CLASS-SOLID-SOLUTION-ALLOY-001", "solid-solution and alloy phase organization", ("NIST-HEA-PHASE",)),
    ("002", "SFT-MAT-CLASS-INTERMETALLIC-ORDER-002", "ordered intermetallic compound organization", ("NIST-HEA-INTERMETALLIC", "NIST-HEA-PHASE")),
    ("003", "SFT-MAT-CLASS-HIGH-ENTROPY-BOUNDARY-003", "compositionally complex and high-entropy alloy boundary", ("NIST-HEA-PHASE", "NIST-HEA-INTERMETALLIC")),
    ("004", "SFT-MAT-CLASS-REFRACTORY-UHT-004", "refractory and ultra-high-temperature material class", ("NIST-HIGH-TEMP-CERAMICS",)),
    ("005", "SFT-MAT-CLASS-CEMENTITIOUS-CONCRETE-005", "cementitious and concrete composite organization", ("NIST-CEMENT-AM",)),
    ("006", "SFT-MAT-CLASS-FIBRE-REINFORCED-006", "fibre-reinforced composite load transfer", ("NIST-ADVANCED-COMPOSITES",)),
    ("007", "SFT-MAT-CLASS-PARTICLE-REINFORCED-007", "particle-reinforced composite load transfer", ("NIST-ADVANCED-COMPOSITES",)),
    ("008", "SFT-MAT-CLASS-METALLIC-GLASS-008", "metallic-glass organization", ("NIST-METALLIC-GLASS",)),
    ("009", "SFT-MAT-CLASS-CERAMIC-SUBCLASSES-009", "structural and functional ceramic subclasses", ("NIST-CERAMIC-AM", "NIST-HIGH-TEMP-CERAMICS")),
    ("010", "SFT-MAT-CLASS-POLYMER-SUBCLASSES-010", "thermoplastic, thermoset and elastomer distinction", ("NIST-MACROMOLECULAR-ARCHITECTURES", "NIST-THERMOSET-GLOSSARY")),
    ("011", "SFT-MAT-CLASS-FUNCTIONALLY-GRADED-011", "gradient and functionally graded material organization", ("NIST-AMMT-GRADED",)),
    ("012", "SFT-MAT-CLASS-ARCHITECTED-CELLULAR-012", "architected and cellular material organization", ("NIST-AUXETIC-ARCHITECTED",)),
)

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    payload = {
        "schema": "sft-v3-materials-class-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "metals_alloys_ceramics_glasses_polymers_composites",
        "selection_rule": "All twelve obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [{"obligation_id": f"SFT-MAT-OBL-CLASS-{number}", "claim_id": claim_id, "target_class": target, "source_identities": list(sources)} for number, claim_id, target, sources in ROWS],
        "target_count": 12,
        "all_family_members_registered": True,
        "target_content_present": False,
        "survivor_identity_present": False,
        "measured_value_present": False,
        "outcome_present": False,
        "failed_route_retires_obligation": False,
    }
    payload["registry_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(payload["registry_identity"])

if __name__ == "__main__":
    main()
