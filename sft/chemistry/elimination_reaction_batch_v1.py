"""Registered ORG-010 inverse-addition elimination law and complete evidence surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.elimination_reaction_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "SFT-CHEM-ELIMINATION-REACTION-FAMILY-010"
OBLIGATION_ID = "SFT-CHEM-OBL-ORG-010"

FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"

LAW_PATH = "sft/chemistry/elimination_reaction_law_v1.py"
LAW_HASH = "sha256:cf72f096c86839a5010293fad12d70851ff9b55cf972b65348deca2f6b87ca9e"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_010_target_identities_v1.json"
IDENTITY_HASH = "sha256:fffd58022997ba69d30e1cd940fc600465b39d9a7c4cfab993b1799c3302cefe"
PRESEAL_PATH = "experiments/sealed_predictions/chemistry_org_010_elimination_reaction_pre_source_v1.json"
PRESEAL_FILE_HASH = "sha256:13869cd3759eea606af331d1aa8468c77f3b1449c41c6c0ac52db757bd702239"
PRESEAL_PAYLOAD_HASH = "sha256:c0a9be98e698ea18317d3cf66f431f56c11e38f78d5bb835f4eb4562d9d08c39"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1/source-inventory-v1.json"
INVENTORY_HASH = "sha256:0d4204dfd4633dbc6ada89cd87cda76813c989f2444490547371d7aca64696de"
ANALYSIS_PATH = "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1/complete-postseal-analysis-v1.json"
ANALYSIS_HASH = "sha256:157144f86339efa5ddb583d860ef1fd444af6761c3080a82465367544735b89b"
IUPAC_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-e02038.json"
IUPAC_HASH = "sha256:99ec6c2aae4b034e06eb5bc91d11c2c3773aefc78819f6406c7efd35bf7ad075"
CAPTURE_TOOL_PATH = "tools/capture_chemistry_org_010_blind_sources_v1.py"
CAPTURE_TOOL_HASH = "sha256:e44b7fd29ebe44dbbedcce0010a029a645325520ab619a81c999719b082263b0"
ANALYSIS_TOOL_PATH = "tools/build_chemistry_org_010_external_v1.py"
ANALYSIS_TOOL_HASH = "sha256:41cd2d211f8ee3ab4b5baac104756db0e176bd979f3e4f73e918d5ca8a953184"

for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (PRESEAL_PATH, PRESEAL_FILE_HASH),
    (INVENTORY_PATH, INVENTORY_HASH),
    (ANALYSIS_PATH, ANALYSIS_HASH),
    (IUPAC_PATH, IUPAC_HASH),
    (CAPTURE_TOOL_PATH, CAPTURE_TOOL_HASH),
    (ANALYSIS_TOOL_PATH, ANALYSIS_TOOL_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-010 authority changed: {path}")

_preseal = json.loads((ROOT / PRESEAL_PATH).read_text(encoding="utf-8"))
_claimed_preseal_hash = _preseal.pop("sealed_payload_hash", None)
if (
    _claimed_preseal_hash != PRESEAL_PAYLOAD_HASH
    or sha256_identity(_preseal) != PRESEAL_PAYLOAD_HASH
    or _preseal.get("supplementary_archive_product_structures_yields_spectra_or_complete_page_contents_opened_before_this_seal") is not False
    or _preseal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
):
    raise ValueError("ORG-010 prediction seal changed")

_analysis = json.loads((ROOT / ANALYSIS_PATH).read_text(encoding="utf-8"))
_products = tuple(_analysis["characterized_product_rows_in_source_order"])
_unsuccessful = tuple(_analysis["unsuccessful_substrate_rows"])
_optimisation = tuple(_analysis["optimisation_tables"])
if len(_products) != 32 or len(_unsuccessful) != 5 or len(_optimisation) != 7:
    raise ValueError("ORG-010 complete external row boundary changed")

TARGET_REFERENCES = (
    ChemistryTargetReference(
        "SFT-CHEM-ORG-010-IUPAC-001",
        "IUPAC:E02038",
        "complete current elimination definition",
        IUPAC_PATH,
        IUPAC_HASH,
    ),
    *(
        ChemistryTargetReference(
            f"SFT-CHEM-ORG-010-PRODUCT-{row['product_code'].upper()}",
            f"RSC:D4SC01905A:{row['product_code']}",
            f"characterization page {row['characterization_start_page']}; observable unsaturation only",
            ANALYSIS_PATH,
            ANALYSIS_HASH,
        )
        for row in _products
    ),
    *(
        ChemistryTargetReference(
            f"SFT-CHEM-ORG-010-UNSUCCESSFUL-{row['ordinal']:02d}",
            f"RSC:D4SC01905A:UNSUCCESSFUL:{row['ordinal']}",
            "printed page 24 unsuccessful-substrate row retained without success filtering",
            ANALYSIS_PATH,
            ANALYSIS_HASH,
        )
        for row in _unsuccessful
    ),
    *(
        ChemistryTargetReference(
            f"SFT-CHEM-ORG-010-OPTIMISATION-{table['table']}",
            f"RSC:D4SC01905A:{table['table']}",
            f"complete printed optimization table on page {table['page']}",
            ANALYSIS_PATH,
            ANALYSIS_HASH,
        )
        for table in _optimisation
    ),
    ChemistryTargetReference(
        "SFT-CHEM-ORG-010-INTERMEDIATE-001",
        "RSC:D4SC01905A:3A-PRIME-TIME-COURSE",
        "pages 29 and 38 complete intermediate/product time-course record",
        ANALYSIS_PATH,
        ANALYSIS_HASH,
    ),
    ChemistryTargetReference(
        "SFT-CHEM-ORG-010-COMPLETE-SUPPLEMENT-001",
        "EUROPE-PMC:PMC11186341:SUPPLEMENT",
        "complete 22-member archive and 117-page supplementary PDF",
        ANALYSIS_PATH,
        ANALYSIS_HASH,
    ),
)

ELIMINATION_REACTION_SPEC = EmpiricalChemistrySpec(
    claim_id=CLAIM_ID,
    title="Exact complete inverse-addition elimination family law",
    statement=(
        "For every complete elimination carrier, every source atom and held-support occurrence is retained across "
        "the complete product carriers; exactly two source adjacencies are removed; and a positive finite family "
        "of multiplicity layers is restored to retained product incidences. This is the exact reversible boundary "
        "of the admitted complete addition transform."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, atom, support, adjacency, multiplicity, site, observation and "
        "extension alternatives; decide every one of the 256 forms only from admitted Fold conservation, graph "
        "and reversible addition laws."
    ),
    grammar_boundary=(
        "Every positive finite complete source carrier and complete product-carrier family; every exact atom and "
        "held-support occurrence; every positive finite restored multiplicity family; every same, adjacent and "
        "non-adjacent site class; the complete IUPAC record; all 22 captured archive members; all 117 PDF pages; "
        "all 32 characterized products; all five unsuccessful rows; all seven optimization tables; and the "
        "complete 3a-prime/3a intermediate record."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "The exact reverse of one admitted complete addition removes the two joining adjacencies, restores at "
        "least one relocated layer to its retained incidence, and partitions the unchanged atom/support carrier."
    ),
    induction_step=(
        "The admitted positive-finite addition induction supplies every next restored multiplicity layer; appending "
        "one fresh unchanged occurrence to source and products preserves every prior incidence and decision."
    ),
    exclusions=(
        "no native numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no conventional elimination name mechanism substrate yield temperature time or product selects the survivor",
        "all five unsuccessful rows, every dash, alternative product, isomer ratio, optimization row and mechanism page remain preserved",
        "the 32 isolated product blocks support observable unsaturation but do not display every coproduct; their complete atom/support balance remains explicitly unresolved",
        "external signed decimal and conventional zero inscriptions remain downstream evidence only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELIMINATION-REACTION-FAMILY-010",
    expected_observation_label="complete-elimination-observable-and-preservation-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=ANALYSIS_PATH,
    falsification_condition=(
        "The claim fails if more than one of 256 generated forms survives; if any atom, support, adjacency, restored "
        "layer, site class or successor is omitted; if the IUPAC inverse-addition/unsaturation relation fails; if "
        "any characterized product lacks its reported unsaturation; if any archive member, PDF page, product, "
        "unsuccessful row, optimization row, alternative or intermediate record is omitted; or if an incomplete "
        "conventional product block is falsely awarded complete atom/support balance."
    ),
)
ELIMINATION_REACTION_SPEC.validate()

__all__ = (
    "ANALYSIS_PATH",
    "CAPTURE_TOOL_PATH",
    "CLAIM_ID",
    "ELIMINATION_REACTION_SPEC",
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_PATH",
    "INVENTORY_PATH",
    "IUPAC_PATH",
    "OBLIGATION_ID",
    "PRESEAL_PATH",
    "TARGET_REFERENCES",
)
