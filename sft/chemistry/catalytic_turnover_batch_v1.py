"""Registered KIN-010 law and complete catalytic-turnover source surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.catalytic_turnover_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-010-catalytic-turnover-v1"
SPEC_PATH = "experiments/external_sources/chemistry/catalytic_turnover_capture_spec_v1.json"
SPEC_HASH = "sha256:e8874415767d9e257d94e860701dc839fdefd2761611a3a399b2885101e9a033"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:1a70201cef55873701d19bae35487868c55fa23852cc251f98df0afec6ec9ee9"
IDENTITY_PATH = "experiments/external_sources/chemistry/catalytic_turnover_target_identities_v1.json"
IDENTITY_HASH = "sha256:379360d1145dce4e4521525e60786e1ab39192f83a9b3cd9d95c13fdabdf7fb7"
TARGET_PATH = "experiments/external_sources/chemistry/catalytic_turnover_withheld_targets_v1.json"
TARGET_HASH = "sha256:b6d7b668b74bb6d4ab3e367791554c788c10946ebe6d6020e3de8362c4a9b5f7"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/catalytic-turnover-primary-records-v1.json"
PRIMARY_HASH = "sha256:d6e382f54f2339b739a09fe26fc77e2d5bec71c90a3cd373a1bdbd9b5dd3c889"

SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/article.html", "sha256:944550f9e96413533bf717b0ed6b346a6378258504f87c346cc0cc7f6340cb52"),
    (f"{SNAPSHOT_ROOT}/article.pdf", "sha256:5d2cabc360de5fc2f3a76210db2102684891918038dd21c1cb5c71f4b0aa5bd3"),
    (f"{SNAPSHOT_ROOT}/supplementary-information.pdf", "sha256:e3c068e905106c00f4ba3c8d8dbf9a02de2c1dbe55c71989d794cdac8c07bc8b"),
    (f"{SNAPSHOT_ROOT}/supplementary-data.zip", "sha256:47f3ef75b4ffdfd5290717b7cf2cb24b9b3ce10211b26409866561da08d68cbd"),
    (f"{SNAPSHOT_ROOT}/supplementary-video.mp4", "sha256:0831dc9a8580fdf090eedf71827e4af96c19cd963d130951af848ab004019d84"),
    (f"{SNAPSHOT_ROOT}/source-data-figure-1.zip", "sha256:baebd7004bc3955f896ce287fd201ee095dee2d66593b8c8d5cdaf348a63e3b3"),
    (f"{SNAPSHOT_ROOT}/source-data-figure-2.zip", "sha256:897b1f44ce77fbbd9c203afd3a7d5e5122fcdeef04aa85fcc33e09d491f0ba4f"),
    (f"{SNAPSHOT_ROOT}/source-data-figure-3.zip", "sha256:fd2925229a50c0357b8c1e3ce9a93d85618813f7adc34d56db77fd2141466ea4"),
    (f"{SNAPSHOT_ROOT}/source-data-figure-4.zip", "sha256:211ba6008a322704d3ddf95c2498f35e584372af2a28fb6fae86b1895607b823"),
    (f"{SNAPSHOT_ROOT}/source-data-figure-6.zip", "sha256:d20b2dc673847428567518bc32a267fb991349186c40f5e811d30cc13fad47a6"),
    (f"{SNAPSHOT_ROOT}/zenodo-record-metadata.json", "sha256:7ca9fc552351d47848abe2a5ca5bffcc20107eb1185fa009e70aec8c8ba5f4ba"),
    (f"{SNAPSHOT_ROOT}/zenodo-complete-source-data.zip", "sha256:7818a239c5205c46447ff44d360ef0bc2238acf0a6465dc87db702f7c82a2c4f"),
)
SOURCE_HASH_BY_DOCUMENT = {Path(path).name: (path, expected) for path, expected in SOURCE_FILES}


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-010 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_target_count") != 497
    or _primary.get("complete_supplementary_page_count") != 106
    or _primary.get("complete_supplementary_movie_frame_count") != 1604
    or _primary.get("complete_archive_member_count") != 387
    or _primary.get("structural_cycle", {}).get("registered_state_count") != 5
    or _primary.get("structural_cycle", {}).get("separately_observed_conductance_state_count") != 4
    or _primary.get("structural_cycle", {}).get("entry_state_equals_return_state") is not True
    or len(_primary.get("complete_substituent_turnover_vector", {}).get("rows", ())) != 7
    or _primary.get("table_s2_and_table_s3_remain_separate_without_selection_or_averaging") is not True
    or _identities.get("complete_registered_target_count") != 497
    or _identities.get("target_values_or_hashes_present") is not False
    or len(_identities.get("rows", ())) != 497
):
    raise ValueError("KIN-010 complete source boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41565-021-00959-4; source-data DOI 10.5281/zenodo.4903414; "
            f"complete source record {row['source_record_ordinal']}; document {row['source_document_identity']}; "
            f"record {row['source_record_identity']}"
        ),
        snapshot_path=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][0],
        snapshot_hash=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][1],
    )
    for row in _identities["rows"]
)


CATALYTIC_TURNOVER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010",
    title="Exact catalytic turnover and cycle-frequency law",
    statement=(
        "A catalytic turnover is forced only when one complete ordered state-transition word carries the same held "
        "catalyst identity from its entry state through every intermediate and returns it to that exact entry state. "
        "The cycle frequency is the exact positive relation between counted complete return words and counted parts "
        "of one held observation interval. No turnover-frequency equation, continuum rate, Michaelis-Menten or "
        "steady-state premise, stochastic cycle weight or fitted catalyst efficiency is imported."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of catalyst, cycle, turnover, frequency, state-status, evidence-status, "
        "provenance and prediction forms; decide all 256 candidates only from admitted exact state-transition, "
        "complete-channel, sequential, parallel and reversible-graph laws."
    ),
    grammar_boundary=(
        "Every finite source-ordered family of complete catalytic cycles with one held catalyst identity, two or more "
        "distinct registered states, one exact transition between each adjacent pair and a final transition returning "
        "to entry, one exact held condition and retained observed, structural, favorable, adverse, control or unresolved "
        "status. External testing binds all 497 pre-registered source records: article landing and unavailable-PDF "
        "response, 106 supplementary pages, one 1,604-frame movie, Zenodo metadata and all 387 members of seven archives."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One complete state-transition word whose final edge returns the unchanged held catalyst to its entry state "
        "forces one turnover; one positive completed-cycle count and one positive interval-part count force their exact ratio."
    ),
    induction_step=(
        "Append the next complete catalyst-return cycle at the next positive source occurrence. Every prior state, "
        "transition, catalyst identity, condition, status, turnover and exact count relation remains unchanged while "
        "the completed-cycle count increases by one."
    ),
    exclusions=(
        "numerical zero", "negative proof quantity", "irrational quantity", "imaginary quantity", "continuum time",
        "imported catalytic rate equation", "turnover-frequency formula", "Michaelis-Menten premise", "steady-state premise",
        "stochastic cycle weight", "fitted catalyst efficiency", "selected cycle or intermediate", "selected condition",
        "selected row, page, frame or archive member", "omitted deactivation, adverse or unresolved record", "average",
        "interpolation", "renormalization", "target-derived correction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CATALYTIC-TURNOVER-CYCLE-FREQUENCY-010",
    expected_observation_label="complete-catalyst-return-and-turnover-cycle-frequency-source-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if catalyst identity differs anywhere in the cycle; if the last transition does not return to "
        "the exact entry state; if any state, transition, condition, status, TOF row, independent rate-table value, raw "
        "trace, page, movie, archive member or unavailable-PDF adverse record is omitted; if four observed conductance "
        "levels are substituted for the five-state structural cycle; if a rate equation, TOF formula, continuum, fit, "
        "steady-state or stochastic premise, selection, average, interpolation or target correction enters; if target "
        "content opens before all 497 identities and the consequence seal; or if either omission or broken-return tampering passes."
    ),
)
CATALYTIC_TURNOVER_SPEC.validate()


__all__ = (
    "CATALYTIC_TURNOVER_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "INVENTORY_HASH", "INVENTORY_PATH",
    "PRIMARY_HASH", "PRIMARY_PATH", "SNAPSHOT_ROOT", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH",
    "TARGET_PATH", "TARGET_REFERENCES",
)
