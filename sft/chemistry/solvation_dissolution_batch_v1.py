"""Registered THERMO-015 law and complete solvation/dissolution surfaces."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.solvation_dissolution_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/thermo-015-solvation-dissolution-v1"
SPEC_PATH = "experiments/external_sources/chemistry/solvation_dissolution_capture_spec_v1.json"
SPEC_HASH = "sha256:448f6a2812536b41cc673acb3d86af85cd25a685e0d6e8aadc0dfbdd47a70541"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/solvation-dissolution-primary-records-v1.json"
PRIMARY_HASH = "sha256:95893551e6923d12303714282811daded3da3afa93fe64227af72af0e0367ba6"
IDENTITY_PATH = "experiments/external_sources/chemistry/solvation_dissolution_target_identities_v1.json"
IDENTITY_HASH = "sha256:e3acde8b1e6b14c71cb58f148ccb0bf21f4f1f22e6fdcc31f7d3da433266c6ae"
TARGET_PATH = "experiments/external_sources/chemistry/solvation_dissolution_withheld_targets_v1.json"
TARGET_HASH = "sha256:3fd55abbd9d6f1879342c0ce22222b5f90c1acc8f463c12852acdbe7f9f30e18"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/freesolv-0.52-database.txt", "sha256:2d13f095713bc39b85f85dd7b4e5483fbb12fc694bf253bb1d92a4c4d484f260"),
    (f"{SNAPSHOT_ROOT}/freesolv-0.52-commit.html", "sha256:a4e2d8de18da1729dcb3cfce2abb11791874e12d379d5a9b913215e089b1aad7"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2016-61-1470-1476.json", "sha256:2a6dc195e56cd2696492c513554da45a98a288b804a57ca5441ef0db66471c77"),
    (f"{SNAPSHOT_ROOT}/nist-trc-thermoml-jced-2016-61-1470-1476.html", "sha256:607faf853da6b4d1f21b84f2c08598391f8ed9ff53fee4616d7db5249e686e3b"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"THERMO-015 registered source changed: {path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 2
    or _primary.get("complete_target_count") != 799
    or _primary.get("source_class_counts") != {"solvation": 642, "dissolution": 157}
    or _primary.get("all_642_FreeSolv_and_157_direct_NIST_rows_preserved") is not True
    or _identities.get("complete_target_count") != 799
    or _identities.get("source_class_counts") != {"solvation": 642, "dissolution": 157}
    or _identities.get("all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 799
):
    raise ValueError("THERMO-015 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"FreeSolv row {row['source_row_ordinal']}"
            if row["source_class"] == "solvation"
            else f"POMD {row['dataset_ordinal']} point {row['source_point_ordinal']}"
        ),
        snapshot_path=PRIMARY_PATH, snapshot_hash=PRIMARY_HASH,
    )
    for row in _identities["rows"]
)


SOLVATION_DISSOLUTION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-SOLVATION-DISSOLUTION-FREE-ORDER-015",
    title="Exact solvation and dissolution free-order law",
    statement=(
        "Solvation and dissolution are exact state-transfer relations whose carrier retains the solute, every solvent, "
        "the distinct source and destination states, and the condition. Free order is represented by a held state "
        "orientation plus exact positive magnitude, never a signed SFT value; solubility is exact positive condition-bound "
        "composition capacity. No force field, continuum solvent, partition or activity fit, solubility-product equation, "
        "logarithm, correlation, regression or fitted parameter enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, identity, state, condition, order, absence, prediction and extension "
        "forms; decide all 256 candidates only from admitted Fold identity, exact state transition, exact order, "
        "solution recurrence, EmptyOne and finite-successor laws."
    ),
    grammar_boundary=(
        "Every finite solvation or dissolution record with one held solute, one or more distinct held solvents, distinct "
        "source and destination states, an exact condition or structural reference absence, and a held order/capacity. "
        "External testing preserves all 642 FreeSolv experimental rows and all 157 direct NIST ThermoML solubility rows."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One solute, one distinct solvent, one source state, one destination state and one exact condition or structural "
        "reference absence form the least complete transfer carrier."
    ),
    induction_step=(
        "Appending a complete record or a further distinct held solvent preserves the finite carrier; common exact support "
        "replication preserves its state relation without refitting."
    ),
    exclusions=(
        "no numerical zero; absent condition or coincident separation is structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported force field, continuum-solvent model, partition coefficient, activity-coefficient fit or solubility-product equation",
        "no correlation, interpolation, regression, fitted parameter, selected compound/solvent/state/condition/row or target correction",
        "no compound, solute, solvent, state, condition, value, uncertainty, reference or target hash before prediction seal",
        "every source row and companion field remains preserved; calculated and correlated companions are never measurements",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-SOLVATION-DISSOLUTION-FREE-ORDER-015",
    expected_observation_label="complete-solvation-dissolution-free-order-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any solute, solvent, source state, destination state or condition is erased; if a signed or "
        "numerical-zero SFT proof value enters; if any force field, continuum-solvent model, partition/activity fit, "
        "solubility-product equation, logarithm, correlation, regression, selection or target correction enters; if target "
        "content opens before all 799 identities seal; if any of 642 FreeSolv or 157 direct NIST rows or their complete "
        "source provenance is omitted; if calculated/correlated companions are counted as measurements; or if any measured "
        "value, orientation, condition or uncertainty is tampered."
    ),
)
SOLVATION_DISSOLUTION_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOLVATION_DISSOLUTION_SPEC",
    "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
