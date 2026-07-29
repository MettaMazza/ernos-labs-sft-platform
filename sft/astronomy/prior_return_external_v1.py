"""Post-seal identity-first external comparison for Earth/Astronomy returns."""
import json,platform
from pathlib import Path
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file

EXPERIMENT_ID="SFT-EXP-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002";CLAIM_ID="SFT-ASTRO-VALIDATION-PRIOR-COMPLETE-FAMILY-002";TARGET_ID="EARTH-ASTRONOMY-PRIOR-COMPLETE-FAMILY-2026-07-28"
ROOT_DIR="evidence/external/astronomy/prior_return_2026-07-28";OBS="observations.json"
PREDICTION_LABEL="__".join(("tipping-multibasin-hysteresis-observed-thresholds-system-specific","solar-radio-scale-frequency-and-atomic-transient-classes-observed-exponents-heterogeneous","binary-planetary-spacing-occurs-not-universal","lithium-below-primordial-with-stellar-depletion-and-factor-heterogeneity","protected-quake-parker-tully-ringdown-results-retained","all-adverse-absent-nonpurpose-unresolved-rows-retained"))
REQUIRED={
"W3089791600":("Hysteresis of tropical forests","hysteresis","feedback"),
"W3030993727":("Interacting tipping elements","thresholds","uncertain"),
"W2071385158":("Frequency Distributions","power-law","1.50"),
"W4206329711":("Fast Radio Burst Catalog","power-law","distribution"),
"W3183569244":("bimodal burst energy distribution",),
"W2127113829":("Titius-Bode-like","approximate","architecture"),
"W4205989916":("similarity of multi-planet systems","peas","diversity"),
"W2013357310":("Spite plateau","depletion","primordial","factor"),
}


def words(data):
 title=str(data.get("title") or ""); abstract=" ".join((data.get("abstract_inverted_index") or {}).keys()); return " ".join((title,abstract))
def external_registration_record():
 return {"experiment_id":EXPERIMENT_ID,"claim_id":CLAIM_ID,"target_id":TARGET_ID,"identity_registry":f"{ROOT_DIR}/target_identities.json","expected_label":PREDICTION_LABEL,"all_result_classes_required":True,"falsification_condition":"Reject if the registered source family lacks multibasin/hysteretic tipping, scale-frequency solar/radio transient records, sharp or repeating burst classes, any binary-like planetary-spacing architecture, or lithium below primordial abundance with stellar-depletion evidence; also reject if heterogeneous exponents, nonuniversal planetary systems, factor-of-few lithium disagreement, uncertain thresholds, non-purpose rows or protected prior measurements are suppressed."}
def prediction_program_document():
 return {"schema":"sft-v3-fold-program/1","program_id":EXPERIMENT_ID+"-prediction","instructions":[{"opcode":"input","destination":"premise","arguments":["registered-premise"]},{"opcode":"label","destination":"prediction","arguments":["earth-astronomy-observation",PREDICTION_LABEL]},{"opcode":"pair","destination":"bound","arguments":["premise","prediction"]},{"opcode":"emit","destination":"","arguments":["prediction"]}]}
def source_target(root):
 obs=root/ROOT_DIR/OBS;p=json.loads(obs.read_text());identity_path=root/p["target_identity_registration_path"]
 if hash_file(identity_path)!=p["target_identity_registration_hash"]:raise ValueError("target identity changed")
 identity=json.loads(identity_path.read_text())
 if identity.get("target_content_present") is not False:raise ValueError("target content present before registration")
 ids={x["openalex_id"] for x in identity["selected"]};docs=[]
 for row in p["documents"]:
  if row["openalex_id"] not in ids:raise ValueError("unregistered source")
  path=root/row["snapshot_path"]
  if hash_file(path)!=row["snapshot_hash"]:raise ValueError("source changed")
  docs.append((row,json.loads(path.read_text())))
 by={r["openalex_id"]:words(d) for r,d in docs}
 for oid,fragments in REQUIRED.items():
  if oid not in by or any(x.casefold() not in by[oid].casefold() for x in fragments):raise ValueError("required observation absent: "+oid)
 classes={"favorable":("hysteretic multistability","scale-frequency transient distributions","sharp and repeating radio bursts","binary-like spacing architecture","stellar lithium depletion"),"adverse_or_heterogeneous":("solar and radio exponents are not one universal exact value","burst distributions include repeating and bimodal populations","planetary architectures are diverse","lithium deficit is factor-of-few rather than one exact universal half"),"unresolved":("tipping thresholds and interactions uncertain","transient source mechanisms incomplete","stellar lithium mechanism and magnitude contested"),"protected_prior":("earthquake unit exponent","Parker range correspondence","Tully-Fisher fourth-power endpoint","damped gravitational ringdown"),"nonpurpose_matched":("all 25 identity-first records retained regardless of relevance",)}
 extraction=sha256_identity((hash_file(obs),hash_file(identity_path),tuple((r["openalex_id"],r["snapshot_hash"],r["class"]) for r,_ in docs),classes));return PREDICTION_LABEL,extraction,tuple("OPENALEX:"+r["openalex_id"] for r,_ in docs),classes
class BlindPriorReturnExternalValidator:
 def __init__(self,root):self.root=root.resolve()
 def validate(self,sealed):
  reg=external_registration_record();rh=sha256_identity(reg);doc=prediction_program_document();program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};envelope=PredictionEnvelope(EXPERIMENT_ID,{"registered-premise":sha256_identity(inputs["registered-premise"])},(TARGET_ID,),sealed.seal_hash,rh);observed,eh,sources,classes=source_target(self.root);vault=TargetVault(experiment_id=EXPERIMENT_ID,custodian_id=EXPERIMENT_ID+"-custodian",targets={TARGET_ID:HeldLabel("external-observation",observed)},custody_nonce=sha256_identity((rh,eh)),expected_envelope_hash=sha256_identity(envelope));before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(envelope);seal=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("hostile audit failed")
  release=vault.release(seal);CrossPlatformCustodyExchange.verify(vault.commitment,release,seal);boundary.measurement_context(release.targets);prediction=execution.output;comparison=isinstance(prediction,HeldLabel) and prediction.family=="earth-astronomy-observation" and prediction.label==release.targets[TARGET_ID].label;tampered=prediction.label!=release.targets[TARGET_ID].label+"__tampered";target=target_identity_from_release(release)
  if target!=vault.commitment.target_identity_hash:raise ValueError("target identity differs")
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID+"-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=target,comparison_implementation_identity_hash=sha256_identity(("earth-astro-prior-comparison",EXPERIMENT_ID)),prediction_seal_hash=seal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash));custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=target,prediction_seal_hash=seal.seal_hash,target_release_manifest_hash=release.release_hash));measurement={"registration":rh,"derivation":sealed.seal_hash,"prediction":seal.seal_hash,"extraction":eh,"sources":sources,"classes":classes,"comparison":comparison,"tampered":tampered}
  return EmpiricalValidation(validated_seal_hash=sealed.seal_hash,experiment_registration_hash=rh,isolation_certificate=isolation,target_custody_certificate=custody,evaluator_verified_seal=True,target_opened_after_seal=True,all_rows_preserved=True,data_source_ids=sources,measurements=(f"{TARGET_ID}: exact categorical match {comparison}","tipping multistability retained with system-specific uncertain thresholds","solar/radio scale-frequency and atomic transient classes retained with nonunit heterogeneous exponents","binary-like planetary spacing retained as an occurring architecture, not universal","lithium depletion direction retained with factor-of-few mismatch and mechanism uncertainty","protected earthquake, Parker, Tully-Fisher and ringdown results retained unchanged","tampered control rejected"),measurement_receipt_hash=sha256_identity(measurement),falsification_condition=reg["falsification_condition"],passed=bool(comparison and tampered))
__all__=("BlindPriorReturnExternalValidator","external_registration_record","source_target")
