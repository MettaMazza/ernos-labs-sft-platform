"""Registered THERMO-009 law and complete NIST solution-activity surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.solution_activity_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-009-solution-activity-v1"
SPEC_PATH = "experiments/external_sources/chemistry/solution_activity_capture_spec_v1.json"
SPEC_HASH = "sha256:bcd3af58c80f7bf971a96d7c94a5f0d961c094bc2082282dc01e58f714ef431b"
RAW_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2019-9b00694.json"
RAW_HASH = "sha256:114d827aa6765f895e86818effe23e5005e4c599cc7996fdc48dc71ab68782ad"
LANDING_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2019-9b00694.html"
LANDING_HASH = "sha256:9b512274ecd27288d60018c1d06090e79019cb8baf6ebc37e0e811474b45cc22"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/solution-activity-primary-records-v1.json"
PRIMARY_HASH = "sha256:d47755ec4ab15f0dbe32338b1bd00d40aea423a2478d214e2b94f8294fb2b478"
IDENTITY_PATH = "experiments/external_sources/chemistry/solution_activity_target_identities_v1.json"
IDENTITY_HASH = "sha256:6e1a1d42e07c1615bd5e5c0a5af957d1c0f29a3238a8a89d62171ecd5ca44cbc"
TARGET_PATH = "experiments/external_sources/chemistry/solution_activity_withheld_targets_v1.json"
TARGET_HASH = "sha256:7651a2366008af411fcc6181c635ffe6e989d79c76a3579ab614889852b7ab4b"

for path, expected in (
    (SPEC_PATH, SPEC_HASH),
    (RAW_PATH, RAW_HASH),
    (LANDING_PATH, LANDING_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-009 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
_targets = json.loads((ROOT / TARGET_PATH).read_text())
if (
    _primary.get("complete_compound_count") != 6
    or _primary.get("complete_dataset_count") != 9
    or _primary.get("complete_activity_row_count") != 204
    or _primary.get("complete_binary_dataset_count") != 5
    or _primary.get("complete_ternary_dataset_count") != 4
    or _primary.get("external_absence_glyph_row_count") != 68
    or _identities.get("complete_target_count") != 204
    or _identities.get(
        "all_compound_temperature_composition_activity_uncertainty_absence_and_target_hash_values_absent"
    )
    is not True
    or len(_identities.get("rows", ())) != 204
    or _targets.get("complete_target_count") != 204
    or len(_targets.get("rows", ())) != 204
):
    raise ValueError("THERMO-009 complete source boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id="NIST-TRC-THERMOML-JCED-2019-9B00694",
        source_locator=f"POMD {row['dataset_ordinal']} source point {row['source_point_ordinal']}",
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


SOLUTION_ACTIVITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    title="Activity and non-ideal composition law",
    statement=(
        "A component's solution activity is the exact positive count of its accessible exchange-support "
        "states over the complete held reference-support count at one fully retained composition and "
        "environment. Non-ideality is the exact relation between joint accessible support and independently "
        "composed support, without a fitted activity coefficient. An absent component is structural EmptyOne. "
        "All 204 solution identities seal before compounds, compositions, temperature or activities open."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, composition, activity, interaction, absence, prediction, "
        "record and extension forms; decide all 256 candidates only from admitted exact support-count, "
        "component-exchange, composition, condition and structural-absence laws."
    ),
    grammar_boundary=(
        "Every finite solution component account with complete phase, environment and exact component "
        "coordinates, accessible/reference/independent support counts and exact-replication closure. External "
        "testing preserves the complete NIST TRC ThermoML record: six compounds, nine binary/ternary datasets, "
        "204 direct isopiestic activity rows and all 68 absent-component boundaries."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One component exchange-support fibre and its held reference support yield the first exact relative "
        "activity; comparison with independently composed support yields the first non-ideal relation."
    ),
    induction_step=(
        "Replicating accessible, reference and independently composed supports by the same exact positive "
        "count preserves their ratio and order, and therefore preserves activity and non-ideal relation."
    ),
    exclusions=(
        "no numerical zero; an absent component is structural EmptyOne and source zero glyphs remain external inscriptions",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported activity-coefficient equation, fugacity model, ideal-mixture prior, fitted interaction parameter or target-derived correction",
        "no compound, temperature, molality, activity, uncertainty, absence flag or target hash before prediction seal",
        "no selected solution, selected composition, deleted absence row or correlated/regressed/model-calculated value used as measurement",
        "every external decimal and zero glyph remains a post-seal source inscription",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    expected_observation_label="complete-activity-nonideal-composition-account",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if activity is detached from component, phase, composition or condition; if accessible "
        "support is not an exact part of held reference support; if non-ideality requires a logarithm, fugacity "
        "model, fitted coefficient, assumed ideality or target-derived correction; if an absent component becomes "
        "numerical zero; if exact replication changes activity or relation; if any target opens before all 204 "
        "identities seal; if any of six compounds, nine datasets, 204 rows, 68 absence boundaries, conditions, "
        "uncertainties or methods is omitted; or if correlated model values enter as measurements."
    ),
)
SOLUTION_ACTIVITY_SPEC.validate()


__all__ = (
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "LANDING_HASH",
    "LANDING_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "RAW_HASH",
    "RAW_PATH",
    "SOLUTION_ACTIVITY_SPEC",
    "SPEC_HASH",
    "SPEC_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
