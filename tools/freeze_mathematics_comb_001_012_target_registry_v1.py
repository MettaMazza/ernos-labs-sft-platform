#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_comb_001_012_target_registry_v1.json"
IDS=("SFT-MATH-COMB-COUNTING-LAWS-001","SFT-MATH-COMB-PERMUTATION-COMBINATION-002","SFT-MATH-COMB-INCLUSION-EXCLUSION-003","SFT-MATH-COMB-PIGEONHOLE-OCCUPANCY-004","SFT-MATH-COMB-RECURRENCE-GENERATING-005","SFT-MATH-COMB-PARTITION-INCIDENCE-006","SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007","SFT-MATH-COMB-PROBABILISTIC-METHOD-CORRESPONDENCE-008","SFT-MATH-COMB-DESIGN-INCIDENCE-009","SFT-MATH-COMB-CODING-PACKING-010","SFT-MATH-COMB-RAMSEY-FORCING-011","SFT-MATH-COMB-SPECIES-COMPOSITION-012")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("COMB registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="COMB"]
 if len(obs)!=len(IDS)!=12:raise SystemExit("COMB census changed")
 p={"schema":"sft-v3-mathematics-comb-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all twelve claims; no proper subset","prohibited_target_fields":["expected count","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":12,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
