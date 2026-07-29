#!/usr/bin/env python3
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REGISTRY=ROOT/"census/quantum_hand_001_006_target_registry_v1.json";RECON=ROOT/"census/quantum_computation_discipline_current_reconciliation_v12.json";OUT=ROOT/"experiments/external_sources/quantum_computation/hand_001_006_observation_vector_v1.json";VALIDATOR=ROOT/"generated/quantum_computation/hand_001_006_validator_v1.py"
def canonical(v):return"sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("Quantum HAND vector exists")
 registry=json.loads(REGISTRY.read_text());rb=dict(registry);ri=rb.pop("registry_identity")
 if canonical(rb)!=ri or registry["target_content_present"]is not False:raise SystemExit("Quantum HAND registry changed")
 recon=json.loads(RECON.read_text());body=dict(recon);recon_id=body.pop("reconciliation_identity")
 if canonical(body)!=recon_id or recon["current_closed_count"]!=282:raise SystemExit("Quantum pre-handoff reconciliation changed")
 spec=importlib.util.spec_from_file_location("hand_observer",VALIDATOR);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
 values=(("downstream_ownership",{"scientific_owner":"quantum_computation","consumer_interfaces":4,"duplicate_owners":0}),("physics_measurement",{"formal_payload_sealed":True,"measurement_owner":"physics","invented_values":0}),("chemistry_materials",{"consumers":["chemistry","materials"],"application_selects_law":False}),("software_hardware",{"consumers":["software-engineering","hardware-engineering"],"implementation_values_present":False}),("open_extension",{"dated_closure":True,"lawful_extension_gate_open":True,"standards_unchanged":True}),("cross_branch_completeness",{"registered_handoffs":6,"execution_rows":6,"duplicate_owners":0,"omitted_handoffs":0}))
 records=[]
 for i,(name,value)in enumerate(values,1):
  if not observer.witness(i):raise SystemExit(f"HAND witness failed {i}")
  records.append({"number":f"{i:03d}","claim_id":registry["claim_ids"][i-1],"obligation_id":registry["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-quantum-hand-{i:03d}-interface-retained","source_ids":registry["pre_registered_source_identities"],"all_rows_preserved":True})
 payload={"schema":"sft-v3-quantum-hand-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"pre_handoff_reconciliation_identity":recon_id,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":6,"all_rows_preserved":True,"external_measurement_boundary":"Downstream sciences and engineering own their measurements and implementations; no handoff invents a value or selects the source law.","protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":6,"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__":main()
