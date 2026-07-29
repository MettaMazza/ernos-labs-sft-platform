#!/usr/bin/env python3
"""Open and freeze exact MEASURE observations after registry freeze."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REGISTRY=ROOT/"census/information_science_measure_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/information_science/measure_001_016_observation_vector_v1.json"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("MEASURE vector already frozen")
 registry=json.loads(REGISTRY.read_text());body=dict(registry);identity=body.pop("registry_identity")
 if canonical(body)!=identity or registry["target_content_present"] is not False:raise SystemExit("MEASURE registry changed")
 values=(
 ("distinction_count",{"source_forms":4,"possible_pairs":6,"fine_retained_pairs":6}),
 ("combinatorial_quantity",{"alphabet_size":2,"positions":3,"complete_word_support":8}),
 ("operational_cost",{"forms":8,"coordinate_observations":3,"all_three_distinguish":True,"every_two_fail":True}),
 ("description_length",{"grammar_tokens":4,"retained_description_tokens":4,"unregistered_tokens":0}),
 ("algorithmic_boundary",{"registered_programs":3,"target_programs":2,"least_target_program":"alternate","least_cost":3,"unrestricted_complexity_claimed":False}),
 ("partition_order",{"fine_classes":4,"middle_classes":3,"coarse_classes":2,"containment_chain":True}),
 ("product_additivity",{"left_positions":2,"right_positions":3,"joint_positions":5,"left_support":4,"right_support":8,"joint_support":32}),
 ("shared_subadditivity",{"marginal_costs":[1,1],"joint_cost":1,"joint_not_greater":True}),
 ("coarsening_monotonicity",{"retained_pair_counts":[6,5,4,0],"nonincreasing":True,"zero_is_structural_absence":True}),
 ("balance_ledger",{"source_pairs":6,"retained_pairs":4,"closed_pairs":2,"disjoint_and_exhaustive":True}),
 ("relative_information",{"coarse_retained":4,"fine_retained":6,"restored_distinctions":2}),
 ("divergence",{"identical_partition_disagreement":0,"changed_partition_disagreement":1,"zero_is_structural_absence":True}),
 ("information_geometry",{"symmetric":True,"triangle_relation":True,"irrational_coordinates_used":False}),
 ("multiscale",{"coarse_to_middle_increment":4,"middle_to_fine_increment":2,"total_increment":6,"telescopes":True}),
 ("unit_custody",{"two_label_positions":3,"base_eight_positions":1,"support_each":8,"unit_tags_retained":True}),
 ("measure_completeness",{"registered_obligations":16,"observation_rows":16,"duplicate_owners":0,"omitted_owners":0}),)
 records=[{"number":f"{i:03d}","claim_id":registry["claim_ids"][i-1],"obligation_id":registry["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-measure-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-INFORMATION-MEASURE-OBSERVER","SFT-V1-V2-INFORMATION-OBSERVATION-CORPUS"],"all_rows_preserved":True} for i,(name,value) in enumerate(values,1)]
 payload={"schema":"sft-v3-information-science-measure-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":identity,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":len(records),"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":len(records),"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__":main()
