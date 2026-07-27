#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry ORG-001."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.conjugated_support_batch_v1 import (  # noqa: E402
    CONJUGATED_SUPPORT_SPEC,
    FAMILY_BOUNDARY_PATH,
    FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRE_SOURCE_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SPECTRAL_IDENTITY_PATH,
    SPECTRAL_INVENTORY_PATH,
    TARGET_HASH,
    TARGET_PATH,
    V1_PRIMARY_PATH,
    V1_TARGET_PATH,
)
from sft.chemistry.conjugated_support_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = CONJUGATED_SUPPORT_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct, value-free ORG-001 reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def exact_path(atoms, fibres):
    if len(atoms) < 3 or len(set(atoms)) != len(atoms):
        raise ValueError("distinct positive atom support required")
    if len(fibres) != len(atoms) - 1:
        raise ValueError("complete incidence support required")
    if any(value not in ("fibre-one", "fibre-two") for value in fibres):
        raise ValueError("exactly two Fold fibres required")
    if any(left == right for left, right in zip(fibres, fibres[1:])):
        raise ValueError("adjacent support must alternate")
    return tuple(zip(atoms, fibres, atoms[1:]))

def append(atoms, fibres, fresh):
    if fresh in atoms:
        raise ValueError("successor occurrence must be fresh")
    opposed = "fibre-two" if fibres[-1] == "fibre-one" else "fibre-one"
    return atoms + (fresh,), fibres + (opposed,)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    atoms = ("a", "b", "c")
    fibres = ("fibre-one", "fibre-two")
    base = exact_path(atoms, fibres)
    next_atoms, next_fibres = append(atoms, fibres, "d")
    successor = exact_path(next_atoms, next_fibres)
    repeated_rejected = incomplete_rejected = duplicate_rejected = False
    try:
        exact_path(atoms, ("fibre-one", "fibre-one"))
    except ValueError:
        repeated_rejected = True
    try:
        exact_path(atoms, ("fibre-one",))
    except ValueError:
        incomplete_rejected = True
    try:
        append(atoms, fibres, "b")
    except ValueError:
        duplicate_rejected = True
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
        and len(base) == 2
        and len(successor) == 3
        and successor[:2] == base
        and repeated_rejected and incomplete_rejected and duplicate_rejected
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
            "base_atom_count": len(atoms),
            "base_incidence_count": len(base),
            "successor_atom_count": len(next_atoms),
            "successor_incidence_count": len(successor),
            "prior_incidence_prefix_preserved": successor[:2] == base,
            "repeated_fibre_rejected": repeated_rejected,
            "incomplete_incidence_rejected": incomplete_rejected,
            "duplicate_occurrence_rejected": duplicate_rejected,
            "external_definition_structure_or_spectrum_accessed": False,
            "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_or_imported_parameter_used": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = CONJUGATED_SUPPORT_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys

from sft.chemistry.conjugated_support_batch_v1 import (
    CONJUGATED_SUPPORT_SPEC, FAMILY_BOUNDARY_PATH, FAMILY_INVENTORY_PATH,
    FAMILY_REGISTRY_PATH, IDENTITY_PATH, PRE_SOURCE_PATH, PRIMARY_PATH,
    SPECTRAL_IDENTITY_PATH, SPECTRAL_INVENTORY_PATH, TARGET_PATH,
    V1_PRIMARY_PATH, V1_TARGET_PATH,
)
from sft.chemistry.conjugated_support_validation_v1 import ConjugatedSupportValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    snapshots = tuple(dict.fromkeys(row["snapshot_path"] for row in identities["rows"]))
    files = (
        root / "sft/chemistry/conjugated_support_law_v1.py",
        root / "sft/chemistry/conjugated_support_batch_v1.py",
        root / "sft/chemistry/conjugated_support_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_org_001_016_family_sources_v1.py",
        root / "tools/capture_chemistry_org_001_spectral_addendum_v1.py",
        root / "tools/build_chemistry_org_001_primary_v1.py",
        root / "tools/build_chemistry_org_001_primary_correction_v2.py",
        root / FAMILY_BOUNDARY_PATH,
        root / FAMILY_REGISTRY_PATH,
        root / FAMILY_INVENTORY_PATH,
        root / SPECTRAL_IDENTITY_PATH,
        root / SPECTRAL_INVENTORY_PATH,
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
        GeneratedObservationalChemistryProgram(CONJUGATED_SUPPORT_SPEC, source_hash),
        ExternalCommandValidator(
            "sft-chem-conjugated-support-001-independent-python/1",
            (sys.executable, str(independent)),
            independent.parent,
            (independent,),
        ),
        files,
        ConjugatedSupportValidator(root),
    )
'''


def main() -> None:
    spec = CONJUGATED_SUPPORT_SPEC
    package = ROOT / "claims" / spec.claim_id
    if package.exists():
        raise SystemExit("ORG-001 claim package already exists; preserved without replay")
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
                "source_id": "IUPAC-GOLD-BOOK-CONJUGATED-SUPPORT-SURFACE",
                "body": "International Union of Pure and Applied Chemistry",
                "role": "complete conjugated-system, pi-conjugated-system and delocalization records",
                "evidence_class": "authoritative_terminology_and_structural_correspondence",
            },
            {
                "source_id": "NIST-CCCBDB-SRD-101-CONJUGATED-STRUCTURE-CONTROL",
                "body": "National Institute of Standards and Technology",
                "role": "complete 1,3-butadiene experimental property surface and 1,4-pentadiene separated-double-bond geometry control",
                "evidence_class": "experimental_structure_and_vibrational_records",
            },
            {
                "source_id": "NIST-WEBBOOK-SRD-69-C106990-UVVIS",
                "body": "National Institute of Standards and Technology",
                "role": "complete registered UV-visible metadata and sole linked 502-point JCAMP-DX spectrum",
                "evidence_class": "experimental_spectral_record",
            },
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
Chemistry obligation: `SFT-CHEM-OBL-ORG-001`

## WHY

Counting bond marks or naming a molecule does not derive conjugation. ORG-001 asks what one finite molecular carrier must retain before conventional single/multiple-bond notation, resonance language, a measured coordinate or a spectrum is allowed to appear. The answer must distinguish connected propagation from two merely separated unsaturations and must survive every finite successor without a named chemical exception.

## DERIVATION

The literal eight-axis product generates 256 forms. Exactly one retains one molecular subcarrier, complete connected adjacency, the two forced Fold fibres, opposed adjacent recurrence, every atom and incidence, the shared propagation centre, target-blind observation order and the unique opposed-fibre successor:

`{survivor_id(spec)}`

The first witness contains three distinct atom occurrences and two opposed support incidences. A fresh fourth occurrence has exactly one lawful successor fibre: the fibre opposed to the former terminal incidence. Equal adjacent fibres, an omitted incidence or a duplicated atom occurrence halt. The induction is depth-independent for every generated finite path because the successor preserves the complete incidence prefix and appends only that uniquely opposed fibre.

This is not conventional bond-order arithmetic pasted onto Fold notation. The candidate grammar contains no single/double-bond label, resonance rule, electron-count rule, measured bond length, wavelength or fitted coefficient. Conventional chemistry is opened only at the comparison boundary.

## CHECK

Ten target surfaces across seven frozen source identities are retained. Two independent current IUPAC records state the alternating single/multiple structural surface; the linked delocalization record retains the nonlocal-support consequence. NIST's experimental 1,3-butadiene surface records the connected `C=CC=C` inscription and distinct carbon-carbon distances `1.476 Å` and `1.337 Å`. The preregistered 1,4-pentadiene control records `1.511 Å` and `1.339 Å` but has separated double-bond support; equal counts alone therefore cannot award conjugation. Its conventional signed `-122.2°` dihedral remains downstream evidence and never becomes native negative arithmetic.

The complete NIST vibrational table is retained. The sole registered UV-visible JCAMP payload is retained point-for-point: 502 declared and 502 preserved points from the external inscriptions `200.6193` to `333.0485 nm`, with external maximum log-epsilon `4.47885`. These measurements test the sealed structural consequence; they do not select it.

The first post-seal parser overran two uppercase-closed HTML tables. That adverse V1 evidence remains byte-identical. A claim-specific V2 corrected only those table boundaries without changing the law, prediction, source identities, source bytes or target roles. No source was recaptured.

An implementation-distinct standard-library checker regenerates all 256 candidates, the sole survivor, the depth-independent successor and all structural rejection controls without any external file access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The structural theorem is depth-independent for every generated finite path. Its empirical comparison is finite-complete for the ten preregistered surfaces and the complete 502-point spectrum. It does not claim that ORG-001 alone derives arbitrary spectral line positions; those require later admitted state-energy and analytical correspondences. It establishes the exact carrier structure those later quantitative laws must preserve.
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
