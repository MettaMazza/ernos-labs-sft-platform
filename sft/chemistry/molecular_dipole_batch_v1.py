"""Registered finite quantitative specification for Chemistry PROP-005."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_dipole_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine import ClosureEvidence, ClosureScope
from sft.engine.canonical import sha256_identity
from sft.engine.model import CandidateDecision
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/molecular_dipole_target_identities_v1.json"
IDENTITY_HASH = "sha256:fbeffee44a4f3231814728c4b2046811a9c90160f889077c1190ea9e0a31f023"
TARGET_PATH = "experiments/external_sources/chemistry/molecular_dipole_withheld_targets_v1.json"
TARGET_HASH = "sha256:c3de218ecc55ed614835ebed25ece8ea3e2d9c2155e12c03c5e91889b6c17e73"

for _path, _hash in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-005 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-molecular-dipole-identities/1"
    or _identity_document.get("all_measurement_values_absent") is not True
    or _identity_document.get("registered_species_order") != ["H2", "D2", "H2O", "D2O", "HDO"]
    or len(_identity_document.get("rows", ())) != 9
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-005 target identity registry is incomplete or contains a value")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identity_document["rows"]
)


class GeneratedFiniteMolecularDipoleChemistryProgram(GeneratedObservationalChemistryProgram):
    """Retain the explicitly finite five-species, nine-measurement boundary."""

    def closure_evidence(self, decisions: Sequence[CandidateDecision]) -> ClosureEvidence:
        record = {
            "claim_id": self.spec.claim_id,
            "result": self.spec.exact_result,
            "boundary": self.spec.grammar_boundary,
            "base": self.spec.induction_base,
            "successor": self.spec.induction_step,
            "exclusions": self.spec.exclusions,
            "witnesses": self.spec.operational_witnesses,
            "survivor": survivor_id(self.spec),
        }
        return ClosureEvidence(
            ClosureScope.FINITE_COMPLETE,
            self.spec.grammar_boundary,
            True,
            True,
            sha256_identity((record, tuple(decisions))),
            None,
        )


MOLECULAR_DIPOLE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005",
    title="Exact molecular dipole organization and squared-magnitude relation",
    statement=(
        "A molecular dipole is the retained orientation of a complete molecular charge-distinction carrier. "
        "Its molecular symmetry closes forbidden components to structural EmptyOne and retains every allowed "
        "component as an exact positive magnitude on a held axis. The orientation-free squared magnitude is "
        "exactly the Junction of those component squares. The relation seals before all nine NIST values open; "
        "the H2/D2 absence rows, water-isotopologue component organization and reported total magnitudes then "
        "test the same law without a signed proof scalar or an irrational square root."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, symmetry, orientation, composition, magnitude, prediction, "
        "record-completeness and extension forms; decide all 256 forms using only admitted charge, geometry, "
        "symmetry, exact arithmetic and measurement-custody laws."
    ),
    grammar_boundary=(
        "The complete registered H2, D2, H2O, D2O and HDO gas-phase vector: two homonuclear total-absence "
        "records and seven water-isotopologue component/total magnitude records, retaining species, molecular "
        "state, geometry, charge-distinction carrier, symmetry, axis, magnitude definition, method, condition, "
        "source and uncertainty; every numerical inscription is withheld until after relation sealing."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "For the first inversion-symmetric homonuclear carrier, every oriented charge-displacement has an "
        "indistinguishable opposed partner, so no axis survives and the magnitude record is structural EmptyOne."
    ),
    induction_step=(
        "Replacing equal endpoints preserves the closed class; introducing a retained unequal charge carrier "
        "leaves the symmetry-allowed axes, and appending each distinct allowed axis adds exactly its positive "
        "square to the magnitude Junction without changing any prior component."
    ),
    exclusions=(
        "no numerical zero, negative, irrational, imaginary, floating, signed or continuum proof value",
        "no conventional vector-space premise, square-root magnitude or signed Cartesian direction in proof",
        "no imported charge model, Stark Hamiltonian, wavefunction, fitted partial charge or molecular coefficient",
        "no measured component, total, uncertainty or source inscription in the law, grammar or prediction",
        "no erased species, state, geometry, charge carrier, symmetry, axis, method or condition",
        "no omitted homonuclear absence row or water-isotopologue component/total row",
        "no claim beyond the registered five-species, nine-row gas-phase boundary",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-DIPOLE-MAGNITUDE-005",
    expected_observation_label="exact-symmetry-component-and-squared-magnitude-relation-across-nine-NIST-rows",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if either registered homonuclear total is not source absence; if H2O or D2O does not "
        "retain exactly one reported component, HDO does not retain exactly two, or any post-seal exact outward "
        "component-square Junction fails to overlap its separately reported squared-total interval; if any row, "
        "identity, state, geometry, symmetry, axis, method, condition or uncertainty is erased; if a value is "
        "readable before sealing; or if a signed, irrational, fitted or continuum rule is introduced."
    ),
)
MOLECULAR_DIPOLE_SPEC.validate()


__all__ = (
    "GeneratedFiniteMolecularDipoleChemistryProgram", "IDENTITY_HASH", "IDENTITY_PATH",
    "MOLECULAR_DIPOLE_SPEC", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
