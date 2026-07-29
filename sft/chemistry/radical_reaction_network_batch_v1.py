"""Registered ORG-013 radical-network law and complete evidence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.radical_reaction_network_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "SFT-CHEM-RADICAL-REACTION-NETWORK-013"
OBLIGATION_ID = "SFT-CHEM-OBL-ORG-013"

AUTHORITIES = (
    ("audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json", "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"),
    ("experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json", "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"),
    ("sft/chemistry/radical_reaction_network_law_v1.py", "sha256:9d8fdb2822078e1543af07684b425d4234dff669d3963104efd19145db4c446d"),
    ("experiments/external_sources/chemistry/org_013_target_identities_v1.json", "sha256:8f8793cad5c1cbf5cc51594197c8f43d75dc2a7e54fc1ac2006389a240fe4044"),
    ("experiments/sealed_predictions/chemistry_org_013_radical_network_pre_source_v1.json", "sha256:d7ad9509321d415f106e1e94e870afd112c4d65c73de35a8e7dc15310c8690c6"),
    ("experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/source-inventory-v1.json", "sha256:b85c4bc4fefea490bf8270043971f60cede2d2aa5261292e2d61684b860f38b0"),
    ("experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/complete-postseal-analysis-v1.json", "sha256:c73c9c4365a75d0a62cf6ab55e316a44516af2d38de6dcbea924c8523f39f562"),
    ("experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/members/PMC11598545/polymers-16-03225.nxml", "sha256:ff27819a129bc340665ac31cf164046358d21a7cc874512e5c5b5a048f062211"),
    ("experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/members/PMC11598545/polymers-16-03225.pdf", "sha256:82623c2e65d4809f19833d9a3fb20b857106d05f518bf3d54ac1235d30d4bffc"),
    ("experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1/members/PMC11598545/polymers-16-03225-s001.zip", "sha256:fbcdd10d7fc012e8d67e1a81f1efd4701867c0af2ee18c8df6a4e810da3baa86"),
    ("tools/capture_chemistry_org_013_oa_package_v1.py", "sha256:1a0a47be0bb4e92ee4afd2bf23419ac1388c0772ac7c808a12e53c2f72b6a076"),
    ("tools/build_chemistry_org_013_external_v1.py", "sha256:9888057b06eff7144bcf9b88923a3dc9308c64b1bb5b0f0aa83807d5cffe89b5"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-c00960.json", "sha256:8c33e0c77b8fffca3a5a43e119dba22e4a610437311e3c5ecb7dfe66e4430659"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-i03042.json", "sha256:f5f9768597b01a6f40697f83d39ce55dd3852224fbc739cc3cc8e9f61b4dbfbc"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-t06274.json", "sha256:3186b083062fe1adac850b20060bb7bf1ab3e8dc49a314b55c3874408c9143cb"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-013 authority changed: {path}")

IDENTITY_PATH, PRESEAL_PATH, INVENTORY_PATH, ANALYSIS_PATH = (AUTHORITIES[index][0] for index in (3, 4, 5, 6))
NXML_PATH, ARTICLE_PDF_PATH, SUPPLEMENT_PATH = (AUTHORITIES[index][0] for index in (7, 8, 9))

_seal = json.loads((ROOT / PRESEAL_PATH).read_text())
_claimed = _seal.pop("sealed_payload_hash", None)
if (
    _claimed != "sha256:7b0568465f6f9762dea5fb4638d89635a6411dd2eafb2b17d4a9dd5af38d2d4a"
    or sha256_identity(_seal) != _claimed
    or _seal.get("official_oa_record_archive_or_members_opened_before_this_seal") is not False
    or _seal.get("exact_article_table_or_supplementary_rows_opened_before_this_seal") is not False
    or _seal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
):
    raise ValueError("ORG-013 prediction seal changed")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text())
_tables = tuple(_analysis["tables_in_source_order"])
if tuple(row["row_count"] for row in _tables) != (47, 12, 4, 4):
    raise ValueError("ORG-013 complete table boundary changed")
_rows = tuple((table["table"], ordinal, row) for table in _tables for ordinal, row in enumerate(table["rows_in_source_order"], 1))

TARGET_REFERENCES = (
    ChemistryTargetReference("SFT-CHEM-ORG-013-IUPAC-CHAIN", "IUPAC:C00960", "complete chain-reaction record", AUTHORITIES[12][0], AUTHORITIES[12][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-013-IUPAC-INITIATION", "IUPAC:I03042", "complete initiation record", AUTHORITIES[13][0], AUTHORITIES[13][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-013-IUPAC-TERMINATION", "IUPAC:T06274", "complete termination record", AUTHORITIES[14][0], AUTHORITIES[14][1]),
    *(
        ChemistryTargetReference(
            f"SFT-CHEM-ORG-013-TABLE-{table}-ROW-{ordinal:02d}",
            f"PMC11598545:TABLE:{table}:ROW:{ordinal}",
            "complete primary table row with every value, unit, condition, uncertainty, sign and absence",
            ANALYSIS_PATH,
            AUTHORITIES[6][1],
        )
        for table, ordinal, _ in _rows
    ),
    ChemistryTargetReference("SFT-CHEM-ORG-013-COMPLETE-ARTICLE", "PMC11598545:ARTICLE", "complete 24-page article and XML", ARTICLE_PDF_PATH, AUTHORITIES[8][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-013-COMPLETE-SUPPLEMENT", "PMC11598545:SUPPLEMENT:S001", "complete five-page supporting-information archive", SUPPLEMENT_PATH, AUTHORITIES[9][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-013-COMPLETE-PACKAGE", "NCBI-OA:PMC11598545", "complete 24-member official open-access archive", INVENTORY_PATH, AUTHORITIES[5][1]),
)

RADICAL_REACTION_NETWORK_SPEC = EmpiricalChemistrySpec(
    claim_id=CLAIM_ID,
    title="Exact initiation, propagation and termination network law",
    statement=(
        "A complete radical network retains two exact held support labels from a closed initiating pair through a "
        "positive finite contiguous propagation family and closes the same labels at termination, with active-site "
        "absence represented only by structural EmptyOne."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, support, initiation, propagation, recurrence, termination, observation and extension coordinates; decide all 256 forms only from admitted Fold laws.",
    grammar_boundary="Every complete finite carrier, two retained radical labels, exact pair opening, every positive finite propagation recurrence, exact pair closure, all three IUPAC records, all 67 article table rows, all 24 archive members and all 29 article/supplement pages.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One closed retained pair opens to two active sites, one active support and one monomer bond layer relocate, and the same two supports close together.",
    induction_step="Each next positive propagation step repeats one exact active-support and bond-layer relocation; appending an unchanged carrier preserves the entire prior trace without a new rule.",
    exclusions=(
        "no native numerical zero; inactive support is structural EmptyOne",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no radical dot reaction name rate energy temperature chain length or measured outcome selects the survivor",
        "all initiation propagation termination transfer signed adverse absent and unresolved rows remain preserved",
        "the article title abstract summary and 25-to-39 kJ mol-1 range are development-observed and never relabelled blind",
        "all conventional signs decimals rates energies temperatures concentrations uncertainties and units remain downstream evidence only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RADICAL-REACTION-NETWORK-013",
    expected_observation_label="complete-radical-network-observable-and-preservation-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=ANALYSIS_PATH,
    falsification_condition=(
        "The claim fails if more than one generated form survives; either held radical support is created, erased or "
        "renamed; initiation, positive propagation, termination or contiguous order is omitted; active absence is made "
        "numerical; any IUPAC record, archive member, one of 67 table rows, 29 pages, measured value, sign, unit, "
        "uncertainty, adverse or absent field is omitted; or an external outcome selects the native law."
    ),
)
RADICAL_REACTION_NETWORK_SPEC.validate()

__all__ = (
    "ANALYSIS_PATH", "ARTICLE_PDF_PATH", "AUTHORITIES", "CLAIM_ID", "IDENTITY_PATH", "INVENTORY_PATH",
    "NXML_PATH", "OBLIGATION_ID", "PRESEAL_PATH", "RADICAL_REACTION_NETWORK_SPEC", "SUPPLEMENT_PATH", "TARGET_REFERENCES",
)
