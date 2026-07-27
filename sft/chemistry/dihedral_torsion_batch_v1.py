"""Registered finite quantitative specification for Chemistry PROP-004."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from sft.chemistry.dihedral_torsion_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ClosureEvidence, ClosureScope
from sft.engine.canonical import sha256_identity
from sft.engine.model import CandidateDecision
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/dihedral_torsion_target_identities_v1.json"
IDENTITY_HASH = "sha256:64ce9b81aa4a979092d9af0dcce852dc72d5b0d52ad3392c0112678268154182"
TARGET_PATH = "experiments/external_sources/chemistry/dihedral_torsion_withheld_targets_v1.json"
TARGET_HASH = "sha256:89218d8bd40d6cc4a822cb3bb0745d8f6f7a7fe78b219022b735ef5bb513ea1e"

for _path, _hash in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-004 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-dihedral-torsion-identities/1"
    or len(_identity_document.get("rows", ())) != 50
    or _identity_document.get("all_angle_and_energy_values_absent") is not True
    or _identity_document.get("complete_registered_two_path_surface") is not True
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-004 identity registry is incomplete or contains a value")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]), source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]), snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identity_document["rows"]
)


class GeneratedFiniteDihedralTorsionChemistryProgram(GeneratedObservationalChemistryProgram):
    """Retain the finite two-rotor, fifty-row registered observation boundary."""

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        record = {
            "claim_id": self.spec.claim_id, "result": self.spec.exact_result,
            "boundary": self.spec.grammar_boundary, "base": self.spec.induction_base,
            "successor": self.spec.induction_step, "exclusions": self.spec.exclusions,
            "witnesses": self.spec.operational_witnesses, "survivor": survivor_id(self.spec),
        }
        return ClosureEvidence(
            ClosureScope.FINITE_COMPLETE, self.spec.grammar_boundary, True, True,
            sha256_identity((record, tuple(decisions))), None,
        )


DIHEDRAL_TORSION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-DIHEDRAL-TORSIONAL-STATE-004",
    title="Exact held-orientation dihedral and torsional-state relation",
    statement=(
        "A molecular dihedral is an ordered four-site periodic carrier with held orientation, not a signed "
        "continuum scalar. At the registered 24-sector resolution, structural EmptyOne, each positive sector "
        "successor and recurrent One exactly generate the coordinate cycle. Complete cyclic neighbour order "
        "forces conformer minima and barriers; each barrier magnitude is the ordered positive Take to its "
        "adjacent conformer. The coordinate and operation seal before all fifty NIST angle and energy rows open."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of ordered carrier, held orientation, sector coordinate, conformer state, "
        "barrier Take, recurrence, value-free prediction and record-completeness forms; decide all 256 from "
        "admitted exact structure and the value-free fifty-row identity surface."
    ),
    grammar_boundary=(
        "The complete two-path NIST CCCBDB gauche-ethanol internal-rotation surface at its registered 24-sector "
        "observation resolution: OH torsion atoms 1-2-3-4 and CH3 torsion atoms 3-2-1-5, each with 24 unique "
        "sector states plus one recurrent endpoint, retaining molecule, state, rotor type, orientation, conformer "
        "and barrier roles, source method/condition and both energy-unit inscriptions."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One ordered four-site carrier at structural EmptyOne retains its molecule, state, rotor and orientation; "
        "one positive successor creates the first exact sector part without a signed or continuum coordinate."
    ),
    induction_step=(
        "Appending one generated sector successor preserves the ordered carrier and exposes exactly one new path "
        "node; complete neighbours force its state role, and the twenty-fourth successor is the recurrent One "
        "identical to the anchor class."
    ),
    exclusions=(
        "no numerical zero; source glyph 0 denotes structural absence only",
        "no negative, irrational, imaginary, floating, signed or continuum proof magnitude",
        "no imported torsional potential, Fourier series, differential equation, saddle equation or fitted coefficient",
        "no measured angle, energy, conformer outcome or barrier magnitude in law, forcing or prediction",
        "no erased molecule, state, ordered atom, rotor type, orientation, path position, method or condition",
        "no selected extrema-only, one-rotor or one-energy-unit subset",
        "no claim beyond the registered ethanol two-rotor observation boundary",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-DIHEDRAL-TORSIONAL-STATE-004",
    expected_observation_label="exact-held-dihedral-cycle-conformer-and-positive-barrier-Take",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any of fifty post-seal source angles differs from its generated EmptyOne/sector-part/"
        "recurrent-One coordinate; if a conformer or barrier fails complete cyclic neighbour order; if any "
        "barrier Take is non-positive or loses an adjacent minimum; if either ordered four-atom carrier, rotor, "
        "orientation, source condition, ordinary row, least-state row or energy-unit inscription is erased; if "
        "any source value is readable before sealing; or if a signed, continuum, fitted or selected-row form is admitted."
    ),
)
DIHEDRAL_TORSION_SPEC.validate()


__all__ = (
    "DIHEDRAL_TORSION_SPEC", "GeneratedFiniteDihedralTorsionChemistryProgram",
    "IDENTITY_HASH", "IDENTITY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
