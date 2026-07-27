"""Registered INORG-011 law and complete sealed authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.organometallic_electron_accounting_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
LAW_PATH = "sft/chemistry/organometallic_electron_accounting_law_v1.py"
LAW_HASH = "sha256:d5a18710a2aad639afea5535fdb5fbb0fbcb9a7274e6b4bd85865513b5171e2a"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorg_011_target_identities_v1.json"
IDENTITY_HASH = "sha256:a439259572b5ea2b89ca4d9b46e659a915e717920f5ff5702862872bd5aa4782"
TARGET_PATH = "experiments/external_sources/chemistry/inorg_011_withheld_targets_v1.json"
TARGET_HASH = "sha256:f547856fc61f6de42089e7ac386bd919ae1488b5c7be8b11dcc8bca9be21d681"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorg-011-primary-records-v1.json"
PRIMARY_HASH = "sha256:7ec6645469a1ea866a80582badabb8e15b9d544c0eb5fab9c76f652eafbfc96a"


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected: raise ValueError(f"INORG-011 registered authority changed: {path}")


_identity = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8")); _rows = tuple(_identity.get("rows", ()))
if _identity.get("complete_registered_target_count") != 4 or _identity.get("target_definitions_examples_values_outcomes_presence_flags_or_payload_hashes_present") is not False or len(_rows) != 4:
    raise ValueError("INORG-011 value-free target boundary changed")


TARGET_REFERENCES = tuple(ChemistryTargetReference(
    row["target_id"], f"{row['authority']}::{row['source_id']}::{row['source_record_role']}::{row['custody_class']}",
    row["registered_identity"], row["snapshot_path"], row["snapshot_sha256"],
) for row in _rows)


ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011",
    title="Exact organometallic electron-support capacity and accounting law",
    statement="The admitted exact s, p and d support widths two, six and ten force capacity eighteen without importing an electron-counting rule. One retained organometallic entity partitions complete complementary fibre-paired electron occurrences into disjoint nonbonded and bond support. Their exact union is held as capacity-complete or capacity-incomplete; each pair successor adds two occurrences and capacity-complete support halts another addition.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, support, capacity, balance, partition, relation, comparison and extension choices; decide all 256 candidates only from admitted spin, exclusion, orbital-support, magnetic-response and INORG-010 dependencies.",
    grammar_boundary="Every finite complementary-pair support partitioned into nonbonded and bond occurrences on one retained organometallic entity, up to the exact generated s+p+d capacity; all four frozen IUPAC scope, component and total surfaces.",
    dimensions=DIMENSIONS, exact_result=EXACT_RESULT,
    induction_base="The first complementary pair has exact count two. Complete s, p and d supports have widths two, six and ten and force capacity eighteen.",
    induction_step="Appending one fresh complementary fibre pair preserves all previous occurrences and the disjoint partition and increments the exact count twice; a capacity-complete support rejects another pair.",
    exclusions=(
        "no numerical zero; empty account support is structural EmptyOne", "no negative irrational imaginary floating signed continuum fitted free or imported parameter",
        "no imported eighteen-electron rule oxidation-state bookkeeping species stability lookup or observed target total in capacity generation",
        "no unpaired or duplicated occurrence inside the stable diamagnetic account", "no omitted IUPAC scope component total analogy citation licence or disclaimer surface",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ORGANOMETALLIC-ELECTRON-ACCOUNTING-011",
    expected_observation_label="complete-stable-complex-electron-account-vector",
    target_rows=TARGET_REFERENCES, observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if capacity is imported rather than regenerated as 2+6+10; if any electron occurrence is missing, duplicated, unpaired or assigned to both account parts; if the exact total or capacity relation differs; if support exceeds capacity without halting; if observed eighteen, oxidation-state bookkeeping or a species lookup selects the law; if any of four IUPAC surfaces is removed; or if outcomes open before the prediction seal.",
)
ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC.validate()


__all__ = (
    "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH", "FAMILY_REGISTRY_PATH", "IDENTITY_HASH", "IDENTITY_PATH",
    "ORGANOMETALLIC_ELECTRON_ACCOUNTING_SPEC", "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
