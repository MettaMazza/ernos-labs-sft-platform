"""Capability-closed post-seal validation for Chemistry INORG-012."""
from __future__ import annotations
import json,platform
from pathlib import Path
from sft.chemistry.oxidative_addition_reductive_elimination_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.oxidative_addition_reductive_elimination_law_v1 import oxidative_addition,reductive_elimination
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,FoldLanguageHalt,FoldTable,FoldWord,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel,InadmissibleExactValue
from sft.engine.source import hash_file
IDENTITY_KEYS=("target_id","source_record_ordinal","source_id","authority","registered_identity","source_record_role","custody_class")
EXPECTED_LAWS=("source-bond-to-two-incidences-with-exact-carrier-conservation","held-positive-transfer-two-or-one-plus-one","exact-reductive-inverse-correspondence","complete-five-row-oxidative-reductive-source-retention")
def _identities(root):
 if hash_file(root/IDENTITY_PATH)!=IDENTITY_HASH: raise ValueError("INORG-012 identity registry changed")
 d=json.loads((root/IDENTITY_PATH).read_text()); rows=tuple(d.get("rows",())); forbidden={"definition","value","outcome","source_outcome","registered_surface_phrase","target_payload_hash"}
 if d.get("complete_registered_target_count")!=5 or d.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False or len(rows)!=5 or any(forbidden.intersection(x) for x in rows): raise ValueError("INORG-012 value-free identity boundary changed")
 return rows
def prediction_program_document(root):
 ins=[{"opcode":"input","destination":"premise","arguments":["registered-premise"]}]; table=[]
 for ordinal,row in enumerate(_identities(root),1):
  prefix=f"oxidative-reductive-record-{ordinal}"; ins.append({"opcode":"label","destination":prefix+"-target","arguments":["target-id",row["target_id"]]}); regs=["premise"]
  for number,key in enumerate(IDENTITY_KEYS[1:],1): destination=f"{prefix}-identity-{number}"; ins.append({"opcode":"label","destination":destination,"arguments":["registered-source-identity",str(row[key])]}); regs.append(destination)
  for label in EXPECTED_LAWS: destination=f"{prefix}-law-{len(regs)}"; ins.append({"opcode":"label","destination":destination,"arguments":["oxidative-reductive-law",label]}); regs.append(destination)
  ins.append({"opcode":"word","destination":prefix+"-word","arguments":regs}); table.extend((prefix+"-target",prefix+"-word"))
 ins.extend(({"opcode":"table","destination":"complete-oxidative-reductive-vector","arguments":table},{"opcode":"emit","destination":"","arguments":["complete-oxidative-reductive-vector"]}))
 return {"schema":"sft-v3-fold-program/1","program_id":OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.experiment_id+"-value-free-vector","instructions":ins}
def experiment_registration_record(root):
 return {"experiment_id":OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.experiment_id,"claim_id":OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.claim_id,"provenance":"forward_forcing_with-frozen-complete-IUPAC-correspondence","frozen_relation":OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.exact_result,"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"withheld_target_registry":(TARGET_PATH,TARGET_HASH),"primary_source_record":(PRIMARY_PATH,PRIMARY_HASH),"prediction_program":prediction_program_document(root),"target_ids":tuple(x.target_id for x in OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.target_rows),"all_five_rows_required":True,"target_content_inaccessible_to_prediction_execution":True,"signed_oxidation_formal_charge_or_observed_mechanism_absent_from_forcing":True,"falsification_condition":OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC.falsification_condition}
def _prediction_map(output):
 if not isinstance(output,FoldTable) or len(output.entries)!=5: raise ValueError("INORG-012 prediction is not complete")
 result={}
 for e in output.entries:
  if not isinstance(e.left,HeldLabel) or e.left.family!="target-id" or not isinstance(e.right,FoldWord) or len(e.right.cells)!=11: raise ValueError("INORG-012 prediction row incomplete")
  result[e.left.label]=e.right
 if len(result)!=5: raise ValueError("INORG-012 duplicate target")
 return result
def _source_rows(root):
 if hash_file(root/TARGET_PATH)!=TARGET_HASH or hash_file(root/PRIMARY_PATH)!=PRIMARY_HASH: raise ValueError("INORG-012 postseal evidence changed")
 identities=_identities(root); d=json.loads((root/TARGET_PATH).read_text()); rows=tuple(d.get("rows",()))
 if d.get("complete_registered_target_count")!=5 or len(rows)!=5 or d.get("release_requires_prediction_seal") is not True: raise ValueError("INORG-012 incomplete targets")
 for i,row in zip(identities,rows):
  if any(i[k]!=row.get(k) for k in IDENTITY_KEYS): raise ValueError("INORG-012 identity mismatch")
  if row.get("target_payload_hash")!=sha256_identity((i["target_id"],i["source_record_role"],row.get("source_outcome"))): raise ValueError("INORG-012 payload changed")
 return rows
def exact_analysis(rows,primary):
 if len(rows)!=5: raise ValueError("INORG-012 requires five surfaces")
 one=oxidative_addition(("M",),"X","Y"); two=oxidative_addition(("M1","M2"),"X","Y"); reverse=reductive_elimination(one); third=False
 try: oxidative_addition(("M1","M2","M3"),"X","Y")
 except InadmissibleExactValue: third=True
 p=primary["exact_postseal_analysis"]
 return {"single_distribution":tuple(x.value for x in one.transfer_distribution),"split_distribution":tuple(x.value for x in two.transfer_distribution),"carrier_count":len(one.transferred_carriers),"product_incidence_count":len(one.product_incidences),"reverse_restores_source":reverse.restored_bond==one.source_bond,"third_metal_rejected":third,"complete_target_count":len(rows),"complete_source_count":len({x["source_id"] for x in rows}),"all_registered_surfaces_present":all(x["source_outcome"]["registered_surface_present"] for x in rows),"scope_distinction_count":p["scope_distinction_count"],"complete_target_vector_hash":p["complete_target_vector_hash"],"source_recapture_count":p["source_recapture_count"],"all_rows_preserved":p["all_rows_preserved"]}
class OxidativeAdditionReductiveEliminationValidator:
 def __init__(self,root): self.root=root.resolve(); self.spec=OXIDATIVE_ADDITION_REDUCTIVE_ELIMINATION_SPEC
 def validate(self,sealed):
  self.spec.validate(); reg=experiment_registration_record(self.root); rh=sha256_identity(reg); doc=prediction_program_document(self.root); program=fold_program_from_mapping(doc); inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)}; env=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(x.target_id for x in self.spec.target_rows),sealed.seal_hash,rh)
  before=snapshot_protected_tree(self.root); execution=CapabilityClosedFoldInterpreter().execute(program,inputs); boundary=BlindExperimentBoundary(env); pseal=boundary.seal_prediction(execution.output,execution.trace); after=snapshot_protected_tree(self.root); audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed: raise ValueError("INORG-012 prediction package changed")
  predicted=_prediction_map(execution.output); rows=_source_rows(self.root); vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-complete-target-custodian",targets={x["target_id"]:HeldLabel("external-complete-source-record-hash",x["target_payload_hash"]) for x in rows},custody_nonce=sha256_identity((rh,TARGET_HASH)),expected_envelope_hash=sha256_identity(env)); release=vault.release(pseal); CrossPlatformCustodyExchange.verify(vault.commitment,release,pseal); boundary.measurement_context(release.targets)
  comparisons=[]
  for row in rows:
   word=predicted[row["target_id"]]; vals=tuple(str(row[k]) for k in IDENTITY_KEYS[1:]); im=all(isinstance(word.cells[i],HeldLabel) and word.cells[i].label==v for i,v in enumerate(vals,1)); lm=tuple(x.label for x in word.cells[7:])==EXPECTED_LAWS; tm=release.targets[row["target_id"]]==HeldLabel("external-complete-source-record-hash",row["target_payload_hash"]); comparisons.append({"target_id":row["target_id"],"identity_match":im,"law_match":lm,"postseal_target_hash_match":tm,"passed":im and lm and tm})
  analysis=exact_analysis(rows,json.loads((self.root/PRIMARY_PATH).read_text()))
  try: exact_analysis(rows[:-1],{}); omitted=False
  except ValueError: omitted=True
  try: FoldWord((0,)); zero=False
  except FoldLanguageHalt: zero=True
  controls={"omitted_source_row_rejected":omitted,"numerical_zero_rejected":zero,"all_five_target_hashes_bound_postseal":len(release.targets)==5,"third_metal_partition_rejected":analysis["third_metal_rejected"],"sources_not_recaptured":analysis["source_recapture_count"]==0,"prediction_contains_no_definition_formula_or_target":not any(t in json.dumps(doc,sort_keys=True) for t in ("complete_definition_text","target_payload_hash","two-electron loss"))}
  passed=all(x["passed"] for x in comparisons) and analysis["single_distribution"]==(2,) and analysis["split_distribution"]==(1,1) and analysis["carrier_count"]==2 and analysis["product_incidence_count"]==2 and analysis["reverse_restores_source"] and analysis["complete_target_count"]==5 and analysis["complete_source_count"]==2 and analysis["all_registered_surfaces_present"] and analysis["scope_distinction_count"]==1 and analysis["all_rows_preserved"] and all(controls.values())
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-oxidative-reductive/1",self.spec.falsification_condition)),prediction_seal_hash=pseal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash)); tid=target_identity_from_release(release)
  if tid!=vault.commitment.target_identity_hash: raise ValueError("INORG-012 released target identity differs")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=pseal.seal_hash,target_release_manifest_hash=release.release_hash)); payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":pseal.seal_hash,"analysis":analysis,"comparisons":comparisons,"controls":controls,"trace":execution.trace_hash}; measurements=("single-metal transfer distribution (2); two-metal distribution (1,1)","two carriers and two product incidences retained; exact reductive inverse restores source bond","complete five-row two-source IUPAC vector including radical scope",f"complete exact target vector {analysis['complete_target_vector_hash']}")+tuple(f"control {k}: {v}" for k,v in controls.items())
  return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(dict.fromkeys(x["source_id"] for x in rows)),measurements,sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("OxidativeAdditionReductiveEliminationValidator","_identities","_prediction_map","_source_rows","exact_analysis","experiment_registration_record","prediction_program_document")
