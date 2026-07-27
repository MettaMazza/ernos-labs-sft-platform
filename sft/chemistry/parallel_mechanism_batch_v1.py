"""Registered KIN-008 law and complete parallel product-time evidence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.parallel_mechanism_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-008-parallel-mechanism-v1"
SPEC_PATH = "experiments/external_sources/chemistry/parallel_mechanism_capture_spec_v1.json"
SPEC_HASH = "sha256:f32b98d3cc4f02c02f01249b0f92ce799d1453ae04d1f8c9c107be6a509a6e89"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:a3c79878aeb0383a64d8bcf9242e9865c791c872ac50f59692348b978cead0d0"
IDENTITY_PATH = "experiments/external_sources/chemistry/parallel_mechanism_target_identities_v1.json"
IDENTITY_HASH = "sha256:08d42e20f3e4fa66ff46f98d046e160e5a7375b32f7d6d036debddfe3f1b90ca"
TARGET_PATH = "experiments/external_sources/chemistry/parallel_mechanism_withheld_targets_v1.json"
TARGET_HASH = "sha256:da263dc7147b66565c6737be47f492fb0c585c6048db078b17f643e037c78443"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/parallel-mechanism-primary-records-v1.json"
PRIMARY_HASH = "sha256:312655c78972e66b2f1bbe544fc005ce4a883fa6f08f43fdda3470f31db46ff0"
ARTICLE_HTML_PATH = f"{SNAPSHOT_ROOT}/article.html"
ARTICLE_HTML_HASH = "sha256:b3e792d3e9720e524850752cf907b8b76e74517207f7a7c8e725ec46dc2a1507"
ARTICLE_PDF_PATH = f"{SNAPSHOT_ROOT}/article.pdf"
ARTICLE_PDF_HASH = "sha256:e31b3a1101c73b22b8c2c3d516deeda00e317a39fd848aae07f01353577abfc1"
SUPPLEMENT_PATH = f"{SNAPSHOT_ROOT}/supplementary-information.pdf"
SUPPLEMENT_HASH = "sha256:9e891d68cebfe6034f265cd99780d91e5d1d916ebf68bae164b3aceb6e005653"
PEER_REVIEW_PATH = f"{SNAPSHOT_ROOT}/transparent-peer-review.pdf"
PEER_REVIEW_HASH = "sha256:391303943597d91ebede3be6aba6608046831237c3a04f78e2ea2ff3fcddab68"
WORKBOOK_PATH = f"{SNAPSHOT_ROOT}/source-data.xlsx"
WORKBOOK_HASH = "sha256:3f6dbcf377f4780aaec4f5a3c1431d4e758a775271d0a6d301bd74aca9087095"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (ARTICLE_HTML_PATH, ARTICLE_HTML_HASH),
    (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH), (SUPPLEMENT_PATH, SUPPLEMENT_HASH),
    (PEER_REVIEW_PATH, PEER_REVIEW_HASH), (WORKBOOK_PATH, WORKBOOK_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-008 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_data_worksheet_count") != 28
    or _primary.get("complete_registered_rectangular_cell_position_count") != 18158
    or _primary.get("parallel_path_count") != 3
    or _primary.get("complete_primary_parallel_product_time_observation_count") != 385
    or _identities.get("complete_registered_target_count") != 28
    or _identities.get("complete_registered_rectangular_cell_position_count") != 18158
    or _identities.get("target_values_or_hashes_present") is not False
    or len(_identities.get("rows", ())) != 28
):
    raise ValueError("KIN-008 complete source boundary changed")

SOURCE_FILES = (
    (ARTICLE_HTML_PATH, ARTICLE_HTML_HASH), (ARTICLE_PDF_PATH, ARTICLE_PDF_HASH),
    (SUPPLEMENT_PATH, SUPPLEMENT_HASH), (PEER_REVIEW_PATH, PEER_REVIEW_HASH),
    (WORKBOOK_PATH, WORKBOOK_HASH),
)

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41467-026-70199-4; complete source-data worksheet "
            f"{row['source_sheet_ordinal']}: {row['source_sheet_identity']}; rectangular surface "
            f"{row['declared_max_row']} by {row['declared_max_column']}"
        ),
        snapshot_path=WORKBOOK_PATH,
        snapshot_hash=WORKBOOK_HASH,
    )
    for row in _identities["rows"]
)


PARALLEL_MECHANISM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
    title="Exact complete-path parallel-mechanism composition law",
    statement=(
        "For one registered reaction with one retained initial state, a parallel mechanism is forced as the complete "
        "source-ordered family of every distinct sequential path word. Each path preserves all states, elementary edges, "
        "intermediates, shared boundaries, terminal occurrences, conditions and statuses; no stochastic premise, fitted "
        "path weight, imported parallel-rate equation or favorable-path selection enters the composition."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, origin, path, composition, sharing, status, provenance and prediction "
        "forms; decide all 256 candidates only from admitted Fold state-transition, graph, complete-channel and "
        "sequential-composition laws."
    ),
    grammar_boundary=(
        "Every finite complete source-ordered family of at least two distinct sequential mechanism words sharing one "
        "registered reaction and one exact initial state, with every path identity, source occurrence, state, elementary "
        "edge, intermediate, condition, status and terminal occurrence retained. External testing preserves the complete "
        "article, supplement, peer-review record, source workbook, all twenty-eight worksheets and all 18,158 registered "
        "rectangular cell positions."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Two distinct complete path words meeting one registered initial boundary force the first parallel family without "
        "a weight, probability or selected path."
    ),
    induction_step=(
        "Appending the next distinct registered path at the next positive source occurrence retains every prior path, "
        "state, edge, shared boundary, terminal occurrence and status exactly."
    ),
    exclusions=(
        "no numerical zero; source glyph 0 is external observed absence and native absence is structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported parallel-reaction equation, stochastic premise, fitted or free path weight or steady-state assumption",
        "no selected favorable path, product, time, condition, replicate, mean, method, worksheet or row",
        "no averaging away replicates, interpolation, inferred path, renormalization, omitted weak/adverse/unresolved/unassigned record or target correction",
        "no product-time value, cell label, formula result or target hash before all twenty-eight worksheet identities seal",
        "source formulas remain disclosed provenance and never become Fold proof parameters",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
    expected_observation_label="complete-twenty-eight-sheet-parallel-product-time-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any registered path, state, edge, shared boundary, terminal occurrence, product, time, "
        "replicate, formula, worksheet cell, weak/adverse/unresolved/unassigned record or source file is omitted; if paths "
        "do not meet one common source; if an imported stochastic/rate law, fit, average, interpolation, selection or target "
        "correction enters; if values open before all twenty-eight identities seal; or if tampering passes."
    ),
)
PARALLEL_MECHANISM_SPEC.validate()


__all__ = (
    "ARTICLE_HTML_HASH", "ARTICLE_HTML_PATH", "ARTICLE_PDF_HASH", "ARTICLE_PDF_PATH", "IDENTITY_HASH",
    "IDENTITY_PATH", "INVENTORY_HASH", "INVENTORY_PATH", "PARALLEL_MECHANISM_SPEC", "PEER_REVIEW_HASH",
    "PEER_REVIEW_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH",
    "SUPPLEMENT_HASH", "SUPPLEMENT_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
    "WORKBOOK_HASH", "WORKBOOK_PATH",
)
