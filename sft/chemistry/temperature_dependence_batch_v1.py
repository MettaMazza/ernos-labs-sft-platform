"""Registered KIN-003 law and complete primary temperature/rate surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.temperature_dependence_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-003-temperature-dependence-v1"
SPEC_PATH = "experiments/external_sources/chemistry/temperature_dependence_capture_spec_v1.json"
SPEC_HASH = "sha256:2298cbf26d1018c3bee8515dafb8302c42b6aa5bd92b57f2e21fa3aeec6df56d"
PDF_PATH = f"{SNAPSHOT_ROOT}/jp505790m-primary-accepted-manuscript.pdf"
PDF_HASH = "sha256:72514fc7892a6fb04a2b1ced7c8ec5c46f114cc76d1a88aeac09ca111f26817c"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/temperature-dependence-primary-records-v1.json"
PRIMARY_HASH = "sha256:5ddb819a17cd233f6c80bc2b1da03a50e30e5d7bc14c7b549ae852e6d8c8fb1c"
IDENTITY_PATH = "experiments/external_sources/chemistry/temperature_dependence_target_identities_v1.json"
IDENTITY_HASH = "sha256:f611fde45610cabb5e2558a1e3afd42e4127ec7ddb618aa87e6ccb7999b7e6e9"
TARGET_PATH = "experiments/external_sources/chemistry/temperature_dependence_withheld_targets_v1.json"
TARGET_HASH = "sha256:cfafdb9ede18d0cf9eea985ce7ec9d9e43da418f4bb288634b54d0836a54475b"
SOURCE_FILES = ((PDF_PATH, PDF_HASH),)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PDF_PATH, PDF_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-003 registered source changed: {path}")
_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_target_count") != 19 or _primary.get("complete_condition_row_count") != 14
    or _primary.get("complete_pdf_page_count") != 27 or _primary.get("table_number") != "1"
    or _primary.get("all_table_1_rows_columns_uncertainties_absences_and_note_preserved") is not True
    or _primary.get("fitted_table_2_excluded_by_prefetch_measured_table_rule") is not True
    or _identities.get("complete_target_count") != 19 or _identities.get("complete_condition_row_count") != 14
    or _identities.get("all_temperature_rate_density_uncertainty_method_note_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 19
):
    raise ValueError("KIN-003 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1021/jp505790m Table 1 condition row {row['source_condition_row_ordinal']} "
            f"registered reaction {row['reaction_key']}"
        ),
        snapshot_path=PDF_PATH, snapshot_hash=PDF_HASH,
    )
    for row in _identities["rows"]
)


TEMPERATURE_DEPENDENCE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003",
    title="Exact condition-bound temperature-dependence relation",
    statement=(
        "Chemical temperature dependence is the complete source-ordered relation between each held registered reaction's "
        "exact positive temperature support and exact positive elementary-transition rate response, retaining density, bath "
        "gas, method, uncertainty, repeated conditions, structural absences and unfavorable rows. The table is the relation; "
        "no Arrhenius, exponential, logarithmic, prefactor or activation fit enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of reaction, temperature, response, condition, completeness, relation, prediction and "
        "extension forms; decide all 256 candidates only from admitted exact arithmetic, temperature correspondence, "
        "finite-microstate, state-energy, free-order, transition-rate, record-retention, EmptyOne and finite-successor laws."
    ),
    grammar_boundary=(
        "Every finite source-bound temperature/rate census for registered reactions with exact positive temperature and rate "
        "supports and complete density, bath-gas, method, uncertainty, structural-absence and source-row provenance. External "
        "testing preserves all fourteen Table 1 condition rows and all nineteen measured reaction-rate targets."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One registered reaction, one exact positive temperature, one exact positive elementary-rate response and one complete condition record form the least relation row.",
    induction_step="Appending one complete measured target row preserves every earlier reaction/temperature/rate record without refitting, selection, averaging or inferred functional form.",
    exclusions=(
        "no numerical zero; absent source rate cells are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported Arrhenius, exponential or logarithmic law, fitted prefactor/activation value or continuum temperature derivative",
        "no interpolation, regression, averaging, selected reaction, temperature, condition, method, row or target-derived correction",
        "no temperature, density, rate, uncertainty, method, note or target hash before prediction seal",
        "source-disclosed confidence intervals remain post-seal measurement provenance and never select the Fold law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003",
    expected_observation_label="complete-two-reaction-condition-bound-temperature-rate-table-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if reaction, temperature, rate, density, bath gas, method, uncertainty, structural absence, source "
        "row or adverse response is erased; if an imported/fitted form or prohibited value enters; if targets open before all "
        "nineteen identities seal; if any measured Table 1 row or column is omitted; or if tampering is accepted."
    ),
)
TEMPERATURE_DEPENDENCE_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "PDF_HASH", "PDF_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES",
    "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES", "TEMPERATURE_DEPENDENCE_SPEC",
)
