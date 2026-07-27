"""Registered finite chemical microstate-support law and blind structure vector."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.finite_microstate_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-001-finite-microstate-v1"
WATER_PATH = f"{SNAPSHOT_ROOT}/nist-webbook-water-gas-calorimetric-table.html"
WATER_HASH = "sha256:7fdfa32385d69f30584214e2c6c770c6f49578fc8a9778182339cd473b7db5ed"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/finite-microstate-primary-records-v1.json"
PRIMARY_HASH = "sha256:a8b27f4a9425782017774fe6112e301d3070b407b76137f1bf6720c2ea8c4f54"
IDENTITY_PATH = "experiments/external_sources/chemistry/finite_microstate_target_identities_v1.json"
IDENTITY_HASH = "sha256:18162121b47989f414c1ca1250d490be9d32d107bbf062e138109ba834ebde76"
TARGET_PATH = "experiments/external_sources/chemistry/finite_microstate_withheld_targets_v1.json"
TARGET_HASH = "sha256:83cefbb2b2c2ba7cc092921dc3e4734c070e10e58845aee75e509615e5e579d4"
POP_IDENTITY_PATH = "experiments/external_sources/chemistry/molecular_measurement_target_identities_v1.json"
POP_IDENTITY_HASH = "sha256:51dc19518f36c7b75342e524a89d60ba96c19dbb944856e83f54563927b59883"
POP_TARGET_PATH = "experiments/external_sources/chemistry/molecular_measurement_withheld_targets_v1.json"
POP_TARGET_HASH = "sha256:5f34dcfb27bb36ca8931e5a26dcfd290285708c7b4a4412884ff794273416eef"


for _path, _hash in (
    (WATER_PATH, WATER_HASH), (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    (POP_IDENTITY_PATH, POP_IDENTITY_HASH), (POP_TARGET_PATH, POP_TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"THERMO-001 registered source changed: {_path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
_identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_targets = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_forbidden = {
    "cells", "temperature_inscription_kelvin", "heat_capacity_inscription", "entropy_inscription",
    "held_gibbs_reference_relation_inscription", "enthalpy_reference_relation_inscription",
    "target_payload", "target_payload_hash", "population", "measured_value",
}
if (
    _primary.get("schema") != "sft-v3-finite-microstate-primary-records/1"
    or _primary.get("state_population_source", {}).get("complete_row_count") != 330
    or _primary.get("calorimetric_source", {}).get("complete_row_count") != 57
    or _primary.get("complete_target_count") != 387
    or _primary.get("finite_rows_only") is not True
    or _primary.get("completed_infinity_or_continuum_ensemble_used") is not False
    or _identities.get("schema") != "sft-v3-finite-microstate-identities/1"
    or _identities.get("complete_state_population_row_count") != 330
    or _identities.get("complete_calorimetric_row_count") != 57
    or _identities.get("complete_target_count") != 387
    or _identities.get("all_populations_temperatures_and_calorimetric_values_absent") is not True
    or len(_identities.get("rows", ())) != 387
    or any(_forbidden.intersection(row) for row in _identities["rows"])
    or _targets.get("schema") != "sft-v3-finite-microstate-withheld-targets/1"
    or _targets.get("release_requires_complete_identity_prediction_seal") is not True
    or _targets.get("identity_registry_hash") != IDENTITY_HASH
    or _targets.get("complete_target_count") != 387
    or len(_targets.get("rows", ())) != 387
):
    raise ValueError("THERMO-001 complete finite source or value-free identity boundary changed")


STATE_SNAPSHOT_PATHS = tuple(sorted({
    str(row["snapshot_path"])
    for row in _identities["rows"]
    if row["source_class"] == "direct-molecular-state-population-and-transition-record"
}))
if (
    len(STATE_SNAPSHOT_PATHS) != 8
    or any(
        hash_file(ROOT / path) != next(
            str(row["snapshot_hash"]) for row in _identities["rows"] if row["snapshot_path"] == path
        )
        for path in STATE_SNAPSHOT_PATHS
    )
):
    raise ValueError("THERMO-001 direct state-population snapshot custody changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row.get("source_locator", f"{row.get('source_file', 'state-record')} :: row {row['source_row_ordinal']}")),
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identities["rows"]
)


FINITE_MICROSTATE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    title="Finite chemical microstate-support law",
    statement=(
        "A chemical thermodynamic support is the complete generated finite tuple of held chemical microstates, "
        "partitioned so every state occurs exactly once in one named macro-observation fibre. Multiplicity is the "
        "exact positive fibre count and statistical weight is that count over the complete finite support count. "
        "All 387 external identities seal before 330 direct state records and 57 calorimetric rows open."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, identity, partition, multiplicity, weight, prediction, record and "
        "extension forms; decide all 256 candidates only from admitted exact state, observation, counting and "
        "thermodynamic carrier laws."
    ),
    grammar_boundary=(
        "Every nonempty finite generated chemical-state tuple and its complete disjoint observation partition, with "
        "one-state finite successor closure. Completed infinity and continuum ensembles are outside the grammar. "
        "External structure is tested on all 330 direct CaH+ state rows and all 57 NIST water calorimetric rows."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One held chemical microstate forces one nonempty support, one exhaustive observation fibre, multiplicity "
        "One and exact weight One over One."
    ),
    induction_step=(
        "Appending one newly generated held microstate and its named observation fibre preserves every previous "
        "state and assignment and extends the complete support by exactly one finite successor."
    ),
    exclusions=(
        "no numerical zero; native absence is structural EmptyOne and external zero glyphs remain source inscriptions",
        "no negative, irrational, imaginary, floating, signed or continuum SFT proof value",
        "no completed infinity, continuum ensemble, partition-function prior or assumed probability distribution",
        "no temperature, population, calorimetric value, target payload or target hash in law, grammar or prediction",
        "no fitted coefficient, species parameter, imported statistical equation or target-selected state partition",
        "no selected species, favorable state rows, deduplication of the NIST regime-boundary row or omitted source row",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-FINITE-MICROSTATE-SUPPORT-001",
    expected_observation_label="complete-finite-held-state-support-with-disjoint-exhaustive-observation-fibres-and-exact-count-weights",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any generated state is omitted, duplicated or assigned to more than one fibre; if "
        "multiplicity or weight requires a distribution prior or fitted coefficient; if finite successor changes "
        "a previous assignment; if any target value opens before the 387-identity seal; if any of 330 state rows or "
        "57 calorimetric rows is omitted or the duplicated 1700 K regime-boundary record is silently deduplicated; "
        "or if a continuum, completed infinity or external thermodynamic equation enters the proof."
    ),
)
FINITE_MICROSTATE_SPEC.validate()


__all__ = (
    "FINITE_MICROSTATE_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH",
    "POP_IDENTITY_HASH", "POP_IDENTITY_PATH", "POP_TARGET_HASH", "POP_TARGET_PATH",
    "SNAPSHOT_ROOT", "STATE_SNAPSHOT_PATHS", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
    "WATER_HASH", "WATER_PATH",
)
