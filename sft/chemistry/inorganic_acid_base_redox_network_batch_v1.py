"""Registered INORG-017 law and sealed authority surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.inorganic_acid_base_redox_network_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
LAW_PATH = "sft/chemistry/inorganic_acid_base_redox_network_law_v1.py"
LAW_HASH = "sha256:1729a28ff992e606f66cec8e654ca119e3eeec3947fc49dbc949f24545963656"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorg_017_target_identities_v1.json"
IDENTITY_HASH = "sha256:acea6aaf9593095e596338040d0ff44eb83b2f2658a09224da3002c6af53ea85"
TARGET_PATH = "experiments/external_sources/chemistry/inorg_017_withheld_targets_v1.json"
TARGET_HASH = "sha256:f1b8828cdcb9da2539472ab63bc33a6983c0101a63b3b9d5c8ba5c59eacf268c"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-017-primary-records-v1.json"
PRIMARY_HASH = "sha256:b7d5e91772a8c1f3642e947bf516dbdd40c677cd1b280b6ef7eb84c431d62fb9"

for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"INORG-017 authority changed: {path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 15
    or _identity_document.get(
        "target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present"
    )
    is not False
    or len(_identity_rows) != 15
):
    raise ValueError("INORG-017 identity boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        "::".join(
            (
                row["authority"],
                row["source_id"],
                row["source_record_role"],
                row["custody_class"],
            )
        ),
        row["registered_identity"],
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _identity_rows
)

INORGANIC_ACID_BASE_REDOX_NETWORK_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-INORGANIC-ACID-BASE-REDOX-NETWORK-017",
    title="Exact inorganic acid/base, redox and reaction-network law",
    statement=(
        "An inorganic reaction network retains every species and every ordered transition. "
        "Lewis joining carries exactly two held electron occurrences from provider to acceptor "
        "and retains the resulting adduct composition. Redox carries one positive complete held "
        "electron support from donor to acceptor, so oxidation and reduction are one conserved "
        "transfer and exact reversal swaps endpoints without signed arithmetic."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, species, acid-base, adduct, redox, coupling, "
        "path and extension alternatives; decide all 256 forms from admitted graph, information "
        "conservation, operational process, Lewis, redox, stoichiometry and reaction dependencies."
    ),
    grammar_boundary=(
        "Every finite complete inorganic species-transition network with Lewis pair/adduct and/or "
        "redox transfer steps and a complete ordered path; all fifteen frozen Lewis acid, Lewis "
        "base, Lewis adduct, oxidation and reduction surfaces."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One exact Lewis step or redox step retains every endpoint, its positive carrier support "
        "and one step identity in the complete network path."
    ),
    induction_step=(
        "Appending one exact step retains all prior species and steps, adds any fresh endpoints, "
        "and appends its step identity once under the same conservation and path law."
    ),
    exclusions=(
        "no numerical zero; an absent transition class is structural EmptyOne",
        "no negative irrational imaginary signed continuum fitted free or imported parameter",
        "no signed oxidation-number arithmetic in the native redox transfer",
        "no independent oxidation and reduction carrier records",
        "no unstructured acid/base mixture substituted for pair-supported adduct composition",
        "no source definition, named criterion or example structure used to select the law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-INORGANIC-ACID-BASE-REDOX-NETWORK-017",
    expected_observation_label="complete-inorganic-acid-base-redox-network-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a species, pair occurrence, adduct or redox carrier is omitted; if "
        "oxidation and reduction do not share one transfer support; if reversal does not swap the "
        "same endpoints and carriers; if path order is incomplete; if signed oxidation numbers "
        "enter forcing; if the absent rendered acid example is manufactured or removed; if any "
        "of fifteen rows is lost; or if outcomes open before prediction sealing."
    ),
)
INORGANIC_ACID_BASE_REDOX_NETWORK_SPEC.validate()

__all__ = (
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "INORGANIC_ACID_BASE_REDOX_NETWORK_SPEC",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
)
