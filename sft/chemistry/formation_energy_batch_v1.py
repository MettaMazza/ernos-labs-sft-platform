"""Registered exact formation-energy relation and blind NIST vector for PROP-013."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.formation_energy_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/prop-013-formation-energy-v1"
LIST_PATH = f"{SNAPSHOT_ROOT}/nist-cccbdb-complete-species-list.html"
LIST_HASH = "sha256:0a4abb0b781609d10db9d90efcfe5f296943a995ea2eb2bb044b9018066aabe1"
CHOICE_PATH = f"{SNAPSHOT_ROOT}/nist-cccbdb-complete-formation-choice-surface.html"
CHOICE_HASH = "sha256:daa2f5695b41f355e2584892905316132c87ec9d13d88b50ab3b61c2a212e2c5"
RESULT_PATH = f"{SNAPSHOT_ROOT}/nist-cccbdb-complete-formation-energy-surface.html"
RESULT_HASH = "sha256:75b9c835af247fac0c542f12d1863e0f0b8d3b8a1c1a744eb1df66c3ad7653b2"
REFERENCE_PATH = f"{SNAPSHOT_ROOT}/nist-cccbdb-thermodynamic-reference-states.html"
REFERENCE_HASH = "sha256:0f39e74274fe3c8b23939df1a6f7ff09d2970a72a1d0355b3a3a3dca55bae898"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/formation-energy-primary-records-v1.json"
PRIMARY_HASH = "sha256:226f9cec93f2c961a3cf04c0ca019e7d1dace67f17434443bf66af510e11abef"
IDENTITY_PATH = "experiments/external_sources/chemistry/formation_energy_target_identities_v1.json"
IDENTITY_HASH = "sha256:00389fa94f56bab42678d727d8aab5711a20a05e2bfcb4fbad8156c3edea65dd"
TARGET_PATH = "experiments/external_sources/chemistry/formation_energy_withheld_targets_v1.json"
TARGET_HASH = "sha256:299aa237ad30061e60c20666ea7ddd265d4eac99952270f25f00090f66f3ec39"


for _path, _hash in (
    (LIST_PATH, LIST_HASH), (CHOICE_PATH, CHOICE_HASH), (RESULT_PATH, RESULT_HASH),
    (REFERENCE_PATH, REFERENCE_HASH), (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-013 registered source changed: {_path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_forbidden = {"source_value_present", "source_value_inscription", "native_value", "external_state_orientation", "exact_positive_magnitude_kJ_per_mol", "structural_absence"}
if (
    _primary.get("schema") != "sft-v3-nist-cccbdb-formation-energy-primary-records/1"
    or _primary.get("complete_listed_species_count") != 2186
    or _primary.get("complete_unique_formula_composition_query_count") != 1193
    or _primary.get("complete_returned_charge_state_choice_count") != 1832
    or _primary.get("complete_listed_composition_without_returned_choice_count") != 83
    or _primary.get("complete_displayed_molecular_row_count") != 1049
    or _primary.get("complete_reference_axis_cell_count") != 2098
    or _primary.get("source_value_present_count") != 1485
    or _primary.get("source_value_absent_count") != 613
    or _primary.get("product_below_reference_count") != 756
    or _primary.get("product_above_reference_count") != 707
    or _primary.get("product_equal_reference_structural_EmptyOne_count") != 22
    or _identity_document.get("schema") != "sft-v3-formation-energy-identities/1"
    or _identity_document.get("complete_target_count") != 2098
    or _identity_document.get("all_formation_values_presence_flags_and_orientations_absent") is not True
    or len(_identity_document.get("rows", ())) != 2098
    or any(row.get("target_value_absent") is not True or _forbidden.intersection(row) for row in _identity_document["rows"])
):
    raise ValueError("PROP-013 complete source or value-free identity boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=RESULT_PATH,
        snapshot_hash=RESULT_HASH,
    )
    for row in _identity_document["rows"]
)


FORMATION_ENERGY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013",
    title="Exact molecular formation-energy relation",
    statement=(
        "A molecular formation-energy record is the exact relation between one completely identified product state "
        "and the exact composition of its named constituent reference states under a held phase and temperature "
        "reference. Unequal endpoints force one held above/below orientation and one exact positive separation; "
        "equality is structural EmptyOne. All 2,098 value-free identities seal before the complete NIST vector of "
        "1,485 printed experimental values and 613 blank cells opens."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, reference, orientation, magnitude, absence, prediction, record "
        "and extension forms; decide all 256 candidates only from admitted exact composition, state order, "
        "conservation, path and target-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent exact product/reference relation for every finite named constituent tuple, tested "
        "against all 2,098 cells from the complete official CCCBDB formation-energy property surface and the "
        "preserved thermodynamic reference-state page. Printed values, blanks and source orientations remain explicit."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One named product state and one nonempty exact constituent-reference composition force either one held "
        "orientation with one exact positive separation or structural equality."
    ),
    induction_step=(
        "Appending the same exact positive state to product and reference preserves orientation and separation; "
        "equal positive repetition preserves orientation and scales separation without a new coefficient."
    ),
    exclusions=(
        "no numerical zero; equality and missing source measurement are distinct structural EmptyOne records",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no measured formation energy or source orientation in the law, grammar, forcing or prediction",
        "no imported thermodynamic convention value, fitted atomic reference or species coefficient",
        "no selected molecule, temperature axis, sign class, favorable value or completed-row subset",
        "no deletion of blanks, exact source equalities, unreturned compositions or reference-state custody",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-FORMATION-ENERGY-013",
    expected_observation_label="held-product-reference-order-with-exact-positive-separation-or-structural-EmptyOne",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if exact product/reference state order does not force the stated held orientation and "
        "positive separation; if shared extension changes the relation; if equality requires numerical zero; if "
        "any of 2,098 cells, 1,485 values, 613 blanks, 756 below, 707 above, 22 equal records, 2,186 listed species, "
        "83 unreturned compositions or the complete reference-state page is omitted; if any target opens before "
        "seal; or if a measured value, imported convention, fitted reference or species coefficient enters the law."
    ),
)
FORMATION_ENERGY_SPEC.validate()


__all__ = (
    "CHOICE_HASH", "CHOICE_PATH", "FORMATION_ENERGY_SPEC", "IDENTITY_HASH", "IDENTITY_PATH",
    "LIST_HASH", "LIST_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "REFERENCE_HASH", "REFERENCE_PATH",
    "RESULT_HASH", "RESULT_PATH", "SNAPSHOT_ROOT", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
