"""Registered finite quantitative specification for Chemistry PROP-002."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from sft.chemistry.bond_dissociation_energy_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ClosureEvidence, ClosureScope
from sft.engine.canonical import sha256_identity
from sft.engine.model import CandidateDecision
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/bond_dissociation_energy_target_identities_v1.json"
IDENTITY_HASH = "sha256:d1ed3e22aac37011c4e957cbc8f022cf3098ca96b1a8c30ee954196c8a6b8f74"
TARGET_PATH = "experiments/external_sources/chemistry/bond_dissociation_energy_withheld_targets_v1.json"
TARGET_HASH = "sha256:03eb76d1aeb6dc4a2066236e24f03d5529e9b247a62294db03837077de87cb9c"

for _path, _hash in (
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-002 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-bond-dissociation-energy-identities/1"
    or len(_identity_document.get("rows", ())) != 8
    or _identity_document.get("all_measurement_values_absent") is not True
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-002 target identity registry is incomplete or contains a value")

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


class GeneratedFiniteDissociationChemistryProgram(GeneratedObservationalChemistryProgram):
    """Retain the explicitly finite H2/D2, historical/current target boundary."""

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


BOND_DISSOCIATION_ENERGY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-BOND-DISSOCIATION-ENERGY-002",
    title="Exact H2/D2 ground-state bond-dissociation path relation",
    statement=(
        "For each registered H2 or D2 channel, the B-prime threshold terminates in one ground-state "
        "atom and one 2s atom, while X-state ground dissociation terminates in two ground-state atoms. Their "
        "shared ground-atom prefix cancels structurally, so D0(M2) is exactly the B-prime threshold after the "
        "held atomic 1S-2S separation is Taken. This relation is sealed without measured values; only afterward "
        "does the complete threshold, atomic and historical/later ground-dissociation vector test it exactly."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of identity, channel, path, operation, public-input, target-custody, "
        "record-completeness and extension forms; decide all 256 using only admitted transition/conservation "
        "laws and the registered source identities."
    ),
    grammar_boundary=(
        "The complete eight-row H2/D2 path vector: two B-prime thresholds, two atomic 1S-2S segments, two "
        "APS-1994 ground-state rows, and the later high-resolution H2-2009 and D2-2022 rows, with species, "
        "state, product channel, condition and uncertainty held and every number withheld until after sealing."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "For one named isotopologue, the excited threshold and ground dissociation paths share one M(1s) "
        "product; exact conservation forces the longer path to Take the sole M(1s)-to-M(2s) segment."
    ),
    induction_step=(
        "Replacing both retained nuclei by the admitted heavier isotope preserves the path topology while "
        "replacing both measured input intervals; the same Take closes D2 and exhausts the two-row boundary."
    ),
    exclusions=(
        "no numerical zero, negative, irrational, imaginary, floating, signed or continuum proof value",
        "no conventional molecular potential, wavefunction, ab-initio energy or fitted bond coefficient",
        "no threshold, atomic-transition or dissociation value in the executable law or prediction",
        "no target-derived atomic transition, selected residual correction or species exception",
        "no erased X state, rotational state, B-prime channel, atomic product state or measurement condition",
        "no omission of a historical or current registered target row",
        "no claim beyond the registered H2/D2 homolytic ground-state boundary",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-BOND-DISSOCIATION-ENERGY-002",
    expected_observation_label="exact-H2-D2-state-path-Take-relation-across-complete-measurement-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if either post-seal threshold Take atomic interval does not overlap every registered "
        "historical and later ground-dissociation interval for its isotopologue; if any of eight measurement "
        "rows, a state, product channel, condition, source or uncertainty is erased; if any measured number is "
        "readable before the relation seal; if a deliberately displaced interval is accepted; or if a fitted "
        "coefficient or correction is introduced."
    ),
)
BOND_DISSOCIATION_ENERGY_SPEC.validate()


__all__ = (
    "BOND_DISSOCIATION_ENERGY_SPEC",
    "GeneratedFiniteDissociationChemistryProgram",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
