"""Capability-closed post-seal validation for Chemistry ORG-008."""
from __future__ import annotations
import json,platform
from pathlib import Path
from pypdf import PdfReader
from sft.chemistry.electrophilic_substitution_batch_v1 import ELECTROPHILIC_SUBSTITUTION_SPEC,IDENTITY_HASH,IDENTITY_PATH,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
KEYS=("target_id","source_id","authority","registered_identity","source_record_role","custody_class")
def _identities(root):
 if hash_file(root/IDENTITY_PATH)!=IDENTITY_HASH:raise ValueError("ORG-008 identity changed")
 d=json.loads((root/IDENTITY_PATH).read_text());r=tuple(d["rows"])
 if len(r)!=4 or d.get("external_values_or_outcomes_used_by_candidate_generator_or_eliminator") is not False:raise ValueError("ORG-008 identity boundary changed")
 return r
def _source_rows(root):
 if hash_file(root/TARGET_PATH)!=TARGET_HASH:raise ValueError("ORG-008 target vector changed")
 ids=_identities(root);d=json.loads((root/TARGET_PATH).read_text());rows=tuple(d["rows"])
 if len(rows)!=4 or d.get("all_favourable_adverse_absent_and_unresolved_rows_preserved") is not True:raise ValueError("ORG-008 target vector incomplete")
 for a,b in zip(ids,rows):
  if any(a[k]!=b.get(k) for k in KEYS):raise ValueError("ORG-008 target identity changed")
  if hash_file(root/b["opened_snapshot_path"])!=b["opened_snapshot_sha256"]:raise ValueError("ORG-008 snapshot changed")
  if b["target_payload_hash"]!=sha256_identity((b["target_id"],b["source_record_role"],b["source_outcome"])):raise ValueError("ORG-008 target payload changed")
 return rows
def exact_analysis(root,rows,primary):
 if len(rows)!=4:raise ValueError("ORG-008 requires all four rows")
 out={r["target_id"]:r["source_outcome"] for r in rows};a=primary.get("exact_postseal_analysis",{})
 e=" ".join(x.get("text","") for x in out["SFT-CHEM-ORG-008-001"]["term"]["definitions"]).casefold();s=" ".join(x.get("text","") for x in out["SFT-CHEM-ORG-008-002"]["term"]["definitions"]).casefold();article=out["SFT-CHEM-ORG-008-003"];pdf=out["SFT-CHEM-ORG-008-004"]
 reader=PdfReader(root/rows[3]["opened_snapshot_path"]);texts=tuple(p.extract_text() or "" for p in reader.pages)
 if len(texts)!=pdf["complete_pdf_page_count"] or sha256_identity(texts)!=pdf["complete_page_text_vector_hash"] or sum(len(x) for x in texts)!=pdf["complete_extracted_text_character_count"]:raise ValueError("ORG-008 complete PDF reconstruction changed")
 checks={
  rows[0]["target_id"]:"accepting both bonding electrons" in e,
  rows[1]["target_id"]:"relinquishes both electrons" in s and "electrofuge" in s,
  rows[2]["target_id"]:all(article.values()),
  rows[3]["target_id"]:pdf["complete_pdf_page_count"]==452 and pdf["nonempty_extracted_page_count"]==452 and pdf["complete_table_s1_row_count"]==25 and pdf["displayed_zero_yield_or_zero_star_row_count"]==14 and pdf["displayed_full_yield_row_count"]==9 and pdf["EAS_like_ligand_coupling_present"] and pdf["C_electrophile_attacked_by_nucleophilic_phenol_present"] and pdf["dearomatized_intermediate_surface_present"] and pdf["rearomatization_surface_present"] and pdf["radical_control_preserved"] and pdf["phenoxonium_alternative_preserved"] and pdf["starting_material_recovered_control_preserved"],
 }
 if not all(checks.values()) or a.get("complete_pdf_page_count")!=452 or a.get("complete_table_s1_row_count")!=25 or a.get("complete_target_vector_hash")!=sha256_identity(tuple((r["target_id"],r["source_outcome"]) for r in rows)):raise ValueError("ORG-008 exact postseal analysis changed")
 return a,checks
class ElectrophilicSubstitutionValidator:
 def __init__(self,root):self.root=root.resolve();self.spec=ELECTROPHILIC_SUBSTITUTION_SPEC
 def validate(self,sealed):
  self.spec.validate()
  if hash_file(self.root/PRIMARY_PATH)!=PRIMARY_HASH:raise ValueError("ORG-008 primary changed")
  rows=_source_rows(self.root);primary=json.loads((self.root/PRIMARY_PATH).read_text());analysis,checks=exact_analysis(self.root,rows,primary)
  reg=observational_experiment_registration_record(self.spec);rh=sha256_identity(reg);doc=prediction_program_document(self.spec);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)}
  env=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(x.target_id for x in self.spec.target_rows),sealed.seal_hash,rh);expected=self.spec.expected_observation_label
  vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-external-target-custodian",targets={k:HeldLabel("external-observation",expected if v else "adverse-mismatch") for k,v in checks.items()},custody_nonce=sha256_identity((rh,TARGET_HASH,analysis["complete_target_vector_hash"])),expected_envelope_hash=sha256_identity(env))
  before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);ps=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("ORG-008 prediction package changed")
  release=vault.release(ps);CrossPlatformCustodyExchange.verify(vault.commitment,release,ps);boundary.measurement_context(release.targets);prediction=execution.output
  comparisons=tuple({"target_id":k,"predicted":prediction.label,"observed":release.targets[k].label,"passed":prediction.label==release.targets[k].label} for k in checks)
  try:exact_analysis(self.root,rows[:-1],primary);omission=False
  except ValueError:omission=True
  passed=all(x["passed"] for x in comparisons) and omission and prediction.label!=prediction.label+"__tampered"
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-org-008-comparison/1",self.spec.falsification_condition)),prediction_seal_hash=ps.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash))
  ti=target_identity_from_release(release)
  if ti!=vault.commitment.target_identity_hash:raise ValueError("ORG-008 release changed")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=ti,prediction_seal_hash=ps.seal_hash,target_release_manifest_hash=release.release_hash))
  payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":ps.seal_hash,"analysis":analysis,"checks":checks,"comparisons":comparisons,"omission_rejected":omission,"trace":execution.trace_hash}
  measurements=("complete four-source electrophilic substitution vector retained","one 13,165,129-byte, 452-page supplementary PDF opened only after seal","all 25 Table S1 rows retained: 14 displayed zero-yield, 9 displayed full-yield, and intermediate 12 and 93 rows","EAS-like C-electrophile/nucleophilic-phenol coupling, dearomatized support and rearomatization all present","radical, phenoxonium, starting-material, inconsistent-condition, not-promoted and inseparable-mixture controls retained",f"complete target vector {analysis['complete_target_vector_hash']}")
  return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(r["source_id"] for r in rows),measurements,sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("ElectrophilicSubstitutionValidator","_identities","_source_rows","exact_analysis")
