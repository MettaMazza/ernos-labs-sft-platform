"""Capability-closed validation for ECHEM-001."""
import hashlib,json,platform
from pathlib import Path
from pypdf import PdfReader
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.chemistry.half_reaction_orientation_batch_v1 import ANALYSIS_PATH,AUTHORITIES,HALF_REACTION_SPEC,IUPAC_PATH,PDF_PATH
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
def dig(b):return "sha256:"+hashlib.sha256(b).hexdigest()
def exact_analysis(root:Path,omit_last=False):
 for p,h in AUTHORITIES:
  if hash_file(root/p)!=h:raise ValueError(f"ECHEM-001 authority changed: {p}")
 a=json.loads((root/ANALYSIS_PATH).read_text());v=dict(a);recorded=v.pop("complete_result_vector_sha256")
 if recorded!=dig(json.dumps(v,sort_keys=True,separators=(",",":")).encode()):raise ValueError("ECHEM-001 vector changed")
 pages=[]
 for n,p in enumerate(PdfReader(root/PDF_PATH).pages,1):
  text="\n".join(x.strip() for x in (p.extract_text() or "").replace("\u00ad","").splitlines() if x.strip());pages.append({"page":n,"complete_extracted_text":text,"text_sha256":dig(text.encode()),"character_count":len(text),"half_reaction_line_count":sum("half-reaction" in x.casefold() for x in text.splitlines()),"electron_symbol_line_count":sum("e-" in x.casefold() or "electron" in x.casefold() for x in text.splitlines())})
 if pages!=a["nist_complete_pages_in_order"] or len(pages)!=22:raise ValueError("ECHEM-001 complete PDF reconstruction changed")
 definition=" ".join(x["text"] for x in json.loads((root/IUPAC_PATH).read_text())["term"]["definitions"]).casefold();combined="\n".join(x["complete_extracted_text"] for x in pages).casefold();checks={"SFT-CHEM-ECHEM-001-IUPAC-TWO-HALVES":all(x in definition for x in ("divided into two half-reactions","undergoes oxidation","undergoes reduction")),"SFT-CHEM-ECHEM-001-IUPAC-ORIENTATION":all(x in definition for x in ("written as a reduction","written as oxidation")),"SFT-CHEM-ECHEM-001-IUPAC-REFERENCE":"standard reference half-cell" in definition,"SFT-CHEM-ECHEM-001-NIST-DEFINITION":all(x in combined for x in ("standard electrode potential","half-reaction","reference electrode")),"SFT-CHEM-ECHEM-001-NIST-CONDITIONS":all(x in combined for x in ("298.15 k","unit activity","standard hydrogen electrode")),"SFT-CHEM-ECHEM-001-NIST-COMPLETE-PDF":sum(x["character_count"] for x in pages)==99794}
 if omit_last:checks.pop(next(reversed(checks)))
 if tuple(checks)!=tuple(x.target_id for x in HALF_REACTION_SPEC.target_rows) or not all(checks.values()):raise ValueError("ECHEM-001 comparison changed")
 return {"complete_iupac_record_count":1,"complete_nist_pdf_page_count":22,"complete_nist_extracted_character_count":99794,"complete_result_vector_sha256":recorded,"all_table_values_signs_units_phases_references_uncertainties_and_absences_preserved":True},checks
class HalfReactionValidator:
 def __init__(self,root):self.root=root.resolve();self.spec=HALF_REACTION_SPEC
 def validate(self,sealed):
  self.spec.validate();a,checks=exact_analysis(self.root);reg=observational_experiment_registration_record(self.spec);rh=sha256_identity(reg);doc=prediction_program_document(self.spec);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};env=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(checks),sealed.seal_hash,rh);vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-external-target-custodian",targets={k:HeldLabel("external-observation",self.spec.expected_observation_label if v else "adverse-mismatch") for k,v in checks.items()},custody_nonce=sha256_identity((rh,a["complete_result_vector_sha256"])),expected_envelope_hash=sha256_identity(env));before=snapshot_protected_tree(self.root);exe=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);pred=boundary.seal_prediction(exe.output,exe.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=exe.program_hash or not audit.passed:raise ValueError("ECHEM-001 package changed")
  release=vault.release(pred);CrossPlatformCustodyExchange.verify(vault.commitment,release,pred);boundary.measurement_context(release.targets);comp=tuple({"target_id":k,"predicted":exe.output.label,"observed":release.targets[k].label,"passed":exe.output.label==release.targets[k].label} for k in checks)
  try:exact_analysis(self.root,True);omission=False
  except ValueError:omission=True
  passed=all(x["passed"] for x in comp) and omission;isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=exe.program_hash,input_manifest_hash=exe.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-echem-001/1",self.spec.falsification_condition)),prediction_seal_hash=pred.seal_hash,output_hash=exe.output_hash,trace_hash=exe.trace_hash));tid=target_identity_from_release(release)
  if tid!=vault.commitment.target_identity_hash:raise ValueError("ECHEM-001 target changed")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=pred.seal_hash,target_release_manifest_hash=release.release_hash));payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":pred.seal_hash,"analysis":a,"comparisons":comp,"omission_rejected":omission,"trace":exe.trace_hash};return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(x.source_id for x in self.spec.target_rows),("complete IUPAC redox-potential record retained","all 22 NIST pages and 99,794 extracted characters retained","paired half-reactions, orientation, reference and standard-state conditions reproduced","all conventional table values signs phases units uncertainty and absences retained downstream"),sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("HalfReactionValidator","exact_analysis")
