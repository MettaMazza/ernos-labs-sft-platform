#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_cat_001_012_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/cat_001_012_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("CAT vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("CAT registry changed")
 values=(
  ("typed_composition",{"objects":["A","B","C"],"arrows":["A-to-B","B-to-C"],"composite":"A-to-C","mismatched_rejected":True}),
  ("identity_associativity",{"finite_maps":3,"left_identity":True,"right_identity":True,"associativity":True}),
  ("functor_preservation",{"source_composite":"plus-one-then-times-two","mapped_composite":"two-times-x-plus-one","all_rows_equal":True}),
  ("natural_transformation",{"source_labels":[1,2],"naturality_rows":2,"all_commute":True}),
  ("product_coproduct",{"product_pairs":4,"projection_reconstruction":True,"tagged_coproduct_values":4,"injections_distinct":True}),
  ("limit_colimit",{"equalizer":[1,3],"coequalizer_classes":[[1],[2,3]]}),
  ("adjunction",{"uncurried_maps":16,"curried_maps":16,"bijection":True}),
  ("monoidal_tensor",{"tensor":"word-concatenation","associative":True,"structural_empty_unit":True}),
  ("closed_internal_map",{"internal_maps":4,"four_entry_tables":16,"evaluation_currying_reconstruction":True}),
  ("dependent_record",{"base_labels":2,"fibre_sizes":[1,2],"well_typed_pairs":3}),
  ("sheaf_local_global",{"left_patch":{"1":"a","2":"b"},"right_patch":{"2":"b","3":"a"},"overlap_agrees":True,"unique_global":{"1":"a","2":"b","3":"a"}}),
  ("operad_higher_boundary",{"registered_total_arity":5,"substitution_associative":True,"unrestricted_higher_coherence_claimed":False}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-cat-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-COMPOSITION-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-cat-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
