#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_prob_001_016_target_registry_v1.json"
IDS=("SFT-MATH-PROB-SUPPORT-CORRESPONDENCE-001","SFT-MATH-PROB-CONDITIONAL-BAYES-002","SFT-MATH-PROB-INDEPENDENCE-FACTORIZATION-003","SFT-MATH-PROB-EXPECTATION-004","SFT-MATH-PROB-VARIANCE-DISPERSION-005","SFT-MATH-PROB-FINITE-DISTRIBUTION-006","SFT-MATH-PROB-LARGE-COUNT-007","SFT-MATH-PROB-CENTRAL-LIMIT-ENCLOSURE-008","SFT-MATH-PROB-ESTIMATION-SUFFICIENT-RECORD-009","SFT-MATH-PROB-CONFIDENCE-CREDIBLE-REGION-010","SFT-MATH-PROB-HYPOTHESIS-ERROR-CUSTODY-011","SFT-MATH-PROB-LIKELIHOOD-EVIDENCE-RATIO-012","SFT-MATH-PROB-BAYESIAN-UPDATE-013","SFT-MATH-PROB-FINITE-STOCHASTIC-PROCESS-014","SFT-MATH-PROB-CONDITIONAL-CONSERVATION-015","SFT-MATH-PROB-IDENTIFIABILITY-016")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("PROB registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="PROB"]
 if len(obs)!=len(IDS)!=16:raise SystemExit("PROB census changed")
 p={"schema":"sft-v3-mathematics-prob-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all sixteen claims; no proper subset","prohibited_target_fields":["expected probability","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":16,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
