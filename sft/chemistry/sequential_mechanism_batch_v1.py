"""Registered KIN-007 law and complete time-resolved intermediate evidence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.sequential_mechanism_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-007-sequential-mechanism-v1"
SPEC_PATH = "experiments/external_sources/chemistry/sequential_mechanism_capture_spec_v1.json"
SPEC_HASH = "sha256:63c2480e05d202d88cfec0268e53d8160cd727a6bee88bd8304f37cd74989f3b"
IDENTITY_PATH = "experiments/external_sources/chemistry/sequential_mechanism_target_identities_v1.json"
IDENTITY_HASH = "sha256:0022b0988832e714876f66ad53c6dc5d4f5324866be0ebfdc59f98e14dae5872"
TARGET_PATH = "experiments/external_sources/chemistry/sequential_mechanism_withheld_targets_v1.json"
TARGET_HASH = "sha256:9b3e5d1319daf7571d7f95c839c17cc44d03e7663c82f0a404aa564e44d24e33"
ARTICLE_PATH = f"{SNAPSHOT_ROOT}/PMC11217357-full-text.xml"
ARTICLE_HASH = "sha256:214ac0642f5f59ed2e8a6e8944e957715facbec55d824a6c22f688767ec11952"
SUPPLEMENT_ZIP_PATH = f"{SNAPSHOT_ROOT}/PMC11217357-supplementary-files.zip"
SUPPLEMENT_ZIP_HASH = "sha256:b8c96995e08632587a626e02b3cdcc92e3b71121307b2daa77a3b4e92caad044"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/sequential-mechanism-primary-records-v1.json"
PRIMARY_HASH = "sha256:66bca327c4ef641d83b160a29692cc8bb60dfbcb0f3dcf88930c1ef013f90211"
CXIDB_PATH = f"{SNAPSHOT_ROOT}/cxidb-221-custody-record-v1.json"
CXIDB_HASH = "sha256:424dcf3f9b642a7b573e2be5339ac1c7e139fc0d32f01cf6b95e07bafb82362a"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    (ARTICLE_PATH, ARTICLE_HASH), (SUPPLEMENT_ZIP_PATH, SUPPLEMENT_ZIP_HASH),
    (PRIMARY_PATH, PRIMARY_HASH), (CXIDB_PATH, CXIDB_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-007 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_target_count") != 17
    or _primary.get("complete_supplementary_file_count") != 13
    or _primary.get("complete_pdb_deposit_count") != 5
    or _primary.get("complete_late_unresolved_state_count") != 2
    or _primary.get("complete_power_titration_column_count") != 7
    or _primary.get("complete_favorable_adverse_unresolved_control_count") != 3
    or _primary.get("experimental_deposited_calculated_and_unresolved_provenance_separated") is not True
    or _identities.get("complete_registered_target_count") != 17
    or _identities.get("all_time_power_coordinate_occupancy_density_resolution_statistic_intermediate_assignment_target_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 17
):
    raise ValueError("KIN-007 complete source boundary changed")

SUPPLEMENT_SOURCE_FILES = tuple(
    (row["snapshot_path"], row["snapshot_hash"]) for row in _primary["complete_supplementary_files"]
)
SUPPLEMENT_TEXT_FILES = tuple(
    (row["text_snapshot_path"], row["text_snapshot_hash"]) for row in _primary["supplement_pdf_records"]
)
PDB_SOURCE_FILES = tuple(
    pair
    for row in _primary["complete_pdb_records"]
    for pair in (
        (row["cif_snapshot_path"], row["cif_snapshot_hash"]),
        (row["rcsb_entry_snapshot_path"], row["rcsb_entry_snapshot_hash"]),
    )
)
if len(SUPPLEMENT_SOURCE_FILES) != 13 or len(SUPPLEMENT_TEXT_FILES) != 3 or len(PDB_SOURCE_FILES) != 10:
    raise ValueError("KIN-007 complete source-file census changed")
for path, expected in SUPPLEMENT_SOURCE_FILES + SUPPLEMENT_TEXT_FILES + PDB_SOURCE_FILES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-007 source snapshot changed: {path}")

SOURCE_FILES = (
    (ARTICLE_PATH, ARTICLE_HASH), (SUPPLEMENT_ZIP_PATH, SUPPLEMENT_ZIP_HASH), (CXIDB_PATH, CXIDB_HASH),
) + SUPPLEMENT_SOURCE_FILES + SUPPLEMENT_TEXT_FILES + PDB_SOURCE_FILES

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41467-024-49814-9; complete registered source record {row['source_row']}; "
            f"class {row['source_record_class']}; PDB identity {row['pdb_identity']}"
        ),
        snapshot_path=ARTICLE_PATH, snapshot_hash=ARTICLE_HASH,
    )
    for row in _identities["rows"]
)


SEQUENTIAL_MECHANISM_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007",
    title="Exact complete-state sequential mechanism composition law",
    statement=(
        "A complete finite mechanism is the exact ordered word of every retained state occurrence and every elementary "
        "transition occurrence whose exit and entry boundaries meet. Composition retains the initial state, terminal state, "
        "every intermediate, condition boundary and measured, adverse or unresolved status exactly once; no differential "
        "equation, exponential decay, fitted lifetime, steady-state premise or selected snapshot enters the law."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of support, adjacency, intermediate, composition, condition, status, provenance and "
        "prediction forms; decide all 256 candidates only from admitted exact state-transition, path, mechanism, rate, "
        "activation-boundary and complete-channel laws."
    ),
    grammar_boundary=(
        "Every finite complete ordered mechanism word with at least two registered state occurrences, exactly one registered "
        "elementary edge between each adjacent occurrence, exact positive ordinals, held conditions and held measured, adverse "
        "or unresolved status. External testing binds seventeen source categories: five deposited structures, two late unresolved "
        "states, seven complete power-titration columns and three favorable, adverse or unresolved controls, together with the "
        "complete article, thirteen supplementary files, three PDFs, five PDB records and CXIDB 221 custody metadata."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="Two retained state occurrences joined by one registered elementary transition force the first exact composition without an intermediate count value.",
    induction_step="Appending the next registered state and matching elementary edge retains every prior state, edge, condition, status and intermediate while making the former terminal state the next explicit intermediate.",
    exclusions=(
        "no numerical zero; absent observations or deposits are structural EmptyOne and external zero glyphs remain source inscriptions only",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported differential equation, exponential decay, fitted lifetime, rate law or steady-state assumption",
        "no interpolation, averaging, inferred missing intermediate, selected time, selected power, omitted parallel path or target correction",
        "no time, power, coordinate, occupancy, density, resolution, assignment, adverse result or target hash before all seventeen identities seal",
        "experimental deposits, calculated QM/MM trajectories, favorable controls, adverse controls and unresolved records remain distinct",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-SEQUENTIAL-MECHANISM-COMPOSITION-007",
    expected_observation_label="complete-time-resolved-intermediate-and-control-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any state, elementary edge, intermediate, condition, PDB record, power column, late record, favorable "
        "control, adverse contamination record or unresolved disclosure is omitted; if adjacent edge boundaries fail; if an "
        "imported evolution law, fit, interpolation, steady state or target correction enters; if experimental and calculated "
        "records mix; if targets open before all seventeen identities seal; or if tampering passes."
    ),
)
SEQUENTIAL_MECHANISM_SPEC.validate()


__all__ = (
    "ARTICLE_HASH", "ARTICLE_PATH", "CXIDB_HASH", "CXIDB_PATH", "IDENTITY_HASH", "IDENTITY_PATH",
    "PDB_SOURCE_FILES", "PRIMARY_HASH", "PRIMARY_PATH", "SEQUENTIAL_MECHANISM_SPEC", "SOURCE_FILES", "SPEC_HASH",
    "SPEC_PATH", "SUPPLEMENT_SOURCE_FILES", "SUPPLEMENT_TEXT_FILES", "SUPPLEMENT_ZIP_HASH", "SUPPLEMENT_ZIP_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
