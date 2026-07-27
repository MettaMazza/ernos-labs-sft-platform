"""Registered KIN-005 law and complete measured H2/D2 boundary-signature surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.transition_boundary_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-005-transition-boundary-v1"
SPEC_PATH = "experiments/external_sources/chemistry/transition_boundary_capture_spec_v1.json"
SPEC_HASH = "sha256:b0f0bd0c2e044f7ffa8cd936cf44f2e6fef5215a1ffd5fde51009fa2181ea9b3"
ARTICLE_PATH = f"{SNAPSHOT_ROOT}/PMC4073644-full-text.xml"
ARTICLE_HASH = "sha256:c720f78b391fa130033271136ba5da57802027165fc0fa9180d758b8f22bb345"
SUPPLEMENT_ZIP_PATH = f"{SNAPSHOT_ROOT}/PMC4073644-supplementary-files.zip"
SUPPLEMENT_ZIP_HASH = "sha256:87d04d5ccf5a3f8f3579c188e349308ffd0e743473cd3c39dca56e13a0a747b3"
SUPPLEMENT_PDF_PATH = f"{SNAPSHOT_ROOT}/nn500703k_si_001.pdf"
SUPPLEMENT_PDF_HASH = "sha256:89aa70668159e758862f8bc656b26237053012b806b0a1dd53634de1efc089f3"
SUPPLEMENT_TEXT_PATH = f"{SNAPSHOT_ROOT}/nn500703k_si_001.txt"
SUPPLEMENT_TEXT_HASH = "sha256:10700936f73d5dfb785bf4c154efec5320482bf4e081e4a43a33ae9bd45e023d"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/transition-boundary-primary-records-v1.json"
PRIMARY_HASH = "sha256:49d32db171dc7b58496cf844dd322658eda8da613b73dfef5bef4c7b3c166a4f"
IDENTITY_PATH = "experiments/external_sources/chemistry/transition_boundary_target_identities_v1.json"
IDENTITY_HASH = "sha256:b19fb80b1f280d631741ffa1d4844e547bd05b457b18a8cd350fbc922ad6cfa0"
TARGET_PATH = "experiments/external_sources/chemistry/transition_boundary_withheld_targets_v1.json"
TARGET_HASH = "sha256:f009c1056a7e91b36c1700c0e0bc80f55f7210c30f68ebadfb9790ee1cb7cf5c"


for path, expected in (
    (SPEC_PATH, SPEC_HASH), (ARTICLE_PATH, ARTICLE_HASH), (SUPPLEMENT_ZIP_PATH, SUPPLEMENT_ZIP_HASH),
    (SUPPLEMENT_PDF_PATH, SUPPLEMENT_PDF_HASH), (SUPPLEMENT_TEXT_PATH, SUPPLEMENT_TEXT_HASH),
    (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-005 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_experimental_target_count") != 2
    or _primary.get("complete_supplementary_file_count") != 13
    or _primary.get("all_article_and_supplement_files_preserved") is not True
    or _primary.get("experimental_and_calculated_provenance_separated") is not True
    or _identities.get("complete_experimental_isotopologue_count") != 2
    or _identities.get("all_isotope_barrier_rate_temperature_exposure_uncertainty_caption_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 2
):
    raise ValueError("KIN-005 complete source boundary changed")

SUPPLEMENT_SOURCE_FILES = tuple(
    (row["snapshot_path"], row["snapshot_hash"])
    for row in _primary["complete_supplementary_files"]
)
if len(SUPPLEMENT_SOURCE_FILES) != 13 or len({path for path, _ in SUPPLEMENT_SOURCE_FILES}) != 13:
    raise ValueError("KIN-005 supplementary file census changed")
for path, expected in SUPPLEMENT_SOURCE_FILES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-005 supplementary source changed: {path}")

SOURCE_FILES = (
    (ARTICLE_PATH, ARTICLE_HASH), (SUPPLEMENT_ZIP_PATH, SUPPLEMENT_ZIP_HASH),
    (SUPPLEMENT_TEXT_PATH, SUPPLEMENT_TEXT_HASH),
) + SUPPLEMENT_SOURCE_FILES

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"],
        source_id=row["source_id"],
        source_locator=f"DOI 10.1021/nn500703k; {row['source_figure_identity']}; isotopologue {row['isotopologue_identity']}",
        snapshot_path=ARTICLE_PATH,
        snapshot_hash=ARTICLE_HASH,
    )
    for row in _identities["rows"]
)


TRANSITION_BOUNDARY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005",
    title="Finite transition-state-equivalent Fold path-boundary law",
    statement=(
        "A complete generated finite reaction path with held reaction, path and isotopologue identities and one unique "
        "greatest exact positive support forces a transition-state-equivalent boundary carrier as the exact entry, boundary "
        "and exit partition. External signed barrier inscriptions remain provenance only and translate to positive magnitude "
        "plus held orientation; no saddle-point continuum or conventional kinetic-isotope equation enters the law."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, identity, location, partition, orientation, observation, provenance and "
        "prediction forms; decide all 256 candidates only from admitted exact arithmetic, finite path, state-transition, "
        "order, retained-information, reaction-mechanism, temperature-dependence and activation-boundary laws."
    ),
    grammar_boundary=(
        "Every finite generated reaction path with held reaction/path/isotopologue identities, structural EmptyOne or exact "
        "positive supports, and one unique greatest support. External testing preserves the complete predeclared primary "
        "article and supplement, both measured H2/D2 signatures, all thirteen supplementary files, and all disclosed "
        "calculated/fitted records as separately classified provenance."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One complete finite path with one unique greatest exact positive state forces one entry-boundary-exit carrier.",
    induction_step="Appending one complete source-bound path preserves every prior path, boundary, isotope identity, measurement and adverse provenance record without reselection, fitting or correction.",
    exclusions=(
        "no numerical zero; structural absence is EmptyOne and external zero glyphs remain provenance only",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported transition-state geometry, saddle-point continuum, conventional KIE equation or Arrhenius law",
        "no fitted barrier, prefactor, model adjustment, selected isotope/surface/condition/row or target-derived correction",
        "no isotope direction, barrier, uncertainty, temperature, exposure, coverage, curve or target hash before prediction seal",
        "calculated, path-integral, DFT and KMC records remain disclosed post-seal provenance and never measurement targets",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005",
    expected_observation_label="complete-measured-H2-D2-transition-boundary-signature-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the finite boundary is not unique, any generated state or held identity is erased, a signed source "
        "inscription becomes a negative SFT number, H2 or D2 is selected away, experimental and calculated provenance are "
        "mixed, any article/supplement record is omitted, targets open before both identities seal, or tampering is accepted."
    ),
)
TRANSITION_BOUNDARY_SPEC.validate()


__all__ = (
    "ARTICLE_HASH", "ARTICLE_PATH", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SOURCE_FILES",
    "SPEC_HASH", "SPEC_PATH", "SUPPLEMENT_PDF_HASH", "SUPPLEMENT_PDF_PATH", "SUPPLEMENT_SOURCE_FILES",
    "SUPPLEMENT_TEXT_HASH", "SUPPLEMENT_TEXT_PATH", "SUPPLEMENT_ZIP_HASH", "SUPPLEMENT_ZIP_PATH", "TARGET_HASH",
    "TARGET_PATH", "TARGET_REFERENCES", "TRANSITION_BOUNDARY_SPEC",
)
