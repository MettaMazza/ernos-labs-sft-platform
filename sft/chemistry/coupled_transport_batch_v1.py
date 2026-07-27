"""Registered THERMO-019 law and complete pairwise coupled-transport surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.coupled_transport_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-019-coupled-transport-v1"
SPEC_PATH = "experiments/external_sources/chemistry/coupled_transport_capture_spec_v1.json"
SPEC_HASH = "sha256:b2298b06853b284b285df81121969885b2759366abc273c7e55585145bf723e2"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/coupled-transport-primary-records-v1.json"
PRIMARY_HASH = "sha256:4932a0d1518888a39bc614e861785bc0e04e17eea402cf4e920101808d172213"
IDENTITY_PATH = "experiments/external_sources/chemistry/coupled_transport_target_identities_v1.json"
IDENTITY_HASH = "sha256:d17f8e5bcc245dd8e4258798dea79fe17a0be7a69ebf8549fb54fd16adfe374f"
TARGET_PATH = "experiments/external_sources/chemistry/coupled_transport_withheld_targets_v1.json"
TARGET_HASH = "sha256:3c6d3f6b996b65ac85f9bbfee83873abf612f1f9be0ac8a550d05cc1946cc1f7"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2015-60-3621-3630.json", "sha256:5d7f67da2061ee82575290141699c397b5facb268fb3b4b77ac9cafb48e9d825"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2015-60-3621-3630.html", "sha256:d05c63f3c913fcaa5c4f5f5876e36fe291946dd4810988383b7c7b8b388896a3"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2006-51-680-685.json", "sha256:f568315d506b1cb9ed431fcab4b6be04e4caf413abd5e8b35940752c551a5009"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2006-51-680-685.html", "sha256:cd3b86ca9e25daac23451b920f6fc6875ba015ca4b2bb375ab7ba7c57ea26212"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2014-59-757-763.json", "sha256:7dd144b02f0d65101b10d0a839f29b12c2b5c2952b19df2193c600e080752d8d"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2014-59-757-763.html", "sha256:0fce1b7620916bdeb88e5272576a44c3beb9ff3c93e28980ff5e707f10300e5b"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-019 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 3
    or _primary.get("complete_dataset_count_across_sources") != 23
    or _primary.get("complete_all_property_point_count_across_sources") != 375
    or _primary.get("complete_target_count") != 232
    or _primary.get("carrier_pair_counts") != {"mass-heat": 22, "mass-charge": 146, "heat-charge": 64}
    or _identities.get("complete_target_count") != 232
    or _identities.get("carrier_pair_counts") != {"mass-heat": 22, "mass-charge": 146, "heat-charge": 64}
    or _identities.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 232
):
    raise ValueError("THERMO-019 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"{row['carrier_pair']} POMD {row['dataset_ordinal']} property {row['property_number']} point {row['source_point_ordinal']}",
        snapshot_path=PRIMARY_PATH, snapshot_hash=PRIMARY_HASH,
    ) for row in _identities["rows"]
)


COUPLED_TRANSPORT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019",
    title="Exact coupled mass, heat and charge transport law",
    statement=(
        "Coupled chemical transport is one counted adjacent-cell transition ledger carrying distinct mass, heat and charge "
        "packets with exact positive resources and held per-carrier orientations. Every pairwise observation is a projection "
        "of the complete triad, not an imported Onsager matrix or continuum flux equation. Chemistry owns composition, phase, "
        "condition and cross-effect provenance; physical energy and charge carriers remain explicit dependencies."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, identity, transition, orientation, resource, magnitude, prediction and extension forms; decide all 256 candidates only from admitted mass, energy, charge, adjacency, transition, conservation, exact-resource, composition, phase, EmptyOne and finite-successor laws.",
    grammar_boundary="Every finite coupled chemical event with complete component and phase identities, the ordered mass/heat/charge triad, counted adjacent cells, per-carrier packets, shared transitions, ticks, boundary and conditions. External testing preserves 232 direct pairwise response rows and all companion properties from three complete NIST sources.",
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="One complete chemical carrier, one phase, two adjacent cells, one positive packet for each of mass, heat and charge, one shared event, one tick, one boundary and one condition form the least coupled record.",
    induction_step="Appending one component, phase, condition, carrier event or measurement record preserves all earlier distinctions; common shared-event/tick replication preserves every exact pairwise response without refitting.",
    exclusions=(
        "no numerical zero; absent external condition coordinates are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported Onsager matrix, continuum gradient or flux equation, phenomenological cross coefficient or fitted transport law",
        "no interpolation, regression, selected substance/pair/property/phase/condition/method/dataset/row or target correction",
        "no substance, carrier pair, property, composition, phase, condition, method, value, uncertainty or target hash before prediction seal",
        "every complete source and companion property remains preserved; companions never become coupled measurements",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COUPLED-MASS-HEAT-CHARGE-TRANSPORT-019",
    expected_observation_label="complete-mass-heat-mass-charge-heat-charge-pairwise-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any component, phase, mass/heat/charge carrier, packet, shared event, cell, tick, boundary, condition "
        "or pairwise projection is erased; if adjacency or carrier conservation fails; if numerical-zero or signed proof value, "
        "Onsager matrix, continuum gradient/flux equation, phenomenological coefficient, fit, logarithm, interpolation, regression, "
        "selection or target correction enters; if target content opens before all 232 identities seal; if any selected response "
        "row, uncertainty, method, dataset, complete source or companion provenance is omitted; or if any target is tampered."
    ),
)
COUPLED_TRANSPORT_SPEC.validate()


__all__ = (
    "COUPLED_TRANSPORT_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES",
    "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
