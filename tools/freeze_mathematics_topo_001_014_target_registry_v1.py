#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_topo_001_014_target_registry_v1.json"
IDS=("SFT-MATH-TOPO-OPEN-SET-SUPPORT-001","SFT-MATH-TOPO-CONTINUITY-TRANSPORT-002","SFT-MATH-TOPO-COMPACT-FINITE-SUBCOVER-003","SFT-MATH-TOPO-CONNECTED-COMPONENT-004","SFT-MATH-TOPO-SEPARATION-FINITE-005","SFT-MATH-TOPO-PRODUCT-QUOTIENT-SUBSPACE-006","SFT-MATH-TOPO-SIMPLICIAL-INCIDENCE-007","SFT-MATH-TOPO-HOMOTOPY-PATH-DEFORMATION-008","SFT-MATH-TOPO-FUNDAMENTAL-CYCLE-GROUP-009","SFT-MATH-TOPO-HOMOLOGY-BOUNDARY-010","SFT-MATH-TOPO-COHOMOLOGY-DUAL-OBSERVATION-011","SFT-MATH-TOPO-MANIFOLD-FINITE-ATLAS-012","SFT-MATH-TOPO-KNOT-LINK-INVARIANTS-013","SFT-MATH-TOPO-PERSISTENT-FEATURE-CUSTODY-014")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("TOPO registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="TOPO"]
 if len(obs)!=len(IDS) or len(IDS)!=14:raise SystemExit("TOPO census changed")
 p={"schema":"sft-v3-mathematics-topo-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all fourteen claims; no proper subset","prohibited_target_fields":["expected invariant","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":14,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
