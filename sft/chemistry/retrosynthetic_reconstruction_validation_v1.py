"""Capability-closed validation for ORG-016."""
import json,platform
from pathlib import Path
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.retrosynthetic_reconstruction_batch_v1 import AUTHORITIES,RETROSYNTHESIS_SPEC
from sft.chemistry.retrosynthetic_reconstruction_law_v1 import exhaustive_reconstruction
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
def exact_analysis(root:Path,omit_last=False):
 for p,h in AUTHORITIES:
  if hash_file(root/p)!=h:raise ValueError(f"ORG-016 authority changed: {p}")
 docs=[json.loads((root/AUTHORITIES[i][0]).read_text()) for i in (5,6)];defs=[" ".join(x["text"] for x in d["term"]["definitions"]).casefold() for d in docs]
 checks={"SFT-CHEM-ORG-016-MECH-COMPLETE":"detailed description of the process leading from the reactants to the products" in defs[0],"SFT-CHEM-ORG-016-MECH-INTERMEDIATES":all(x in defs[0] for x in ("reaction intermediates","products","transition states")),"SFT-CHEM-ORG-016-MECH-ALTERNATIVES":"alternative mechanisms not excluded by the evidence" in defs[0],"SFT-CHEM-ORG-016-MECH-INCOMPLETE":"based on incomplete experimental data" in defs[0],"SFT-CHEM-ORG-016-PATH-MECHANISM":"synonym for mechanism" in defs[1],"SFT-CHEM-ORG-016-PATH-TRAJECTORY":"trajectory on the potential-energy surface" in defs[1],"SFT-CHEM-ORG-016-PATH-STEPS":"sequence of synthetic steps" in defs[1]}
 if omit_last:checks.pop(next(reversed(checks)))
 if tuple(checks)!=tuple(x.target_id for x in RETROSYNTHESIS_SPEC.target_rows) or not all(checks.values()):raise ValueError("ORG-016 complete source comparison changed")
 def carrier(n):return tuple(HeldLabel("synthesis-carrier-occurrence",f"v{n}-{i}") for i in range(1,n+1))
 four,five=exhaustive_reconstruction(carrier(4)),exhaustive_reconstruction(carrier(5))
 if len(four)!=5 or len(five)!=14 or any(x.forward_reconstruction!=x.carrier for x in (*four,*five)):raise ValueError("ORG-016 exhaustive tree census changed")
 return {"complete_iupac_record_count":2,"source_target_count":7,"four_leaf_complete_tree_count":5,"five_leaf_successor_tree_count":14,"all_19_trees_forward_reconstruct_exactly":True,"alternative_and_incomplete_evidence_rows_preserved":True},checks
class RetrosynthesisValidator:
 def __init__(self,root):self.root=root.resolve();self.spec=RETROSYNTHESIS_SPEC
 def validate(self,sealed):
  self.spec.validate();a,checks=exact_analysis(self.root);reg=observational_experiment_registration_record(self.spec);rh=sha256_identity(reg);doc=prediction_program_document(self.spec);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};env=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(checks),sealed.seal_hash,rh);vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-external-target-custodian",targets={k:HeldLabel("external-observation",self.spec.expected_observation_label if v else "adverse-mismatch") for k,v in checks.items()},custody_nonce=sha256_identity((rh,AUTHORITIES[5][1],AUTHORITIES[6][1],5,14)),expected_envelope_hash=sha256_identity(env));before=snapshot_protected_tree(self.root);exe=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);pred=boundary.seal_prediction(exe.output,exe.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=exe.program_hash or not audit.passed:raise ValueError("ORG-016 prediction package changed")
  release=vault.release(pred);CrossPlatformCustodyExchange.verify(vault.commitment,release,pred);boundary.measurement_context(release.targets);comp=tuple({"target_id":k,"predicted":exe.output.label,"observed":release.targets[k].label,"passed":exe.output.label==release.targets[k].label} for k in checks)
  try:exact_analysis(self.root,True);omission=False
  except ValueError:omission=True
  passed=all(x["passed"] for x in comp) and omission;isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=exe.program_hash,input_manifest_hash=exe.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-org-016/1",self.spec.falsification_condition)),prediction_seal_hash=pred.seal_hash,output_hash=exe.output_hash,trace_hash=exe.trace_hash));tid=target_identity_from_release(release)
  if tid!=vault.commitment.target_identity_hash:raise ValueError("ORG-016 target release changed")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=pred.seal_hash,target_release_manifest_hash=release.release_hash));payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":pred.seal_hash,"analysis":a,"comparisons":comp,"omission_rejected":omission,"trace":exe.trace_hash};return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(x.source_id for x in self.spec.target_rows),("both complete IUPAC records retained","five four-leaf trees and fourteen five-leaf successor trees generated exactly","all nineteen bounded trees forward-reconstruct their exact target","alternative mechanisms and incomplete-evidence disclosures retained"),sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("RetrosynthesisValidator","exact_analysis")
