"""Registered finite quantitative specification for Chemistry PROP-003."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from sft.chemistry.bond_angle_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ClosureEvidence, ClosureScope
from sft.engine.canonical import sha256_identity
from sft.engine.model import CandidateDecision
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import survivor_id


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/bond_angle_target_identities_v1.json"
IDENTITY_HASH = "sha256:3d3c67505120a588c014f1417f518edda10295cfd9eb55a84530e50fd2f2cbcc"
TARGET_PATH = "experiments/external_sources/chemistry/bond_angle_withheld_targets_v1.json"
TARGET_HASH = "sha256:f6f614ad7ee9f7d992a80cf61b9b49443b7f1fe8d14cd186a33566f759f06b7e"

for _path, _hash in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-003 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-molecular-bond-angle-identities/1"
    or len(_identity_document.get("rows", ())) != 4
    or _identity_document.get("all_measurement_values_absent") is not True
    or _identity_document.get("complete_registered_carrier_vector") is not True
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-003 target identity registry is incomplete or contains a value")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]), source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]), snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identity_document["rows"]
)


class GeneratedFiniteBondAngleChemistryProgram(GeneratedObservationalChemistryProgram):
    """Retain the explicitly finite registered molecular-angle carrier boundary."""

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


BOND_ANGLE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-BOND-ANGLE-003",
    title="Exact symmetry-forced molecular bond-angle relation",
    statement=(
        "A closed molecular turn divided into n symmetry-indistinguishable positive ligand sectors has no "
        "lawful unequal-sector form: unequal parts would introduce an ungenerated distinction. Each sector is "
        "therefore exactly 1/n turn and a retained k-sector separation is exactly k/n turn. The structural "
        "fractions seal without degrees; only afterward are all four NIST CCCBDB BF3, XeF2 and XeF4 angle rows opened."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, cyclic order, sector partition, angle relation, prediction "
        "custody, measurement custody, record completeness and extension forms; decide all 256 using only "
        "admitted exact structure and the value-free registered target identities."
    ),
    grammar_boundary=(
        "The complete registered symmetry-forced molecular-angle vector at the official source display "
        "resolution: BF3 trigonal-planar adjacent aFBF, XeF2 linear opposite aFXeF, and XeF4 square-planar "
        "adjacent and opposite aFXeF, retaining species, neutral state, geometry, angle role, coordinate, "
        "method/condition, source identity and source comment."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "Two indistinguishable opposed sectors exhaust one closed turn; neither can differ without a retained "
        "distinction, so the separation is one of two equal parts."
    ),
    induction_step=(
        "Adding one indistinguishable sector to an n-sector closed cycle preserves equality and exhaustive "
        "Junction; every retained k-sector path remains the exact part k/n without a new parameter."
    ),
    exclusions=(
        "no numerical zero, negative, irrational, imaginary, floating, signed or continuum proof value",
        "no continuum trigonometry, Cartesian coordinate fit, wavefunction, hybridization model or imported angle equation",
        "no measured degree value or degree-scale conversion in the law, candidate forcing or prediction",
        "no unequal sector, fitted angular correction, species coefficient or exception",
        "no erased species, state, point group, geometry, coordinate, angle role, method, condition or source comment",
        "no omission of either XeF4 row or selection of only one favorable molecule",
        "no claim for tetrahedral or other ungenerated non-cyclic-equal-sector geometry in this receipt",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-BOND-ANGLE-003",
    expected_observation_label="exact-equal-sector-turn-fraction-across-complete-four-angle-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any sealed turn fraction translated after release does not equal its source-bound "
        "degree inscription at the registered observation resolution; if any of the four rows or its species, "
        "state, geometry, angle definition, method/condition or comment is erased; if a degree value is readable "
        "before prediction sealing; if a displaced, swapped, wrong-count or unsupported-geometry control is "
        "accepted; or if a fitted correction or continuum construction is introduced."
    ),
)
BOND_ANGLE_SPEC.validate()


__all__ = (
    "BOND_ANGLE_SPEC", "GeneratedFiniteBondAngleChemistryProgram", "IDENTITY_HASH", "IDENTITY_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
