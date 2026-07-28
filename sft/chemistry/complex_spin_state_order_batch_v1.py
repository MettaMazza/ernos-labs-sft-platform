"""Registered INORG-007 law and sealed authority surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.complex_spin_state_order_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_INORG_004_017_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:87998e9fa168d82dd80c28abc9910502bfb23da0c26cb6b1ecedfb88142642bc"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e03724f16e4866b43b5f3b53a6804588a2c86f5405bcda37cfb717e5724bb7c2"
LAW_PATH = "sft/chemistry/complex_spin_state_order_law_v1.py"
LAW_HASH = "sha256:279e1e175fbbd6588dfd113d2a708d08c9970c2f9487387dc184976107329ba7"
IDENTITY_PATH = "experiments/external_sources/chemistry/complex_spin_state_order_target_identities_v1.json"
IDENTITY_HASH = "sha256:0bac4d73f7add7f9dd93a42b59da32b783225a2b34e92015e31b0c9cdaf06a79"
TARGET_PATH = "experiments/external_sources/chemistry/complex_spin_state_order_withheld_targets_v1.json"
TARGET_HASH = "sha256:c428c6350e9d4f6c79e362ef9b256cf278b003529e2d5d82cf793f639822866d"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/complex-spin-state-order-primary-records-v1.json"
PRIMARY_HASH = "sha256:bad9ea5c0bf768db64a2fda8739f45889ab24cef27c2d089fffea7992684ee7e"


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"INORG-007 registered authority changed: {path}")


_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 3
    or _identity_document.get("target_values_definitions_terms_distances_temperatures_outcomes_or_payload_hashes_present") is not False
    or len(_rows) != 3
    or tuple(row["source_record_ordinal"] for row in _rows) != (1, 2, 3)
):
    raise ValueError("INORG-007 value-free target identity boundary changed")


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


COMPLEX_SPIN_STATE_ORDER_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-COMPLEX-SPIN-STATE-ORDER-007",
    title="Exact complex spin-state extrema, order and crossover",
    statement="For the forced three-plus-two split support, exhaustive pair/single occupancy of six retained electron occurrences produces ten symmetry-distinct signatures. The low-spin state is uniquely the least split-crossing and then least-unmatched signature: three lower pairs, spin width one and structural EmptyOne crossings. The high-spin state is uniquely the greatest-unmatched and then least-crossing signature: one lower pair, two lower singles, two upper singles, spin width five and two crossings. Exact pair-closure plus retained crossing path counts force the order vector high-before-low, crossover coincidence and low-before-high for diluted EmptyOne, first-retained and second-retained interaction recurrence. Admitted geometric dilution therefore reverses the state order without any fitted field, pairing, temperature or distance parameter.",
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, split, enumeration, low extremum, high extremum, cost, order and extension choices; decide all 256 candidates only from admitted support, occupancy, state-order, INORG-006 split and geometric-dilution dependencies.",
    grammar_boundary="Every symmetry-distinct pair/single occupancy of six electron occurrences across the forced three-plus-two support; the two complete extrema; every structural EmptyOne or positive interaction recurrence; all three frozen INORG-007 external source identities and their favorable, conventional and transport-mismatch surfaces.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="At diluted structural EmptyOne recurrence, split crossings retain no separate path cost; the complete census forces the high-spin extremum to precede the low-spin extremum by its smaller pair-closure count.",
    induction_step="Each positive interaction successor adds exactly the retained split-crossing count to every state's path cost. The low extremum has structural EmptyOne crossings while the high extremum has two, so the first successor is the unique coincidence boundary and every later successor preserves low-before-high order without an extra rule.",
    exclusions=(
        "no numerical zero; native absence and the diluted boundary are structural EmptyOne",
        "no negative irrational imaginary floating signed spin or continuum proof quantity",
        "no imported crystal-field ligand-field orbital Hamiltonian pairing-energy or spectrochemical model",
        "no free or fitted field strength, crossover threshold, temperature, distance, species rule or tolerance",
        "no measured definition, term, bond length or temperature in generation, enumeration or survivor decision",
        "no deletion or correction of the registered HT06789 to LT06788 transport mismatch",
        "no claim that the Fold recurrence derives the dimensional pm or K inscriptions; they are complete post-seal comparison values",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-COMPLEX-SPIN-STATE-ORDER-007",
    expected_observation_label="complete-high-low-crossover-definition-and-exact-value-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition="The claim fails if the complete six-electron quotient census is not ten; if either extremum is nonunique; if the exact low and high signatures, spin widths or crossing counts differ; if the weak/boundary/strong order vector differs; if numerical zero, signed spin, a field or pairing parameter, a dimensional fit or measured target enters forcing; if any of the three registered external rows or the HT06789 transport mismatch is removed; or if the complete post-seal crossover row does not retain low spin at the shorter reported distance and high spin at the longer reported distance.",
)
COMPLEX_SPIN_STATE_ORDER_SPEC.validate()


__all__ = (
    "COMPLEX_SPIN_STATE_ORDER_SPEC", "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
