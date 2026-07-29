#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT/"experiments/external_sources/mathematics/graph_001_014_observation_vector_v1.json";OUT=ROOT/"experiments/external_sources/mathematics/graph_001_014_observation_vector_v2.json"
OLD_FILE_HASH="sha256:412bb2f69817c3f179953594940c62dfc1138ff995aad2281d680eb72282162c"
def canon(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def file_hash(path):return "sha256:"+hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("GRAPH corrected vector already frozen")
 if file_hash(OLD)!=OLD_FILE_HASH:raise SystemExit("GRAPH adverse predecessor changed")
 old=json.loads(OLD.read_text());body=dict(old);old_identity=body.pop("vector_identity")
 if canon(body)!=old_identity:raise SystemExit("GRAPH adverse predecessor identity changed")
 records=[dict(row) for row in old["records"]];last=dict(records[-1]);last["exact_observation"]={"time_respecting_path":[1,2,3,4],"arrival_time":3,"static_but_time_forbidden_path":[1,4,3]};last["correction_reason"]="The first proposed forbidden route shared a time-three terminal edge and therefore did not distinguish static from temporal reachability; the adverse row is preserved in the predecessor vector and this independent route reverses from time three to time two.";records[-1]=last
 value={"schema":"sft-v3-mathematics-graph-observation-vector/2","date":"2026-07-29","authority":"Maria Smith","registry_identity":old["registry_identity"],"adverse_predecessor_vector_identity":old_identity,"adverse_predecessor_file_hash":OLD_FILE_HASH,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":14,"all_rows_preserved":True,"adverse_rows_preserved":True,"protected_engine_or_verifier_edit_made":False};value["vector_identity"]=canon(value);OUT.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":14,"identity":value["vector_identity"],"adverse_predecessor":old_identity},indent=2))
if __name__=="__main__":main()
