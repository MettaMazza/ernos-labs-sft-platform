"""Registered KIN-006 law and complete experimental eight-channel branching surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.competing_channel_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-006-competing-channel-v1"
SPEC_PATH = "experiments/external_sources/chemistry/competing_channel_capture_spec_v1.json"
SPEC_HASH = "sha256:8ddf07528578576a12867f3c8ccf0d7690567bf59376ccbcde08576bb3731ca2"
ARTICLE_PATH = f"{SNAPSHOT_ROOT}/PMC11245511-full-text.xml"
ARTICLE_HASH = "sha256:ed762002b7f739d41f750e55f053fa2943498da7f01253880cab9f2d61525763"
SUPPLEMENT_ZIP_PATH = f"{SNAPSHOT_ROOT}/PMC11245511-supplementary-files.zip"
SUPPLEMENT_ZIP_HASH = "sha256:c889230356f4dfd83429a3ce31bef50c4e11dac91ecc6b7243421c83091c01ac"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/competing-channel-primary-records-v1.json"
PRIMARY_HASH = "sha256:c099cc768960967362267fbb1821156426374c3e5cda7b6ee91b1c664d24baf6"
IDENTITY_PATH = "experiments/external_sources/chemistry/competing_channel_target_identities_v1.json"
IDENTITY_HASH = "sha256:80fdbf5003e8b82398383c99ce4a127202affd21e6935f08514461e16d56b8b4"
TARGET_PATH = "experiments/external_sources/chemistry/competing_channel_withheld_targets_v1.json"
TARGET_HASH = "sha256:05f1926ad452280d03920c92cb49088784198d300883757f7439021db57315e7"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (ARTICLE_PATH, ARTICLE_HASH), (SUPPLEMENT_ZIP_PATH, SUPPLEMENT_ZIP_HASH),
    (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-006 registered source changed: {path}")
_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_product_channel_count") != 8
    or _primary.get("complete_supplementary_file_count") != 19
    or _primary.get("exact_experimental_branching_support_sum") != "1"
    or _primary.get("experimental_and_calculated_columns_separated") is not True
    or _identities.get("complete_registered_product_channel_count") != 8
    or _identities.get("all_branching_condition_spectrum_uncertainty_analysis_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 8
):
    raise ValueError("KIN-006 complete source boundary changed")
SUPPLEMENT_SOURCE_FILES = tuple(
    (row["snapshot_path"], row["snapshot_hash"]) for row in _primary["complete_supplementary_files"]
)
SUPPLEMENT_TEXT_FILES = tuple(
    (row["text_snapshot_path"], row["text_snapshot_hash"]) for row in _primary["supplement_pdf_records"]
)
if len(SUPPLEMENT_SOURCE_FILES) != 19 or len(SUPPLEMENT_TEXT_FILES) != 2:
    raise ValueError("KIN-006 supplement census changed")
for path, expected in SUPPLEMENT_SOURCE_FILES + SUPPLEMENT_TEXT_FILES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-006 supplementary source changed: {path}")
SOURCE_FILES = (
    (ARTICLE_PATH, ARTICLE_HASH), (SUPPLEMENT_ZIP_PATH, SUPPLEMENT_ZIP_HASH),
) + SUPPLEMENT_SOURCE_FILES + SUPPLEMENT_TEXT_FILES

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"DOI 10.1038/s42004-024-01239-7; complete primary branching table; source row {row['source_product_row']}; {row['product_channel_identity']}",
        snapshot_path=ARTICLE_PATH, snapshot_hash=ARTICLE_HASH,
    )
    for row in _identities["rows"]
)


COMPETING_CHANNEL_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    title="Exact complete-support competing-channel branching relation",
    statement=(
        "For one complete source-ordered set of registered product channels under a held reaction and condition, exact "
        "retained channel support forces the complete support as its exact sum and every branch share as channel support "
        "over that complete support. Structural EmptyOne rows remain held; no imported probability normalization, fitted "
        "branching equation or favorable-channel selection enters the relation."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, whole, relation, identity, absence, record, provenance and prediction "
        "forms; decide all 256 candidates only from admitted exact arithmetic, combinatorics, conditional information, "
        "reaction-mechanism, complete path, rate, activation and transition-boundary laws."
    ),
    grammar_boundary=(
        "Every finite complete source-ordered product-channel word with held reaction, condition, product and row identities, "
        "exact positive support or structural EmptyOne, at least two competing channels and one positive complete support. "
        "External testing preserves all eight experimental products, every uncertainty, the separate calculated column, the "
        "complete article, nineteen supplementary files and both supplement PDFs."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="Two retained registered product channels with positive complete support force the first exact branch partition of One.",
    induction_step="Appending the next complete source channel retains every prior identity and raw support while recomputing the uniquely forced complete-support shares without selection, fitting or correction.",
    exclusions=(
        "no numerical zero; absent reported support is structural EmptyOne and external zero glyphs remain provenance only",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported probability normalization, stochastic premise, branching equation or fitted branching ratio",
        "no renormalization, averaging, selected favorable channel, omitted weak/null/unresolved product or target correction",
        "no branch value, condition, uncertainty, spectrum, analysis result or target hash before all eight identities seal",
        "experimental and calculated columns remain distinct; Monte Carlo and reference-spectrum analysis remain disclosed provenance",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COMPETING-CHANNEL-BRANCHING-006",
    expected_observation_label="complete-experimental-eight-product-branching-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a registered channel, weak product, uncertainty, source row or adverse disclosure is erased; if "
        "shares do not reconstruct One exactly; if an imported normalization, fit, renormalization or selected channel enters; "
        "if experimental and calculated columns mix; if targets open before all eight identities seal; or if tampering passes."
    ),
)
COMPETING_CHANNEL_SPEC.validate()


__all__ = (
    "ARTICLE_HASH", "ARTICLE_PATH", "COMPETING_CHANNEL_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH",
    "PRIMARY_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "SUPPLEMENT_SOURCE_FILES", "SUPPLEMENT_TEXT_FILES",
    "SUPPLEMENT_ZIP_HASH", "SUPPLEMENT_ZIP_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
