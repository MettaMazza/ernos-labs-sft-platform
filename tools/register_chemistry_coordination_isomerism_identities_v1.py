#!/usr/bin/env python3
"""Register the value-free INORG-005 surface from the frozen family capture."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from sft.engine.source import hash_file  # noqa: E402

REGISTRY = ROOT / "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
INVENTORY_HASH = "sha256:e03724f16e4866b43b5f3b53a6804588a2c86f5405bcda37cfb717e5724bb7c2"
OUTPUT = ROOT / "experiments/external_sources/chemistry/coordination_isomerism_target_identities_v1.json"
SOURCE_IDS = ("IUPAC-I03294", "IUPAC-G02620", "IUPAC-O04308")
ROLES = ("complete-source-file", "presented-term-identity", "complete-definition-surface", "source-citation-status-license-disclaimer-surface")

def main():
    for p,h in ((REGISTRY,REGISTRY_HASH),(INVENTORY,INVENTORY_HASH)):
        if hash_file(p)!=h: raise SystemExit("VOID_INVALID_HALTED: INORG-005 family authority changed")
    reg=json.loads(REGISTRY.read_text()); inv=json.loads(INVENTORY.read_text())
    by_source={r['source_id']:r for r in reg['sources']}; by_capture={r['source_id']:r for r in inv['rows']}
    rows=[]
    for sid in SOURCE_IDS:
        s=by_source[sid]; c=by_capture[sid]
        for role in ROLES:
            rows.append({"target_id":f"SFT-CHEM-INORG005-ISOMER-{len(rows)+1:03d}","source_record_ordinal":len(rows)+1,"authority":s['authority'],"source_id":sid,"registered_identity":s['identity'],"source_record_role":role,"source_locator":s['uri'],"snapshot_path":c['snapshot_path'],"snapshot_sha256":c['snapshot_sha256']})
    payload={"schema":"sft-v3-coordination-isomerism-target-identities/1","chemistry_obligation":"SFT-CHEM-OBL-INORG-005","claim_id":"SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005","family_identity_registry_sha256":REGISTRY_HASH,"family_source_inventory_sha256":INVENTORY_HASH,"complete_registered_target_count":len(rows),"target_values_or_payload_hashes_present":False,"all_definition_class_example_formula_status_source_citation_license_disclaimer_and_target_payload_values_absent":True,"rows":rows}
    OUTPUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(hash_file(OUTPUT),len(rows))
if __name__=='__main__':main()
