"""Registered ORG-009 addition law and complete V1--V9 evidence history."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.addition_reaction_law_v3 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "SFT-CHEM-ADDITION-REACTION-FAMILY-009"
OBLIGATION_ID = "SFT-CHEM-OBL-ORG-009"

FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:00ed97e8dec313d65d2b9f6af595e3e3787a99aa60b86814f1a00f318abf011e"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:8b35e1f37dbf80713c47404d946a320da8d7011deaa5dbee7fe8393b58793cee"

LAW_PATH = "sft/chemistry/addition_reaction_law_v3.py"
LAW_HASH = "sha256:fb4f8b12698b7800f89a117648b7fb311f7ad733f15e420c33f67f9309aef9c8"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_009_target_identities_v9.json"
IDENTITY_HASH = "sha256:763e26e4d60699e7af4ddffb71789b9535df2959259abfed8b29a67e650b7138"
PRESEAL_PATH = "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_ord_v9.json"
PRESEAL_FILE_HASH = "sha256:045b5a0960e729450a6b5d0670fe3d6337c6d066c97ede3e865550b12fdf98cc"
PRESEAL_PAYLOAD_HASH = "sha256:cdc4cb97a28cf077b377eb9e97bc627882d773fad111a35ea69fd661a55396d3"
METADATA_PATH = "experiments/external_sources/chemistry/snapshots/org-009-ord-metadata-v9/huggingface-parquet-metadata-v9.json"
METADATA_HASH = "sha256:53d469d1e960fbaa307351510544ffedecb812a4c061b112dce70b774962e25a"
INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9/source-inventory-v9.json"
INVENTORY_HASH = "sha256:a4fe3ee3452b423ae2fb41f1901767e6c6002604be73c7b75035fbeaf2a6dc03"
SELECTION_PATH = "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9/source-only-selection-v9.json"
SELECTION_HASH = "sha256:6320e2e258f264dee49265a1fc73463be5c8a944d53c807e855ec440bc6ba3e4"
SELECTION_SEAL_PATH = "experiments/sealed_predictions/chemistry_org_009_ord_source_selection_v9.json"
SELECTION_SEAL_HASH = "sha256:b909b6f46caf9b361cc0b1221b440f7898f679f2c935da379105f69359513994"
COMPARISON_PATH = "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9/product-comparison-v9.json"
COMPARISON_HASH = "sha256:ae8b152f09ebdd07e068890f0bff121d6dcfe189f57b6999ea79a6c22f29f96c"

HISTORY_PATHS = tuple(
    [f"experiments/external_sources/chemistry/org_009_target_identities_v{version}.json" for version in range(1, 9)]
    + [f"experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v{version}.json" for version in range(1, 6)]
    + [
        "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_product_v6.json",
        "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_query_v7.json",
        "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_product_v8.json",
        "experiments/sealed_predictions/chemistry_org_009_localmapper_source_selection_v5.json",
        "experiments/sealed_predictions/chemistry_org_009_cycloaddition_source_selection_v6.json",
        "experiments/sealed_predictions/chemistry_org_009_azide_alkyne_source_selection_v8.json",
        "experiments/external_sources/chemistry/snapshots/org-009-rhea-blind-v1/source-inventory-v1.json",
        "experiments/external_sources/chemistry/snapshots/org-009-uspto50k-blind-v2/source-inventory-v2.json",
        "experiments/external_sources/chemistry/snapshots/org-009-schneider50k-blind-v3/source-inventory-v3.json",
        "experiments/external_sources/chemistry/snapshots/org-009-mars-blind-v4/source-inventory-v4.json",
        "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/source-inventory-v5.json",
        "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/source-only-selection-v5.json",
        "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-source-selection-v6.json",
        "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-product-comparison-v6.json",
        "experiments/external_sources/chemistry/snapshots/org-009-rhea-diels-alder-query-v7/source-inventory-v7.json",
        "experiments/external_sources/chemistry/snapshots/org-009-rhea-diels-alder-query-v7/rhea-diels-alder-query.tsv",
        "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/azide-alkyne-source-selection-v8.json",
        "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/azide-alkyne-product-comparison-v8.json",
    ]
)

TOOL_PATHS = (
    "tools/register_chemistry_org_009_ord_holdout_v9.py",
    "tools/capture_chemistry_org_009_ord_holdout_v9.py",
    "tools/select_chemistry_org_009_ord_sources_v9.py",
    "tools/build_chemistry_org_009_ord_external_v9.py",
)

for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (PRESEAL_PATH, PRESEAL_FILE_HASH),
    (METADATA_PATH, METADATA_HASH),
    (INVENTORY_PATH, INVENTORY_HASH),
    (SELECTION_PATH, SELECTION_HASH),
    (SELECTION_SEAL_PATH, SELECTION_SEAL_HASH),
    (COMPARISON_PATH, COMPARISON_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-009 authority changed: {path}")

for path in HISTORY_PATHS + TOOL_PATHS:
    if not (ROOT / path).is_file():
        raise ValueError(f"ORG-009 preserved evidence is absent: {path}")

_preseal = json.loads((ROOT / PRESEAL_PATH).read_text(encoding="utf-8"))
_claimed_payload_hash = _preseal.pop("sealed_payload_hash", None)
if (
    _claimed_payload_hash != PRESEAL_PAYLOAD_HASH
    or sha256_identity(_preseal) != PRESEAL_PAYLOAD_HASH
    or _preseal.get("ord_reaction_rows_or_products_opened_before_v9_seal") is not False
    or _preseal.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
    or _preseal.get("all_v1_through_v8_results_preserved") is not True
):
    raise ValueError("ORG-009 prediction seal changed")

_selection = json.loads((ROOT / SELECTION_PATH).read_text(encoding="utf-8"))
_comparison = json.loads((ROOT / COMPARISON_PATH).read_text(encoding="utf-8"))
_selected_rows = tuple(_selection["selected_in_payload_and_row_order"])
_comparison_rows = tuple(_comparison["results_in_frozen_order"])
if len(_selected_rows) != 28 or len(_comparison_rows) != 28:
    raise ValueError("ORG-009 complete selected boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=f"SFT-CHEM-ORG-009-ORD-REACTION-{ordinal:03d}",
        source_id=f"ORD:{row['config']}:{row['reaction_id']}",
        source_locator=f"row:{row['row_ordinal']}:source-selected-before-product-open",
        snapshot_path=COMPARISON_PATH,
        snapshot_hash=COMPARISON_HASH,
    )
    for ordinal, row in enumerate(_selected_rows, 1)
)

ADDITION_REACTION_SPEC = EmpiricalChemistrySpec(
    claim_id=CLAIM_ID,
    title="Exact complete addition-reaction family law",
    statement=(
        "For every complete addition transform, every source carrier, atom occurrence and held support occurrence "
        "is retained in one product; exactly two new cross-component adjacencies form; a positive finite family "
        "of multiplicity layers relocates while each reduced endpoint retains its base incidence; and every exact "
        "same-site, adjacent-site and non-adjacent-site attachment class remains generated."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, atom, support, adjacency, multiplicity, site, observation and "
        "extension alternatives; decide all 256 forms solely from admitted Fold conservation and transition laws."
    ),
    grammar_boundary=(
        "Every positive finite multicarrier source becoming one product; every exact atom and held-support occurrence; "
        "every two-adjacency cross-carrier orientation; every positive finite reduced multiplicity family; every "
        "componentwise same, adjacent and non-adjacent site class; all V1--V9 records; all 48 independent ORD payloads; "
        "and all 28 source-selected product vectors."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Two complete source carriers force one retained product, exactly two new cross-carrier adjacencies and at "
        "least one relocated multiplicity layer while every atom and support occurrence remains exact."
    ),
    induction_step=(
        "Append one fresh unchanged occurrence and support to a retained source carrier and the identical product "
        "carrier; every prior occurrence, adjacency, relocation, site class and decision remains unchanged."
    ),
    exclusions=(
        "no native numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no conventional addition name product database row atom map or measured outcome selects the survivor",
        "all V1--V8 absent adverse unresolved and failed-universal results remain preserved and cannot award closure",
        "all 48 non-USPTO ORD payloads and all 28 preselected reactions remain required without post-outcome filtering",
        "external signed decimal aromatic and conventional bond inscriptions remain downstream evidence only",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ADDITION-REACTION-FAMILY-009",
    expected_observation_label="complete-addition-adjacency-and-multiplicity-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=COMPARISON_PATH,
    falsification_condition=(
        "The claim fails if any carrier, atom, support, new adjacency, multiplicity relocation, site class, prior "
        "attempt, payload or selected reaction is omitted; if more than one of 256 forms survives; if any selected "
        "ORD reaction lacks a complete element-preserving correspondence with exactly two generated cross-carrier "
        "adjacencies and positive finite multiplicity relocation; or if any adverse or unresolved row is filtered."
    ),
)
ADDITION_REACTION_SPEC.validate()

__all__ = (
    "ADDITION_REACTION_SPEC",
    "CLAIM_ID",
    "COMPARISON_HASH",
    "COMPARISON_PATH",
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "HISTORY_PATHS",
    "IDENTITY_PATH",
    "INVENTORY_PATH",
    "METADATA_PATH",
    "OBLIGATION_ID",
    "PRESEAL_PATH",
    "SELECTION_PATH",
    "SELECTION_SEAL_PATH",
    "TARGET_REFERENCES",
    "TOOL_PATHS",
)
