"""Registered chemical temperature correspondence and blind thermometric value vector."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.temperature_correspondence_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-002-temperature-correspondence-v1"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/chemical-temperature-primary-records-v1.json"
PRIMARY_HASH = "sha256:a20431a2644dbb5c41dd009472fd1c57b597611904739d118c64cbb07caf1bb9"
IDENTITY_PATH = "experiments/external_sources/chemistry/chemical_temperature_target_identities_v1.json"
IDENTITY_HASH = "sha256:ccfce4f71bb3eb8edfc96e2b9b7b6e68e54643c83bce87c6beb98e8b94c907ea"
TARGET_PATH = "experiments/external_sources/chemistry/chemical_temperature_withheld_targets_v1.json"
TARGET_HASH = "sha256:93819764e02927c5f15ac2b52f58219d4b2429c24621f9f38e017f07c0223d70"
PHYSICS_RECORD_PATH = "experiments/external_sources/physics/snapshots/thermal-equilibrium-postseal-source-record.json"
PHYSICS_RECORD_HASH = "sha256:8048a2397c064290a0b948b4238b4133c1a2e5c76a72ecf0c47222c9a951d7b5"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt", "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"),
    ("experiments/external_sources/physics/snapshots/nist-acoustic-boltzmann-2017.pdf", "sha256:1cbb21f0e5817270b5e028105aa79fea22017fd84130c2c4b79d1492fb37e418"),
    ("experiments/external_sources/physics/snapshots/nist-electronic-boltzmann-2011.pdf", "sha256:187066b5390d57a3c058e0a34f6c7803a659045ba714ca4b25eed7b84b212bbb"),
)


for _path, _hash in (
    (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    (PHYSICS_RECORD_PATH, PHYSICS_RECORD_HASH), *SOURCE_FILES,
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"THERMO-002 registered source changed: {_path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_forbidden = {
    "exact_si_common_carrier_scaled_numerator", "common_scale_denominator",
    "measured_center_scaled_numerator", "measured_standard_uncertainty_scaled_numerator",
    "measured_interval_lower_scaled_numerator", "measured_interval_upper_scaled_numerator",
    "relative_standard_uncertainty_parts_per_million", "relative_combined_uncertainty_parts_per_million",
    "temperature_measures_average_kinetic_energy", "noise_power_depends_on_resistance_and_temperature",
    "reported_relation_accuracy_parts_per_million",
}
if (
    _primary.get("schema") != "sft-v3-chemical-temperature-primary-records/1"
    or _primary.get("identity_registry_hash_before_target_open") != IDENTITY_HASH
    or _primary.get("complete_target_count") != 3
    or _primary.get("complete_physically_distinct_route_count") != 2
    or _primary.get("external_values_used_as_proof_parameters") is not False
    or _identities.get("schema") != "sft-v3-chemical-temperature-identities/1"
    or _identities.get("complete_target_count") != 3
    or _identities.get("complete_physically_distinct_route_count") != 2
    or _identities.get("all_values_uncertainties_intervals_and_relation_flags_absent") is not True
    or len(_identities.get("rows", ())) != 3
    or any(_forbidden.intersection(row) for row in _identities["rows"])
    or _targets.get("schema") != "sft-v3-chemical-temperature-withheld-targets/1"
    or _targets.get("release_requires_complete_identity_prediction_seal") is not True
    or _targets.get("identity_registry_hash") != IDENTITY_HASH
    or _targets.get("complete_target_count") != 3
    or _targets.get("measurement_routes_physically_distinct") is not True
    or _targets.get("all_registered_rows_retained") is not True
    or len(_targets.get("rows", ())) != 3
):
    raise ValueError("THERMO-002 complete source or value-free identity boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]), source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]), snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identities["rows"]
)


TEMPERATURE_CORRESPONDENCE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    title="Chemical temperature correspondence",
    statement=(
        "Chemistry consumes the admitted Physics temperature carrier without rescaling it. Composition, phase, "
        "equilibrium reference and thermometric route remain held chemical identities, while equilibrated contexts "
        "share one exact carrier and composition-dependent consequences attach without a fitted conversion. Three "
        "value-free identities seal before the exact SI carrier and two independent thermometry intervals open."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of authority, composition, condition, relation, equilibrium, prediction, "
        "record and extension forms; decide all 256 candidates only from admitted Physics temperature/equilibrium "
        "and exact Chemistry state-support laws."
    ),
    grammar_boundary=(
        "Every finite set of held chemical contexts sharing one admitted Physics temperature carrier at one held "
        "equilibrium reference, with append-only composition consequences. External testing retains the exact SI "
        "carrier, the complete acoustic-argon interval and the complete independent Johnson-noise interval."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One chemical composition, phase, route and equilibrium reference consume one exact positive admitted "
        "Physics temperature carrier unchanged."
    ),
    induction_step=(
        "Appending one new composition-dependent consequence retains every existing context and the same common "
        "Physics carrier without a new scale, coefficient or route-specific correction."
    ),
    exclusions=(
        "no numerical zero; external zero glyphs remain source inscriptions and native absence is structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no Chemistry-specific redefinition, rescaling, calibration coefficient or fitted temperature conversion",
        "no measured center, uncertainty, interval endpoint, relation flag or target hash in law, grammar or prediction",
        "no selected thermometry route, omitted uncertainty endpoint, composition erasure or target-selected equilibrium",
        "no imported continuum distribution, conventional thermodynamic equation or composition-specific free parameter",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    expected_observation_label="one-unchanged-physics-temperature-carrier-across-held-chemical-compositions-and-equilibrated-routes",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if Chemistry requires a different temperature carrier, composition-dependent scale or "
        "route-specific correction; if adding a composition changes the common carrier; if any target value opens "
        "before all three identities seal; if the exact SI carrier lies outside either complete measured interval; "
        "if argon, gas phase, TPW reference, kinetic-temperature relation, Johnson response, uncertainty endpoint or "
        "source limitation is omitted; or if target values select the law."
    ),
)
TEMPERATURE_CORRESPONDENCE_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "PHYSICS_RECORD_HASH", "PHYSICS_RECORD_PATH",
    "PRIMARY_HASH", "PRIMARY_PATH", "SNAPSHOT_ROOT", "SOURCE_FILES", "TARGET_HASH", "TARGET_PATH",
    "TARGET_REFERENCES", "TEMPERATURE_CORRESPONDENCE_SPEC",
)
