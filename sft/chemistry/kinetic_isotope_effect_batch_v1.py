"""Registered KIN-012 law and complete kinetic isotope-effect source surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.kinetic_isotope_effect_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-012-kinetic-isotope-effect-v1"
SPEC_PATH = "experiments/external_sources/chemistry/kinetic_isotope_effect_capture_spec_v1.json"
SPEC_HASH = "sha256:b534bf7f099b8b264cbf0da8a5bbb4516add619550e5cf7502eae30d867c8586"
INVENTORY_PATH = f"{SNAPSHOT_ROOT}/source-inventory-v1.json"
INVENTORY_HASH = "sha256:b9ad3fb9f3f553488f84547ff7f7d73a3994be497cae22d58fe57ff8b1d18deb"
IDENTITY_PATH = "experiments/external_sources/chemistry/kinetic_isotope_effect_target_identities_v1.json"
IDENTITY_HASH = "sha256:9c528afc1d5edfa3c07ca6efdc1c857367ae033fe2f0e8bdbc181500f9b3ef1b"
TARGET_PATH = "experiments/external_sources/chemistry/kinetic_isotope_effect_withheld_targets_v1.json"
TARGET_HASH = "sha256:3664a32c0ab683184648aa0bc3821f87351d065091f76e90511f35e1b1396e34"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/kinetic-isotope-effect-primary-records-v1.json"
PRIMARY_HASH = "sha256:b6acab11a3bd249b943b96c6d61b508527d0d96e410689d2d83b62c20de179f9"

SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/article.html", "sha256:70c4df3c39bbdcdd5b6552ae8f6df8858e7cdaa2b8b07341b86bc710585f6b88"),
    (f"{SNAPSHOT_ROOT}/article.pdf", "sha256:b99de8ff662d5ed440bc96c204154c6f4dffc64f46a1d4d878ae91046afa1f74"),
    (f"{SNAPSHOT_ROOT}/supplementary-information.pdf", "sha256:0dd4046a4a855eed85859cdaa3175bd669b2ee92097af0b153de81ae03b687af"),
    (f"{SNAPSHOT_ROOT}/reporting-summary.pdf", "sha256:ec5a457e495c9f4ea288550123ebb4ba2673f1e15e4b1a3aebd1337ecd25a5bd"),
    (f"{SNAPSHOT_ROOT}/source-data.xlsx", "sha256:9eec1e46a8ab599a9bc9a763a39f22accc3bd60da719a72cd85870b7b5fb703b"),
)
SOURCE_HASH_BY_DOCUMENT = {Path(path).name: (path, expected) for path, expected in SOURCE_FILES}

for path, expected in (
    (SPEC_PATH, SPEC_HASH), (INVENTORY_PATH, INVENTORY_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), *SOURCE_FILES,
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-012 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_registered_target_count") != 71
    or _primary.get("complete_pdf_page_count") != 47
    or _primary.get("complete_source_data_worksheet_count") != 23
    or _primary.get("complete_explicit_rate_ratio_vector_count") != 90
    or _primary.get("complete_source_data_nonempty_cell_count") != 923260
    or len(_primary.get("source_reported_direct_decay_KIE_external_inscriptions", ())) != 3
    or _primary.get("three_independent_experiments_retained_without_averaging") is not True
    or _identities.get("complete_registered_target_count") != 71
    or _identities.get("target_values_or_hashes_present") is not False
    or len(_identities.get("rows", ())) != 71
):
    raise ValueError("KIN-012 complete source boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=(
            f"DOI 10.1038/s41467-024-44753-x; complete source record {row['source_record_ordinal']}; "
            f"document {row['source_document_identity']}; record {row['source_record_identity']}"
        ),
        snapshot_path=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][0],
        snapshot_hash=SOURCE_HASH_BY_DOCUMENT[row["source_document_identity"]][1],
    )
    for row in _identities["rows"]
)

KINETIC_ISOTOPE_EFFECT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012",
    title="Exact kinetic isotope-effect relation",
    statement=(
        "For two distinct held isotopologue identities traversing the same complete reaction path under the same held "
        "condition, each event rate is independently forced as completed events per exact positive observation parts. "
        "Their ordered quotient is the exact kinetic isotope-effect relation; greater, lesser or equal direction remains "
        "a held label. No kinetic-isotope equation, numerical mass premise, mass-frequency law, continuum, fitted exponent "
        "or statistical weight is imported."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of identity, path, rate, relation, orientation, observation, provenance and prediction "
        "forms; decide all 256 candidates only from admitted exact isotope identity, state-transition, mechanism and rate laws."
    ),
    grammar_boundary=(
        "Every finite source-ordered family of complete ordered isotopologue pairs retaining two distinct held isotope "
        "identities on one identical reaction path and condition, two independently counted exact positive event rates, "
        "one exact positive quotient and every favorable, adverse, control or unresolved status. External testing binds all "
        "71 pre-registered records: article landing, 47 PDF pages and all 23 complete source-data worksheets containing "
        "923,260 nonempty cells, ninety explicit rate-ratio rows and three direct decay KIE inscriptions."
    ),
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base=(
        "One complete ordered pair of distinct held isotopologues on the same path and condition, with two exact positive "
        "counted rates, forces one exact positive ordered rate ratio and one held orientation."
    ),
    induction_step=(
        "Append the next complete isotopologue pair at the next positive source occurrence. Every prior identity, path, "
        "condition, exact rate, quotient, orientation and status remains unchanged."
    ),
    exclusions=(
        "numerical zero", "negative proof quantity", "irrational quantity", "imaginary quantity", "numerical isotope mass",
        "kinetic isotope-effect equation", "mass-frequency law", "transition-state premise", "continuum time",
        "fitted exponent", "statistical weight", "selected isotopologue, reaction or condition", "selected page, worksheet or row",
        "omitted replicate, adverse or unresolved record", "average", "digitization", "interpolation", "renormalization",
        "target-derived correction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-KINETIC-ISOTOPE-EFFECT-012",
    expected_observation_label="complete-isotopologue-rate-ratio-source-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if either isotope identity, any path role or condition is erased or differs between a pair; if "
        "either rate is not independently counted from exact positive events and observation parts; if an ordered quotient "
        "or its held orientation is altered; if any of the 71 source records, 47 pages, 23 worksheets, 923,260 nonempty cells, "
        "ninety explicit ratios, three decay KIEs, replicate, normal, inverse, near-equal, reviewer challenge or source "
        "limitation is omitted; if a KIE equation, numerical mass, mass-frequency law, continuum, fit, exponent, statistical "
        "weight, selection, averaging, digitization or target correction enters; if target content opens before all 71 "
        "identities and the consequence seal; or if omission or mismatched-path tampering passes."
    ),
)
KINETIC_ISOTOPE_EFFECT_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "INVENTORY_HASH", "INVENTORY_PATH", "KINETIC_ISOTOPE_EFFECT_SPEC",
    "PRIMARY_HASH", "PRIMARY_PATH", "SNAPSHOT_ROOT", "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH",
    "TARGET_PATH", "TARGET_REFERENCES",
)
