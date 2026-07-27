"""Capability-closed validation for Chemistry INORG-013."""
from __future__ import annotations
import json,platform
from pathlib import Path
from sft.chemistry.insertion_elimination_pathway_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,INSERTION_ELIMINATION_PATHWAY_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.insertion_elimination_pathway_law_v1 import elimination,extrusion,insertion,migratory_insertion
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,FoldLanguageHalt,FoldTable,FoldWord,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
IDENTITY_KEYS=("target_id","source_record_ordinal","source_id","authority","registered_identity","source_record_role","custody_class")
EXPECTED_LAWS=("complete-before-after-removed-added-adjacency-trace","insertion-and-exact-extrusion-boundary","migration-plus-insertion-and-two-eliminand-laws","complete-ten-row-scope-absence-and-product-retention")
def _identities(root):
 if hash_file(root/IDENTITY_PATH)!=IDENTITY_HASH:raise ValueError("INORG-013 identity changed")
 d=json.loads((root/IDENTITY_PATH).read_text());rows=tuple(d.get("rows",()));forbidden={"definition","value","outcome","source_outcome","registered_surface_phrase","target_payload_hash"}
 if d.get("complete_registered_target_count")!=10 or d.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False or len(rows)!=10 or any(forbidden.intersection(x) for x in rows):raise ValueError("INORG-013 value-free boundary changed")
 return rows
def prediction_program_document(root):
 ins=[{"opcode":"input","destination":"premise","arguments":["registered-premise"]}];table=[]
 for n,row in enumerate(_identities(root),1):
  p=f"insertion-elimination-record-{n}";ins.append({"opcode":"label","destination":p+"-target","arguments":["target-id",row["target_id"]]});regs=["premise"]
  for i,k in enumerate(IDENTITY_KEYS[1:],1):dest=f"{p}-identity-{i}";ins.append({"opcode":"label","destination":dest,"arguments":["registered-source-identity",str(row[k])]});regs.append(dest)
  for label in EXPECTED_LAWS:dest=f"{p}-law-{len(regs)}";ins.append({"opcode":"label","destination":dest,"arguments":["insertion-elimination-law",label]});regs.append(dest)
  ins.append({"opcode":"word","destination":p+"-word","arguments":regs});table.extend((p+"-target",p+"-word"))
 ins.extend(({"opcode":"table","destination":"complete-insertion-elimination-vector","arguments":table},{"opcode":"emit","destination":"","arguments":["complete-insertion-elimination-vector"]}));return {"schema":"sft-v3-fold-program/1","program_id":INSERTION_ELIMINATION_PATHWAY_SPEC.experiment_id+"-value-free-vector","instructions":ins}
def experiment_registration_record(root):return {"experiment_id":INSERTION_ELIMINATION_PATHWAY_SPEC.experiment_id,"claim_id":INSERTION_ELIMINATION_PATHWAY_SPEC.claim_id,"provenance":"forward_forcing_with-frozen-complete-IUPAC-vector","frozen_relation":INSERTION_ELIMINATION_PATHWAY_SPEC.exact_result,"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"withheld_target_registry":(TARGET_PATH,TARGET_HASH),"primary_source_record":(PRIMARY_PATH,PRIMARY_HASH),"prediction_program":prediction_program_document(root),"target_ids":tuple(x.target_id for x in INSERTION_ELIMINATION_PATHWAY_SPEC.target_rows),"all_ten_rows_required":True,"target_content_inaccessible_to_prediction_execution":True,"host_lattice_scope_and_absent_rendered_example_preserved":True,"falsification_condition":INSERTION_ELIMINATION_PATHWAY_SPEC.falsification_condition}
def _prediction_map(out):
 if not isinstance(out,FoldTable) or len(out.entries)!=10:raise ValueError("INORG-013 prediction incomplete")
 r={}
 for e in out.entries:
  if not isinstance(e.left,HeldLabel) or e.left.family!="target-id" or not isinstance(e.right,FoldWord) or len(e.right.cells)!=11:raise ValueError("INORG-013 row incomplete")
  r[e.left.label]=e.right
 if len(r)!=10:raise ValueError("INORG-013 duplicate target")
 return r
def _source_rows(root):
 if hash_file(root/TARGET_PATH)!=TARGET_HASH or hash_file(root/PRIMARY_PATH)!=PRIMARY_HASH:raise ValueError("INORG-013 evidence changed")
 ids=_identities(root);d=json.loads((root/TARGET_PATH).read_text());rows=tuple(d.get("rows",()))
 if d.get("complete_registered_target_count")!=10 or len(rows)!=10 or d.get("release_requires_prediction_seal") is not True:raise ValueError("INORG-013 targets incomplete")
 for i,row in zip(ids,rows):
  if any(i[k]!=row.get(k) for k in IDENTITY_KEYS):raise ValueError("INORG-013 identity mismatch")
  if row.get("target_payload_hash")!=sha256_identity((i["target_id"],i["source_record_role"],row.get("source_outcome"))):raise ValueError("INORG-013 payload changed")
 return rows
def exact_analysis(rows,primary):
 if len(rows)!=10:raise ValueError("INORG-013 requires ten surfaces")
 ins=insertion("X","Z","Y");rev=extrusion(ins);mig=migratory_insertion("M","X","Y");distinct=elimination("A","B","X","Y");same=elimination("A","A","X","Y");p=primary["exact_postseal_analysis"]
 return {"insertion_before_count":len(ins.before),"insertion_after_count":len(ins.after),"insertion_removed_count":len(ins.removed),"insertion_added_count":len(ins.added),"extrusion_restores_source":rev.after==ins.before,"migratory_composition":tuple(x.label for x in mig.composition),"migratory_common_edge_count":len(set(mig.before)&set(mig.after)),"distinct_eliminand_removed_count":len(distinct.removed),"single_centre_carrier_count":len(same.carriers),"complete_target_count":len(rows),"complete_source_count":len({x["source_id"] for x in rows}),"all_registered_surfaces_present":all(x["source_outcome"]["registered_surface_present"] for x in rows),"scope_distinction_count":p["scope_distinction_count"],"rendered_structure_absence_count":p["rendered_structure_absence_count"],"complete_target_vector_hash":p["complete_target_vector_hash"],"source_recapture_count":p["source_recapture_count"],"all_rows_preserved":p["all_rows_preserved"]}
class InsertionEliminationPathwayValidator:
 def __init__(self,root):self.root=root.resolve();self.spec=INSERTION_ELIMINATION_PATHWAY_SPEC
 def validate(self,sealed):
  self.spec.validate();reg=experiment_registration_record(self.root);rh=sha256_identity(reg);doc=prediction_program_document(self.root);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};env=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(x.target_id for x in self.spec.target_rows),sealed.seal_hash,rh);before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);pseal=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("INORG-013 package changed")
  predicted=_prediction_map(execution.output);rows=_source_rows(self.root);vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-complete-target-custodian",targets={x["target_id"]:HeldLabel("external-complete-source-record-hash",x["target_payload_hash"]) for x in rows},custody_nonce=sha256_identity((rh,TARGET_HASH)),expected_envelope_hash=sha256_identity(env));release=vault.release(pseal);CrossPlatformCustodyExchange.verify(vault.commitment,release,pseal);boundary.measurement_context(release.targets);comparisons=[]
  for row in rows:
   word=predicted[row["target_id"]];vals=tuple(str(row[k]) for k in IDENTITY_KEYS[1:]);im=all(isinstance(word.cells[i],HeldLabel) and word.cells[i].label==v for i,v in enumerate(vals,1));lm=tuple(x.label for x in word.cells[7:])==EXPECTED_LAWS;tm=release.targets[row["target_id"]]==HeldLabel("external-complete-source-record-hash",row["target_payload_hash"]);comparisons.append({"target_id":row["target_id"],"identity_match":im,"law_match":lm,"postseal_target_hash_match":tm,"passed":im and lm and tm})
  a=exact_analysis(rows,json.loads((self.root/PRIMARY_PATH).read_text()))
  try:exact_analysis(rows[:-1],{});om=False
  except ValueError:om=True
  try:FoldWord((0,));zr=False
  except FoldLanguageHalt:zr=True
  controls={"omitted_source_row_rejected":om,"numerical_zero_rejected":zr,"all_ten_target_hashes_bound_postseal":len(release.targets)==10,"absent_rendered_example_preserved":a["rendered_structure_absence_count"]==1,"sources_not_recaptured":a["source_recapture_count"]==0,"prediction_contains_no_definition_product_or_target":not any(t in json.dumps(doc,sort_keys=True) for t in ("complete_definition_text","target_payload_hash","X-Z + Y -> X-Y-Z"))}
  passed=all(x["passed"] for x in comparisons) and (a["insertion_before_count"],a["insertion_after_count"],a["insertion_removed_count"],a["insertion_added_count"])==(1,2,1,2) and a["extrusion_restores_source"] and a["migratory_composition"]==("migration","insertion") and a["migratory_common_edge_count"]==1 and a["distinct_eliminand_removed_count"]==2 and a["single_centre_carrier_count"]==3 and a["complete_target_count"]==10 and a["complete_source_count"]==3 and a["all_registered_surfaces_present"] and a["scope_distinction_count"]==1 and a["all_rows_preserved"] and all(controls.values())
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-insertion-elimination/1",self.spec.falsification_condition)),prediction_seal_hash=pseal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash));tid=target_identity_from_release(release)
  if tid!=vault.commitment.target_identity_hash:raise ValueError("INORG-013 target identity differs")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=pseal.seal_hash,target_release_manifest_hash=release.release_hash));payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":pseal.seal_hash,"analysis":a,"comparisons":comparisons,"controls":controls,"trace":execution.trace_hash};measurements=("insertion adjacency counts before/after 1/2 and removed/added 1/2; extrusion exact inverse","migratory composition migration plus insertion; distinct- and single-centre elimination retained","complete ten-row three-source IUPAC vector including host-lattice scope and absent rendered example",f"complete exact target vector {a['complete_target_vector_hash']}")+tuple(f"control {k}: {v}" for k,v in controls.items());return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(dict.fromkeys(x["source_id"] for x in rows)),measurements,sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("InsertionEliminationPathwayValidator","_identities","_prediction_map","_source_rows","exact_analysis","experiment_registration_record","prediction_program_document")
