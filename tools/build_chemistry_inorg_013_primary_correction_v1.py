#!/usr/bin/env python3
"""Correct INORG-013's pre-admission rendered-example boundary without changing its sealed identities."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from sft.engine.canonical import sha256_identity  # noqa:E402
from sft.engine.source import hash_file  # noqa:E402
IDENTITY_PATH="experiments/external_sources/chemistry/inorg_013_target_identities_v1.json"
IDENTITY_HASH="sha256:62bdd91e56629d4c841657ea94e339dd49b00913f11e58dbb73c67537ef46fa1"
PREDECESSOR_TARGET="experiments/external_sources/chemistry/inorg_013_withheld_targets_v1.json"
PREDECESSOR_TARGET_HASH="sha256:084892e879489e69e6c8219eadabc6a4c70e78235e107f75e1ced7fd578a5ad5"
def main():
 if hash_file(ROOT/IDENTITY_PATH)!=IDENTITY_HASH or hash_file(ROOT/PREDECESSOR_TARGET)!=PREDECESSOR_TARGET_HASH:raise SystemExit("INORG-013 sealed identity or preserved predecessor changed")
 identity=json.loads((ROOT/IDENTITY_PATH).read_text());old=json.loads((ROOT/PREDECESSOR_TARGET).read_text());rows=[]
 for ident,row in zip(identity["rows"],old["rows"]):
  if any(ident[k]!=row[k] for k in ident):raise SystemExit("predecessor target identity mismatch")
  outcome=dict(row["source_outcome"])
  if ident["source_record_role"]=="carbene-example-introduced-with-rendered-structure-absent":
   text=outcome["complete_definition_text"];segment=text.split("reaction:",1)[1].split("The reverse of an insertion",1)[0].strip();outcome["introduced_example_structure_present_after_colon"]=bool(segment);outcome["rendered_example_boundary_method"]="text strictly between example colon and following reverse-insertion sentence"
  corrected={**ident,"source_outcome":outcome};corrected["target_payload_hash"]=sha256_identity((ident["target_id"],ident["source_record_role"],outcome));rows.append(corrected)
 target={"schema":"sft-v3-postseal-complete-target-vector/2","claim_id":identity["claim_id"],"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"preserved_pre_admission_predecessor":(PREDECESSOR_TARGET,PREDECESSOR_TARGET_HASH),"correction_scope":"rendered example boundary only; identities, source bytes, law and comparison rows unchanged","release_requires_prediction_seal":True,"complete_registered_target_count":len(rows),"all_favourable_adverse_absent_scope_and_unresolved_rows_preserved":True,"rows":rows}
 tp=ROOT/"experiments/external_sources/chemistry/inorg_013_withheld_targets_v2.json";tp.write_text(json.dumps(target,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
 analysis={"complete_target_count":len(rows),"complete_source_count":len({x["source_id"] for x in rows}),"all_registered_surfaces_present":all(x["source_outcome"]["registered_surface_present"] for x in rows),"development_observed_target_count":sum("development-observed" in x["custody_class"] for x in rows),"identity_only_unopened_target_count":sum("identity-only-unopened" in x["custody_class"] for x in rows),"scope_distinction_count":sum("scope-distinction" in x["source_record_role"] for x in rows),"explicit_exclusion_count":sum("exclusion" in x["source_record_role"] for x in rows),"rendered_structure_absence_count":sum(x["source_outcome"].get("introduced_example_structure_present_after_colon") is False for x in rows),"complete_target_vector_hash":sha256_identity(tuple((x["target_id"],x["source_outcome"]) for x in rows)),"source_recapture_count":0,"all_rows_preserved":True}
 primary={"schema":"sft-v3-postseal-primary-analysis/2","claim_id":identity["claim_id"],"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"target_registry":("experiments/external_sources/chemistry/inorg_013_withheld_targets_v2.json",hash_file(tp)),"preserved_pre_admission_predecessor":(PREDECESSOR_TARGET,PREDECESSOR_TARGET_HASH),"exact_postseal_analysis":analysis}
 pp=ROOT/"experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-013-primary-records-v2.json";pp.write_text(json.dumps(primary,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8");print(tp.relative_to(ROOT),hash_file(tp));print(pp.relative_to(ROOT),hash_file(pp));print("rendered_structure_absence_count",analysis["rendered_structure_absence_count"])
if __name__=="__main__":main()
