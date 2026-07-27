"""Registered THERMO-013 law and complete NIST binary/ternary coexistence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.multicomponent_phase_diagram_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-013-multicomponent-phase-diagram-v1"
SPEC_PATH = "experiments/external_sources/chemistry/multicomponent_phase_diagram_capture_spec_v1.json"
SPEC_HASH = "sha256:d020adceefee9226b8424e92e732e3161623044fab299a4987f7bae5575fe8ad"
RAW_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jct-2012-47-260-266.json"
RAW_HASH = "sha256:1a000209fcb0ab63029b57473cfe5fa2e864c3c49ecb8bfb9c53423ba6378936"
LANDING_PATH = f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jct-2012-47-260-266.html"
LANDING_HASH = "sha256:6462874a85325da5020bd0e13b123a0a964b7da733e4ee3e1c4e474241d43a23"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/multicomponent-phase-diagram-primary-records-v1.json"
PRIMARY_HASH = "sha256:002d35382b2165490a46e0d49f655c21682a33828c7ced5d5019d2c4771aaf6e"
IDENTITY_PATH = "experiments/external_sources/chemistry/multicomponent_phase_diagram_target_identities_v1.json"
IDENTITY_HASH = "sha256:ac347149fc63857a5d0f411e57f1a95b89e7631ba603b6a6986b2639cbb1faf5"
TARGET_PATH = "experiments/external_sources/chemistry/multicomponent_phase_diagram_withheld_targets_v1.json"
TARGET_HASH = "sha256:536aed9eef5fc78044a12e70a92dbc3712ba4b93bfe50851731b442d8f5a5792"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (RAW_PATH, RAW_HASH), (LANDING_PATH, LANDING_HASH),
    (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-013 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_compound_count") != 3
    or _primary.get("complete_source_dataset_count") != 17
    or _primary.get("complete_source_point_count") != 187
    or _primary.get("complete_companion_pure_dataset_count") != 6
    or _primary.get("complete_binary_dataset_count") != 10
    or _primary.get("complete_binary_pair_count") != 5
    or _primary.get("complete_binary_coexistence_point_count") != 65
    or _primary.get("complete_ternary_dataset_count") != 1
    or _primary.get("complete_ternary_coexistence_point_count") != 51
    or _primary.get("complete_coexistence_target_count") != 116
    or _identities.get("complete_target_count") != 116
    or _identities.get("binary_target_count") != 65
    or _identities.get("ternary_target_count") != 51
    or _identities.get("all_compound_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 116
):
    raise ValueError("THERMO-013 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id="NIST-TRC-THERMOML-JCT-2012-47-260-266",
        source_locator=(
            f"POMD {','.join(str(value) for value in row['dataset_ordinals'])} "
            f"source point {row['source_point_ordinal']} ({row['dataset_class']})"
        ),
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


MULTICOMPONENT_PHASE_DIAGRAM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013",
    title="Finite exact multicomponent phase-diagram relation",
    statement=(
        "A binary or higher multicomponent two-phase diagram is the exact finite word of complete coexistence "
        "records. Each phase is a held component-coordinate word closing exactly to the One; both phases retain "
        "the same ordered component identities, every component preserves exact exchange-support balance, and "
        "the phase-rule relation leaves component-count degree support. External zero glyphs denote structural "
        "EmptyOne only. No lever rule, Gibbs triangle, convex hull, continuum, interpolation, regression or fit enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, composition, phase, balance, degree, absence, prediction and "
        "extension forms; decide all 256 candidates only from admitted exact composition, component exchange, "
        "phase-rule cancellation, EmptyOne and finite-word successor laws."
    ),
    grammar_boundary=(
        "Every finite positive word of binary-or-higher, two-distinct-phase coexistence points whose complete exact "
        "phase-coordinate words close to the One and whose componentwise exchange supports are equal. External "
        "testing preserves all five binary dataset pairs and 65 points, the complete 51-point ternary dataset, all "
        "six companion pure datasets and the complete 17-dataset, 187-point parent source."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Two held components, two distinct exact phase words closing to the One, equal componentwise exchange "
        "supports and one complete positive environment form the least multicomponent coexistence record."
    ),
    induction_step=(
        "Appending any further complete exchange-balanced coexistence record preserves the exact finite diagram; "
        "common positive replication of every paired component exchange support preserves balance at every depth."
    ),
    exclusions=(
        "no numerical zero; source zero glyphs translate only to structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported lever rule, tie-line equation, Gibbs triangle, convex hull or equation of state",
        "no continuum phase diagram, interpolation, regression, fitted interaction parameter or target-derived correction",
        "no compound, phase, temperature, pressure, composition, uncertainty or target hash before prediction seal",
        "no selected system, dataset, phase, point, azeotropic region or favorable diagram segment",
        "every source decimal remains a post-seal external inscription and the complete source remains preserved",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013",
    expected_observation_label="complete-finite-binary-and-ternary-coexistence-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if either phase loses a component or does not close exactly to the One; if phase identities "
        "are not distinct; if componentwise exchange support is unbalanced; if two-phase degree support is not the "
        "component count; if an external zero becomes a number rather than EmptyOne; if any imported geometric or "
        "continuum phase construction, equation of state, interpolation, regression, fit, selection or target-derived "
        "correction enters; if targets open before all 116 identities seal; if any of five binary pairs, 65 binary "
        "points, 51 ternary points, six companion datasets, uncertainties, methods, provenance or the complete "
        "17-dataset 187-point source is omitted; or if any measured coordinate is tampered."
    ),
)
MULTICOMPONENT_PHASE_DIAGRAM_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "LANDING_HASH", "LANDING_PATH",
    "MULTICOMPONENT_PHASE_DIAGRAM_SPEC", "PRIMARY_HASH", "PRIMARY_PATH", "RAW_HASH", "RAW_PATH",
    "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
