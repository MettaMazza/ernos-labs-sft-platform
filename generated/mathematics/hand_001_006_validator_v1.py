#!/usr/bin/env python3
"""Implementation-distinct exact validator for HAND-001--006."""
import hashlib,json,sys
from itertools import product
from pathlib import Path
REL=("single-owner-downstream-reference","typed-measurement-boundary","sealed-formal-empirical-join","premise-free-correspondence-translation","dated-complete-extension-open","complete-cross-branch-handoff-certificate")
VECTOR_HASH="869ef00db9d85d6d9cccb612aebd197ae50ec3bc30912274b1a3747da500eade"
def witness(i,root):
 path=root/"experiments/external_sources/mathematics/hand_001_006_observation_vector_v1.json"
 if hashlib.sha256(path.read_bytes()).hexdigest()!=VECTOR_HASH:return False
 row=json.loads(path.read_text())["records"][i-1]["exact_observation"]
 if i==1:return row["ownership_transfer"] is False and row["duplicate_owner"] is False
 if i==2:return row["boundary_explicit"] and len(row["empirical_branch_owns"])==4
 if i==3:return row["joined_only_by_registered_target"]
 if i==4:return row["premise_role"] is False and row["correspondence_must_preserve_SFT_boundary"]
 if i==5:return row["lawful_extension_open"] and row["permanent_lock"] is False and row["new_claim_requires_full_protocol"]
 return row["pre_handoff_closed"]+row["registered_handoff_obligations"]==row["expected_post_handoff_total"]==row["frozen_census_total"]==323 and row["single_owner_required"]
def surface(i):
 axes=(("duplicated-or-transferred-owner","single-mathematics-owner"),("untyped-downstream-import",REL[i-1]),("measurement-as-math-premise","empirical-owner-post-seal-measurement"),("sampled-interfaces","complete-frozen-handoff-census"),("outcome-selected","root-bound-forward-forcing"),("conventional-model-premise","explicit-comparison-boundary"),("mutable-authority","unchanged-sealed-authority"),("permanent-lock-or-fit","dated-complete-lawful-extension"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i,root)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_handoff_witness":witness(i,root)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
