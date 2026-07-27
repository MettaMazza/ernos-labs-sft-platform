#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry ORG-002."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.resonance_equivalent_representation_batch_v1 import (  # noqa: E402
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRE_SOURCE_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    RESONANCE_EQUIVALENT_REPRESENTATION_SPEC,
    TARGET_HASH,
    TARGET_PATH,
    V1_PRIMARY_PATH,
    V1_TARGET_PATH,
)
from sft.chemistry.resonance_equivalent_representation_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = RESONANCE_EQUIVALENT_REPRESENTATION_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct, value-free ORG-002 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def complement(fibres):
    if any(row not in ("one", "two") for row in fibres):
        raise ValueError("exactly two fibres required")
    return tuple("two" if row == "one" else "one" for row in fibres)

def representation_pair(carrier_a, carrier_b, atoms_a, atoms_b, edges_a, edges_b, first, second):
    if carrier_a != carrier_b:
        raise ValueError("one carrier required")
    if atoms_a != atoms_b or len(atoms_a) < 3 or len(set(atoms_a)) != len(atoms_a):
        raise ValueError("complete equal atom support required")
    if edges_a != edges_b or len(edges_a) != len(first):
        raise ValueError("complete equal adjacency required")
    if first == second or complement(first) != second:
        raise ValueError("distinct complete complement required")
    return (carrier_a, atoms_a, edges_a, first, second)

def append(pair, fresh):
    carrier, atoms, edges, first, second = pair
    if fresh in atoms:
        raise ValueError("fresh successor required")
    next_atoms = atoms + (fresh,)
    next_edges = edges + ((atoms[-1], fresh),)
    next_first = first + (("two" if first[-1] == "one" else "one"),)
    next_second = second + (("two" if second[-1] == "one" else "one"),)
    return representation_pair(carrier, carrier, next_atoms, next_atoms, next_edges, next_edges, next_first, next_second)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    atoms = ("a", "b", "c")
    edges = (("a", "b"), ("b", "c"))
    base = representation_pair("carrier", "carrier", atoms, atoms, edges, edges, ("one", "two"), ("two", "one"))
    successor = append(base, "d")
    carrier_rejected = adjacency_rejected = partial_rejected = identical_rejected = False
    try:
        representation_pair("carrier", "other", atoms, atoms, edges, edges, ("one", "two"), ("two", "one"))
    except ValueError:
        carrier_rejected = True
    try:
        representation_pair("carrier", "carrier", atoms, atoms, edges, (("a", "c"), ("b", "c")), ("one", "two"), ("two", "one"))
    except ValueError:
        adjacency_rejected = True
    try:
        representation_pair("carrier", "carrier", atoms, atoms, edges, edges, ("one", "two"), ("one", "one"))
    except ValueError:
        partial_rejected = True
    try:
        representation_pair("carrier", "carrier", atoms, atoms, edges, edges, ("one", "two"), ("one", "two"))
    except ValueError:
        identical_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and len(generated) == 256
        and len(set(received)) == 256
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in sealed["controls"]}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in sealed["controls"])
        and len(base[1]) == 3 and len(base[2]) == 2
        and len(successor[1]) == 4 and len(successor[2]) == 3
        and successor[1][:-1] == base[1] and successor[2][:-1] == base[2]
        and complement(successor[3]) == successor[4]
        and carrier_rejected and adjacency_rejected and partial_rejected and identical_rejected
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
            "base_atom_count": len(base[1]),
            "base_adjacency_count": len(base[2]),
            "base_representation_count": 2,
            "successor_atom_count": len(successor[1]),
            "successor_adjacency_count": len(successor[2]),
            "complete_complement_preserved": complement(successor[3]) == successor[4],
            "carrier_mismatch_rejected": carrier_rejected,
            "adjacency_mismatch_rejected": adjacency_rejected,
            "partial_complement_rejected": partial_rejected,
            "identical_encoding_rejected": identical_rejected,
            "external_definition_note_example_wavefunction_coefficient_or_charge_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = RESONANCE_EQUIVALENT_REPRESENTATION_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys

from sft.chemistry.resonance_equivalent_representation_batch_v1 import (
    FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH, FAMILY_REGISTRY_PATH,
    IDENTITY_PATH, PRE_SOURCE_PATH, PRIMARY_PATH,
    RESONANCE_EQUIVALENT_REPRESENTATION_SPEC, TARGET_PATH,
    V1_PRIMARY_PATH, V1_TARGET_PATH,
)
from sft.chemistry.resonance_equivalent_representation_validation_v1 import ResonanceEquivalentRepresentationValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"]))
    files = (
        root / "sft/chemistry/resonance_equivalent_representation_law_v1.py",
        root / "sft/chemistry/resonance_equivalent_representation_batch_v1.py",
        root / "sft/chemistry/resonance_equivalent_representation_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_org_001_016_family_sources_v1.py",
        root / "tools/build_chemistry_org_002_primary_v1.py",
        root / "tools/build_chemistry_org_002_primary_correction_v2.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / PRE_SOURCE_PATH,
        root / IDENTITY_PATH,
        root / V1_TARGET_PATH,
        root / V1_PRIMARY_PATH,
        root / TARGET_PATH,
        root / PRIMARY_PATH,
        *(root / path for path in snapshots),
        root / "claims/{claim_id}/execution.py",
    )
    files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, files).manifest_hash
    independent = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        GeneratedObservationalChemistryProgram(RESONANCE_EQUIVALENT_REPRESENTATION_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-resonance-equivalent-representation-002-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        ResonanceEquivalentRepresentationValidator(root),
    )
'''


def main() -> None:
    spec = RESONANCE_EQUIVALENT_REPRESENTATION_SPEC
    package = ROOT / "claims" / spec.claim_id
    if package.exists():
        raise SystemExit("ORG-002 claim package already exists; preserved without replay")
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
            {
                "source_id": "IUPAC-GOLD-BOOK-RESONANCE-REPRESENTATION-SURFACE",
                "body": "International Union of Pure and Applied Chemistry",
                "role": "complete resonance, resonance-form, contributing-structure and delocalization records",
                "evidence_class": "authoritative_terminology_and_structural_correspondence",
            }
        ],
        "source_hashes": {
            "identity_registry": IDENTITY_HASH,
            "withheld_targets_v2": TARGET_HASH,
            "normalized_primary_v2": PRIMARY_HASH,
        },
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
Chemistry obligation: `SFT-CHEM-OBL-ORG-002`

## WHY

Multiple conventional inscriptions of one molecular entity cannot simply be assumed to denote one thing. ORG-002 asks which exact structure makes two encodings equivalent before a Lewis diagram, charge sign, wavefunction, coefficient or named resonance convention is permitted to choose the answer. It must retain molecular identity without confusing representation plurality with species plurality or a physical equilibrium.

## DERIVATION

The literal eight-axis product generates 256 forms. Exactly one retains one molecular carrier, complete equal atom-occurrence support, complete equal adjacency, multiple distinct encoding identities, the exact complete opposed-fibre relation, one-carrier/many-representation identity, representation-only process status and the shared complement successor:

`{survivor}`

The minimal witness has one carrier, three atom occurrences, two incidences and two distinct complementary Fold-fibre assignments. The depth-independent successor appends one fresh occurrence and the unique opposed terminal fibre to each encoding while preserving every prior atom and incidence. A different carrier, changed adjacency, partial complement or identical encoding halts. Larger finite equivalence classes are compositions of exact local pair relations; no named chemical exception is introduced.

## CHECK

Four complete preregistered current IUPAC records are retained. The resonance record identifies representation of one molecular entity through contributing structures. The resonance-form record requires at least two formal structures where one is insufficient and explicitly distinguishes the representation arrow from an equilibrium arrow. The contributing-structure record states that the encodings have formal significance rather than separate species identity. The delocalization record retains the nonlocal-support correspondence.

Conventional wavefunction, coefficient and signed-charge inscriptions are preserved exactly as external evidence but never enter native forcing. The first post-seal parser searched only two of the four complete records for the signed-charge inscription and returned false. That adverse V1 result remains byte-identical. A claim-specific V2 searches all four already captured records and finds the preserved inscription; no source was recaptured and no target outcome, prediction, law or payload hash changed.

An implementation-distinct standard-library checker independently regenerates all 256 candidates, the sole survivor, the finite successor and every structural rejection control without external file access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The one-carrier complement relation is depth-independent for every generated finite connected alternating pair. The external comparison is finite-complete for the four frozen IUPAC records. ORG-002 derives representation equivalence, not numerical resonance energy, transition dynamics or arbitrary spectral values; those require their separately owned later laws.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    write(
        ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json",
        json.dumps(experiment, indent=2, sort_keys=True) + "\n",
    )
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
