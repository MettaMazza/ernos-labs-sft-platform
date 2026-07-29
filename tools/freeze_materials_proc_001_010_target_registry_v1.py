#!/usr/bin/env python3
"""Freeze all PROC target identities before source capture or outcome extraction."""

from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "census/materials_proc_001_010_target_registry_v1.json"
ROWS = (
    ("001", "SFT-MAT-PROC-CASTING-HISTORY-001", "casting and mould-filling material history", ("NIST-MOULD-FILLING",)),
    ("002", "SFT-MAT-PROC-FORMING-TEXTURE-002", "thermomechanical forming and texture", ("NIST-CRYSTALLOGRAPHIC-TEXTURE",)),
    ("003", "SFT-MAT-PROC-MACHINING-DAMAGE-003", "machining-induced surface and damage state", ("NIST-SUBSURFACE-DAMAGE",)),
    ("004", "SFT-MAT-PROC-ADDITIVE-BUILD-004", "additive layer-build and melt-pool history", ("NIST-MELT-POOL-COOLING",)),
    ("005", "SFT-MAT-PROC-THIN-FILM-GROWTH-005", "thin-film deposition and growth", ("NIST-PULSED-LASER-DEPOSITION",)),
    ("006", "SFT-MAT-PROC-EPITAXY-MATCHING-006", "epitaxial growth and lattice matching", ("NIST-NANOWIRE-LATTICE-MATCH",)),
    ("007", "SFT-MAT-PROC-JOINING-INTERFACE-007", "welding brazing and joining interface", ("NIST-WELD-MONITORING",)),
    ("008", "SFT-MAT-PROC-POLYMER-ORIENTATION-008", "polymer processing and orientation history", ("NIST-POLYMER-ORIENTATION",)),
    ("009", "SFT-MAT-PROC-POWDER-COMPACTION-009", "powder processing and compaction", ("NIST-POWDER-COMPACTION",)),
    ("010", "SFT-MAT-PROC-WINDOW-PROVENANCE-010", "process-window provenance and reproducibility ledger", ("NIST-REPRODUCIBLE-PROCESS-MONITORING",)),
)


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    value = {
        "schema": "sft-v3-materials-proc-target-identities/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "processing_solidification_sintering_heat_treatment_additive",
        "selection_rule": "All ten obligations and authoritative target identities are frozen as one whole subcategory before detailed outcome extraction.",
        "custody_disclosure": "Source identities and target classes only; no value, fragment, candidate, survivor or outcome.",
        "targets": [
            {"obligation_id": f"SFT-MAT-OBL-PROC-{number}", "claim_id": claim_id, "target_class": target_class, "source_identities": list(source_ids)}
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
