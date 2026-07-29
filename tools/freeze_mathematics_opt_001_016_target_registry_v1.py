#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_opt_001_016_target_registry_v1.json"
IDS=("SFT-MATH-OPT-FEASIBLE-OBJECTIVE-ORDER-001","SFT-MATH-OPT-FINITE-EXTREMA-002","SFT-MATH-OPT-PARETO-DOMINANCE-003","SFT-MATH-OPT-LINEAR-PROGRAM-004","SFT-MATH-OPT-INTEGER-COMBINATORIAL-005","SFT-MATH-OPT-CONVEX-CORRESPONDENCE-006","SFT-MATH-OPT-DUAL-CERTIFICATE-007","SFT-MATH-OPT-VARIATIONAL-CORRESPONDENCE-008","SFT-MATH-OPT-DYNAMIC-PROGRAMMING-009","SFT-MATH-OPT-GENERATED-STATE-CONTROL-010","SFT-MATH-OPT-GAME-EQUILIBRIUM-011","SFT-MATH-OPT-DECISION-LOSS-012","SFT-MATH-OPT-FLOW-SCHEDULING-013","SFT-MATH-OPT-ROBUST-BOUNDED-UNCERTAINTY-014","SFT-MATH-OPT-APPROXIMATION-GAP-015","SFT-MATH-OPT-INFEASIBLE-UNBOUNDED-BOUNDARY-016")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("OPT registry already frozen")
 census=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in census["obligations"] if x["family"]=="OPT"]
 if len(obs)!=len(IDS)!=16:raise SystemExit("OPT census changed")
 p={"schema":"sft-v3-mathematics-opt-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":census["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all sixteen claims; no proper subset","prohibited_target_fields":["expected optimum","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":16,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
