"""Registered THERMO-018 law and complete thermal-conductivity surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.thermal_conductivity_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-018-thermal-conductivity-v1"
SPEC_PATH = "experiments/external_sources/chemistry/thermal_conductivity_capture_spec_v1.json"
SPEC_HASH = "sha256:7dd5d45a8cc06bb2472daa4951b1297c5f73fba9ce1575526ac6dcac829d3473"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/thermal-conductivity-primary-records-v1.json"
PRIMARY_HASH = "sha256:83ba98c5a0a234dd09d5704facfbc4461d38b1d0447a912a89e29677d7e7c679"
IDENTITY_PATH = "experiments/external_sources/chemistry/thermal_conductivity_target_identities_v1.json"
IDENTITY_HASH = "sha256:679af271eb6b9dc075548f1e40f411788b23224626b77b6f56e14fbe2fa7dd4f"
TARGET_PATH = "experiments/external_sources/chemistry/thermal_conductivity_withheld_targets_v1.json"
TARGET_HASH = "sha256:747997159dc49b5751d482f4ecb89604cf444e6a6b854abcfae4cf9f2b7f9cd5"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2013-58-663-670.json", "sha256:b0db6f1490cb13ecfa48da138ac3acee8c0602f9a537c28185aefba78177bfc5"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2013-58-663-670.html", "sha256:717e58cd19f820cd4f11c75368a935a38acb7f6b7d7a2fcbad49ffe28ca5b934"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jct-2019-133-135-142.json", "sha256:eec2f7f13b731b4d15b43342cda3fc2fed3ff35f478502a62888abe5d1f7ab55"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jct-2019-133-135-142.html", "sha256:af9eb25a2d050522181b6aac5eb78a69facb9f1961137222e0343df7cd41eeb7"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2018-477-78-86.json", "sha256:7dd4a12c63e6764bc2d586649e44565c42005df445fed1655280d40d27918ada"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-fpe-2018-477-78-86.html", "sha256:2bb63904e9fd886680a0c79752db0ef32dc007b190dc4c0404dc95caeb05bc85"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-018 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 3
    or _primary.get("complete_dataset_count_across_sources") != 61
    or _primary.get("complete_all_property_point_count_across_sources") != 679
    or _primary.get("complete_target_count") != 655
    or _primary.get("mixture_class_counts") != {"pure": 123, "binary": 273, "ternary": 259}
    or _primary.get("phase_counts") != {"Gas": 51, "Liquid": 571, "Crystal 2": 33}
    or _identities.get("complete_target_count") != 655
    or _identities.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 655
):
    raise ValueError("THERMO-018 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"POMD {row['dataset_ordinal']} property {row['property_number']} point {row['source_point_ordinal']} (thermal conductivity)",
        snapshot_path=PRIMARY_PATH, snapshot_hash=PRIMARY_HASH,
    ) for row in _identities["rows"]
)


THERMAL_CONDUCTIVITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-THERMAL-CONDUCTIVITY-RELATION-018",
    title="Exact composition-bound thermal-conductivity law",
    statement=(
        "Chemical thermal conductivity is counted adjacent-cell energy-packet transfer per exact tick, boundary and "
        "thermal-order separation while retaining every component, phase and condition. Chemistry owns composition-, "
        "species-, phase- and condition-dependence; the energy carrier is inherited explicitly from Physics. Measured "
        "conductivity is exact positive post-seal support, with direction held as a label rather than a signed magnitude."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, identity, transfer, orientation, resource, magnitude, prediction and extension forms; decide all 256 candidates only from admitted energy, thermal-order, adjacency, transition, conservation, exact-resource, composition, phase, EmptyOne and finite-successor laws.",
    grammar_boundary="Every finite pure, binary or ternary thermal-conductivity record with complete component identities, phase, exact conditions, counted adjacent cells, thermal orders, energy packets, transfers, ticks and boundary support. External testing preserves all 655 direct conductivity points and all companion properties from three complete NIST sources.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One complete component carrier, one phase, two adjacent cells, two distinct positive thermal orders, one energy packet, one transfer, one tick, one boundary and one exact condition form the least chemical thermal-conductivity record.",
    induction_step="Appending one complete component, phase, condition, transfer or measurement record preserves all earlier distinctions; common transfer/tick replication preserves exact response and held direction without refitting.",
    exclusions=(
        "no numerical zero; absent external condition coordinates are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported Fourier constitutive equation, continuum temperature gradient, kinetic-theory formula, fitted mixing or temperature law",
        "no interpolation, regression, selected substance/mixture/phase/condition/method/dataset/property/row or target correction",
        "no substance, composition, phase, temperature, pressure, method, value, uncertainty or target hash before prediction seal",
        "every complete source and non-conductivity companion remains preserved; companions never become conductivity measurements",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-THERMAL-CONDUCTIVITY-RELATION-018",
    expected_observation_label="complete-pure-binary-ternary-gas-liquid-crystal-thermal-conductivity-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any component, phase, condition, cell, thermal order, energy packet, transfer, tick or boundary "
        "is erased; if adjacency or energy conservation fails; if numerical-zero or signed proof value, continuum gradient, "
        "Fourier/kinetic/mixing/temperature fit, logarithm, interpolation, regression, selection or target correction enters; "
        "if target content opens before all 655 identities seal; if any direct conductivity row, uncertainty, method, dataset, "
        "complete source or companion provenance is omitted; or if any target is tampered."
    ),
)
THERMAL_CONDUCTIVITY_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES", "THERMAL_CONDUCTIVITY_SPEC",
)
