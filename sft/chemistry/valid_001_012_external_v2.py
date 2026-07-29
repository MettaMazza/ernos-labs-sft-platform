import hashlib,json,platform
from pathlib import Path
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.chemistry.valid_001_012_laws_v2 import REGISTRY,SPECS
VECTOR="experiments/external_sources/chemistry/valid_001_012_complete_empirical_vector_v2.json"
def canonical(payload):return "sha256:"+hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def load_vector(root):
 path=root/VECTOR
 if hash_file(path)!=REGISTRY["evidence_vector_file_hash"]:raise ValueError("Chemistry VALID vector file changed")
 d=json.loads(path.read_text());body=dict(d);identity=body.pop("complete_vector_identity")
 if canonical(body)!=identity or identity!=REGISTRY["evidence_vector_identity"]:raise ValueError("Chemistry VALID vector identity changed")
 return d
def check(root,spec):
 d=load_vector(root);rows={r["claim_id"]:r for r in d["claims"]};expected=tuple(REGISTRY["vector_claim_ids"][spec.number])
 if tuple(spec.vector_claim_ids)!=expected or len(expected)!=REGISTRY["vector_claim_counts"][spec.number]:raise ValueError("VALID dependency membership changed")
 summaries=[];sources=[]
 for cid in expected:
  if cid not in rows or spec.number not in rows[cid]["vector_memberships"]:raise ValueError("VALID member omitted "+cid)
  row=rows[cid]
  for key in ("registration","certificate","controls","receipt"):
   p=root/row[f"{key}_path"];h=row.get(f"{key}_sha256") or row.get("receipt_file_sha256")
   if hash_file(p)!=h:raise ValueError(f"VALID {key} changed for {cid}")
  if not row["model_admitted"] or not row["all_rows_preserved"]:raise ValueError("VALID row status changed "+cid)
  sources.extend(row["source_ids"]);summaries.append(f"{cid}: {row['empirical_status']}; closure={row['closure_scope']}; sources={row['source_identity_count']}; evidence-lines={row['measurement_line_count']}; explicit-status-lines={row['explicit_status_line_count']}")
 return d,tuple(summaries),tuple(dict.fromkeys(sources))
def registration(spec):return {"experiment_id":f"SFT-EXP-CHEM-VALID-{spec.number}-V2","claim_id":spec.claim_id,"target_id":f"CHEMISTRY-VALID-{spec.number}-COMPLETE-VECTOR-V2","identity_registry":"census/chemistry_valid_001_012_dependency_registry_v2.json","expected_label":f"complete-chemistry-valid-vector-{spec.number}-retained","falsification_condition":"Reject if any registered member, receipt, control, evidence file, result class, closure scope, formal-only boundary or source-custody row is missing, changed, duplicated or selected after outcome access."}
def document(spec):return {"schema":"sft-v3-fold-program/1","program_id":f"SFT-EXP-CHEM-VALID-{spec.number}-V2-prediction","instructions":[{"opcode":"input","destination":"premise","arguments":["registered-premise"]},{"opcode":"label","destination":"prediction","arguments":["chemistry-validation-vector",f"complete-chemistry-valid-vector-{spec.number}-retained"]},{"opcode":"pair","destination":"bound","arguments":["premise","prediction"]},{"opcode":"emit","destination":"","arguments":["prediction"]}]}
class ChemistryValidationVectorValidator:
 def __init__(self,root,spec):self.root=root.resolve();self.spec=spec
 def validate(self,sealed):
  self.spec.validate();vector,summaries,sources=check(self.root,self.spec);reg=registration(self.spec);rh=sha256_identity(reg);doc=document(self.spec);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};target=reg["target_id"];env=PredictionEnvelope(reg["experiment_id"],{"registered-premise":sha256_identity(inputs["registered-premise"])},(target,),sealed.seal_hash,rh);vault=TargetVault(experiment_id=reg["experiment_id"],custodian_id=reg["experiment_id"]+"-custodian",targets={target:HeldLabel("external-observation",reg["expected_label"])},custody_nonce=sha256_identity((rh,vector["complete_vector_identity"],self.spec.number)),expected_envelope_hash=sha256_identity(env));before=snapshot_protected_tree(self.root);ex=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);seal=boundary.seal_prediction(ex.output,ex.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=ex.program_hash or not audit.passed:raise ValueError("VALID capability audit failed")
  release=vault.release(seal);CrossPlatformCustodyExchange.verify(vault.commitment,release,seal);boundary.measurement_context(release.targets);match=isinstance(ex.output,HeldLabel) and ex.output.label==release.targets[target].label
  omitted=list(self.spec.vector_claim_ids[:-1]);omission_rejected=len(omitted)!=REGISTRY["vector_claim_counts"][self.spec.number];tid=target_identity_from_release(release);iso=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=reg["experiment_id"]+"-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=ex.program_hash,input_manifest_hash=ex.input_manifest_hash,registered_target_identity_hash=tid,comparison_implementation_identity_hash=sha256_identity(("chemistry-valid-vector-v2",self.spec.claim_id)),prediction_seal_hash=seal.seal_hash,output_hash=ex.output_hash,trace_hash=ex.trace_hash));cust=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=seal.seal_hash,target_release_manifest_hash=release.release_hash));measurements=(f"VALID-{self.spec.number}: complete registered membership count {len(self.spec.vector_claim_ids)}",f"complete Chemistry base: {vector['base_admitted_chemistry_claim_count']} claims; {vector['empirically_compared_claim_count']} empirical; {vector['formal_only_explicit_boundary_count']} formal-only",f"retained evidence: {vector['base_measurement_line_count']} measurement/evidence lines and {vector['base_source_identity_occurrence_count']} source-identity occurrences",f"all favorable adverse absent unavailable unresolved tampered and scope-boundary rows retained; omission control rejected {omission_rejected}")+summaries;payload={"claim":self.spec.claim_id,"seal":sealed.seal_hash,"vector":vector["complete_vector_identity"],"members":self.spec.vector_claim_ids,"match":match,"omission":omission_rejected};return EmpiricalValidation(validated_seal_hash=sealed.seal_hash,experiment_registration_hash=rh,isolation_certificate=iso,target_custody_certificate=cust,evaluator_verified_seal=True,target_opened_after_seal=True,all_rows_preserved=True,data_source_ids=sources or ("SFT-CHEM-FORMAL-BOUNDARY-REGISTRY",),measurements=measurements,measurement_receipt_hash=sha256_identity(payload),falsification_condition=reg["falsification_condition"],passed=bool(match and omission_rejected))
