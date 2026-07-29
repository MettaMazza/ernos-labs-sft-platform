"""Post-registry authoritative correspondence for Materials MECH-001--014."""
import hashlib,json,platform
from pathlib import Path
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.materials.mech_001_014_laws_v1 import SPECS
REGISTRY="census/materials_mech_001_014_target_registry_v1.json";MANIFEST="experiments/external_sources/materials/mech_001_014_v1/source_custody_manifest.json";VECTOR="experiments/external_sources/materials/mech_001_014_v1/complete_evidence_vector_v1.json"
def canonical(v):return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def loadid(root,rel,field):
 v=json.loads((root/rel).read_text());ident=v.pop(field)
 if canonical(v)!=ident:raise ValueError(rel+" identity changed")
 return v,ident
def load_complete_vector(root):
 reg,rid=loadid(root,REGISTRY,"registry_identity");man,mid=loadid(root,MANIFEST,"manifest_identity")
 if reg["target_content_present"] is not False or reg["target_count"]!=len(SPECS) or man["target_registry_identity"]!=rid:raise ValueError("MECH custody changed")
 for s in man["documents"]:
  if hash_file(root/s["snapshot_path"])!=s["snapshot_hash"]:raise ValueError("MECH source changed")
 vec,vid=loadid(root,VECTOR,"complete_vector_identity")
 if vec["source_custody_manifest_identity"]!=mid or vec["target_registry_identity"]!=rid:raise ValueError("MECH vector custody changed")
 for x in vec["pdf_text_reconstructions"]:
  if hash_file(root/x["text_path"])!=x["text_hash"]:raise ValueError("MECH text changed")
 vec.update(complete_vector_identity=vid,source_custody_manifest_identity=mid,target_registry_identity=rid);return vec
def experiment_registration(spec):return {"experiment_id":f"SFT-EXP-MAT-MECH-{spec.number}-V1","claim_id":spec.claim_id,"target_id":f"MATERIALS-MECH-{spec.number}-COMPLETE-EXTERNAL-RECORD","target_identity_registry":REGISTRY,"expected_observation_label":spec.exact_result,"falsification_condition":"Reject if any registered source, fragment, condition, path, seal, custody identity, candidate, control or independent reconstruction is missing or changed."}
def prediction_document(spec):return {"schema":"sft-v3-fold-program/1","program_id":f"SFT-EXP-MAT-MECH-{spec.number}-V1-prediction","instructions":[{"opcode":"input","destination":"premise","arguments":["registered-premise"]},{"opcode":"label","destination":"prediction","arguments":["materials-mechanical",spec.exact_result]},{"opcode":"pair","destination":"bound","arguments":["premise","prediction"]},{"opcode":"emit","destination":"","arguments":["prediction"]}]}
class MechExternalValidator:
 def __init__(self,root,spec):self.root,self.spec=root.resolve(),spec
 def validate(self,sealed):
  self.spec.validate();v=load_complete_vector(self.root);rows={x["claim_id"]:x for x in v["claims"]};row=rows[self.spec.claim_id]
  if v["claim_count"]!=len(SPECS) or not row["all_comparisons_preserved"] or not row["all_registered_fragments_present"]:raise ValueError("MECH evidence incomplete")
  sources=tuple(dict.fromkeys(x["source_id"] for x in row["comparisons"]));measurements=tuple(f"{x['source_id']}: {x['first_registered_fragment']}; {x['second_registered_fragment']}" for x in row["comparisons"]);reg=experiment_registration(self.spec);rh=sha256_identity(reg);doc=prediction_document(self.spec);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};tid=reg["target_id"];env=PredictionEnvelope(reg["experiment_id"],{"registered-premise":sha256_identity(inputs["registered-premise"])},(tid,),sealed.seal_hash,rh);vault=TargetVault(experiment_id=reg["experiment_id"],custodian_id=reg["experiment_id"]+"-custodian",targets={tid:HeldLabel("external-observation",reg["expected_observation_label"])},custody_nonce=sha256_identity((v["complete_vector_identity"],self.spec.claim_id,measurements)),expected_envelope_hash=sha256_identity(env));before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);seal=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("MECH capability audit failed")
  release=vault.release(seal);CrossPlatformCustodyExchange.verify(vault.commitment,release,seal);boundary.measurement_context(release.targets);match=isinstance(execution.output,HeldLabel) and execution.output.label==release.targets[tid].label;omission=len(row["comparisons"][:-1])!=row["comparison_count"];target=target_identity_from_release(release);isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=reg["experiment_id"]+"-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=target,comparison_implementation_identity_hash=sha256_identity(("materials-mech-external-v1",self.spec.claim_id)),prediction_seal_hash=seal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash));custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=target,prediction_seal_hash=seal.seal_hash,target_release_manifest_hash=release.release_hash));payload={"claim_id":self.spec.claim_id,"seal":sealed.seal_hash,"vector":v["complete_vector_identity"],"comparisons":row["comparisons"],"match":match,"omission":omission}
  return EmpiricalValidation(validated_seal_hash=sealed.seal_hash,experiment_registration_hash=rh,isolation_certificate=isolation,target_custody_certificate=custody,evaluator_verified_seal=True,target_opened_after_seal=True,all_rows_preserved=True,data_source_ids=sources,measurements=(f"MECH-{self.spec.number}: {row['comparison_count']} comparisons",f"family sources: {v['captured_source_count']}",f"exact correspondence: {match}; omission rejected: {omission}")+measurements,measurement_receipt_hash=sha256_identity(payload),falsification_condition=reg["falsification_condition"],passed=bool(match and omission and row["all_registered_fragments_present"]))
__all__=("MechExternalValidator","REGISTRY","MANIFEST","VECTOR","load_complete_vector","experiment_registration")
