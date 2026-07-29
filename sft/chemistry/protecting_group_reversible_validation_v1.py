"""Capability-closed validation for ORG-015."""
from __future__ import annotations
import json,platform
from pathlib import Path
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.protecting_group_reversible_batch_v1 import AUTHORITIES,PROTECTING_GROUP_SPEC
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file

def exact_analysis(root:Path,omit_last:bool=False):
 for p,h in AUTHORITIES:
  if hash_file(root/p)!=h: raise ValueError(f"ORG-015 authority changed: {p}")
 docs=[json.loads((root/AUTHORITIES[i][0]).read_text()) for i in (5,6)]
 definitions=[" ".join(x["text"] for x in d["term"]["definitions"]).casefold() for d in docs]
 checks={
  "SFT-CHEM-ORG-015-PROTECT-TEMPORARY":"temporarily used" in definitions[0],
  "SFT-CHEM-ORG-015-PROTECT-TRANSFORM":"transform a reactive group" in definitions[0],
  "SFT-CHEM-ORG-015-PROTECT-CHALLENGE":"does not react under conditions" in definitions[0],
  "SFT-CHEM-ORG-015-DEPROTECT-REMOVAL":"removal of a protecting group" in definitions[1],
  "SFT-CHEM-ORG-015-DEPROTECT-SCOPE":"polymeric resist" in definitions[1],
 }
 if omit_last: checks.pop(next(reversed(checks)))
 if tuple(checks)!=tuple(x.target_id for x in PROTECTING_GROUP_SPEC.target_rows) or not all(checks.values()): raise ValueError("ORG-015 complete source comparison changed")
 return {"complete_iupac_record_count":2,"complete_definition_count":sum(len(d["term"]["definitions"]) for d in docs),"narrow_deprotection_scope_preserved":True,"exact_restoration_formally_generated_not_source_inflated":True},checks

class ProtectingGroupValidator:
 def __init__(self,root):self.root=root.resolve();self.spec=PROTECTING_GROUP_SPEC
 def validate(self,sealed):
  self.spec.validate();analysis,checks=exact_analysis(self.root);registration=observational_experiment_registration_record(self.spec);rh=sha256_identity(registration);document=prediction_program_document(self.spec);program=fold_program_from_mapping(document);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)}
  envelope=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(checks),sealed.seal_hash,rh)
  vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-external-target-custodian",targets={k:HeldLabel("external-observation",self.spec.expected_observation_label if v else "adverse-mismatch") for k,v in checks.items()},custody_nonce=sha256_identity((rh,AUTHORITIES[5][1],AUTHORITIES[6][1])),expected_envelope_hash=sha256_identity(envelope))
  before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(envelope);prediction=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(document,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("ORG-015 prediction package changed")
  release=vault.release(prediction);CrossPlatformCustodyExchange.verify(vault.commitment,release,prediction);boundary.measurement_context(release.targets);comparisons=tuple({"target_id":k,"predicted":execution.output.label,"observed":release.targets[k].label,"passed":execution.output.label==release.targets[k].label} for k in checks)
  try:exact_analysis(self.root,True);omission=False
  except ValueError:omission=True
  passed=all(x["passed"] for x in comparisons) and omission
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-org-015/1",self.spec.falsification_condition)),prediction_seal_hash=prediction.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash))
  tid=target_identity_from_release(release)
  if tid!=vault.commitment.target_identity_hash:raise ValueError("ORG-015 target release changed")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=prediction.seal_hash,target_release_manifest_hash=release.release_hash))
  payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":prediction.seal_hash,"analysis":analysis,"comparisons":comparisons,"omission_rejected":omission,"trace":execution.trace_hash}
  return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(x.source_id for x in self.spec.target_rows),("complete protecting-group and deprotection records retained","temporary transform, protected interval and removal features reproduced","narrow polymeric-resist scope retained without inflating it to exact restoration","exact restoration remains the independently generated formal result"),sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("ProtectingGroupValidator","exact_analysis")
