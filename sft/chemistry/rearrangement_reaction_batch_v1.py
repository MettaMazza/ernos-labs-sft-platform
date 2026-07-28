"""Registered ORG-011 complete rearrangement law and evidence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.rearrangement_reaction_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011"
OBLIGATION_ID = "SFT-CHEM-OBL-ORG-011"

AUTHORITIES = (
    ("audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json", "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"),
    ("experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json", "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json", "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"),
    ("sft/chemistry/rearrangement_reaction_law_v1.py", "sha256:9e06ff8f7e720ef9efb6b79db6c501d8b01d04506744b84362c7b614c0d9ce3a"),
    ("experiments/external_sources/chemistry/org_011_target_identities_v1.json", "sha256:7fe944b94b3796a55124388d9ef4228df5e0aca1daf45d5c10c7b87ca1b54490"),
    ("experiments/external_sources/chemistry/org_011_target_identities_v2.json", "sha256:8ce3b0650526f9b3ce6fa66694e44e5771c41fe02447fd12b82b7270f364728d"),
    ("experiments/sealed_predictions/chemistry_org_011_rearrangement_reaction_pre_source_v1.json", "sha256:261ca2fed579e3a02906c04edf3c7e44fd5c752ecf6abfb3b24f08945e682b1c"),
    ("experiments/sealed_predictions/chemistry_org_011_rearrangement_reaction_pre_source_v2.json", "sha256:6808f37f9cf1faa657e5f5a5c65483f6b8585aa35bd0fd229774165ed1691c7c"),
    ("experiments/external_sources/chemistry/snapshots/org-011-europe-pmc-blind-v1/source-inventory-v1.json", "sha256:5613c4057adf9c3d7d7d09ebbd3d7e06bc24bf9ff8e575132c2c20b39569879b"),
    ("experiments/external_sources/chemistry/snapshots/org-011-europe-pmc-blind-v1/complete-postseal-analysis-v1.json", "sha256:ac22ce665f1b93617b07705518b499ef233c1a8e22122bd27a6768180dfbe031"),
    ("experiments/external_sources/chemistry/snapshots/org-011-claisen-blind-v2/source-inventory-v2.json", "sha256:7a66799333f95fe3ae35f060d2b7f1e81a01d4a41112d4dd159f6a513a66f11c"),
    ("experiments/external_sources/chemistry/snapshots/org-011-claisen-blind-v2/acs-figshare-s001-record-v2.json", "sha256:6bdf4f6b04d7521ec68674d32852ba0f743603382273ed4431b0251a6119655a"),
    ("experiments/external_sources/chemistry/snapshots/org-011-claisen-blind-v2/complete-postseal-analysis-v2.json", "sha256:2e200b570d0a407ef960fc02e0cd203d73f970af0c666fe5478f930385ef1a27"),
    ("experiments/external_sources/chemistry/snapshots/org-011-claisen-blind-v2/ja803370x_si_001.pdf", "sha256:c4720e6f02dfe930c2b0b45630e8b6a8f15b95108f0285fcfc35e30a0a0d9ca3"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-m03997.json", "sha256:55614e4895882e0d0405d675ffce95f09fffbf30f0f001e071b138655a3ccedd"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05194.html", "sha256:420b101c1f21ba8055e107379491a899067479c12002a6ae0707016eeadde0ba"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05196.json", "sha256:70da8c9927572e8c39fec4b69fb711b7ebdc5581b275dd310a46fd3a3551d17c"),
    ("tools/capture_chemistry_org_011_blind_sources_v1.py", "sha256:62a787e014d470255a0c8059ba35b427c710969aeccd9251cb8eb8676c0b925a"),
    ("tools/build_chemistry_org_011_external_v1.py", "sha256:21cddf23094fce442406603269fb277748e5c174ec65b5a06ce8bd3d19856d34"),
    ("tools/capture_chemistry_org_011_claisen_blind_v2.py", "sha256:7e993ee95eafe6a6b54375e3cf4b499310464f5a32e924e47ebfb7ab3b575103"),
    ("tools/build_chemistry_org_011_claisen_external_v2.py", "sha256:f2b87cd71e8e914ef725d2d1b2a676b61c3fcb6ef374061adba6c3d1d812817d"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-011 authority changed: {path}")

V1_ANALYSIS_PATH = AUTHORITIES[9][0]
ANALYSIS_PATH = AUTHORITIES[12][0]
INVENTORY_PATH = AUTHORITIES[10][0]
PDF_PATH = AUTHORITIES[13][0]
IDENTITY_PATH = AUTHORITIES[5][0]
PRESEAL_PATH = AUTHORITIES[7][0]

_preseal = json.loads((ROOT / PRESEAL_PATH).read_text(encoding="utf-8"))
_claimed = _preseal.pop("sealed_payload_hash", None)
if (
    _claimed != "sha256:a772e044a114e8cea5d8698148f46ffe8d6b4f0165eb976b3513eb2245bed36e"
    or sha256_identity(_preseal) != _claimed
    or _preseal.get("new_supplementary_pdf_pages_characterization_structures_formulas_or_spectra_opened_before_this_seal") is not False
    or _preseal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
):
    raise ValueError("ORG-011 prediction seal changed")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text(encoding="utf-8"))
_pairs = tuple(_analysis["explicit_claisen_source_product_pairs_in_source_order"])
if len(_pairs) != 8:
    raise ValueError("ORG-011 complete pair boundary changed")

TARGET_REFERENCES = (
    ChemistryTargetReference("SFT-CHEM-ORG-011-IUPAC-MOLECULAR", "IUPAC:M03997", "complete molecular-rearrangement record", AUTHORITIES[14][0], AUTHORITIES[14][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-011-IUPAC-REARRANGEMENT", "IUPAC:R05194", "complete rearrangement alias record", AUTHORITIES[15][0], AUTHORITIES[15][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-011-IUPAC-STAGE", "IUPAC:R05196", "complete rearrangement-stage record", AUTHORITIES[16][0], AUTHORITIES[16][1]),
    *(
        ChemistryTargetReference(
            f"SFT-CHEM-ORG-011-CLAISEN-PAIR-{row['ordinal']:02d}",
            f"ACS-FIGSHARE:10.1021/ja803370x.s001:PAIR:{row['ordinal']}",
            f"complete source page {row['source_characterization_page']} and product page {row['product_characterization_page']}",
            ANALYSIS_PATH,
            AUTHORITIES[12][1],
        )
        for row in _pairs
    ),
    ChemistryTargetReference("SFT-CHEM-ORG-011-OPTIMIZATION-03", "ACS-FIGSHARE:10.1021/ja803370x.s001:PAGE:3", "complete optimization and non-detection page", ANALYSIS_PATH, AUTHORITIES[12][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-011-OPTIMIZATION-04", "ACS-FIGSHARE:10.1021/ja803370x.s001:PAGE:4", "complete counterion and catalyst screen page", ANALYSIS_PATH, AUTHORITIES[12][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-011-TRANSITION-RELATION", "ACS-FIGSHARE:10.1021/ja803370x.s001:PAGE:37", "complete conventional transition-relation page", ANALYSIS_PATH, AUTHORITIES[12][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-011-FIRST-BLIND-SURFACE", "EUROPE-PMC:ORG-011:V1", "complete first unresolved blind surface preserved", V1_ANALYSIS_PATH, AUTHORITIES[9][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-011-COMPLETE-SUPPLEMENT", "ACS-FIGSHARE:10.1021/ja803370x.s001", "complete official 38-page supporting information", ANALYSIS_PATH, AUTHORITIES[12][1]),
)

REARRANGEMENT_REACTION_SPEC = EmpiricalChemistrySpec(
    claim_id=CLAIM_ID,
    title="Exact composition-retaining molecular rearrangement law",
    statement=(
        "A complete rearrangement retains every atom and held-support occurrence of one connected carrier while "
        "a positive finite family of held supports changes exact incidence; every nonoriginal incidence, direct or "
        "opened-reclosure path, degenerate trace and unchanged successor remains generated."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, atom, support, adjacency, path, alternative, observation and "
        "extension coordinates; decide all 256 forms only from admitted Fold conservation, graph and reversible laws."
    ),
    grammar_boundary=(
        "Every positive finite connected source/terminal carrier pair; every exact atom and held support; every "
        "nonoriginal target incidence; both direct and opened-reclosure paths; constitutionally degenerate traces; "
        "three complete IUPAC records; the preserved first blind surface; all 38 pages and all eight exact Claisen pairs."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One retained held support moves from its source atom pair to one different generated pair while every atom, "
        "support and unchanged incidence remains explicit and the reverse reconstruction returns exactly."
    ),
    induction_step=(
        "Every next positive finite moved-support family is generated by the same incidence rule; appending a fresh "
        "unchanged atom and support preserves the complete prior rearrangement and all decisions."
    ),
    exclusions=(
        "no native numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no reaction name mechanism yield selectivity temperature time mass formula or measured product selects the survivor",
        "all optimization, non-detection, signed stereochemical, spectral, adverse, absent and unresolved rows remain preserved",
        "the first blind incomplete-carrier surface remains unresolved and is never relabelled favorable",
        "conventional imaginary-frequency and signed decimal inscriptions remain downstream evidence only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-REARRANGEMENT-REACTION-FAMILY-011",
    expected_observation_label="complete-rearrangement-observable-and-preservation-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=ANALYSIS_PATH,
    falsification_condition=(
        "The claim fails if more than one generated form survives; any atom, held support, alternative incidence, "
        "path, degenerate trace or successor is omitted; any of eight endpoint inventories differs; any pair lacks "
        "a positive connectivity change; any page, optimization, non-detection, signed, spectral or first-surface row "
        "is omitted; or the external record is allowed to select the law."
    ),
)
REARRANGEMENT_REACTION_SPEC.validate()

__all__ = (
    "ANALYSIS_PATH",
    "AUTHORITIES",
    "CLAIM_ID",
    "IDENTITY_PATH",
    "INVENTORY_PATH",
    "OBLIGATION_ID",
    "PDF_PATH",
    "PRESEAL_PATH",
    "REARRANGEMENT_REACTION_SPEC",
    "TARGET_REFERENCES",
    "V1_ANALYSIS_PATH",
)
