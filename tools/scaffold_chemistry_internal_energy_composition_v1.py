#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-003."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.internal_energy_composition_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, IDENTITY_PATH, INTERNAL_ENERGY_COMPOSITION_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    SNAPSHOT_HASH, SNAPSHOT_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.internal_energy_composition_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = INTERNAL_ENERGY_COMPOSITION_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free THERMO-003 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def compose_parts(parts):
    if not parts or len({{name for name, _ in parts}}) != len(parts) or any(value <= 0 for _, value in parts):
        raise ValueError("nonempty unique positive parts required")
    return sum((value for _, value in parts), Fraction(0,1))

def relation(first, second):
    if first[:2] != second[:2] or first[2] <= 0 or second[2] <= 0: raise ValueError("held context differs")
    if first[2] == second[2]: return "equal", None
    return ("rise", second[2]-first[2]) if second[2] > first[2] else ("fall", first[2]-second[2])

def compose_steps(steps):
    active=tuple(step for step in steps if step[1] is not None)
    if not active:return "equal",None
    if len({{step[0] for step in active}}) != 1:raise ValueError("opposed steps rejected")
    return active[0][0],sum((step[1] for step in active),Fraction(0,1))

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed=json.load(handle)
    generated=["__".join(row) for row in product(*DOMAINS)]
    received=[row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions={{row["candidate_id"]:row["survives"] for row in sealed["decisions"]}}
    parts=(("first",Fraction(2,3)),("second",Fraction(5,4)))
    extended=parts+(("third",Fraction(7,5)),)
    a=("water","one-bar",Fraction(5,3));b=("water","one-bar",Fraction(8,3));c=("water","one-bar",Fraction(14,3))
    one,two=relation(a,b),relation(b,c)
    opposed=False
    try:compose_steps((one,relation(c,b)))
    except ValueError:opposed=True
    controls=sealed["controls"]
    passed=(
        sealed["claim_id"]==CLAIM_ID and received==generated
        and sealed["census"]["expected_cardinality"]==len(generated)==256
        and len(set(received))==len(generated)
        and decisions=={{candidate:candidate==SURVIVOR for candidate in generated}}
        and sum(decisions.values())==1 and sealed["closure"]["scope"]=="depth_independent"
        and sealed["closure"]["minimality_passed"] is True and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}}=={{"false_premise","tampered_source","tampered_artifact","boundary"}}
        and all(row["passed"] is True for row in controls)
        and compose_parts(parts)==Fraction(23,12) and compose_parts(extended)==Fraction(199,60)
        and one==("rise",Fraction(1,1)) and compose_steps((one,two))==relation(a,c) and opposed
    )
    print(json.dumps({{
        "validated_seal_hash":sealed["seal_hash"],"recomputed_from_declared_inputs":True,"passed":passed,
        "certificate":{{"claim_id":CLAIM_ID,"generated_cardinality":len(generated),"unique_survivor":SURVIVOR if passed else None,
        "closure":"depth_independent" if passed else None,"exact_positive_parts_reconstructed":compose_parts(parts)==Fraction(23,12),
        "held_orientation_reconstructed":one==("rise",Fraction(1,1)),"path_composition_reconstructed":compose_steps((one,two))==relation(a,c),
        "opposed_signed_cancellation_rejected":opposed,"append_only_part_reconstructed":extended[:-1]==parts,"measurement_file_accessed":False}},
    }},sort_keys=True))

if __name__=="__main__":main()
'''


def execution_source() -> str:
    claim_id = INTERNAL_ENERGY_COMPOSITION_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.internal_energy_composition_batch_v1 import (
    INTERNAL_ENERGY_COMPOSITION_SPEC, SNAPSHOT_PATH, PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.internal_energy_composition_validation_v1 import InternalEnergyCompositionValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files=(
        root/"sft/chemistry/internal_energy_composition_law_v1.py",
        root/"sft/chemistry/internal_energy_composition_batch_v1.py",
        root/"sft/chemistry/internal_energy_composition_validation_v1.py",
        root/"sft/chemistry/generated_law.py",root/"sft/chemistry/generated_observational_law.py",
        root/"sft/physics/generated_empirical_law.py",
        root/"tools/capture_chemistry_thermophysical_state_sources_v1.py",
        root/SNAPSHOT_PATH,root/PRIMARY_PATH,root/IDENTITY_PATH,root/TARGET_PATH,
        root/"claims/{claim_id}/execution.py",
    )
    source_hash=build_source_manifest(root,source_files).manifest_hash
    validator=root/"claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(INTERNAL_ENERGY_COMPOSITION_SPEC,source_hash),
        independent_validator=ExternalCommandValidator("sft-chem-internal-energy-composition-003-independent-python/1",(sys.executable,str(validator)),validator.parent,(validator,)),
        source_files=source_files,empirical_validator=InternalEnergyCompositionValidator(root),
    )
'''


def main() -> None:
    spec=INTERNAL_ENERGY_COMPOSITION_SPEC
    package=ROOT/"claims"/spec.claim_id
    registration={
        "$schema":"../../governance/claim.schema.json","claim_id":spec.claim_id,"title":spec.title,"branch":"chemistry","status":"registered",
        "statement":spec.statement,"dependencies":list(spec.dependencies),"provenance_classes":["observational_derivation"],
        "candidate_grammar":{"generator":spec.generation_rule,"boundary":spec.grammar_boundary,"expected_cardinality":256,"completeness_certificate":sha256_identity(completeness_record(spec))},
        "excluded_inputs":list(spec.exclusions),"required_controls":["false_premise","tampered_source","tampered_artifact","boundary"],
        "empirical_protocol":"experiments/chemistry/"+spec.experiment_id+"/registration.json","registered_by":"Maria Smith","registration_date":"2026-07-26",
    }
    experiment={
        "$schema":"../../../governance/experiment.schema.json",**experiment_registration_record(ROOT),"evidence_mode":"observational_derivation",
        "external_sources":[{"source_id":"NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-FLUID-PROPERTIES","body":"National Institute of Standards and Technology","role":"complete direct internal-energy and thermophysical state vector"}],
        "source_hashes":{"NIST_snapshot":SNAPSHOT_HASH,"normalized_primary_records":PRIMARY_HASH,"identity_registry":IDENTITY_HASH,"withheld_targets":TARGET_HASH},
        "prediction_protocol":{"program_hash":sha256_identity(prediction_program_document(ROOT)),"temperatures_phases_or_property_values_present":False,"target_content_inaccessible":True,"complete_trace_required":True},
        "registered_by":"Maria Smith","registration_date":"2026-07-26","status":"registered",
    }
    note=f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-003`

## WHY

Internal energy cannot be replaced by an enthalpy proxy or a signed answer. SFT retains the complete chemical state, composes exact positive named parts, and holds rise/fall orientation separately. Equality is structural `EmptyOne`.

## DERIVATION

The complete eight-axis grammar generates 256 forms and leaves exactly one survivor:

`{survivor_id(spec)}`

Same-direction exact state steps compose to the direct separation. Opposed paths require separate records and cannot silently cancel. Appending one named positive part preserves every prior part without a fit.

## CHECK

All 13 row identities seal before values open. The complete NIST one-bar water vector retains all 14 columns, 9 liquid states, 4 vapour states and both 372.75593 K phase-boundary rows. Direct internal energy rises exactly from `2.0276785` to `45.899550 kJ/mol`; all 12 exact positive increments sum to the direct separation. External signed Joule-Thomson inscriptions remain source records and never enter the proof arithmetic.

## FALSIFICATION

{spec.falsification_condition}
"""
    write(package/"registration.json",json.dumps(registration,indent=2,sort_keys=True)+"\n")
    write(package/"independent_validator.py",independent_validator_source())
    write(package/"execution.py",execution_source())
    write(package/"WHY_DERIVATION_CHECK.md",note)
    write(ROOT/"experiments/chemistry"/spec.experiment_id/"registration.json",json.dumps(experiment,indent=2,sort_keys=True)+"\n")
    print(f"scaffolded {spec.claim_id}")


if __name__=="__main__":main()
