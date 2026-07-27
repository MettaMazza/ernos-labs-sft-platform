"""Registered THERMO-010 law and complete NIST real-gas equilibrium surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.real_gas_exchange_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-010-real-gas-equilibrium-v1"
SPEC_PATH = "experiments/external_sources/chemistry/real_gas_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:9935f5e2e67e62329bb976c7f22e196b9f3e48d61c6c9681ebf8b539eb0bb66e"
RAW_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2019-485-145-152.json"
RAW_HASH = "sha256:fdaaa9d89f1a324610ae9c5d77b4b129207b6a291e586c3bc3c42c17043724dc"
LANDING_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2019-485-145-152.html"
LANDING_HASH = "sha256:40921df1b606fea01575c7cb28fbe8b497ebb0700a77404df1fba7eede44fcb6"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/real-gas-equilibrium-primary-records-v1.json"
PRIMARY_HASH = "sha256:a522dfbb55b0424c5f50e54993a83dba38f46254e41440d6cd7fccc69d6b5012"
IDENTITY_PATH = "experiments/external_sources/chemistry/real_gas_equilibrium_target_identities_v1.json"
IDENTITY_HASH = "sha256:8bcf92103101ae6cab852ce5ad4a23598bcc6a0c7832523dd51fb5b95ebbc6d8"
TARGET_PATH = "experiments/external_sources/chemistry/real_gas_equilibrium_withheld_targets_v1.json"
TARGET_HASH = "sha256:5618d38b949d0e1cbde8ce3ef5553af795a82666dfe958ff558a8943e4f22f26"


for path, expected in (
    (SPEC_PATH, SPEC_HASH),
    (RAW_PATH, RAW_HASH),
    (LANDING_PATH, LANDING_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-010 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
_targets = json.loads((ROOT / TARGET_PATH).read_text())
if (
    _primary.get("complete_compound_count") != 5
    or _primary.get("complete_source_dataset_count") != 21
    or _primary.get("complete_source_point_count") != 176
    or _primary.get("complete_equilibrium_pressure_dataset_count") != 7
    or _primary.get("complete_gas_composition_dataset_count") != 3
    or _primary.get("complete_equilibrium_state_count") != 94
    or _primary.get("matched_gas_composition_state_count") != 59
    or _primary.get("pressure_only_equilibrium_state_count") != 35
    or _identities.get("complete_target_count") != 94
    or _identities.get(
        "all_compound_temperature_pressure_composition_phase_equilibrium_uncertainty_and_target_hash_values_absent"
    )
    is not True
    or len(_identities.get("rows", ())) != 94
    or _targets.get("complete_target_count") != 94
    or len(_targets.get("rows", ())) != 94
):
    raise ValueError("THERMO-010 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id="NIST-TRC-THERMOML-FPE-2019-485-145-152",
        source_locator=(
            f"POMD {row['pressure_dataset_ordinal']} source point {row['pressure_point_ordinal']}"
        ),
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


REAL_GAS_EXCHANGE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010",
    title="Fugacity-equivalent real-gas mixture law",
    statement=(
        "A component's Fold-native fugacity equivalent is its exact positive accessible gas exchange-support "
        "count over the complete held reference-support count at one retained pressure, temperature and "
        "composition. Real-gas interaction is the exact joint-versus-independent support relation, and phase "
        "equilibrium is exact component exchange-support balance. No fugacity equation, equation of state, "
        "logarithm or fitted correction is imported. All 94 real-gas equilibrium identities seal before values open."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, state, component, relation, equilibrium, prediction, record "
        "and extension forms; decide all 256 candidates only from admitted finite-support, component-exchange, "
        "phase-equilibrium, held-coordinate and exact-replication laws."
    ),
    grammar_boundary=(
        "Every finite gas-mixture component exchange account with held component, gas phase, pressure, "
        "temperature, composition, accessible/reference/independent support and partner-phase support. External "
        "testing preserves the complete NIST TRC ThermoML source: five compounds, 21 datasets, 176 raw points, "
        "seven direct pressure datasets, three paired vapor-composition datasets and all 94 equilibrium states."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One accessible component exchange-support fibre held against one complete reference support yields the "
        "first fugacity-equivalent relation; equality with one partner-phase support yields the first balance."
    ),
    induction_step=(
        "Replicating accessible, reference, independently composed and partner-phase supports by the same exact "
        "positive count preserves their ratios and order/equality relations at every finite depth."
    ),
    exclusions=(
        "no numerical zero; absent support is structural EmptyOne and any external zero glyph remains an interface inscription",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported fugacity equation, chemical-potential logarithm, ideal-gas law, equation of state, compressibility or virial fit",
        "no fitted interaction parameter, selected mixture, selected state, target-derived correction or measured-value lookup",
        "no compound, temperature, pressure, liquid/gas composition, uncertainty or target hash before prediction seal",
        "no correlated, regressed, Peng-Robinson, Wong-Sandler, NRTL or model-calculated value used as a measurement",
        "every external decimal remains a post-seal source inscription bound to the complete measurement record",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010",
    expected_observation_label="complete-fugacity-equivalent-real-gas-exchange-account",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the exchange relation is detached from component, phase, pressure, temperature or "
        "composition; if accessible/reference support is not exact positive; if equilibrium is not exact component "
        "exchange balance; if any fugacity equation, equation of state, logarithm, ideal-gas assumption, fit or "
        "target-derived correction enters; if exact replication changes a relation; if a target opens before all "
        "94 identities seal; if any of five compounds, 21 datasets, 176 points, 94 equilibrium states, 59 paired "
        "composition states, 35 pressure-only states, conditions, uncertainties or methods is omitted; or if a "
        "correlated/model-calculated value is treated as measurement."
    ),
)
REAL_GAS_EXCHANGE_SPEC.validate()


__all__ = (
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "LANDING_HASH",
    "LANDING_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "RAW_HASH",
    "RAW_PATH",
    "REAL_GAS_EXCHANGE_SPEC",
    "SPEC_HASH",
    "SPEC_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
