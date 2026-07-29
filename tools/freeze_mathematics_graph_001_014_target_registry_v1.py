#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_graph_001_014_target_registry_v1.json"
IDS=("SFT-MATH-GRAPH-IDENTITY-ISOMORPHISM-001","SFT-MATH-GRAPH-PATH-REACHABILITY-CYCLE-002","SFT-MATH-GRAPH-CONNECTIVITY-CUT-FLOW-003","SFT-MATH-GRAPH-TREE-FOREST-SPANNING-004","SFT-MATH-GRAPH-PLANARITY-EMBEDDING-005","SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006","SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007","SFT-MATH-GRAPH-DIRECTED-CAUSAL-REACHABILITY-008","SFT-MATH-GRAPH-WEIGHTED-NETWORK-EXACT-PARTS-009","SFT-MATH-GRAPH-HYPERGRAPH-HIGHER-INCIDENCE-010","SFT-MATH-GRAPH-MATROID-INDEPENDENCE-011","SFT-MATH-GRAPH-RELIABILITY-FAILURE-CUSTODY-012","SFT-MATH-GRAPH-SPECTRAL-CORRESPONDENCE-013","SFT-MATH-GRAPH-DYNAMIC-TEMPORAL-NETWORK-014")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("GRAPH registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="GRAPH"]
 if len(obs)!=len(IDS) or len(IDS)!=14:raise SystemExit("GRAPH census changed")
 p={"schema":"sft-v3-mathematics-graph-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all fourteen claims; no proper subset","prohibited_target_fields":["expected count","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":14,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
