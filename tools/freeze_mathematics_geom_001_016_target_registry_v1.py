#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/"census/mathematics_geom_001_016_target_registry_v1.json"
IDS=("SFT-MATH-GEOM-POINT-INCIDENCE-COORDINATE-001","SFT-MATH-GEOM-EUCLIDEAN-DISTANCE-002","SFT-MATH-GEOM-AFFINE-INVARIANCE-003","SFT-MATH-GEOM-PROJECTIVE-PERSPECTIVE-004","SFT-MATH-GEOM-CONVEX-HULL-SEPARATION-005","SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006","SFT-MATH-GEOM-POLYHEDRAL-EULER-INCIDENCE-007","SFT-MATH-GEOM-COMPUTATIONAL-PREDICATES-008","SFT-MATH-GEOM-ORIENTATION-INTERSECTION-009","SFT-MATH-GEOM-ALGEBRAIC-SOLUTION-SET-010","SFT-MATH-GEOM-DIFFERENTIAL-FINITE-CHART-011","SFT-MATH-GEOM-CURVATURE-FINITE-TRANSPORT-012","SFT-MATH-GEOM-METRIC-GEODESIC-013","SFT-MATH-GEOM-FRACTAL-SELF-SIMILAR-014","SFT-MATH-GEOM-PACKING-COVERING-TESSELLATION-015","SFT-MATH-GEOM-TRANSFORMATION-GROUPS-016")
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("GEOM registry already frozen")
 c=json.loads((ROOT/"census/mathematics_discipline_obligations.json").read_text());obs=[x for x in c["obligations"] if x["family"]=="GEOM"]
 if len(obs)!=len(IDS) or len(IDS)!=16:raise SystemExit("GEOM census changed")
 p={"schema":"sft-v3-mathematics-geom-value-free-registry/1","date":"2026-07-29","authority":"Maria Smith","frozen_before_observation_access":True,"target_content_present":False,"mathematics_census_identity":c["census_identity"],"claim_ids":IDS,"obligation_ids":[x["obligation_id"] for x in obs],"question_titles":[x["title"] for x in obs],"completion_unit":"all sixteen claims; no proper subset","prohibited_target_fields":["expected coordinate result","selected survivor","match result","imported theorem answer"]};p["registry_identity"]=canon(p);OUT.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n");print(json.dumps({"claims":16,"identity":p["registry_identity"]},indent=2))
if __name__=="__main__":main()
