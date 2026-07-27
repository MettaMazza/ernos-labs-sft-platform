"""Registered THERMO-012 law and complete NIST one-component coexistence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.one_component_phase_boundary_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-012-one-component-phase-boundary-v1"
SPEC_PATH = "experiments/external_sources/chemistry/one_component_phase_boundary_capture_spec_v1.json"
SPEC_HASH = "sha256:4db9cc027e04d154d05e1996cc5ed05bd27b9a9a300f5db98c1fca2ec6cfbfc3"
RAW_PATH = "experiments/external_sources/chemistry/snapshots/thermo-010-real-gas-equilibrium-v1/nist-trc-thermoml-fpe-2019-485-145-152.json"
RAW_HASH = "sha256:fdaaa9d89f1a324610ae9c5d77b4b129207b6a291e586c3bc3c42c17043724dc"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/one-component-phase-boundary-primary-records-v1.json"
PRIMARY_HASH = "sha256:33789b36e4fc91ade528aba22b9d9b27bc666fd74e6b82be65a0ea451381b017"
IDENTITY_PATH = "experiments/external_sources/chemistry/one_component_phase_boundary_target_identities_v1.json"
IDENTITY_HASH = "sha256:3f37dd294e65daa566d55f8d27d1d891a46d9375666038becd68ae955b884293"
TARGET_PATH = "experiments/external_sources/chemistry/one_component_phase_boundary_withheld_targets_v1.json"
TARGET_HASH = "sha256:9310be78aa44c9ee932df8ee4afc96835ffce84c76e204893467cef98a61e39b"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (RAW_PATH, RAW_HASH), (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-012 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
_targets = json.loads((ROOT / TARGET_PATH).read_text())
if (
    _primary.get("complete_parent_compound_count") != 5
    or _primary.get("complete_parent_dataset_count") != 21
    or _primary.get("complete_parent_point_count") != 176
    or _primary.get("complete_direct_one_component_dataset_count") != 3
    or _primary.get("complete_direct_one_component_point_count") != 15
    or _primary.get("complete_distinct_one_component_count") != 2
    or _identities.get("complete_target_count") != 15
    or _identities.get("all_compound_temperature_pressure_phase_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 15
    or _targets.get("complete_target_count") != 15
    or len(_targets.get("rows", ())) != 15
):
    raise ValueError("THERMO-012 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id="NIST-TRC-THERMOML-FPE-2019-485-145-152",
        source_locator=f"POMD {row['dataset_ordinal']} source point {row['source_point_ordinal']}",
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


ONE_COMPONENT_PHASE_BOUNDARY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012",
    title="One-component finite phase-boundary relation",
    statement=(
        "A one-component two-phase boundary is the exact finite ordered word of complete coexistence points. At "
        "each point the component exchange supports of the two held phases are equal; the phase-rule relation "
        "leaves one independent held coordinate support. For a stable liquid-vapor successor, exact temperature "
        "and pressure supports are co-ordered. No differential equation, interpolated continuum or fitted slope enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, phase, balance, degree, response, boundary, prediction and "
        "extension forms; decide all 256 candidates only from admitted component identity, exchange balance, "
        "phase-rule cancellation, exact order and finite-word successor laws."
    ),
    grammar_boundary=(
        "Every finite positive word of one-component, two-distinct-phase, exactly exchange-balanced coexistence "
        "points whose held temperature and pressure supports are strictly co-ordered in source succession. "
        "External testing preserves both compounds, all three direct datasets, all fifteen measured points, "
        "all twelve adjacent successions and the complete 21-dataset 176-point parent source."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One held component, two distinct phases, equal component exchange supports and one complete positive "
        "temperature-pressure record form the least coexistence-boundary word."
    ),
    induction_step=(
        "Appending one later exchange-balanced point with strictly greater exact temperature and pressure supports "
        "preserves the complete finite boundary; common exact support replication preserves balance and order."
    ),
    exclusions=(
        "no numerical zero; absent separation at exact exchange balance is structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported Clausius-Clapeyron equation, differential equation, equation of state or vapor-pressure equation",
        "no interpolation, regression, fitted slope, selected compound, selected curve segment or target-derived correction",
        "no compound, phase, temperature, pressure, uncertainty or target hash before prediction seal",
        "every external decimal remains a post-seal source inscription and every parent-source row remains preserved",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012",
    expected_observation_label="complete-one-component-finite-coexistence-boundary",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a point loses component, phase, temperature, pressure or exchange-support identity; if "
        "the phase pair is not distinct or exchange balanced; if one-component two-phase support does not leave "
        "one independent carrier; if a later stable liquid-vapor point does not preserve exact temperature-pressure "
        "co-order; if any differential equation, equation of state, interpolation, fit, selected compound/interval "
        "or target-derived correction enters; if targets open before all fifteen identities seal; if either compound, "
        "any of three datasets, fifteen points, twelve adjacent successions, uncertainties, methods or the complete "
        "parent source is omitted; or if any measured coordinate is tampered."
    ),
)
ONE_COMPONENT_PHASE_BOUNDARY_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "ONE_COMPONENT_PHASE_BOUNDARY_SPEC", "PRIMARY_HASH", "PRIMARY_PATH",
    "RAW_HASH", "RAW_PATH", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
