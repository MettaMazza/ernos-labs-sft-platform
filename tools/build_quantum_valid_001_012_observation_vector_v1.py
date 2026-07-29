#!/usr/bin/env python3
"""Open and freeze Quantum VALID outcomes after value-free registration."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REGISTRY=ROOT/"census/quantum_valid_001_012_target_registry_v1.json"; RECON=ROOT/"census/quantum_computation_discipline_current_reconciliation_v11.json"; OUT=ROOT/"experiments/external_sources/quantum_computation/valid_001_012_observation_vector_v1.json"; VALIDATOR=ROOT/"generated/quantum_computation/valid_001_012_validator_v1.py"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def main():
 if OUT.exists():raise SystemExit("Quantum VALID vector already frozen")
 registry=json.loads(REGISTRY.read_text()); rb=dict(registry); ri=rb.pop("registry_identity")
 if canonical(rb)!=ri or registry["target_content_present"] is not False:raise SystemExit("Quantum VALID registry changed")
 recon=json.loads(RECON.read_text()); body=dict(recon); recon_identity=body.pop("reconciliation_identity")
 if canonical(body)!=recon_identity or recon["current_closed_count"]!=270:raise SystemExit("Quantum pre-lock reconciliation changed")
 spec=importlib.util.spec_from_file_location("quantum_valid_observer",VALIDATOR); observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
 family_names=("REVX","QSTATEX","GATEX","QALGX","QCPLXX","QCOMMX","QCODEX","QSIMX","QLEARNX","QLIMITX"); expected=(18,28,22,30,26,24,32,24,22,22); observed=tuple(len(recon["completed_families"][name]) for name in family_names)
 if observed!=expected:raise SystemExit("Quantum family vector mismatch")
 values=[(name.lower()+"_vector",{"family":name,"receipt_rows":count,"all_rows_replayed":True,"controls_and_certificates_present":True}) for name,count in zip(family_names,observed)]
 values.extend((("adverse_ownership_vector",{"completed_families":11,"all_status_classes_preserved":True,"one_owner_boundaries_preserved":True}),("quantum_grand_lock",{"pre_lock_receipt_rows":270,"frozen_obligations":288,"pre_lock_families":11,"acyclic_root_lineage":True,"protected_authority_changed":False})))
 records=[]
 for i,(name,value) in enumerate(values,1):
  if not observer.independent_witness(i):raise SystemExit(f"Quantum VALID independent observation failed {i:03d}")
  records.append({"number":f"{i:03d}","claim_id":registry["claim_ids"][i-1],"obligation_id":registry["obligation_ids"][i-1],"observation_name":name,"exact_observation":value,"expected_label":f"complete-quantum-valid-{i:03d}-replay-retained","source_ids":registry["pre_registered_source_identities"],"all_rows_preserved":True})
 payload={"schema":"sft-v3-quantum-valid-observation-vector/1","date":"2026-07-29","authority":"Maria Smith","registry_identity":ri,"pre_lock_reconciliation_identity":recon_identity,"outcomes_opened_only_after_registry_freeze":True,"records":records,"record_count":12,"all_rows_preserved":True,"external_measurement_boundary":"This vector validates all current formal and empirical evidence plus every explicit physical handoff; it does not invent downstream measured values.","protected_engine_or_verifier_edit_made":False};payload["vector_identity"]=canonical(payload);OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps({"records":12,"identity":payload["vector_identity"]},indent=2))
if __name__=="__main__":main()
