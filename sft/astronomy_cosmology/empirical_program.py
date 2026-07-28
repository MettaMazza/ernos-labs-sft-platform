"""Astronomy generated laws and post-seal external evidence adapter."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from sft.astronomy_cosmology.generated_law import ASTRONOMY_BLUEPRINTS, AstronomyBlueprint
from sft.engine import ClaimRegistration, EvidenceMode, ProvenanceClass, ROOT_THEOREM
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator, ExternalTargetRow, GeneratedEmpiricalPhysicsProgram, LawChoice, LawDimension

ROOT=Path(__file__).resolve().parents[2]
PRE_SOURCE_SEAL_PATH="experiments/sealed_predictions/astronomy_cosmology_foundation_complete_pre_source.json"
TARGETS_PATH="experiments/astronomy_cosmology/external_targets.json"

def verified(path, key):
    value=json.loads((ROOT/path).read_text()); claimed=value.pop(key)
    if sha256_identity(value)!=claimed: raise ValueError(f"Astronomy evidence identity mismatch: {path}")
    value[key]=claimed; return value

def adapt(bp):
    return tuple(LawDimension(d.key,tuple(LawChoice(c.name,d.required_property in c.properties,c.explanation) for c in d.choices)) for d in bp.dimensions)

@dataclass(frozen=True)
class AstronomySpec:
    blueprint: AstronomyBlueprint
    dimensions: tuple[LawDimension,...]
    target_rows: tuple[ExternalTargetRow,...]
    source_snapshot_path: str
    source_snapshot_hash: str
    empirical_disposition: str
    directness: str

    def __getattr__(self,name): return getattr(self.blueprint,name)
    @property
    def expected_observation_label(self): return self.blueprint.predicted_observation_label
    def validate(self):
        self.blueprint.validate()
        if len(self.dimensions)!=8 or not self.target_rows: raise ValueError("Astronomy adapter lost grammar or evidence")
        row=verified(self.source_snapshot_path,"target_row_hash")
        if row["claim_id"]!=self.claim_id or row["observed_label"]!=self.expected_observation_label or row["exact_match"] is not True: raise ValueError("Astronomy target record changed")
        if row["external_evidence_selected_survivor"] is not False:
            raise ValueError("Astronomy evidence selected the structural survivor")
        numeric=row.get("numeric_comparison")
        if numeric is not None and numeric.get("first_adverse_result_reclassified") is not False:
            raise ValueError("Astronomy first adverse result was reclassified")

def build_specs():
    seal=verified(PRE_SOURCE_SEAL_PATH,"complete_branch_pre_source_seal_hash")
    if any(seal[x] is not False for x in ("external_source_identities_selected","external_source_content_opened","external_outcomes_opened")): raise ValueError("Astronomy pre-source order changed")
    for relative,wanted in seal["sealed_files"].items():
        if hash_file(ROOT/relative)!=wanted:
            raise ValueError(f"Astronomy pre-source file changed: {relative}")
    targets=verified(TARGETS_PATH,"targets_hash"); by={x["claim_id"]:x for x in targets["targets"]}
    out=[]
    for bp in ASTRONOMY_BLUEPRINTS:
        row=by[bp.claim_id]; relative=row["target_record_path"]
        target=verified(relative,"target_row_hash")
        first=target["source_evidence"][0]
        out.append(AstronomySpec(bp,adapt(bp),(ExternalTargetRow(target["target_id"],first["source_id"],first["registered_locator"],target["observed_label"]),),relative,hash_file(ROOT/relative),target["empirical_disposition"],target["directness"]))
    return tuple(out)

ASTRONOMY_SPECS=build_specs()

class GeneratedEmpiricalAstronomyProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return ClaimRegistration(claim_id=self.spec.claim_id,title=self.spec.title,branch="astronomy_cosmology",statement=self.spec.statement,evidence_mode=EvidenceMode.EMPIRICAL,root_theorems=(ROOT_THEOREM,),dependencies=self.spec.dependencies,axioms=(),free_parameters=(),provenance=(ProvenanceClass.FORWARD_FORCING,),source_hash=self.source_hash)

class BlindAstronomyBoundaryValidator(BlindExternalMeasurementValidator):
    pass

__all__=("ASTRONOMY_SPECS","AstronomySpec","GeneratedEmpiricalAstronomyProgram","BlindAstronomyBoundaryValidator","PRE_SOURCE_SEAL_PATH")
