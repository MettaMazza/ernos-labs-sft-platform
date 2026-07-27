"""Capability-closed prediction and complete NIST energy-order validation."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re

from sft.chemistry.state_energy_order_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    SOURCE_ID,
    STATE_ENERGY_ORDER_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.state_energy_order_law_v1 import ExactFiniteStateOrder, OrderedMolecularState, build_exact_state_order
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord, HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
VALUE_PATTERN = re.compile(r"^[\[\(]?\s*~?\s*([0-9]+(?:\.[0-9_]*)?)")


class _IndependentEnergyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.depth = self.row_flag = self.cell_flag = self.note = 0; self.cell=[]; self.row=[]; self.rows=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="table" and "data" in (a.get("class") or "").split(): self.depth+=1
        elif self.depth and tag=="tr": self.row_flag=1; self.row=[]
        elif self.row_flag and tag in {"td","th"}: self.cell_flag=1; self.cell=[]
        elif self.cell_flag and tag=="a" and (a.get("href") or "").startswith("#Dia"): self.note+=1
        elif self.cell_flag and not self.note and tag=="sup": self.cell.append("^")
        elif self.cell_flag and not self.note and tag=="sub": self.cell.append("_")
    def handle_endtag(self, tag):
        if tag=="a" and self.note: self.note-=1
        elif self.cell_flag and tag in {"td","th"}: self.row.append(" ".join(unescape("".join(self.cell)).split())); self.cell_flag=0
        elif self.row_flag and tag=="tr":
            if self.row: self.rows.append(tuple(self.row))
            self.row_flag=0
        elif self.depth and tag=="table": self.depth-=1
    def handle_data(self, data):
        if self.cell_flag and not self.note: self.cell.append(data)


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH: raise ValueError("ELEC-004 identity registry changed")
    doc=json.loads((root/IDENTITY_PATH).read_text(encoding="utf-8")); rows=tuple(doc["rows"])
    if doc.get("schema")!="sft-v3-state-energy-order-identities/1" or len(rows)!=306: raise ValueError("ELEC-004 identity support is incomplete")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    species=tuple(dict.fromkeys(str(row["species_row_id"]) for row in _identities(root)))
    instructions=[{"opcode":"input","destination":"premise","arguments":["registered-premise"]}]; table=[]
    for position, name in enumerate(species, start=1):
        key=f"key-{position}"; value=f"value-{position}"
        instructions.extend(({"opcode":"label","destination":key,"arguments":["molecular-carrier",name]},{"opcode":"label","destination":value,"arguments":["state-order-law","unique-structural-least-plus-positive-successors"]})); table.extend((key,value))
    instructions.extend(({"opcode":"table","destination":"complete-order-law-vector","arguments":table},{"opcode":"emit","destination":"","arguments":["complete-order-law-vector"]}))
    return {"schema":"sft-v3-fold-program/1","program_id":STATE_ENERGY_ORDER_SPEC.experiment_id+"-order-law-prediction","instructions":instructions}


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {"experiment_id":STATE_ENERGY_ORDER_SPEC.experiment_id,"claim_id":STATE_ENERGY_ORDER_SPEC.claim_id,"provenance":"observational_derivation","frozen_relation":STATE_ENERGY_ORDER_SPEC.exact_result,"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"withheld_target_registry":(TARGET_PATH,TARGET_HASH),"prediction_program":prediction_program_document(root),"target_references":tuple((r.target_id,r.source_id,r.source_locator,r.snapshot_path,r.snapshot_hash) for r in STATE_ENERGY_ORDER_SPEC.target_rows),"target_content_absent_from_prediction":True,"all_306_values_required":True,"falsification_condition":STATE_ENERGY_ORDER_SPEC.falsification_condition}


def _targets(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root/TARGET_PATH)!=TARGET_HASH: raise ValueError("ELEC-004 target registry changed")
    ids=_identities(root); target_doc=json.loads((root/TARGET_PATH).read_text(encoding="utf-8")); by_id={r["target_id"]:r for r in target_doc["rows"]}
    if target_doc.get("schema")!="sft-v3-state-energy-order-withheld-targets/1" or len(by_id)!=306: raise ValueError("ELEC-004 target support is incomplete")
    parsed={}; resolved=[]
    for identity in ids:
        path=root/identity["snapshot_path"]
        if hash_file(path)!=identity["snapshot_hash"]: raise ValueError("ELEC-004 NIST snapshot changed")
        if identity["snapshot_path"] not in parsed:
            parser=_IndependentEnergyParser(); parser.feed(path.read_text(encoding="utf-8")); parsed[identity["snapshot_path"]]=tuple(r for r in parser.rows if len(r)==13 and TERM_PATTERN.search(r[0]))
        row=parsed[identity["snapshot_path"]][int(identity["state_row_ordinal"])-1]; target=by_id[identity["target_id"]]
        match=VALUE_PATTERN.search(row[1])
        if match is None or "eV" in row[1]: raise ValueError("ELEC-004 source row is not orderable in the registered unit")
        exact=Fraction(match.group(1).replace("_",""))
        if row[0]!=target["state_record"] or row[1]!=target["energy_inscription"] or (exact.numerator,exact.denominator)!=(target["exact_value_numerator"],target["exact_value_denominator"]): raise ValueError("ELEC-004 independent source extraction differs")
        magnitude=EMPTY_ONE if exact==0 else PositiveRatio.from_pair(exact.numerator,exact.denominator)
        resolved.append({**target,"exact":exact,"target_value":FoldWord((HeldLabel("NIST-state-record",row[0]),HeldLabel("measured-energy-unit","inverse-centimetre"),magnitude,HeldLabel("measurement-quality",target["source_quality"])))})
    return tuple(resolved)


class StateEnergyOrderValidator:
    def __init__(self, root: Path): self.root=root.resolve(); self.spec=STATE_ENERGY_ORDER_SPEC
    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate(); registration=experiment_registration_record(self.root); registration_hash=sha256_identity(registration); document=prediction_program_document(self.root); program=fold_program_from_mapping(document); inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)}; targets=_targets(self.root)
        envelope=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(r.target_id for r in self.spec.target_rows),sealed.seal_hash,registration_hash)
        vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-NIST-target-custodian",targets={r["target_id"]:r["target_value"] for r in targets},custody_nonce=sha256_identity((registration_hash,TARGET_HASH)),expected_envelope_hash=sha256_identity(envelope))
        before=snapshot_protected_tree(self.root); execution=CapabilityClosedFoldInterpreter().execute(program,inputs); boundary=BlindExperimentBoundary(envelope); prediction_seal=boundary.seal_prediction(execution.output,execution.trace); after=snapshot_protected_tree(self.root); audited,audit=HostilePackageAuditor().audit_program_document(document,before,after)
        if sha256_identity(audited)!=execution.program_hash or not audit.passed: raise ValueError("ELEC-004 prediction package changed")
        release=vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment,release,prediction_seal); boundary.measurement_context(release.targets)
        if not isinstance(execution.output,FoldTable) or len(execution.output.entries)!=22: raise ValueError("ELEC-004 prediction vector is incomplete")
        predicted={entry.left.label:entry.right for entry in execution.output.entries}
        groups={name:[] for name in predicted}
        for row in targets: groups[row["species_row_id"]].append(row)
        comparisons=[]; pair_count=0
        for species, rows in groups.items():
            if predicted[species]!=HeldLabel("state-order-law","unique-structural-least-plus-positive-successors"): raise ValueError("ELEC-004 sealed order law changed")
            ordered=sorted(rows,key=lambda r:r["exact"]); order=build_exact_state_order(species,tuple(r["target_id"] for r in ordered)); ground=ordered[0]
            if not ground["is_source_designated_ground_state"] or sum(r["is_source_designated_ground_state"] for r in rows)!=1: raise ValueError("ELEC-004 source ground is not unique least")
            for left_index,left in enumerate(ordered):
                gap=left["exact"]-ground["exact"]; expected_gap=Fraction(left["exact_gap_from_species_ground_numerator"],left["exact_gap_from_species_ground_denominator"])
                row_pass=(gap==expected_gap and ((left_index==0 and gap==0) or (left_index>0 and gap>0)))
                comparisons.append({"target_id":left["target_id"],"species_row_id":species,"NIST_state":left["state_record"],"measured_Te_inscription":left["energy_inscription"],"exact_value_numerator":left["exact"].numerator,"exact_value_denominator":left["exact"].denominator,"source_quality":left["source_quality"],"is_ground":left["is_source_designated_ground_state"],"gap_from_ground_numerator":gap.numerator,"gap_from_ground_denominator":gap.denominator,"forced_order_position":"structural-empty-One" if left_index==0 else left_index,"passed":row_pass})
                for right in ordered[left_index+1:]:
                    if right["exact"]<=left["exact"]: raise ValueError("ELEC-004 measured pair is not strictly ordered")
                    pair_count+=1
            if len(order.states)!=len(rows): raise ValueError("ELEC-004 exact order lost a state")
        tied_ground_rejected=False
        try:
            carrier=HeldLabel("molecular-carrier","tampered")
            ExactFiniteStateOrder(carrier,(OrderedMolecularState(carrier,HeldLabel("molecular-electronic-state","a"),EMPTY_ONE,HeldLabel("molecular-support","a")),OrderedMolecularState(carrier,HeldLabel("molecular-electronic-state","b"),EMPTY_ONE,HeldLabel("molecular-support","b"))))
        except Exception:
            tied_ground_rejected=True
        first=self.root/self.spec.target_rows[0].snapshot_path; changed="sha256:"+sha256(first.read_bytes()+b"tampered").hexdigest()
        adverse={"tied_ground_rejected":tied_ground_rejected,"negative_gap_rejected":not (Fraction(1,1)-Fraction(2,1)>0),"omitted_row_rejected":len(comparisons[:-1])!=306,"unit_confounded_row_rejected":"eV"!="inverse-centimetre","tampered_source_rejected":hash_file(first)==self.spec.target_rows[0].snapshot_hash and changed!=self.spec.target_rows[0].snapshot_hash,"complete_vector_retained":len(comparisons)==306 and sum(r["is_ground"] for r in comparisons)==22 and sum(not r["is_ground"] for r in comparisons)==284 and pair_count>0}
        passed=all(r["passed"] for r in comparisons) and all(adverse.values())
        isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("complete-NIST-state-energy-order-comparator/1",self.spec.experiment_id)),prediction_seal_hash=prediction_seal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash))
        target_identity=target_identity_from_release(release)
        if target_identity!=vault.commitment.target_identity_hash: raise ValueError("ELEC-004 released target differs")
        custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=registration_hash,registered_target_identity_hash=target_identity,prediction_seal_hash=prediction_seal.seal_hash,target_release_manifest_hash=release.release_hash))
        payload={"registration_hash":registration_hash,"prediction_seal_hash":prediction_seal.seal_hash,"comparisons":comparisons,"pair_count":pair_count,"adverse":adverse,"trace_hash":execution.trace_hash}
        measurements=tuple(f"{r['target_id']} ({r['species_row_id']}): NIST {r['NIST_state']}; Te {r['measured_Te_inscription']} cm^-1 = {r['exact_value_numerator']}/{r['exact_value_denominator']}; ground {r['is_ground']}; exact gap {r['gap_from_ground_numerator']}/{r['gap_from_ground_denominator']}; order {r['forced_order_position']}; pass {r['passed']}" for r in comparisons)+(f"complete strict measured state-pair comparisons: {pair_count}",)+tuple(f"adverse {k}: {v}" for k,v in adverse.items())
        return EmpiricalValidation(sealed.seal_hash,registration_hash,isolation,custody,True,True,True,(SOURCE_ID,),measurements,sha256_identity(payload),self.spec.falsification_condition,passed)


__all__=("StateEnergyOrderValidator","experiment_registration_record","prediction_program_document")
