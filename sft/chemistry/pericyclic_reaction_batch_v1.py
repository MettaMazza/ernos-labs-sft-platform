"""Registered ORG-012 complete cyclic-transition law and evidence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.pericyclic_reaction_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012"
OBLIGATION_ID = "SFT-CHEM-OBL-ORG-012"

AUTHORITIES = (
    ("audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json", "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"),
    ("experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json", "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"),
    ("sft/chemistry/pericyclic_reaction_law_v1.py", "sha256:62c3a99545ce9be8c19c1d9eab69b16dad23357818850ab60d4e90f8ad0dd004"),
    ("experiments/external_sources/chemistry/org_012_target_identities_v1.json", "sha256:28bb4368b39d7249ad5a561bb97e9f96674036fcc433194f4b07d1bdba1d1afa"),
    ("experiments/sealed_predictions/chemistry_org_012_pericyclic_reaction_pre_source_v1.json", "sha256:fdde5db01fad8cedbfea089099924d710d9a1a8d7e6d9954867d0e4f169aff6b"),
    ("experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/source-inventory-v1.json", "sha256:66d0b968d32a47fa48a58e6ce797e1a285b873f4c4011e50db49acf34f9a6f50"),
    ("experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/complete-postseal-analysis-v1.json", "sha256:93c98ac499a34a654e87e1e81fa3ae40d06a5ae8e0efc68ff5550951355b22a4"),
    ("experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/members/PMC8162770/SC-011-D0SC04553E.nxml", "sha256:7bd269a764fdd5ab7b9b83787c70b4c84313289bacb0153e8163d2024cb94312"),
    ("experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/members/PMC8162770/SC-011-D0SC04553E.pdf", "sha256:4cf2aa95787ab44d9dca1b806e0c7318a13d746d1e5a0da01f39a5f4748b48bf"),
    ("experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/members/PMC8162770/SC-011-D0SC04553E-s001.pdf", "sha256:26c5c09b6920c437538d0473b0acdd93da4050edf5e4becb1f8175cd87124fe6"),
    ("experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1/members/PMC8162770/SC-011-D0SC04553E-s002.cif", "sha256:cd2a848715bd1d513de5d93de0d313c457a940028d1fc3b88cb78094b286abb2"),
    ("tools/capture_chemistry_org_012_oa_package_v1.py", "sha256:5091a214e5db02f47f8a90545efcc5b406a376582dbc69c3c7a412621da7dfec"),
    ("tools/build_chemistry_org_012_external_v1.py", "sha256:b5e24d91a72bec56e109ba78e18aa9df712683c081d8570a6b79a2ddd8b853bf"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-p04491.json", "sha256:cb5be92166e5a42b37710bccdc101f56e15c96e9925b02b9dec71af43892c968"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-c01496.json", "sha256:d74d74ee41c355e2d1776788094a7d4ad725229fb56e1d76a787a8bdeaa19535"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-012 authority changed: {path}")

IDENTITY_PATH = AUTHORITIES[3][0]
PRESEAL_PATH = AUTHORITIES[4][0]
INVENTORY_PATH = AUTHORITIES[5][0]
ANALYSIS_PATH = AUTHORITIES[6][0]
NXML_PATH = AUTHORITIES[7][0]
ARTICLE_PDF_PATH = AUTHORITIES[8][0]
SUPPLEMENT_PDF_PATH = AUTHORITIES[9][0]
CIF_PATH = AUTHORITIES[10][0]

_preseal = json.loads((ROOT / PRESEAL_PATH).read_text(encoding="utf-8"))
_claimed = _preseal.pop("sealed_payload_hash", None)
if (
    _claimed != "sha256:8c0734c27d86bf7dad75a3fa4399742dbb09566c6d6e828faa59abeea636c8d2"
    or sha256_identity(_preseal) != _claimed
    or _preseal.get("official_oa_archive_downloaded_or_opened_before_this_seal") is not False
    or _preseal.get("exact_article_table_or_supplementary_rows_opened_before_this_seal") is not False
    or _preseal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
):
    raise ValueError("ORG-012 prediction seal changed")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text(encoding="utf-8"))
_rows = tuple(_analysis["primary_table_rows_in_source_order"])
if len(_rows) != 32 or tuple(row["ordinal"] for row in _rows) != tuple(range(1, 33)):
    raise ValueError("ORG-012 complete primary-row boundary changed")

TARGET_REFERENCES = (
    ChemistryTargetReference("SFT-CHEM-ORG-012-IUPAC-PERICYCLIC", "IUPAC:P04491", "complete pericyclic-reaction record", AUTHORITIES[13][0], AUTHORITIES[13][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-012-IUPAC-CYCLOADDITION", "IUPAC:C01496", "complete cycloaddition record", AUTHORITIES[14][0], AUTHORITIES[14][1]),
    *(
        ChemistryTargetReference(
            f"SFT-CHEM-ORG-012-PRIMARY-ROW-{row['ordinal']:02d}",
            f"PMC8162770:TABLE-1:ROW:{row['ordinal']}",
            "complete Table 1 row including conventional condition, yield, reported and absent ratio fields",
            ANALYSIS_PATH,
            AUTHORITIES[6][1],
        )
        for row in _rows
    ),
    ChemistryTargetReference("SFT-CHEM-ORG-012-COMPLETE-ARTICLE", "PMC8162770:ARTICLE", "complete 12-page article and XML", ARTICLE_PDF_PATH, AUTHORITIES[8][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-012-COMPLETE-SUPPLEMENT", "PMC8162770:SUPPLEMENT:S001", "complete 203-page supporting information", SUPPLEMENT_PDF_PATH, AUTHORITIES[9][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-012-COMPLETE-CIF", "PMC8162770:SUPPLEMENT:S002", "complete crystallographic information file", CIF_PATH, AUTHORITIES[10][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-012-COMPLETE-PACKAGE", "NCBI-OA:PMC8162770", "complete 44-member official open-access archive", INVENTORY_PATH, AUTHORITIES[5][1]),
)

PERICYCLIC_REACTION_SPEC = EmpiricalChemistrySpec(
    claim_id=CLAIM_ID,
    title="Exact cyclic-transition and relative-orientation law",
    statement=(
        "A pericyclic Fold transition retains the complete source and terminal carriers and every held support, "
        "changes a positive finite support family inside one generated closed cycle, and exhausts four joint face "
        "assignments into exactly two relative-orientation classes without selecting one from measured products."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, cycle, support, transition, phase, stereochemistry, observation "
        "and extension coordinates; decide all 256 forms only from admitted Fold conservation and composition laws."
    ),
    grammar_boundary=(
        "Every positive finite retained source/terminal carrier; every generated closed transition cycle; every moved "
        "held support; all four two-fibre face assignments; both global-complement classes; two complete IUPAC records; "
        "all 32 primary rows, 44 archive members, 12 article pages, 203 supplementary pages and the complete CIF."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One six-occurrence closed transition retains every atom and support, moves three exact support incidences, "
        "generates four face assignments and reconstructs exactly in reverse."
    ),
    induction_step=(
        "Appending one fresh unchanged atom and support preserves the complete prior closed cycle, moved-support family, "
        "face assignment product, relative classes and every candidate decision without an additional rule."
    ),
    exclusions=(
        "no native numerical zero; structural absence is EmptyOne and may be displayed as 0",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no orbital rule reaction name energy yield ratio temperature condition or measured product selects the survivor",
        "all four face assignments and both relative classes remain generated without ranking",
        "all favorable adverse equal absent unresolved computational and experimental rows remain preserved",
        "the title abstract and general article conclusion are disclosed as development-observed and never called blind",
        "conventional signed decimal zero energy ratio temperature time and yield inscriptions remain downstream evidence only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-PERICYCLIC-REACTION-FAMILY-012",
    expected_observation_label="complete-pericyclic-observable-and-preservation-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=ANALYSIS_PATH,
    falsification_condition=(
        "The claim fails if more than one generated form survives; any carrier, cycle edge, held support, face assignment, "
        "relative class or unchanged successor is omitted; any of 32 primary rows, 44 archive members, 12 article pages, "
        "203 supplementary pages, the CIF, favorable, adverse, equal, absent or unresolved row is omitted; the reported "
        "vector lacks representatives of both generated classes; or any external outcome selects the native law."
    ),
)
PERICYCLIC_REACTION_SPEC.validate()

__all__ = (
    "ANALYSIS_PATH", "ARTICLE_PDF_PATH", "AUTHORITIES", "CIF_PATH", "CLAIM_ID", "IDENTITY_PATH",
    "INVENTORY_PATH", "NXML_PATH", "OBLIGATION_ID", "PERICYCLIC_REACTION_SPEC", "PRESEAL_PATH",
    "SUPPLEMENT_PDF_PATH", "TARGET_REFERENCES",
)
