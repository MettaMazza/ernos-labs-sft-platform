#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_anal_001_016_target_registry_v1.json"
IDS=("SFT-MATH-ANAL-SEQUENCE-CONVERGENCE-001","SFT-MATH-ANAL-CAUCHY-SUPPORT-002","SFT-MATH-ANAL-COMPLETENESS-CORRESPONDENCE-003","SFT-MATH-ANAL-SERIES-REMAINDER-004","SFT-MATH-ANAL-POWER-SERIES-TRUNCATION-005","SFT-MATH-ANAL-FUNCTIONAL-SPACE-REPRESENTATION-006","SFT-MATH-ANAL-NORM-SEMINORM-METRIC-007","SFT-MATH-ANAL-BOUNDED-COMPACT-OPERATOR-008","SFT-MATH-ANAL-HARMONIC-FOURIER-SUPPORT-009","SFT-MATH-ANAL-TRANSFORM-INVERSION-010","SFT-MATH-ANAL-CONVOLUTION-CORRELATION-011","SFT-MATH-ANAL-ORTHOGONAL-BASIS-EXPANSION-012","SFT-MATH-ANAL-DISTRIBUTIONAL-WEAK-OBSERVATION-013","SFT-MATH-ANAL-NONLINEAR-CONTRACTION-014","SFT-MATH-ANAL-COMPLEX-HELD-PAIR-015","SFT-MATH-ANAL-SPECTRAL-MEASURE-016")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("ANAL registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="ANAL"]
 if len(obs)!=len(IDS) or len(IDS)!=16:raise SystemExit("ANAL census changed")
 p={"schema":"sft-v3-mathematics-anal-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all sixteen claims; no proper subset","prohibited_target_fields":["expected limit or transform value","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":16,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
