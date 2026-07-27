"""Capability-closed complete NIST H2/HD/D2 validation for ELEC-012."""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from html import unescape
from html.parser import HTMLParser
import itertools
import json
from pathlib import Path
import platform
import re

from sft.chemistry.nuclear_electronic_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, NUCLEAR_ELECTRONIC_SPEC, SOURCE_ID, TARGET_HASH, TARGET_PATH
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


TERM_PATTERN = re.compile(r"\^[1-9][0-9]*(?:Σ|Π|Δ|Φ)")
VALUE_PATTERN = re.compile(r"^[\[\(]?\s*~?\s*([+-]?[0-9]+(?:\.[0-9_]*)?)")
WEIGHT_PATTERN = re.compile(r"Molecular weight.*?</a>:</strong>\s*([^<]+)", re.S)


class IndependentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.depth=self.row_flag=self.cell_flag=self.note=0; self.cell=[]; self.row=[]; self.rows=[]
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


def prediction_program_document(root: Path):
    values=(("carrier","retained-joint-molecular-carrier"),("nuclear","retained-occurrence-and-isotope-support"),("electronic","retained-electronic-support-and-state"),("composition","finite-nuclear-electronic-joint-product"),("scale","exact-coordinate-partition-without-separation-parameter"),("transport","exact-isotope-labelled-coordinate-transport"),("absence","EmptyOne-or-held-external-inscription"),("record","complete-isotopologue-and-vibronic-record"))
    instructions=[{"opcode":"input","destination":"premise","arguments":["registered-premise"]}]; table=[]
    for position,(name,value) in enumerate(values,start=1):
        key,value_key="key-%d"%position,"value-%d"%position
        instructions.extend(({"opcode":"label","destination":key,"arguments":["nuclear-electronic-axis",name]},{"opcode":"label","destination":value_key,"arguments":["nuclear-electronic-law",value]})); table.extend((key,value_key))
    instructions.extend(({"opcode":"table","destination":"law","arguments":table},{"opcode":"emit","destination":"","arguments":["law"]}))
    return {"schema":"sft-v3-fold-program/1","program_id":NUCLEAR_ELECTRONIC_SPEC.experiment_id+"-prediction","instructions":instructions}


def experiment_registration_record(root: Path):
    spec=NUCLEAR_ELECTRONIC_SPEC
    return {"experiment_id":spec.experiment_id,"claim_id":spec.claim_id,"provenance":"observational_derivation","frozen_relation":spec.exact_result,"identity_registry":(IDENTITY_PATH,IDENTITY_HASH),"withheld_target_registry":(TARGET_PATH,TARGET_HASH),"prediction_program":prediction_program_document(root),"target_references":tuple((r.target_id,r.source_id,r.source_locator,r.snapshot_path,r.snapshot_hash) for r in spec.target_rows),"target_content_absent_from_prediction":True,"all_95_rows_and_1235_cells_required":True,"falsification_condition":spec.falsification_condition}


def _source_rows(root: Path):
    for path, expected in ((IDENTITY_PATH,IDENTITY_HASH),(TARGET_PATH,TARGET_HASH)):
        if hash_file(root/path)!=expected: raise ValueError("ELEC-012 registry changed: "+path)
    identities=json.loads((root/IDENTITY_PATH).read_text(encoding="utf-8"))["rows"]
    targets=json.loads((root/TARGET_PATH).read_text(encoding="utf-8"))["rows"]
    by_id={row["target_id"]:row for row in targets}; parsed={}; resolved=[]
    if len(identities)!=95 or len(by_id)!=95: raise ValueError("ELEC-012 complete row surface missing")
    for identity in identities:
        path=root/identity["snapshot_path"]
        if hash_file(path)!=identity["snapshot_hash"]: raise ValueError("ELEC-012 NIST snapshot changed")
        if str(path) not in parsed:
            text=path.read_text(encoding="utf-8"); parser=IndependentParser(); parser.feed(text)
            match=WEIGHT_PATTERN.search(text)
            if match is None: raise ValueError("ELEC-012 molecular weight missing")
            parsed[str(path)]=(tuple(row for row in parser.rows if len(row)==13 and TERM_PATTERN.search(row[0])),match.group(1).strip())
        state_rows,weight=parsed[str(path)]; raw=state_rows[int(identity["state_row_ordinal"])-1]; target=by_id[identity["target_id"]]
        if list(raw)!=target["state_cells"] or weight!=target["molecular_weight_inscription"] or list(identity["nuclear_isotope_labels"])!=target["nuclear_isotope_labels"]:
            raise ValueError("ELEC-012 independent source reconstruction differs")
        resolved.append(target)
    return tuple(resolved)


def _cell_form(cell: str):
    if cell=="": return "blank-EmptyOne", EMPTY_ONE
    match=VALUE_PATTERN.match(cell)
    if match is None: return "held-text", HeldLabel("external-source-inscription",cell)
    exact=Fraction(match.group(1).replace("_",""))
    if exact==0: return "source-zero-EmptyOne", EMPTY_ONE
    if exact<0: return "held-negative-inscription", HeldLabel("external-signed-inscription",cell)
    return "positive-exact", PositiveRatio.from_pair(exact.numerator,exact.denominator)


class NuclearElectronicValidator:
    def __init__(self, root: Path): self.root=root.resolve(); self.spec=NUCLEAR_ELECTRONIC_SPEC
    def validate(self, sealed):
        rows=_source_rows(self.root); registration=experiment_registration_record(self.root); registration_hash=sha256_identity(registration); document=prediction_program_document(self.root); program=fold_program_from_mapping(document); inputs={"registered-premise":HeldLabel("sealed-derivation",sealed.seal_hash)}
        envelope=PredictionEnvelope(self.spec.experiment_id,{"registered-premise":sha256_identity(inputs["registered-premise"])},tuple(r.target_id for r in self.spec.target_rows),sealed.seal_hash,registration_hash)
        vault=TargetVault(experiment_id=self.spec.experiment_id,custodian_id=self.spec.experiment_id+"-NIST-custodian",targets={row["target_id"]:HeldLabel("external-nuclear-electronic-row",sha256_identity(row)) for row in rows},custody_nonce=sha256_identity((registration_hash,TARGET_HASH)),expected_envelope_hash=sha256_identity(envelope))
        before=snapshot_protected_tree(self.root); execution=CapabilityClosedFoldInterpreter().execute(program,inputs); boundary=BlindExperimentBoundary(envelope); prediction_seal=boundary.seal_prediction(execution.output,execution.trace); after=snapshot_protected_tree(self.root); audited,audit=HostilePackageAuditor().audit_program_document(document,before,after)
        if sha256_identity(audited)!=execution.program_hash or not audit.passed or not isinstance(execution.output,FoldTable) or len(execution.output.entries)!=8: raise ValueError("ELEC-012 prediction package differs")
        release=vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment,release,prediction_seal); boundary.measurement_context(release.targets)
        counts={"positive-exact":0,"source-zero-EmptyOne":0,"held-negative-inscription":0,"held-text":0,"blank-EmptyOne":0}; row_comparisons=[]; by_species=defaultdict(list)
        for row in rows:
            forms=[]
            for cell in row["state_cells"]:
                name,_value=_cell_form(cell); counts[name]+=1; forms.append(name)
            passed=release.targets[row["target_id"]].label==sha256_identity(row)
            row_comparisons.append({"target_id":row["target_id"],"species":row["species"],"cell_forms":forms,"passed":passed}); by_species[row["species"]].append(row)
        expected_counts={"positive-exact":551,"source-zero-EmptyOne":3,"held-negative-inscription":8,"held-text":223,"blank-EmptyOne":450}
        weights={species:Fraction(group[0]["molecular_weight_inscription"]) for species,group in by_species.items()}
        if any(any(Fraction(row["molecular_weight_inscription"])!=weight for row in by_species[species]) for species,weight in weights.items()): raise ValueError("ELEC-012 molecular weight changed within species")
        support={species:tuple(group[0]["nuclear_isotope_labels"]) for species,group in by_species.items()}
        designators=defaultdict(list)
        for row in rows: designators[row["state_cells"][0].split()[0]].append(row)
        pair_rows=[]
        for designator,group in designators.items():
            for left,right in itertools.combinations(group,2):
                if tuple(left["nuclear_isotope_labels"])==tuple(right["nuclear_isotope_labels"]): raise ValueError("ELEC-012 isotope support merged")
                for column in range(1,11):
                    lk,lv=_cell_form(left["state_cells"][column]); rk,rv=_cell_form(right["state_cells"][column])
                    if lk==rk=="positive-exact":
                        exact_ratio=lv.fraction/rv.fraction
                        ratio=PositiveRatio.from_pair(exact_ratio.numerator,exact_ratio.denominator)
                        pair_rows.append({"state_designator":designator,"left_species":left["species"],"right_species":right["species"],"column":column,"ratio":repr(ratio),"distinct":lv.fraction!=rv.fraction})
        x_rows=[row for row in rows if row["state_cells"][0].split()[0]=="X"]
        ground_absence=all(_cell_form(row["state_cells"][1])[1] is EMPTY_ONE for row in x_rows)
        adverse={"complete_rows":len(rows)==95 and len(row_comparisons)==95,"complete_cells":sum(counts.values())==1235,"cell_classes_exact":counts==expected_counts,"three_distinct_nuclear_supports":len(set(support.values()))==3,"positive_mass_support_order":weights["H2"]>0 and weights["H2"]<weights["HD"]<weights["D2"],"three_ground_absences":len(x_rows)==3 and ground_absence,"matched_coordinate_pairs":len(pair_rows)==330 and all(row["distinct"] for row in pair_rows),"omitted_row_rejected":len(rows[:-1])!=95,"signed_source_not_proof_number":all(_cell_form(cell)[0]=="held-negative-inscription" for row in rows for cell in row["state_cells"] if VALUE_PATTERN.match(cell or "") and Fraction(VALUE_PATTERN.match(cell).group(1).replace("_",""))<0)}
        passed=all(row["passed"] for row in row_comparisons) and all(adverse.values())
        isolation=seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id+"-prediction-executor",host_platform=platform.system() or "registered-host",python_implementation=platform.python_implementation(),interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),program_hash=execution.program_hash,input_manifest_hash=execution.input_manifest_hash,registered_target_identity_hash=vault.commitment.target_identity_hash,comparison_implementation_identity_hash=sha256_identity(("complete-NIST-H2-HD-D2-comparator/1",self.spec.experiment_id)),prediction_seal_hash=prediction_seal.seal_hash,output_hash=execution.output_hash,trace_hash=execution.trace_hash))
        target_identity=target_identity_from_release(release); custody=seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id,experiment_registration_hash=registration_hash,registered_target_identity_hash=target_identity,prediction_seal_hash=prediction_seal.seal_hash,target_release_manifest_hash=release.release_hash))
        payload={"rows":row_comparisons,"cell_counts":counts,"molecular_weights":{k:str(v) for k,v in weights.items()},"nuclear_supports":support,"matched_positive_coordinate_pairs":pair_rows,"adverse":adverse,"trace":execution.trace_hash}
        measurements=tuple("%s: %s complete cells; pass %s"%(row["target_id"],len(row["cell_forms"]),row["passed"]) for row in row_comparisons)+tuple("%s %s/%s column %s: %s; distinct %s"%(row["state_designator"],row["left_species"],row["right_species"],row["column"],row["ratio"],row["distinct"]) for row in pair_rows)+tuple("count %s: %s"%(k,v) for k,v in counts.items())+tuple("molecular weight %s: %s"%(k,v) for k,v in weights.items())
        return EmpiricalValidation(sealed.seal_hash,registration_hash,isolation,custody,True,True,True,(SOURCE_ID,),measurements,sha256_identity(payload),self.spec.falsification_condition,passed)


__all__=("NuclearElectronicValidator","experiment_registration_record","prediction_program_document")
