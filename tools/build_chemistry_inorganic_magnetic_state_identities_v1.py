#!/usr/bin/env python3
"""Mechanically bind the complete value-free INORG-009 identity vector."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


LAW_PATH = "sft/chemistry/inorganic_magnetic_state_law_v1.py"
LAW_HASH = "sha256:27c299058fa6ec1489155395766f280e3cd6e29d0786828d0e75c2d0018e9452"
ADDENDUM_PATH = "experiments/external_sources/chemistry/inorg_009_magnetic_shared_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:b55fb12e09536da326158a016df2ccd028f4a0e8bb84ddb736a2252dbdbff161"
SHARED_IDENTITY_PATH = "experiments/external_sources/chemistry/magnetic_response_target_identities_v1.json"
SHARED_IDENTITY_HASH = "sha256:aeaf62719a5c7699f9743722df5ffbafb7ffc3337e366f8321bc2a2dbe357259"
OUTPUT = ROOT / "experiments/external_sources/chemistry/inorganic_magnetic_state_target_identities_v1.json"
IUPAC = (
    ("IUPAC-M03689", "magnetic susceptibility", "magnetic-susceptibility-definition", "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-m03689.json", "sha256:534938682aa98e7100d33d0b4dc9ce1f05f25df5e96531c2a5cd2f6964272bb8"),
    ("IUPAC-P04404", "paramagnetic", "paramagnetic-field-relation-definition", "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-p04404.json", "sha256:3193024dddd186c4f543531da9080f672dc57b07a92d743dc6c9baf52fc31959"),
    ("IUPAC-D01668", "diamagnetic", "diamagnetic-field-relation-definition", "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-d01668.json", "sha256:bee30fa49e3a8353347daf13172f50f3c0cca59bdffa790de8839aa3386ccd83"),
)


def main() -> None:
    for path, expected in ((LAW_PATH, LAW_HASH), (ADDENDUM_PATH, ADDENDUM_HASH), (SHARED_IDENTITY_PATH, SHARED_IDENTITY_HASH)):
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"INORG-009 sealed identity input changed: {path}")
    if OUTPUT.exists():
        raise SystemExit("INORG-009 identity vector already exists; preserved without regeneration")
    rows = []
    for ordinal, (source_id, identity, role, path, source_hash) in enumerate(IUPAC, start=1):
        if hash_file(ROOT / path) != source_hash:
            raise SystemExit(f"INORG-009 IUPAC source changed: {source_id}")
        rows.append({
            "target_id": f"SFT-CHEM-INORG-009-IUPAC-{ordinal:03d}", "source_record_ordinal": ordinal,
            "source_id": source_id, "authority": "IUPAC", "registered_identity": identity,
            "source_record_role": role, "custody_class": "family-identity-sealed-before-capture",
            "snapshot_path": path, "snapshot_sha256": source_hash,
        })
    shared = json.loads((ROOT / SHARED_IDENTITY_PATH).read_text(encoding="utf-8"))
    if shared.get("complete_target_count") != 174 or shared.get("all_magnetic_values_and_orientations_absent") is not True or len(shared.get("rows", ())) != 174:
        raise SystemExit("INORG-009 shared identity vector is not complete and value-free")
    for shared_ordinal, source in enumerate(shared["rows"], start=1):
        rows.append({
            "target_id": f"SFT-CHEM-INORG-009-NIST-{shared_ordinal:03d}",
            "source_record_ordinal": shared_ordinal + 3,
            "source_id": source["source_id"], "authority": "NIST",
            "registered_identity": source["measurement_kind"],
            "source_record_role": "shared-complete-magnetic-response-cell",
            "custody_class": "shared-prior-value-free-sealed-admitted-evidence",
            "shared_prior_target_id": source["target_id"],
            "database": source["database"], "source_locator": source["source_locator"],
            "section": source["section"], "table_ordinal": source["table_ordinal"],
            "row_ordinal": source["row_ordinal"], "column_ordinal": source["column_ordinal"],
            "magnetic_parameter": source["magnetic_parameter"], "identity_context": source["identity_context"],
        })
    document = {
        "schema": "sft-v3-chemistry-inorganic-magnetic-state-target-identities/1",
        "claim_id": "SFT-CHEM-INORGANIC-MAGNETIC-STATE-009", "obligation_id": "SFT-CHEM-OBL-INORG-009",
        "law_seal": {"path": LAW_PATH, "sha256": LAW_HASH},
        "shared_source_addendum": {"path": ADDENDUM_PATH, "sha256": ADDENDUM_HASH},
        "selection_rule": "Retain all three frozen IUPAC identities followed by all 174 shared PROP-012 identities in their original order.",
        "target_values_orientations_presence_flags_definitions_outcomes_or_payload_hashes_present": False,
        "complete_registered_target_count": 177, "rows": rows,
    }
    OUTPUT.write_text(json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(hash_file(OUTPUT))


if __name__ == "__main__":
    main()
