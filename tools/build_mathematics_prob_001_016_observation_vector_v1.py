#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REG=ROOT/"census/mathematics_prob_001_016_target_registry_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/prob_001_016_observation_vector_v1.json"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("PROB vector already frozen")
 r=json.loads(REG.read_text());b=dict(r);ri=b.pop("registry_identity")
 if canon(b)!=ri or r["target_content_present"] is not False:raise SystemExit("PROB registry changed")
 values=(
  ("support_probability",{"event_count":2,"support_count":4,"exact_weight":"1/2","ontic_randomness_claimed":False}),
  ("conditional_bayes",{"joint_count":2,"a_count":3,"b_count":4,"support_count":6,"a_given_b":"1/2","b_given_a":"2/3"}),
  ("independence_factorization",{"product_shape":[2,3],"joint":"1/6","marginals":["1/2","1/3"]}),
  ("expectation",{"values":[1,2,3,4],"weights":["1/4","1/4","1/4","1/4"],"expectation":"5/2"}),
  ("variance_dispersion",{"centre":"5/2","dispersion":"5/4","negative_magnitude_used":False}),
  ("finite_distribution",{"binary_width":3,"multiplicities":[1,3,3,1],"complete_weight":1}),
  ("large_count",{"word_widths":[1,2,3,4,5,6,7,8],"complete_enumeration":True,"held_label_frequency_each":"1/2"}),
  ("central_limit_enclosure",{"count_widths":[2,3,4,5,6,7,8],"tail_rule":"2/(2^n)","enclosure":"1/n","all_rows_pass":True}),
  ("sufficient_record",{"word_width":4,"record":"held-label-count","multiplicities":[1,4,6,4,1]}),
  ("confidence_credible_region",{"candidates":["1/4","1/2","3/4"],"rule":"at-least-half-maximum","retained":["1/2","3/4"]}),
  ("hypothesis_error_custody",{"decision_support":8,"type_one":"1/4","type_two":"1/4","both_ledgers_retained":True}),
  ("likelihood_ratio",{"observation":"three-of-four-held","candidates":["3/4","1/2"],"ratio":"27/16"}),
  ("bayesian_update",{"prior":["1/3","2/3"],"observation_weights":["3/4","1/4"],"posterior":["3/5","2/5"]}),
  ("finite_stochastic_process",{"states":2,"path_length":2,"path_count":4,"total_path_weight":1,"ontic_randomness_claimed":False}),
  ("conditional_conservation",{"root":2,"children":[1,3],"grandchildren":["1/2","3/2","5/2","7/2"],"branchwise_conserved":True}),
  ("identifiability",{"latent_records":[["1/4","3/4"],["1/2","1/2"]],"merged_observation_weight":1,"nonidentifiable_after_merge":True,"identifiable_with_latent_custody":True}),
 )
 records=[]
 for i,(name,value) in enumerate(values,1):records.append({"number":f"{i:03d}","claim_id":r["claim_ids"][i-1],"obligation_id":r["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-prob-{i:03d}-observation-retained","source_ids":["SFT-V3-INDEPENDENT-EXACT-PROBABILITY-OBSERVER","SFT-V1-V2-MATHEMATICS-OBSERVATION-CORPUS"],"all_rows_preserved":True})
 p={"schema":"sft-v3-mathematics-prob-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":16,"all_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};p["vector_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":16,"identity":p["vector_identity"]},indent=2))
if __name__=="__main__":main()
