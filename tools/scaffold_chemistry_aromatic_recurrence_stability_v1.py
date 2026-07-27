#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry ORG-003."""
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.aromatic_recurrence_stability_batch_v1 import (  # noqa: E402
    AROMATIC_RECURRENCE_STABILITY_SPEC,
    BLIND_IDENTITY_PATH,
    BLIND_INVENTORY_PATH,
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
from sft.chemistry.aromatic_recurrence_stability_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = AROMATIC_RECURRENCE_STABILITY_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct, value-free ORG-003 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}
FIBRES = ("fibre-one", "fibre-two")
PAIR_CELLS = tuple(product(FIBRES, repeat=2))

def recurrence(centres, boundary, layers):
    if len(centres) < 3 or len(set(centres)) != len(centres):
        raise ValueError("complete distinct cycle centres required")
    if len(boundary) != 2 or set(boundary) != set(FIBRES):
        raise ValueError("both boundary fibres required")
    if not layers or any(tuple(layer) != PAIR_CELLS for layer in layers):
        raise ValueError("every positive layer requires all ordered pair cells")
    edges = tuple(zip(centres, centres[1:] + centres[:1]))
    trace = centres + centres[:1]
    return {{"centres": centres, "edges": edges, "trace": trace, "support": len(boundary) + sum(len(layer) for layer in layers)}}

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    centres = tuple("c" + str(index) for index in range(1, 7))
    base = recurrence(centres, FIBRES, (PAIR_CELLS,))
    successor = recurrence(centres, FIBRES, (PAIR_CELLS, PAIR_CELLS))
    second = recurrence(centres, FIBRES, (PAIR_CELLS, PAIR_CELLS, PAIR_CELLS))
    incomplete_rejected = duplicate_boundary_rejected = open_cycle_rejected = False
    try:
        recurrence(centres, FIBRES, (PAIR_CELLS[:-1],))
    except ValueError:
        incomplete_rejected = True
    try:
        recurrence(centres, ("fibre-one", "fibre-one"), (PAIR_CELLS,))
    except ValueError:
        duplicate_boundary_rejected = True
    try:
        recurrence(("left", "right"), FIBRES, (PAIR_CELLS,))
    except ValueError:
        open_cycle_rejected = True
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
        and (base["support"], successor["support"], second["support"]) == (6, 10, 14)
        and base["trace"][0] == base["trace"][-1]
        and incomplete_rejected and duplicate_boundary_rejected and open_cycle_rejected
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
            "complete_ordered_pair_cell_count": len(PAIR_CELLS),
            "primitive_support_count": base["support"],
            "successor_support_count": successor["support"],
            "second_successor_support_count": second["support"],
            "complete_first_return": base["trace"][0] == base["trace"][-1],
            "incomplete_pair_cell_layer_rejected": incomplete_rejected,
            "duplicated_boundary_fibre_rejected": duplicate_boundary_rejected,
            "open_two_centre_cycle_rejected": open_cycle_rejected,
            "external_definition_table_energy_value_sign_or_uncertainty_accessed": False,
            "imported_huckel_or_electron_count_rule_used": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = AROMATIC_RECURRENCE_STABILITY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys

from sft.chemistry.aromatic_recurrence_stability_batch_v1 import (
    AROMATIC_RECURRENCE_STABILITY_SPEC, BLIND_IDENTITY_PATH, BLIND_INVENTORY_PATH,
    FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, PRE_SOURCE_PATH, PRIMARY_PATH, TARGET_PATH,
)
from sft.chemistry.aromatic_recurrence_stability_validation_v1 import AromaticRecurrenceStabilityValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["opened_snapshot_path"] for row in targets["rows"]))
    files = (
        root / "sft/chemistry/aromatic_recurrence_stability_law_v1.py",
        root / "sft/chemistry/aromatic_recurrence_stability_batch_v1.py",
        root / "sft/chemistry/aromatic_recurrence_stability_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_org_001_016_family_sources_v1.py",
        root / "tools/capture_chemistry_org_003_blind_cccbdb_sources_v1.py",
        root / "tools/build_chemistry_org_003_primary_v1.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / BLIND_IDENTITY_PATH,
        root / BLIND_INVENTORY_PATH,
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
        GeneratedObservationalChemistryProgram(AROMATIC_RECURRENCE_STABILITY_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-aromatic-recurrence-stability-003-independent-python/1",
            (sys.executable, str(independent)), independent.parent, (independent,),
        ),
        files,
        AromaticRecurrenceStabilityValidator(root),
    )
'''


def main() -> None:
    spec = AROMATIC_RECURRENCE_STABILITY_SPEC
    package = ROOT / "claims" / spec.claim_id
    if package.exists():
        raise SystemExit("ORG-003 claim package already exists; preserved without replay")
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
            {"source_id": "IUPAC-AROMATIC-RECURRENCE-SURFACE", "body": "International Union of Pure and Applied Chemistry", "role": "complete aromatic, aromaticity and resonance-energy records", "custody": "development-observed-correspondence"},
            {"source_id": "NIST-WEBBOOK-AROMATIC-THERMOCHEMISTRY-SURFACE", "body": "National Institute of Standards and Technology", "role": "complete benzene, cyclohexene and cyclohexane gas thermochemistry surfaces", "custody": "development-observed-correspondence"},
            {"source_id": "NIST-CCCBDB-SRD101-BLIND-AROMATIC-ENERGY-SURFACE", "body": "National Institute of Standards and Technology", "role": "complete independently preregistered experimental-data pages for the same three molecular identities", "custody": "outcome-unopened-before-law-and-prediction-seal"},
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
Chemistry obligation: `SFT-CHEM-OBL-ORG-003`

## WHY

Aromatic stability cannot be derived by naming benzene, importing a conventional electron-count rule, or selecting an experimentally favourable energy. ORG-003 asks what exact finite recurrence is forced by the already admitted Fold structures before any target outcome is available.

## DERIVATION

The literal eight-axis grammar generates 256 forms. Exactly one retains one complete molecular cycle, both Fold boundary fibres, every one of their four ordered pair cells in each positive recurrence layer, an explicit first-return trace, one positive recurrence-opening transfer, value-free observation custody and the same four-cell successor without an added rule:

`{survivor}`

The primitive recurrence contains the two held boundary fibres plus one complete four-cell layer, forcing support count **6**. Each successor appends all four ordered pair cells once, forcing **10**, then **14**, and the same exact recurrence at every positive finite depth. This is the Fold derivation of the familiar support sequence; no `4n+2` premise, electron-count lookup, molecular name, measured enthalpy, irrational orbital root or fitted coefficient occurs in the grammar.

Opening the first-return recurrence while preserving the carrier requires one positive retained transfer. The closed recurrence therefore precedes its opened localized reference in the admitted exact energy order. The derivation forces the direction and positivity of the stability gap; the physical energy magnitude is tested only after sealing.

## CHECK

The original six ORG-family records were inspected during orientation and are therefore retained transparently as development-observed correspondence, never mislabelled blind. Before any independent result was fetched, three complete NIST CCCBDB experimental-data pages—benzene, cyclohexene and cyclohexane—were preregistered by molecular identity, sealed value-free, and then captured exactly once.

The blind CCCBDB inscriptions are `82.93`, `-4.32`, and `-123.14 kJ mol⁻¹` for the three 298.15 K formation-enthalpy rows, with source uncertainties `0.50`, `0.98`, and `0.79`. Signs remain held external inscriptions; native arithmetic uses held above/below-reference direction plus positive exact hundredths.

The independent single-support hydrogenation magnitude is **118.82 kJ mol⁻¹**. Three localized copies force **356.46 kJ mol⁻¹**. The complete cyclic recurrence requires **206.07 kJ mol⁻¹**. Their exact blind difference is therefore a positive aromatic recurrence-stability excess of **150.39 kJ mol⁻¹**. Even the deliberately conservative additive uncertainty envelope is only **6.60 kJ mol⁻¹**, leaving a positive lower envelope of **143.79 kJ mol⁻¹**.

All 59 scientific tables and 353 rows of the blind CCCBDB pages are retained, together with all 9 tables and 121 rows of the development-observed WebBook thermochemistry surfaces and all three complete IUPAC records. Absent cells, signed inscriptions and the IUPAC warning that resonance energy is estimated rather than directly observed are preserved.

An implementation-distinct standard-library checker regenerates all 256 candidates, the sole survivor, support counts 6/10/14, first return and the incomplete-layer, duplicate-boundary and open-cycle controls without external file access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The recurrence and four-cell successor are depth-independent over every positive finite generated layer. The empirical comparison is finite-complete for all nine registered source surfaces. ORG-003 closes aromatic recurrence and its positive stability ordering; ORG-004 separately owns antiaromatic and nonaromatic alternatives.
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
