"""Registered KIN-002 law and complete concentration/rate table surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.concentration_dependence_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-002-concentration-dependence-v1"
SPEC_PATH = "experiments/external_sources/chemistry/concentration_dependence_capture_spec_v1.json"
SPEC_HASH = "sha256:d80a5a54d5191df6ef702a8818c49b5cd964140b9106da6516aa4043792cde0d"
PDF_PATH = f"{SNAPSHOT_ROOT}/c3cp54664k-primary-article.pdf"
PDF_HASH = "sha256:26b1d1696587cb669f5d8761c78046ad280d73ab7b0653b2dea39461e78f8acb"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/concentration-dependence-primary-records-v1.json"
PRIMARY_HASH = "sha256:de0d8d963114e2f74535fa5a08d3c31a77005d6e62c2adaa1ae65868ec2b4af9"
IDENTITY_PATH = "experiments/external_sources/chemistry/concentration_dependence_target_identities_v1.json"
IDENTITY_HASH = "sha256:d266ebece950622f6e9d7ec4a8ecac19c6c3e4ca0fa6c1b32b732ace88101f87"
TARGET_PATH = "experiments/external_sources/chemistry/concentration_dependence_withheld_targets_v1.json"
TARGET_HASH = "sha256:e174583b18628890cbcd36da6d95fc7ffb6dd1d91c4964c393b0f0095f0f84a4"
SOURCE_FILES = ((PDF_PATH, PDF_HASH),)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PDF_PATH, PDF_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-002 registered source changed: {path}")
_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_target_count") != 9 or _primary.get("complete_pdf_page_count") != 13
    or _primary.get("table_number") != "2" or _primary.get("all_table_2_rows_uncertainties_and_notes_preserved") is not True
    or _identities.get("complete_target_count") != 9
    or _identities.get("all_species_temperature_density_rate_uncertainty_method_note_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 9
):
    raise ValueError("KIN-002 complete source boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"DOI 10.1039/C3CP54664K Table 2 row {row['source_row_ordinal']}",
        snapshot_path=PDF_PATH, snapshot_hash=PDF_HASH,
    ) for row in _identities["rows"]
)


CONCENTRATION_DEPENDENCE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    title="Exact condition-bound concentration-dependence relation",
    statement=(
        "Chemical concentration dependence is the complete source-ordered relation between one held reactant's exact "
        "positive concentration support and exact positive elementary-transition rate response, retaining every condition, "
        "method, uncertainty and unfavorable row. The relation is the complete table; no power law, order or exponent is fitted."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of reactant, intervention, response, condition, completeness, relation, prediction and extension forms; decide all 256 candidates only from admitted exact arithmetic, intervention, observation, transition-rate, condition, record-retention, EmptyOne and finite-successor laws.",
    grammar_boundary="Every finite source-bound concentration/rate census for one registered reactant with exact positive concentration and rate supports and complete condition, method, uncertainty and row provenance. External testing preserves all nine rows, columns, uncertainties and notes in the complete primary-source Table 2.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One registered reactant, one exact positive concentration intervention, one exact positive elementary-rate response and one complete condition record form the least relation row.",
    induction_step="Appending one complete source row preserves every earlier concentration/rate pair and record without refitting, selection, averaging or inferred exponent.",
    exclusions=(
        "no numerical zero; absent external coordinates are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported mass-action or power law, conventional reaction order, fitted exponent/coefficient or continuum concentration derivative",
        "no interpolation, regression, averaging, selected favorable row or target-derived correction",
        "no species, temperature, density, rate, uncertainty, method, note or target hash before prediction seal",
        "source-disclosed fitted confidence intervals remain post-seal provenance and never select the Fold law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002",
    expected_observation_label="complete-condition-bound-concentration-rate-table-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if reactant, concentration, rate, condition, method, uncertainty, row or adverse response is erased; "
        "if a conventional/fitted law or prohibited value enters; if targets open before all nine identities seal; if any "
        "Table 2 row, column, uncertainty or note is omitted; or if tampering is accepted."
    ),
)
CONCENTRATION_DEPENDENCE_SPEC.validate()


__all__ = (
    "CONCENTRATION_DEPENDENCE_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PDF_HASH", "PDF_PATH", "PRIMARY_HASH",
    "PRIMARY_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
