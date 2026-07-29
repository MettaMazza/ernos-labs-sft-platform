"""Registered ORG-014 selectivity law and complete distribution surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.selectivity_distribution_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "SFT-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014"
OBLIGATION_ID = "SFT-CHEM-OBL-ORG-014"
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/org-014-selectivity-distribution-v1/complete-postseal-product-distribution-v1.json"
PARQUET_PATH = "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9/ord_dataset-feaf1b793c6d408aaec1cac7cc3ceadc.parquet"
AUTHORITIES = (
    ("audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json", "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"),
    ("experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json", "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"),
    ("sft/chemistry/selectivity_distribution_law_v1.py", "sha256:e5e28a1f43e21871463da32615c0818947eec7988c8a242dde3684ea410117b8"),
    ("experiments/external_sources/chemistry/org_014_target_identities_v1.json", "sha256:40e157871d179786dd786c8427019541997c90ba3d3566755ce062abdbbf650a"),
    ("experiments/sealed_predictions/chemistry_org_014_selectivity_distribution_pre_source_v1.json", "sha256:e7d8309f8908cac4f9ab2d7588295a80877749f3a808662b7240fbd5aecef7b1"),
    (ANALYSIS_PATH, "sha256:3d3f2a4ea2a8eb3403ef65693a065c2886abbc888b2be4b65923e1947435d933"),
    (PARQUET_PATH, "sha256:ebefbe9aba687f182d4f068e94be0f7fd71d1189bdb2eff2aca6fedf4d522bf3"),
    ("tools/build_chemistry_org_014_external_v1.py", "sha256:83db565e96fd95d288d74cae7626a4fcf5b232a0f082e9428b9f4b40f95d588f"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-c01051.json", "sha256:a77907eddbf3fd523a249c275a4cd90844185c45617a230fe47ea30663033088"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05243.json", "sha256:9b50f87f8aa6e76effcfeeb5110baf0b31991b8b8059f8520ee7960358221aab"),
    ("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-s05991.json", "sha256:a54e5bace79d2add9152125a40d9e563196db36c3f8a8aaab7be46e9cdad713c"),
)
for path, expected in AUTHORITIES:
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-014 authority changed: {path}")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text())
if _analysis.get("complete_registered_reaction_row_count") != 130 or len(_analysis.get("reaction_rows_in_preregistered_order", ())) != 130:
    raise ValueError("ORG-014 complete reaction-row surface changed")

TARGET_REFERENCES = (
    ChemistryTargetReference("SFT-CHEM-ORG-014-IUPAC-CHEMO", "IUPAC-C01051", "complete current chemoselectivity definition", AUTHORITIES[8][0], AUTHORITIES[8][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-014-IUPAC-REGIO", "IUPAC-R05243", "complete current regioselectivity definition", AUTHORITIES[9][0], AUTHORITIES[9][1]),
    ChemistryTargetReference("SFT-CHEM-ORG-014-IUPAC-STEREO", "IUPAC-S05991", "complete current stereoselectivity definition", AUTHORITIES[10][0], AUTHORITIES[10][1]),
) + tuple(
    ChemistryTargetReference(
        f"SFT-CHEM-ORG-014-ORD-ROW-{ordinal:03d}",
        "ORD-FEAF1B793C6D408AAEC1CAC7CC3CEADC",
        f"preregistered complete row {ordinal} of 130, including every outcome, product, identifier and measurement",
        ANALYSIS_PATH,
        AUTHORITIES[5][1],
    )
    for ordinal in range(1, 131)
)

SELECTIVITY_DISTRIBUTION_SPEC = EmpiricalChemistrySpec(
    claim_id=CLAIM_ID,
    title="Fold chemo-, regio- and stereoselectivity with complete product distributions",
    statement=(
        "The complete positive-finite product support is forced before observation. Chemo-, regio- and stereo-"
        "selectivity are exact partitions of that support; every reported product and amount or structural absence "
        "is retained after sealing, with no major-product filter."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the Cartesian product of the eight registered binary structural decisions exactly once.",
    grammar_boundary="Eight dimensions exhaust carrier, three selectivity partitions, amount custody, complete observation, native arithmetic and extension.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One source with one positive-finite generated product support retains each exact partition and every reported row.",
    induction_step="Appending one fresh product identity preserves all prior products, classes and held amount records without a new rule.",
    exclusions=(
        "no numerical zero, negative, irrational, imaginary, continuum probability, fitted coefficient or random selector in the native law",
        "no named reaction, measured yield, major product or external product structure selects the generated support",
        "all conventional decimals, signs, units, values and absences remain downstream source records",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-SELECTIVITY-COMPLETE-DISTRIBUTION-014",
    expected_observation_label="complete-selectivity-distribution-observable-and-preservation-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=ANALYSIS_PATH,
    falsification_condition=(
        "The claim fails if more than one form survives; any generated product or selectivity partition is erased; "
        "a reported amount selects product support; any one of 130 preregistered reactions, 130 outcomes, 152 products, "
        "302 identifiers, 195 measurement records, adverse or absent row is omitted; a major-product filter is used; "
        "or external outcomes enter native candidate generation or elimination."
    ),
)
SELECTIVITY_DISTRIBUTION_SPEC.validate()

COMPLETENESS_CERTIFICATE = sha256_identity((
    CLAIM_ID, tuple(row.target_id for row in TARGET_REFERENCES), 130, 152, 302, 195,
    _analysis["complete_result_vector_sha256"], EXACT_RESULT,
))

__all__ = (
    "ANALYSIS_PATH", "AUTHORITIES", "CLAIM_ID", "COMPLETENESS_CERTIFICATE", "OBLIGATION_ID",
    "PARQUET_PATH", "SELECTIVITY_DISTRIBUTION_SPEC", "TARGET_REFERENCES",
)
