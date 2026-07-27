"""Registered KIN-004 law and complete NIST experimental barrier surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.activation_barrier_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-004-activation-barrier-v1"
SPEC_PATH = "experiments/external_sources/chemistry/activation_barrier_capture_spec_v1.json"
SPEC_HASH = "sha256:c29aa3d64e8cb0802e91fba795f4c1f71b2ddf05de33b114c2e095ebce991e9f"
INDEX_PATH = f"{SNAPSHOT_ROOT}/nist-cccbdb-experimental-internal-rotation-barrier-index.html"
INDEX_HASH = "sha256:09b78e156784b7ec1a69a632582077c39690388b5d47a1d2a9528bd58483c6b1"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/activation-barrier-primary-records-v1.json"
PRIMARY_HASH = "sha256:2cbb1ba77b1dc672be235d8c45052499d4d12526fb467f8f85dcb62ddaf87f73"
IDENTITY_PATH = "experiments/external_sources/chemistry/activation_barrier_target_identities_v1.json"
IDENTITY_HASH = "sha256:d056cb5269d9879f0f6005d9ca75f6e44aad535e42961f4b9671ac3454c954a6"
TARGET_PATH = "experiments/external_sources/chemistry/activation_barrier_withheld_targets_v1.json"
TARGET_HASH = "sha256:341a1d016527aa9c4e044f87f74f5ae7efab5aedb898a6e7470388c705002fc4"


for path, expected in ((SPEC_PATH, SPEC_HASH), (INDEX_PATH, INDEX_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH)):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-004 registered source changed: {path}")
_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_index_species_count") != 41 or _primary.get("complete_detail_target_count") != 44
    or _primary.get("complete_path_state_count") != 782 or _primary.get("complete_unresolved_path_row_count") != 1
    or _primary.get("all_index_species_detail_pages_path_states_references_values_and_absences_preserved") is not True
    or _identities.get("complete_index_species_count") != 41 or _identities.get("complete_detail_target_count") != 44
    or _identities.get("all_species_path_state_identities_retained") is not True
    or _identities.get("all_barrier_unit_uncertainty_method_note_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 44
):
    raise ValueError("KIN-004 complete source boundary changed")


DETAIL_SOURCE_FILES = tuple(
    (row["snapshot_path"], row["snapshot_hash"])
    for row in _primary["complete_detail_pages"]
)
if len(DETAIL_SOURCE_FILES) != 41 or len({path for path, _ in DETAIL_SOURCE_FILES}) != 41:
    raise ValueError("KIN-004 complete detail-page census changed")
for path, expected in DETAIL_SOURCE_FILES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-004 detail source changed: {path}")
SOURCE_FILES = ((INDEX_PATH, INDEX_HASH),) + DETAIL_SOURCE_FILES


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"NIST SRD 101 experimental internal-rotation barrier; species {row['species_name']}; "
            f"CAS identity {row['casno_source_identity']}; torsion {row['torsion_index_source_identity']}"
        ),
        snapshot_path=next(
            page["snapshot_path"] for page in _primary["complete_detail_pages"]
            if page["source_detail_ordinal"] == row["source_detail_ordinal"]
        ),
        snapshot_hash=next(
            page["snapshot_hash"] for page in _primary["complete_detail_pages"]
            if page["source_detail_ordinal"] == row["source_detail_ordinal"]
        ),
    )
    for row in _identities["rows"]
)


ACTIVATION_BARRIER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
    title="Exact generated-path activation-barrier value relation",
    statement=(
        "For a complete generated reaction path with retained species, torsion and state identities, exact relative support "
        "and structural least-state EmptyOne force the activation barrier as the greatest positive path support under a held "
        "least-state-to-boundary orientation. Complete source profiles, references, absences and unresolved rows remain held."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of path, source, boundary, reference, minimality, identity, record and prediction forms; "
        "decide all 256 candidates only from admitted exact arithmetic, discrete path, order, state-energy, free-order, "
        "reaction-mechanism, structural activation-boundary, EmptyOne, record-retention and finite-successor laws."
    ),
    grammar_boundary=(
        "Every finite generated discrete path with held species/path/state identities, exact positive relative supports or "
        "structural EmptyOne, complete source provenance and one greatest positive boundary. External testing preserves the "
        "complete NIST SRD 101 experimental collection: 41 species, 44 torsion targets, 782 path states and one unresolved row."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One retained generated path with a structural least state and one positive crossing state forces the first barrier.",
    induction_step="Appending one complete source-bound path preserves every prior path, state, barrier, reference, absence and unresolved record without refitting or reselection.",
    exclusions=(
        "no numerical zero; external zero-energy glyphs and absent source coordinates become structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported transition-state or saddle-point continuum, Arrhenius law, fitted activation value or absolute energy origin",
        "no interpolation, regression, averaging, selected species/path/state/method/row or target-derived correction",
        "no barrier, unit, uncertainty, method, note, profile or target hash before prediction seal",
        "source citations and parameter disclosures remain post-seal provenance and never select the Fold law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004",
    expected_observation_label="complete-generated-path-experimental-barrier-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a species, path, state, source, barrier, structural least state, absence, unresolved row or adverse "
        "profile is erased; if an imported/fitted continuum form or prohibited value enters; if targets open before all "
        "forty-four identities seal; if any NIST index species/detail page is omitted; or if tampering is accepted."
    ),
)
ACTIVATION_BARRIER_SPEC.validate()


__all__ = (
    "ACTIVATION_BARRIER_SPEC", "DETAIL_SOURCE_FILES", "IDENTITY_HASH", "IDENTITY_PATH", "INDEX_HASH", "INDEX_PATH",
    "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH",
    "TARGET_REFERENCES",
)
