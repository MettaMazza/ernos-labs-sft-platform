"""Registered INORG-008 law and complete sealed authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.inorganic_colour_transition_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:4624c5ac9ae4981e1c4ad424e2bcfdb9ba0c43ddcdaabbd16bc84a30487ae7d1"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e631c5d914b9f18315a4fb7927044c4b76574bb7461c884a23ba835c504ecbd5"
LAW_PATH = "sft/chemistry/inorganic_colour_transition_law_v1.py"
LAW_HASH = "sha256:b0c83c8c6c025bf61f31e33cda54a74675ec8ac2d89e9b800639f329372480bf"
ADDENDUM_PATH = "experiments/external_sources/chemistry/inorg_008_absorption_shared_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:e6719491d5f20147bbded3f849ba3aa71bcb6d4d201e485e87ecd102496bb319"
IDENTITY_PATH = "experiments/external_sources/chemistry/inorganic_colour_transition_target_identities_v1.json"
IDENTITY_HASH = "sha256:104256d68f89a5573c8ba529787405e1279bc03132519894228f31c9d94d9b4f"
TARGET_PATH = "experiments/external_sources/chemistry/inorganic_colour_transition_withheld_targets_v1.json"
TARGET_HASH = "sha256:cedca8d948231637a320f791bee0ec1f2b96509cf896878c084a532685ff648f"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/inorganic-colour-transition-primary-records-v1.json"
PRIMARY_HASH = "sha256:89bb7ebe8dd8597e1bfb32ab487c16842e149262e28477ea5c7188602617a4ec"
SHARED_TARGET_PATH = "experiments/external_sources/chemistry/ligand_state_splitting_withheld_targets_v1.json"
SHARED_TARGET_HASH = "sha256:2a843c7924c4f332c60c72dbb6338f9284fff6674d5f1ad76619388218c0d554"


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH),
    (ADDENDUM_PATH, ADDENDUM_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH), (SHARED_TARGET_PATH, SHARED_TARGET_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-008 registered authority changed: {path}")


_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 8
    or _identity_document.get("target_values_definitions_peak_positions_intensities_band_counts_outcomes_or_payload_hashes_present") is not False
    or len(_rows) != 8
    or tuple(row["source_record_ordinal"] for row in _rows) != tuple(range(1, 9))
):
    raise ValueError("INORG-008 value-free target identity boundary changed")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        row["target_id"],
        f"{row['authority']}::{row['source_id']}::{row['source_record_role']}::{row['custody_class']}",
        f"{row['source_id']} :: {row['source_record_role']} :: {row['custody_class']}",
        row["snapshot_path"],
        row["snapshot_sha256"],
    )
    for row in _rows
)


INORGANIC_COLOUR_TRANSITION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008",
    title="Exact inorganic electronic-transition and selective-colour law",
    statement="Ligand and metal are the two retained electronic carrier kinds of a coordination entity, forcing the complete four-class directed transition product ligand-to-ligand, ligand-to-metal, metal-to-ligand and metal-to-metal. Every transition retains two state identities, a held source-target direction and the exact positive state-order gap. Selective absorption is a positive proper subset of complete incident observation support; inorganic colour is the exact nonempty complementary observation class retained after that absorption. No wavelength, colour wheel, orbital assignment, peak selection or fitted threshold enters the law.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, endpoints, state, direction, gap, absorption, colour and extension choices; decide all 256 candidates only from admitted distinction, order, transition, selection-rule and INORG-004/006/007 dependencies.",
    grammar_boundary="Every ordered ligand/metal carrier pair in one retained coordination entity; every positive exact state successor; every positive proper absorbed subset of a finite complete incident observation support; four frozen definitions and four immutable complete NIST spectra with original custody classes preserved.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="For two incident distinctions, absorbing either one is the first proper selective partition and leaves exactly one retained colour distinction. The four directed carrier classes are already complete at two carrier kinds.",
    induction_step="Appending one new incident distinction preserves the prior absorbed/retained partition and places the new distinction in exactly one class. Appending one positive state successor preserves endpoint identity and increments only the exact positive order gap. No new carrier or colour rule is introduced.",
    exclusions=(
        "no numerical zero; absence is structural EmptyOne",
        "no negative irrational imaginary floating signed continuum or complex-valued proof quantity",
        "no imported orbital assignment ligand-field Hamiltonian colour wheel visual-response curve or wavelength-to-colour table",
        "no selected peak smoothing threshold intensity cutoff fitted wavelength dimensional anchor or species exception",
        "no recapture deletion relabeling or custody-class promotion of shared admitted spectra",
        "no claim that a conventional colour name, wavelength or intensity is natively derived by the structural law",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-INORGANIC-COLOUR-ELECTRONIC-TRANSITION-008",
    expected_observation_label="complete-transition-definition-and-shared-absorption-spectrum-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if the two carrier kinds do not generate exactly four directed classes; if endpoint identity, direction or positive order gap is lost; if absorbed and retained distinctions do not form a complete nonempty partition; if numerical zero, a signed/continuum quantity, orbital model, colour wheel, selected peak, smoothing, fitted threshold or dimensional target enters forcing; if any of the eight rows or original custody classes is removed; or if any complete external spectrum lacks positive exact selective-maximum support under the registered no-smoothing/no-threshold rule.",
)
INORGANIC_COLOUR_TRANSITION_SPEC.validate()


__all__ = (
    "ADDENDUM_PATH", "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH", "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH", "IDENTITY_PATH", "INORGANIC_COLOUR_TRANSITION_SPEC", "PRIMARY_HASH",
    "PRIMARY_PATH", "SHARED_TARGET_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
