"""Registered THERMO-008 law and complete fixed-pressure multicomponent VLE surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.component_exchange_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-008-component-exchange-v1"
SPEC_PATH = "experiments/external_sources/chemistry/component_exchange_capture_spec_v2.json"
SPEC_HASH = "sha256:f6ae8d2c1e45da5b1ff25d19933dbf7f14afb5508ab51bd042807d3635abf864"
RAW_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2019-9b00414.json"
RAW_HASH = "sha256:8bf7ce04c1a08434807489d29a9d6a0c366200b042c08d8ba6edfd61f25c675b"
LANDING_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2019-9b00414.html"
LANDING_HASH = "sha256:970eb47e49bf38446dd9eeb4b9c2871644ef59a02d178ce44b63fb1c7ae15ffb"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/component-exchange-primary-records-v1.json"
PRIMARY_HASH = "sha256:006956947701247b87e566e762c4e3e0286df79e25137d7ed1daacbc9faa158f"
IDENTITY_PATH = "experiments/external_sources/chemistry/component_exchange_target_identities_v1.json"
IDENTITY_HASH = "sha256:8fb540f04200401d83abd4b24ffdb62b916947e4217d2555dbde1987a37954af"
TARGET_PATH = "experiments/external_sources/chemistry/component_exchange_withheld_targets_v1.json"
TARGET_HASH = "sha256:5299ca7bcc6e4d16a84321422fd170ef3f471a23acc4033873c26bfb8bc5f789"

for path, expected in (
    (SPEC_PATH, SPEC_HASH),
    (RAW_PATH, RAW_HASH),
    (LANDING_PATH, LANDING_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-008 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
_targets = json.loads((ROOT / TARGET_PATH).read_text())
if (
    _primary.get("complete_source_compound_count") != 5
    or _primary.get("complete_source_dataset_count") != 13
    or _primary.get("complete_binary_system_count") != 4
    or _primary.get("complete_matched_multicomponent_target_count") != 74
    or _primary.get("complete_unmatched_temperature_endpoint_count") != 8
    or _identities.get("complete_target_count") != 74
    or _identities.get(
        "all_compound_temperature_pressure_composition_equilibrium_and_target_hash_values_absent"
    )
    is not True
    or len(_identities.get("rows", ())) != 74
    or _targets.get("complete_target_count") != 74
    or len(_targets.get("rows", ())) != 74
):
    raise ValueError("THERMO-008 complete source boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id="NIST-TRC-THERMOML-JCED-2019-9B00414",
        source_locator=(
            f"paired POMD {row['temperature_dataset_ordinal']}/{row['composition_dataset_ordinal']} "
            f"common point {row['common_interior_point_ordinal']}"
        ),
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


COMPONENT_EXCHANGE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    title="Chemical-potential-equivalent component law",
    statement=(
        "The chemical-potential-equivalent of one held component is its complete exact marginal "
        "addition account in a named phase: retained-energy increment and closed-distinction increment. "
        "At one fixed finite environment, paired component exchange is directed only by strict product "
        "order; exact account equality is equilibrium with structural EmptyOne separations and does not "
        "require equal bulk phase compositions. All 74 multicomponent equilibrium identities seal before "
        "compound, temperature, pressure or composition values open."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of accounts, identity, exchange, support, relation, prediction, "
        "record and extension forms; decide all 256 candidates only from admitted exact composition, "
        "transfer, energy, distinction and equilibrium laws."
    ),
    grammar_boundary=(
        "Every finite pair of distinct phase-specific addition accounts for the same held component at "
        "one held environment, with paired one-component exchange, exact positive marginal support and "
        "common-context successor closure. External testing preserves the complete NIST TRC ThermoML "
        "record: four binary systems, 74 matched interior VLE records and eight unmatched endpoints."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One component and two distinct phases at one fixed environment supply the first paired exchange. "
        "Strict product order directs exchange; exact equality supplies equilibrium."
    ),
    induction_step=(
        "Adding the same fresh exact positive energy and distinction context to both phase-specific "
        "component accounts preserves every comparison and therefore preserves direction or equilibrium."
    ),
    exclusions=(
        "no numerical zero; native absence and exact equality separations use structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported chemical-potential equation, activity coefficient, fugacity model, fitted weight or target-derived account",
        "no compound, temperature, pressure, liquid composition, gas composition, equilibrium result or target hash before prediction seal",
        "no selected mixture, selected row, deleted endpoint, fitted composition or model-correlated value used as measurement",
        "external decimal, zero and signed comparison glyphs remain post-seal source inscriptions only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    expected_observation_label="complete-chemical-potential-equivalent-component-exchange-account",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a component changes identity during exchange; if donor and receiver do not "
        "share one finite environment; if total component carrier is not conserved; if direction requires "
        "a signed scalar, logarithm, fitted activity coefficient or arbitrary tie-break; if equal complete "
        "accounts do not yield equilibrium or are incorrectly required to have equal bulk compositions; "
        "if a common context changes the relation; if any target opens before all 74 identities seal; if "
        "any of four systems, 74 matched interiors, eight unmatched endpoints, source conditions or "
        "uncertainties is omitted; or if measured values select the law."
    ),
)
COMPONENT_EXCHANGE_SPEC.validate()


__all__ = (
    "COMPONENT_EXCHANGE_SPEC",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "LANDING_HASH",
    "LANDING_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "RAW_HASH",
    "RAW_PATH",
    "SPEC_HASH",
    "SPEC_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
