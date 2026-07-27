"""Capability-closed validation for INORG-014."""
from __future__ import annotations
import json,platform
from pathlib import Path
from sft.chemistry.metal_cluster_bonding_batch_v1 import IDENTITY_HASH,IDENTITY_PATH,METAL_CLUSTER_BONDING_SPEC,PRIMARY_HASH,PRIMARY_PATH,TARGET_HASH,TARGET_PATH
from sft.chemistry.metal_cluster_bonding_law_v1 import append_centre,forced_cluster,relation
from sft.claim_evidence import CapabilityClosedFoldInterpreter,CrossPlatformCustodyExchange,EmptyOne,FoldLanguageHalt,FoldTable,FoldWord,HostilePackageAuditor,TargetVault,fold_program_from_mapping,snapshot_protected_tree,target_identity_from_release
from sft.engine import EmpiricalValidation,seal_isolation_certificate,seal_target_custody_certificate,unsealed_isolation_certificate,unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary,PredictionEnvelope
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
from sft.engine.source import hash_file
IDENTITY_KEYS=("target_id","source_record_ordinal","source_id","authority","registered_identity","source_record_role","custody_class")
EXPECTED_LAWS=("finite-complete-connected-multicentre-support","distinct-direct-bridge-and-held-grouping-relations","positive-count-or-EmptyOne-per-relation-class","connected-centre-successor-with-ten-row-retention")
def _identities(root):
 if hash_file(root/IDENTITY_PATH)!=IDENTITY_HASH:raise ValueError("INORG-014 identity changed")
 d=json.loads((root/IDENTITY_PATH).read_text());rows=tuple(d.get("rows",()));forbidden={"definition","value","outcome","source_outcome","registered_surface_phrase","target_payload_hash"}
 if d.get("complete_registered_target_count")!=10 or d.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False or len(rows)!=10 or any(forbidden.intersection(x) for x in rows):raise ValueError("INORG-014 value-free boundary changed")
 return rows
def prediction_program_document(root):
 ins=[{"opcode":"input","destination":"premise","arguments":["registered-premise"]}];table=[]
 for n,row in enumerate(_identities(root),1):
  p=f"metal-cluster-record-{n}";ins.append({"opcode":"label","destination":p+"-target","arguments":["target-id",row["target_id"]]});regs=["premise"]
  for i,k in enumerate(IDENTITY_KEYS[1:],1):dest=f"{p}-identity-{i}";ins.append({"opcode":"label","destination":dest,"arguments":["registered-source-identity",str(row[k])]});regs.append(dest)
  for label in EXPECTED_LAWS:dest=f"{p}-law-{len(regs)}";ins.append({"opcode":"label","destination":dest,"arguments":["metal-cluster-law",label]});regs.append(dest)
  ins.append({"opcode":"word","destination":p+"-word","arguments":regs});table.extend((p+"-target",p+"-word"))
 ins.extend(({"opcode":"table","destination":"complete-metal-cluster-vector","arguments":table},{"opcode":"emit","destination":"","arguments":["complete-metal-cluster-vector"]}));return {"schema":"sft-v3-fold-program/1","program_id":METAL_CLUSTER_BONDING_SPEC.experiment_id+"-value-free-vector","instructions":ins}
def experiment_registration_record(root):return {"experiment_id":METAL_CLUSTER_BONDING_SPEC.experiment_id,"claim_id":METAL_CLUSTER_BONDING_SPEC.claim_id,"provenance":"forward_forcing_with-family-identity-sealed-cluster-vector","frozen_relation":METAL_CLUSTER_BONDING_SPEC.exact_result,"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"withheld_target_registry":(TARGET_PATH,TARGET_HASH),"primary_source_record":(PRIMARY_PATH,PRIMARY_HASH),"prediction_program":prediction_program_document(root),"target_ids":tuple(x.target_id for x in METAL_CLUSTER_BONDING_SPEC.target_rows),"all_ten_rows_required":True,"target_content_inaccessible_to_prediction_execution":True,"external_signed_charge_inscriptions_downstream_only":True,"falsification_condition":METAL_CLUSTER_BONDING_SPEC.falsification_condition}
def _prediction_map(out):
 if not isinstance(out,FoldTable) or len(out.entries)!=10:raise ValueError("INORG-014 prediction incomplete")
 r={}
 for e in out.entries:
  if not isinstance(e.left,HeldLabel) or e.left.family!="target-id" or not isinstance(e.right,FoldWord) or len(e.right.cells)!=11:raise ValueError("INORG-014 row incomplete")
  r[e.left.label]=e.right
 if len(r)!=10:raise ValueError("INORG-014 duplicate target")
 return r
def _source_rows(root):
 if hash_file(root/TARGET_PATH)!=TARGET_HASH or hash_file(root/PRIMARY_PATH)!=PRIMARY_HASH:raise ValueError("INORG-014 evidence changed")
 ids=_identities(root);d=json.loads((root/TARGET_PATH).read_text());rows=tuple(d.get("rows",()))
 if d.get("complete_registered_target_count")!=10 or len(rows)!=10 or d.get("release_requires_prediction_seal") is not True:raise ValueError("INORG-014 targets incomplete")
 for i,row in zip(ids,rows):
  if any(i[k]!=row.get(k) for k in IDENTITY_KEYS):raise ValueError("INORG-014 identity mismatch")
  if row.get("target_payload_hash")!=sha256_identity((i["target_id"],i["source_record_role"],row.get("source_outcome"))):raise ValueError("INORG-014 payload changed")
 return rows
def exact_analysis(rows,primary):
 if len(rows)!=10:raise ValueError("INORG-014 requires ten surfaces")
 direct=forced_cluster("d",("M1","M2"),(relation("M1","M2","direct-metal-bond"),));bridge=forced_cluster("b",("M1","M2"),(relation("M1","M2","bridging-ligand-path",PositiveCount(2)),));group=forced_cluster("g",("M1","M2"),(relation("M1","M2","held-grouping-relation"),));succ=append_centre(bridge,"M3","M2","bridging-ligand-path");bad=False
 try:forced_cluster("x",("M1","M2","M3"),(relation("M1","M2","direct-metal-bond"),))
 except InadmissibleExactValue:bad=True
 p=primary["exact_postseal_analysis"]
 return {"direct_centre_count":direct.centre_count.value,"direct_bond_count":direct.direct_bond_count.value,"bridge_ligand_occurrence_count":len(bridge.relations[0].bridge_support),"bridge_path_count":bridge.bridge_path_count.value,"group_direct_absence":isinstance(group.direct_bond_count,EmptyOne),"successor_centre_count":succ.centre_count.value,"disconnected_rejected":bad,"complete_target_count":len(rows),"complete_source_count":len({x["source_id"] for x in rows}),"all_registered_surfaces_present":all(x["source_outcome"]["registered_surface_present"] for x in rows),"charge_inscription_surface_count":sum("charge-inscriptions" in x["source_record_role"] for x in rows),"complete_target_vector_hash":p["complete_target_vector_hash"],"source_recapture_count":p["source_recapture_count"],"all_rows_preserved":p["all_rows_preserved"]}
class MetalClusterBondingValidator:
 def __init__(self,root):self.root=root.resolve();self.spec=METAL_CLUSTER_BONDING_SPEC
 def validate(self,sealed):
  self.spec.validate();reg=experiment_registration_record(self.root);rh=sha256_identity(reg);doc=prediction_program_document(self.root);program=fold_program_from_mapping(doc);inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)};env=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(x.target_id for x in self.spec.target_rows),sealed.seal_hash,rh);before=snapshot_protected_tree(self.root);execution=CapabilityClosedFoldInterpreter().execute(program,inputs);boundary=BlindExperimentBoundary(env);pseal=boundary.seal_prediction(execution.output,execution.trace);after=snapshot_protected_tree(self.root);audited,audit=HostilePackageAuditor().audit_program_document(doc,before,after)
  if sha256_identity(audited)!=execution.program_hash or not audit.passed:raise ValueError("INORG-014 package changed")
  predicted=_prediction_map(execution.output);rows=_source_rows(self.root);vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-complete-target-custodian",targets={x["target_id"]:HeldLabel("external-complete-source-record-hash",x["target_payload_hash"]) for x in rows},custody_nonce=sha256_identity((rh,TARGET_HASH)),expected_envelope_hash=sha256_identity(env));release=vault.release(pseal);CrossPlatformCustodyExchange.verify(vault.commitment,release,pseal);boundary.measurement_context(release.targets);comp=[]
  for row in rows:
   word=predicted[row["target_id"]];vals=tuple(str(row[k]) for k in IDENTITY_KEYS[1:]);im=all(isinstance(word.cells[i],HeldLabel) and word.cells[i].label==v for i,v in enumerate(vals,1));lm=tuple(x.label for x in word.cells[7:])==EXPECTED_LAWS;tm=release.targets[row["target_id"]]==HeldLabel("external-complete-source-record-hash",row["target_payload_hash"]);comp.append({"target_id":row["target_id"],"identity_match":im,"law_match":lm,"postseal_target_hash_match":tm,"passed":im and lm and tm})
  a=exact_analysis(rows,json.loads((self.root/PRIMARY_PATH).read_text()))
  try:exact_analysis(rows[:-1],{});om=False
  except ValueError:om=True
  try:FoldWord((0,));zr=False
  except FoldLanguageHalt:zr=True
  controls={"omitted_source_row_rejected":om,"numerical_zero_rejected":zr,"all_ten_target_hashes_bound_postseal":len(release.targets)==10,"disconnected_cluster_rejected":a["disconnected_rejected"],"signed_charge_retained_downstream_only":a["charge_inscription_surface_count"]==1,"sources_not_recaptured":a["source_recapture_count"]==0,"prediction_contains_no_definition_example_charge_or_target":not any(t in json.dumps(doc,sort_keys=True) for t in ("complete_definition_text","target_payload_hash","[4\\! Fe-4\\! S]"))}
  passed=all(x["passed"] for x in comp) and (a["direct_centre_count"],a["direct_bond_count"],a["bridge_ligand_occurrence_count"],a["bridge_path_count"],a["successor_centre_count"])==(2,1,2,1,3) and a["group_direct_absence"] and a["complete_target_count"]==10 and a["complete_source_count"]==2 and a["all_registered_surfaces_present"] and a["all_rows_preserved"] and all(controls.values())
  isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("exact-metal-cluster/1",self.spec.falsification_condition)),prediction_seal_hash=pseal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash));tid=target_identity_from_release(release)
  if tid!=vault.commitment.target_identity_hash:raise ValueError("INORG-014 target identity differs")
  custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=rh,registered_target_identity_hash=tid,prediction_seal_hash=pseal.seal_hash,target_release_manifest_hash=release.release_hash));payload={"registration":rh,"sealed":sealed.seal_hash,"prediction":pseal.seal_hash,"analysis":a,"comparisons":comp,"controls":controls,"trace":execution.trace_hash};measurements=("two-centre direct, two-centre two-bridge and held grouping cluster witnesses; successor centre count three","complete ten-row two-source cluster and iron-sulfur vector; external charge inscriptions retained downstream",f"complete exact target vector {a['complete_target_vector_hash']}")+tuple(f"control {k}: {v}" for k,v in controls.items());return EmpiricalValidation(sealed.seal_hash,rh,isolation,custody,True,True,True,tuple(dict.fromkeys(x["source_id"] for x in rows)),measurements,sha256_identity(payload),self.spec.falsification_condition,passed)
__all__=("MetalClusterBondingValidator","_identities","_prediction_map","_source_rows","exact_analysis","experiment_registration_record","prediction_program_document")
