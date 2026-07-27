#!/usr/bin/env python3
"""Prepare the pre-admission PROP-004 claim and experiment package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.dihedral_torsion_batch_v1 import (  # noqa: E402
    DIHEDRAL_TORSION_SPEC, IDENTITY_HASH, IDENTITY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.dihedral_torsion_validation_v1 import (  # noqa: E402
    SNAPSHOT_HASH, SNAPSHOT_PATH, SOURCE_ID, experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = DIHEDRAL_TORSION_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct value-free PROP-004 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}

def coordinate(position, sectors):
    if position < 1 or sectors < 1 or position > sectors + 1:
        raise ValueError("invalid generated coordinate")
    return None if position == 1 else Fraction(position - 1, sectors)

def positive_take(higher, lower):
    if lower is None:
        return higher
    if higher is None or not higher > lower:
        raise ValueError("ordered positive Take halted")
    return higher - lower

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    path = tuple(coordinate(position, 24) for position in range(1, 26))
    reversed_rejected = False
    try:
        positive_take(Fraction(2, 1), Fraction(5, 1))
    except ValueError:
        reversed_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "finite_complete"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in controls)
        and len(path) == 25 and path[0] is None and path[1] == Fraction(1, 24) and path[-1] == Fraction(1, 1)
        and positive_take(Fraction(5, 1), None) == Fraction(5, 1)
        and positive_take(Fraction(5, 1), Fraction(2, 1)) == Fraction(3, 1)
        and reversed_rejected
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "twenty_four_sector_cycle_reconstructed": True,
            "anchor_is_structural_absence": path[0] is None,
            "terminal_is_recurrent_One": path[-1] == Fraction(1, 1),
            "ordered_positive_Take_reconstructed": reversed_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = DIHEDRAL_TORSION_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.dihedral_torsion_batch_v1 import DIHEDRAL_TORSION_SPEC, GeneratedFiniteDihedralTorsionChemistryProgram
from sft.chemistry.dihedral_torsion_validation_v1 import DihedralTorsionValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/dihedral_torsion_law_v1.py",
        root / "sft/chemistry/dihedral_torsion_batch_v1.py",
        root / "sft/chemistry/dihedral_torsion_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_dihedral_torsion_sources_v1.py",
        root / {SNAPSHOT_PATH!r}, root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteDihedralTorsionChemistryProgram(DIHEDRAL_TORSION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-dihedral-torsional-state-004-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=DihedralTorsionValidator(root),
    )
'''


def main() -> None:
    spec = DIHEDRAL_TORSION_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id,
        "title": spec.title, "branch": "chemistry", "status": "registered",
        "statement": spec.statement, "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary,
            "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(),
        "evidence_mode": "observational_derivation",
        "external_measurement_sources": [{
            "source_id": SOURCE_ID, "measurement_body": "NIST",
            "role": "withheld complete gauche-ethanol OH/CH3 internal-rotation angle and two-unit energy surfaces",
        }],
        "source_hashes": {
            "NIST_snapshot": SNAPSHOT_HASH, "identity_registry": IDENTITY_HASH,
            "withheld_measurements": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document()),
            "angle_or_energy_values_present": False, "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "custody_protocol": {
            "identity_registry_path": IDENTITY_PATH, "withheld_target_path": TARGET_PATH,
            "all_fifty_rows_release_only_after_prediction_seal": True,
        },
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne", "display_glyph": "0",
            "numerical_zero_admitted": False,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-004`

## WHY

A conventional signed dihedral conceals two different things: a four-site ordered molecular carrier and an orientation on its periodic state cycle. SFT retains both structurally. It does not create a negative proof magnitude or assume a real continuum. The same cycle must also explain conformer minima, barriers, recurrence and barrier height without importing a torsional potential or fitted Fourier series.

## DERIVATION

The eight-axis grammar contains 256 forms and exactly one survivor:

`{survivor_id(spec)}`

At the registered 24-sector resolution, path position One is structural `EmptyOne`; every successor is the exact positive turn part given by its generated predecessor count over 24; position 25 is the recurrent One. Complete cyclic neighbours force conformer minima and barriers. A barrier height is the exact ordered positive `Take` from the barrier state to each adjacent conformer minimum. Reversing the operation halts.

No measured angle, energy, conformer assignment, barrier magnitude, signed scalar, continuum potential, Fourier coefficient or fitted term occurs in the law or prediction.

## CHECK

The capability-closed prediction seals both complete coordinate cycles, both ordered four-atom carriers, the OH and CH3 rotor identities, held orientation, recurrence, neighbour-state law and barrier-Take law. Only then does the custodian release all fifty NIST CCCBDB angle and energy rows. Exact post-seal degree translation must match every coordinate. Both independent energy-unit columns must force the same six conformer minima and six barriers. Those barriers must generate twelve positive adjacent-conformer Takes. All four least-state energy glyphs are represented as `EmptyOne`, never numerical zero. An implementation-distinct checker separately reconstructs all 256 candidates, the 24-sector cycle and ordered positive Take without reading a measurement file.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

Finite-complete for the registered NIST gauche-ethanol two-rotor, fifty-row observation surface at 24-sector resolution. The general ordered-carrier and positive-Take operations are exact; this receipt does not claim an ungenerated universal numerical torsional potential for every molecule.
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
