"""Registered exact molecular magnetic-response law and blind NIST vector."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.magnetic_response_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_DIR = "experiments/external_sources/chemistry/snapshots/prop-012-magnetic-response-v1"
RESOLUTION_PATH = SNAPSHOT_DIR + "/nist-complete-constants-page-resolution-v1.json"
RESOLUTION_HASH = "sha256:b0acd2ba6511052e5522e78ecd97c852d14faf1508067c01eb7e56df6517c306"
DIATOMIC_HOLDINGS_PATH = SNAPSHOT_DIR + "/nist-diatomic-holdings.html"
DIATOMIC_HOLDINGS_HASH = "sha256:f55a09ac6a6d9a38cddc6b0e0872ec0ff53bed6dd7a4926e573543791761c432"
TRIATOMIC_HOLDINGS_PATH = SNAPSHOT_DIR + "/nist-triatomic-holdings.html"
TRIATOMIC_HOLDINGS_HASH = "sha256:1c6b6b595641fc4cdde8319fb7ce5d1572fe14d821bb6d0739d9f9e771655389"
HYDROCARBON_HOLDINGS_PATH = SNAPSHOT_DIR + "/nist-hydrocarbon-holdings.html"
HYDROCARBON_HOLDINGS_HASH = "sha256:7c825267dc82c88cac5a5b67fd391075b44c7d688cb89c5daea2e9606e38ceae"
DIATOMIC_PDF_PATH = SNAPSHOT_DIR + "/nist-jpcrd-microwave-spectral-tables-i-diatomic-1974.pdf"
DIATOMIC_PDF_HASH = "sha256:392f8941a7a83ca1d0cd035c15c79547e5f65544e0a216801bcafda3a8a41e01"
DIATOMIC_TEXT_PATH = SNAPSHOT_DIR + "/nist-jpcrd-microwave-spectral-tables-i-diatomic-1974-extracted.txt"
DIATOMIC_TEXT_HASH = "sha256:8586e532ab441dd5a882d6dd135ac01cff2cf78fc4f399aefa1c90fc9d819801"
PRIMARY_PATH = SNAPSHOT_DIR + "/magnetic-response-primary-records-v1.json"
PRIMARY_HASH = "sha256:af4fc413c056cd2caf8867b855f4ed948f2ba62a9576265c571f05dfd5a6d3d2"
IDENTITY_PATH = "experiments/external_sources/chemistry/magnetic_response_target_identities_v1.json"
IDENTITY_HASH = "sha256:aeaf62719a5c7699f9743722df5ffbafb7ffc3337e366f8321bc2a2dbe357259"
TARGET_PATH = "experiments/external_sources/chemistry/magnetic_response_withheld_targets_v1.json"
TARGET_HASH = "sha256:7ce119e64518c20376cdba0f1a8e0814ee76d48a6ee50acd562cfd4f44c8211d"


for _path, _hash in (
    (RESOLUTION_PATH, RESOLUTION_HASH), (DIATOMIC_HOLDINGS_PATH, DIATOMIC_HOLDINGS_HASH),
    (TRIATOMIC_HOLDINGS_PATH, TRIATOMIC_HOLDINGS_HASH), (HYDROCARBON_HOLDINGS_PATH, HYDROCARBON_HOLDINGS_HASH),
    (DIATOMIC_PDF_PATH, DIATOMIC_PDF_HASH), (DIATOMIC_TEXT_PATH, DIATOMIC_TEXT_HASH),
    (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-012 registered source changed: {_path}")


_primary = json.loads((ROOT / PRIMARY_PATH).read_text(encoding="utf-8"))
if (
    _primary.get("schema") != "sft-v3-nist-molecular-magnetic-response-primary-records/1"
    or _primary.get("complete_declared_molecule_count") != 267
    or _primary.get("complete_holding_group_count") != 215
    or _primary.get("complete_constants_page_count") != 215
    or _primary.get("retrieved_constants_page_count") != 94
    or _primary.get("official_linked_unavailable_page_count") != 121
    or _primary.get("diatomic_reference_pdf_target_count") != 22
    or _primary.get("complete_target_cell_count") != 174
    or _primary.get("source_value_present_count") != 136
    or _primary.get("source_value_absent_count") != 38
    or len(_primary.get("rows", ())) != 174
):
    raise ValueError("PROP-012 primary source boundary changed")
for _page in _primary["complete_constants_page_manifest"]:
    if _page["snapshot_path"] is not None and hash_file(ROOT / _page["snapshot_path"]) != _page["snapshot_hash"]:
        raise ValueError(f"PROP-012 constants snapshot changed: {_page['snapshot_path']}")


_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_forbidden = {"source_value_present", "source_value_inscription", "native_value", "external_orientation"}
if (
    _identity_document.get("schema") != "sft-v3-magnetic-response-identities/1"
    or _identity_document.get("all_magnetic_values_and_orientations_absent") is not True
    or _identity_document.get("complete_target_count") != 174
    or len(_identity_document.get("rows", ())) != 174
    or any(row.get("target_value_absent") is not True or _forbidden.intersection(row) for row in _identity_document["rows"])
):
    raise ValueError("PROP-012 identity registry is incomplete or contains a target")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=PRIMARY_PATH,
        snapshot_hash=PRIMARY_HASH,
    )
    for row in _identity_document["rows"]
)


MAGNETIC_RESPONSE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012",
    title="Exact molecular magnetic-response relation",
    statement=(
        "A complete molecular state retains spin, orbital and rotational support with two opposed orientations as "
        "held labels. Equal complementary support closes to structural EmptyOne; unmatched support retains a positive "
        "count and its generating orientation. Molecular moment is the exact positive response count per positive "
        "angular recurrence, and susceptibility is the exact positive induced response per positive applied-field act. "
        "All 174 NIST g-factor and magnetic-susceptibility cells seal without their values or orientations before the "
        "136 printed magnitudes and 38 blanks open. No fitted g-factor, continuum derivative or species coefficient enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, orientation, closure, moment, susceptibility, prediction, record and "
        "extension forms; decide all 256 candidates from admitted exact molecular-state, spin, field and response laws."
    ),
    grammar_boundary=(
        "Every generated finite molecular state with positive angular and field counts, plus all 267 molecules represented "
        "by the 215 NIST SRD 114/115/117 holding groups, every accessible triatomic/hydrocarbon constants page, every "
        "officially linked unavailable diatomic page, and the complete 162-page NIST diatomic reference-data table."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One retained unmatched orientation over one positive angular recurrence forces one positive moment class; one "
        "positive induced response over one positive field act forces one positive susceptibility class."
    ),
    induction_step=(
        "Appending one complementary pair preserves structural closure, while equal positive repetition of response and "
        "field acts preserves the exact susceptibility ratio for every finite depth."
    ),
    exclusions=(
        "no numerical zero; balanced support and blank source cells use structural EmptyOne",
        "no negative, irrational, imaginary, floating or continuum proof value",
        "no signed direction scalar; source signs remain external held orientations",
        "no continuum field derivative, differential susceptibility equation or imported magnetic potential",
        "no measured moment or susceptibility in law, grammar, candidate forcing or prediction",
        "no fitted g-factor, species coefficient, residual or selected molecule subset",
        "no nuclear quadrupole chi tensor misclassified as magnetic susceptibility",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-MAGNETIC-RESPONSE-012",
    expected_observation_label="exact-positive-held-orientation-moment-and-susceptibility-ratio-or-structural-EmptyOne",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if opposing directions require signed proof numbers; if equal support does not close structurally; "
        "if a retained molecular moment or susceptibility cannot be expressed as the declared exact positive count ratio; "
        "if equal repetition changes susceptibility; if any of the 174 registered cells, 136 printed values, 38 blanks, "
        "215 holding groups, 121 unavailable linked pages or 162 PDF pages is concealed; if a quadrupole chi is relabelled "
        "as susceptibility; if targets open before sealing; or if a continuum, fitted or species-specific rule enters."
    ),
)
MAGNETIC_RESPONSE_SPEC.validate()


__all__ = (
    "DIATOMIC_HOLDINGS_HASH", "DIATOMIC_HOLDINGS_PATH", "DIATOMIC_PDF_HASH", "DIATOMIC_PDF_PATH",
    "DIATOMIC_TEXT_HASH", "DIATOMIC_TEXT_PATH", "HYDROCARBON_HOLDINGS_HASH", "HYDROCARBON_HOLDINGS_PATH",
    "IDENTITY_HASH", "IDENTITY_PATH", "MAGNETIC_RESPONSE_SPEC", "PRIMARY_HASH", "PRIMARY_PATH",
    "RESOLUTION_HASH", "RESOLUTION_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
    "TRIATOMIC_HOLDINGS_HASH", "TRIATOMIC_HOLDINGS_PATH",
)
