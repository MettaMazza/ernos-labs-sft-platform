#!/usr/bin/env python3
"""Implementation-distinct exact validator for VALID-001--012."""
import hashlib,json,sys
from itertools import product
from pathlib import Path
REL=("complete-arithmetic-algebra-vector","complete-combinatorics-graph-vector","complete-linear-algebraic-vector","complete-order-geometry-vector","complete-topology-calculus-analysis-vector","complete-equation-measure-vector","complete-probability-statistics-vector","complete-optimization-dynamics-vector","complete-logic-compositional-vector","complete-numerical-symbolic-vector","complete-adverse-boundary-custody","complete-mathematics-validation-grand-lock")
EXPECTED=(55,26,30,28,42,22,16,28,28,22,8)
VECTOR_HASH="c6d5fde086cb181ea37cab74de4f6f3cd52d156f8e12f6e72d10d2a87d971d6e"
def witness(i,root):
 path=root/"experiments/external_sources/mathematics/valid_001_012_observation_vector_v1.json"
 if hashlib.sha256(path.read_bytes()).hexdigest()!=VECTOR_HASH:return False
 vector=json.loads(path.read_text());row=vector["records"][i-1]["exact_observation"]
 if i<=10:return row["claim_count"]==EXPECTED[i-1] and len(row["receipt_hashes"])==EXPECTED[i-1] and len(set(row["receipt_hashes"]))==EXPECTED[i-1]
 if i==11:return row["claim_count"]==8 and row["boundary_record_count"]==vector["boundary_record_count"]==305 and row["favorable_adverse_absent_unresolved_and_boundary_rows_preserved"]
 return row["covered_pre_validation_claims"]==row["unique_claim_ids"]==row["unique_receipt_hashes"]==305 and row["completed_family_count"]==22 and row["open_only_valid_and_hand"]==18 and row["all_named_groups_and_boundary_rows_present"]
def surface(i):
 axes=(("partial-or-duplicate-vector","complete-disjoint-receipt-vector"),("declared-pass-without-record",REL[i-1]),("favorable-only-selection","all-outcome-classes-retained"),("sampled-claims","complete-frozen-census-reconciliation"),("outcome-selected","root-bound-forward-forcing"),("preopened-result","post-registry-exact-observation"),("mutable-authority","unchanged-sealed-authority"),("permanent-lock-or-fit","dated-complete-extension-open"));rows=tuple("__".join(x) for x in product(*axes));return rows,"__".join(x[1] for x in axes)
def main():
 cid,root,path=sys.argv[1],Path(sys.argv[2]),Path(sys.argv[3]);i=int(cid.rsplit("-",1)[-1]);sealed=json.loads(path.read_text());rows,sur=surface(i);got=tuple(x["candidate_id"] for x in sealed["census"]["candidates"]);dec={x["candidate_id"]:bool(x["survives"]) for x in sealed["decisions"]};expected={x:x==sur for x in rows};passed=all((got==rows,len(set(got))==len(got)==256,dec==expected,sum(expected.values())==1,len(sealed["controls"])==4,all(x["passed"] for x in sealed["controls"]),sealed["closure"]["scope"]=="depth_independent",witness(i,root)));print(json.dumps({"passed":passed,"validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"certificate":{"candidate_count":256,"unique_survivor_count":1,"complete_validation_witness":witness(i,root)}}));raise SystemExit(0 if passed else 1)
if __name__=="__main__":main()
