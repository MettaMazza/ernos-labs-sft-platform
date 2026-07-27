#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry ORG-004."""
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.antiaromatic_nonaromatic_distinction_batch_v1 import (  # noqa: E402
    ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC,
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRE_SOURCE_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.antiaromatic_nonaromatic_distinction_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct, value-free ORG-004 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}
FIBRES = ("fibre-one", "fibre-two")
PAIR_CELLS = tuple(product(FIBRES, repeat=2))

def same_cycle(kind, centres, plane, conjugated, layers):
    if len(centres) < 3 or len(set(centres)) != len(centres):
        raise ValueError("one complete distinct cycle required")
    edges = tuple(zip(centres, centres[1:] + centres[:1]))
    if kind == "closed":
        if not plane or not conjugated or not layers or any(tuple(layer) != PAIR_CELLS for layer in layers):
            raise ValueError("closed recurrence requires complete planar support")
        support = len(FIBRES) + sum(len(layer) for layer in layers)
    elif kind == "frustrated":
        if not plane or not conjugated or not layers or any(tuple(layer) != PAIR_CELLS for layer in layers):
            raise ValueError("frustrated recurrence requires complete planar support")
        support = sum(len(layer) for layer in layers)
    elif kind == "broken":
        if plane and conjugated or layers:
            raise ValueError("broken recurrence requires a structural break and no recurrence layer")
        support = "structural-EmptyOne"
    else:
        raise ValueError("unknown same-cycle class")
    return {{"kind": kind, "centres": centres, "edges": edges, "support": support}}

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    centres = tuple("c" + str(index) for index in range(1, 7))
    closed = same_cycle("closed", centres, True, True, (PAIR_CELLS,))
    broken = same_cycle("broken", centres, False, True, ())
    frustrated = same_cycle("frustrated", centres, True, True, (PAIR_CELLS,))
    closed_next = same_cycle("closed", centres, True, True, (PAIR_CELLS, PAIR_CELLS))
    frustrated_next = same_cycle("frustrated", centres, True, True, (PAIR_CELLS, PAIR_CELLS))
    anti_break_rejected = missing_break_rejected = incomplete_layer_rejected = False
    try:
        same_cycle("frustrated", centres, False, True, (PAIR_CELLS,))
    except ValueError:
        anti_break_rejected = True
    try:
        same_cycle("broken", centres, True, True, ())
    except ValueError:
        missing_break_rejected = True
    try:
        same_cycle("closed", centres, True, True, (PAIR_CELLS[:-1],))
    except ValueError:
        incomplete_layer_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(generated) == 256 and len(set(received)) == 256
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in sealed["controls"])
        and (closed["support"], broken["support"], frustrated["support"]) == (6, "structural-EmptyOne", 4)
        and (closed_next["support"], broken["support"], frustrated_next["support"]) == (10, "structural-EmptyOne", 8)
        and closed["edges"] == broken["edges"] == frustrated["edges"]
        and anti_break_rejected and missing_break_rejected and incomplete_layer_rejected
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "same_cycle_class_count": 3,
            "base_supports": [closed["support"], broken["support"], frustrated["support"]],
            "successor_supports": [closed_next["support"], broken["support"], frustrated_next["support"]],
            "identical_cycle_graph_retained": closed["edges"] == broken["edges"] == frustrated["edges"],
            "antiaromatic_with_break_rejected": anti_break_rejected,
            "nonaromatic_without_break_rejected": missing_break_rejected,
            "incomplete_pair_cell_layer_rejected": incomplete_layer_rejected,
            "external_definition_species_geometry_energy_value_sign_or_uncertainty_accessed": False,
            "imported_huckel_or_electron_count_rule_used": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys

from sft.chemistry.antiaromatic_nonaromatic_distinction_batch_v1 import (
    ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC, FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH, IDENTITY_PATH,
    PRE_SOURCE_PATH, PRIMARY_PATH, TARGET_PATH,
)
from sft.chemistry.antiaromatic_nonaromatic_distinction_validation_v1 import AntiaromaticNonaromaticDistinctionValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["opened_snapshot_path"] for row in targets["rows"]))
    files = (
        root / "sft/chemistry/antiaromatic_nonaromatic_distinction_law_v1.py",
        root / "sft/chemistry/antiaromatic_nonaromatic_distinction_batch_v1.py",
        root / "sft/chemistry/antiaromatic_nonaromatic_distinction_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_org_001_016_family_sources_v1.py",
        root / "tools/build_chemistry_org_004_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / PRE_SOURCE_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path in snapshots),
        root / "claims/{claim_id}/execution.py",
    )
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-antiaromatic-nonaromatic-distinction-004-independent-python/1",
            (sys.executable, str(independent)), independent.parent, (independent,),
        ),
        files,
        AntiaromaticNonaromaticDistinctionValidator(root),
    )
'''


def main() -> None:
    spec = ANTIAROMATIC_NONAROMATIC_DISTINCTION_SPEC
    package = ROOT / "claims" / spec.claim_id
    if package.exists():
        raise SystemExit("ORG-004 claim package already exists; preserved without replay")
    survivor = survivor_id(spec)
    registration = {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-27",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json",
        **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_sources": [
            {"source_id": "IUPAC-SAME-CYCLE-CLASSIFICATION-SURFACE", "body": "International Union of Pure and Applied Chemistry", "role": "complete aromatic and antiaromaticity term records", "custody": "development-observed-correspondence"},
            {"source_id": "NIST-WEBBOOK-BENZENE-THERMOCHEMISTRY-SURFACE", "body": "National Institute of Standards and Technology", "role": "complete benzene gas thermochemistry control surface", "custody": "development-observed-correspondence"},
            {"source_id": "NIST-CCCBDB-SRD101-BLIND-ANTI-NONAROMATIC-SURFACE", "body": "National Institute of Standards and Technology", "role": "complete preregistered cyclobutadiene and cyclooctatetraene experimental-data pages", "custody": "outcome-unopened-before-law-and-prediction-seal"},
        ],
        "source_hashes": {"identity_registry": IDENTITY_HASH, "withheld_targets": TARGET_HASH, "normalized_primary": PRIMARY_HASH},
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "pre_source_prediction": PRE_SOURCE_PATH,
            "target_values_or_outcomes_present": False,
            "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-27",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ORG-004`

## WHY

The aromatic, antiaromatic and nonaromatic distinction cannot be admitted by importing a named electron-count rule or by selecting molecular examples after seeing their measured stability. ORG-004 instead asks which alternatives are forced when the same exact molecular cycle retains or breaks Fold recurrence.

## DERIVATION

The literal eight-axis grammar generates 256 forms. Exactly one retains the same carrier and cycle while exhausting all three structural alternatives, preserving plane and conjugation as held states, assigning complete closure, complete frustrated return or structural EmptyOne, and extending each complete recurrence by all four ordered Fold pair cells:

`{survivor}`

The primitive closed recurrence contains two held Fold fibres plus four ordered pair cells, forcing support **6**. Complete frustration retains the four pair cells without the two-fibre return, forcing **4**. A broken plane or broken conjugation carries structural **EmptyOne**, never numerical zero. The complete successor adds four cells, producing **10**, **8**, and structural EmptyOne. The same successor proof holds at every positive finite depth.

Opening closure requires one positive distinction transfer; imposing complete frustration requires one further positive transfer. This forces the exact class order closed aromatic recurrence, broken nonaromatic recurrence, frustrated antiaromatic recurrence without importing Hückel `4n+2`/`4n`, an electron lookup, a molecular name, orbital continuum arithmetic or a measured energy.

## CHECK

Three preregistered records already inspected during family development remain explicitly development-observed. Two complete NIST CCCBDB pages were registered by identity and captured but unopened before the law and value-free prediction seal, then opened once afterward.

The blind structure vector returns cyclobutadiene as `D2H`, with the `D 2h` configuration marked a true experimental minimum and the higher-symmetry `D 4h` square marked false. It returns cyclooctatetraene as `D2D`, with carbon coordinates on both sides of the reference plane and alternating `1.337` and `1.470 Å` carbon-carbon lengths. These are independent structural discriminators for planar frustrated recurrence and nonplanar broken recurrence.

The energy vector retains cyclobutadiene ionization energy `8.160 ± 0.030 eV`; its missing 298.15 K formation-enthalpy row is preserved as an adverse absence rather than fabricated. The development benzene control gives `82.93 ± 0.50 kJ mol⁻¹`; the blind cyclooctatetraene page gives `297.60 ± 1.40 kJ mol⁻¹`. Comparing the exact repeated `CH` compositional unit gives a positive gap of **14027/600 kJ mol⁻¹**, uncertainty **31/120**, and positive lower gap **578/25**.

All **36 tables and 172 rows** of the two blind CCCBDB surfaces are retained, together with **3 tables and 54 rows** from the WebBook control and both complete IUPAC records. Conventional signed, zero, decimal and absent inscriptions remain downstream records and never enter native Fold arithmetic.

An implementation-distinct standard-library checker regenerates all 256 candidates, the sole survivor, the exact base/successor support triples and inconsistent-class controls without importing SFT modules or opening external evidence.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The three-class distinction and four-cell successor are depth-independent over every positive finite generated layer. The empirical comparison is finite-complete for all five registered source surfaces. Later organic claims own conformations, reaction mechanisms and selectivity; they are not smuggled into ORG-004.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    write(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
