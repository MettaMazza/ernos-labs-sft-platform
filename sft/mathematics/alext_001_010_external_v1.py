"""Post-registry exact observation validator for ALEXT-001--010."""
import hashlib,json,platform
from pathlib import Path
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
REGISTRY="census/mathematics_alext_001_010_target_registry_v1.json";REGISTRY_HASH="sha256:1a4ecd513ec25fdbbe43ad7a4f95f2544081acb033cadb1eb4212c79a8d004af"
VECTOR="experiments/external_sources/mathematics/alext_001_010_observation_vector_v1.json";VECTOR_HASH="sha256:569d4c4e6c7b5637eb7f51466e1f9d20db66be92c1e43c31c0fd2047bd390be7"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def load(root):
 rp=root/REGISTRY;vp=root/VECTOR
 if hash_file(rp)!=REGISTRY_HASH or hash_file(vp)!=VECTOR_HASH:raise ValueError("ALEXT frozen observation files changed")
 r=json.loads(rp.read_text());v=json.loads(vp.read_text());rb=dict(r);ri=rb.pop("registry_identity");vb=dict(v);vi=vb.pop("vector_identity")
 if canonical(rb)!=ri or canonical(vb)!=vi or v["registry_identity"]!=ri or r["target_content_present"] is not False:raise ValueError("ALEXT frozen identities changed")
 return r,v
def registration(spec):return {"experiment_id":f"SFT-EXP-MATH-ALEXT-{spec.claim_id.rsplit('-',1)[-1]}-V1","claim_id":spec.claim_id,"target_id":f"MATH-ALEXT-{spec.claim_id.rsplit('-',1)[-1]}-EXACT-OBSERVATION-V1","expected_label":f"complete-alext-{spec.claim_id.rsplit('-',1)[-1]}-observation-retained","registry":REGISTRY,"falsification_condition":"Reject if the value-free registry, exact observation, candidate census, survivor, source identity, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."}
def document(spec):
 n=spec.claim_id.rsplit("-",1)[-1];return {"schema":"sft-v3-fold-program/1","program_id":f"SFT-EXP-MATH-ALEXT-{n}-V1-prediction","instructions":[{"opcode":"input","destination":"premise","arguments":["registered-premise"]},{"opcode":"label","destination":"prediction","arguments":["algebraic-extension-observation",f"complete-alext-{n}-observation-retained"]},{"opcode":"pair","destination":"bound","arguments":["premise","prediction"]},{"opcode":"emit","destination":"","arguments":["prediction"]}]}
class AlgebraicExtensionObservationValidator:
 def __init__(self,root,spec):self.root=root.resolve();self.spec=spec
 def validate(self,sealed):
  self.spec.validate();registry,vector=load(self.root);number=self.spec.claim_id.rsplit("-",1)[-1];row=next(x for x in vector["records"] if x["number"]==number)
  if row["claim_id"]!=self.spec.claim_id or not row["all_rows_preserved"]:raise ValueError("ALEXT observation membership changed")
  reg=registration(self.spec);rh=sha256_identity(reg);doc=document(self.spec);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};target=reg["target_id"]
  envelope=PredictionEnvelope(reg["experiment_id"],{"registered-premise":sha256_identity(inputs["registered-premise"])},(target,),sealed.seal_hash,rh)
  vault=TargetVault(experiment_id=reg["experiment_id"],custodian_id=reg["experiment_id"]+"-custodian",targets={target:HeldLabel("external-observation",row["expected_label"])},custody_nonce=sha256_identity((rh,vector["vector_identity"],number)),expected_envelope_hash=sha256_identity(envelope))
  before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(envelope);prediction=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("ALEXT capability audit failed")
  release=vault.release(prediction);CrossPlatformCustodyExchange.verify(vault.commitment,release,prediction);boundary.measurement_context(release.targets);matched=isinstance(execution.output,HeldLabel) and execution.output.label==release.targets[target].label;tid=target_identity_from_release(release)
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=reg["experiment_id"]+"-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=tid,comparison_implementation_identity_hash=sha256_identity(("mathematics-alext-observer-v1",self.spec.claim_id)),prediction_seal_hash=prediction.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash))
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=prediction.seal_hash,target_release_manifest_hash=release.release_hash))
  measurements=(f"ALEXT-{number}: {row['observation_name']}","exact observation: "+json.dumps(row["exact_observation"],sort_keys=True,separators=(",",":")),f"complete family observation custody: {vector['record_count']} records; all rows preserved",f"irrational and imaginary scalars remain outside admitted proof values; exact structures and enclosures are retained")
  payload={"claim":self.spec.claim_id,"seal":sealed.seal_hash,"registry":registry["registry_identity"],"vector":vector["vector_identity"],"observation":row["exact_observation"],"match":matched}
  return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(row["source_ids"]),measurements,sha256_identity(payload),reg["falsification_condition"],bool(matched and vector["all_rows_preserved"]))
