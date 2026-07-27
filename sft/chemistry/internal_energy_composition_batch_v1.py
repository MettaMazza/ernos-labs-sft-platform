"""Registered internal-energy composition law and blind NIST state vector."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.internal_energy_composition_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-shared-water-isobar-v1"
SNAPSHOT_PATH = f"{SNAPSHOT_ROOT}/nist-webbook-water-isobar-1bar-300-400K.html"
SNAPSHOT_HASH = "sha256:fe25279cb2c8f54a749b503dc17249656e8ac773be0b273aa3f99d283d15050c"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/thermophysical-state-primary-records-v1.json"
PRIMARY_HASH = "sha256:48d25011fb7b87017a06e8b0e89d3f4a8d9928ef74625008cd2f7cba9a124c95"
IDENTITY_PATH = "experiments/external_sources/chemistry/thermophysical_state_target_identities_v1.json"
IDENTITY_HASH = "sha256:1161a9a8913ddedd309110077bcdab883fbb1f7046a59e279e8972f435602025"
TARGET_PATH = "experiments/external_sources/chemistry/thermophysical_state_withheld_targets_v1.json"
TARGET_HASH = "sha256:707f5005e6a47197f320e98977d2a2c000dfa4bc2877f81c6e38b1a6c7d637ad"


for _path, _hash in (
    (SNAPSHOT_PATH, SNAPSHOT_HASH), (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"THERMO-003 registered source changed: {_path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_value_columns = {
    "temperature-kelvin", "pressure-bar", "density-mole-per-litre", "volume-litre-per-mole",
    "internal-energy-kilojoule-per-mole", "enthalpy-kilojoule-per-mole",
    "entropy-joule-per-mole-kelvin", "isochoric-heat-capacity-joule-per-mole-kelvin",
    "isobaric-heat-capacity-joule-per-mole-kelvin", "sound-speed-metre-per-second",
    "joule-thomson-kelvin-per-bar", "viscosity-micropascal-second",
    "thermal-conductivity-watt-per-metre-kelvin", "phase-identity", "snapshot_hash",
}
if (
    _primary.get("schema") != "sft-v3-thermophysical-state-primary-records/1"
    or _primary.get("identity_registry_hash_before_source_response_open") != IDENTITY_HASH
    or _primary.get("complete_returned_row_count") != 13
    or _primary.get("liquid_row_count") != 9 or _primary.get("vapor_row_count") != 4
    or _primary.get("phase_boundary_row_count") != 2
    or _primary.get("all_fourteen_returned_columns_preserved") is not True
    or _primary.get("external_values_used_as_proof_parameters") is not False
    or _identities.get("schema") != "sft-v3-thermophysical-state-identities/1"
    or _identities.get("complete_query_identity_count") != 13
    or _identities.get("all_returned_temperatures_phases_and_property_values_absent") is not True
    or len(_identities.get("rows", ())) != 13
    or any(_value_columns.intersection(row) for row in _identities["rows"])
    or _targets.get("schema") != "sft-v3-thermophysical-state-withheld-targets/1"
    or _targets.get("release_requires_complete_identity_prediction_seal") is not True
    or _targets.get("identity_registry_hash") != IDENTITY_HASH
    or _targets.get("complete_target_count") != 13
    or len(_targets.get("rows", ())) != 13
):
    raise ValueError("THERMO-003 complete source or value-free identity boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=f"one-bar water isobaric table :: returned row {row['source_row_ordinal']}",
        snapshot_path=SNAPSHOT_PATH, snapshot_hash=SNAPSHOT_HASH,
    )
    for row in _identities["rows"]
)


INTERNAL_ENERGY_COMPOSITION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    title="Internal-energy composition law",
    statement=(
        "A complete chemical internal-energy state retains composition, molecular state, phase and environment. "
        "Its content is the exact composition of nonempty named positive parts. Change direction is a held rise/fall "
        "label and its magnitude is exact positive separation; equality is structural EmptyOne. All 13 NIST state "
        "identities seal before the complete 14-column internal-energy vector opens."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, parts, orientation, equality, path, prediction, record and extension "
        "forms; decide all 256 candidates only from admitted exact composition, order, energy-conservation and "
        "finite-state laws."
    ),
    grammar_boundary=(
        "Every finite nonempty named positive energy-part tuple and every finite same-orientation chemical-state path, "
        "with append-only successor closure. External testing uses every row and every column returned by the frozen "
        "NIST one-bar water query from 300 to 400 K, including both phase-boundary states."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One complete chemical state with one named exact positive internal-energy part forces one retained total and "
        "one held state identity."
    ),
    induction_step=(
        "Appending one new named exact positive part preserves every earlier part and adds its content exactly once; "
        "appending one same-direction state step preserves all earlier path records and adds its positive magnitude."
    ),
    exclusions=(
        "no numerical zero; equal energy states use structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no measured state value, phase, temperature, target payload or target hash in law, grammar or prediction",
        "no fitted constituent contribution, residual energy, imported thermodynamic equation or species coefficient",
        "no endpoint-only signed cancellation, selected temperature row, selected phase or deleted phase-boundary state",
        "external signed glyphs remain source inscriptions and never enter an SFT proof magnitude",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
    expected_observation_label="complete-held-internal-energy-state-with-positive-part-and-oriented-step-composition",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if internal energy requires a fitted or unnamed contribution; if change direction requires a "
        "negative proof magnitude; if exact successive same-direction steps do not compose to the direct separation; "
        "if appending a part changes an earlier part; if any target opens before all 13 identities seal; if any of 13 "
        "rows, 14 columns, 9 liquid rows, 4 vapour rows or either 372.75593 K phase-boundary state is omitted; if the "
        "complete direct internal-energy path is not exact and increasing; or if target values select the law."
    ),
)
INTERNAL_ENERGY_COMPOSITION_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "INTERNAL_ENERGY_COMPOSITION_SPEC", "PRIMARY_HASH", "PRIMARY_PATH",
    "SNAPSHOT_HASH", "SNAPSHOT_PATH", "SNAPSHOT_ROOT", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
