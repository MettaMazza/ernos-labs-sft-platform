"""Registered ORG-005 conformer algorithm and complete authority surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.conformer_generation_equivalence_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"
LAW_PATH = "sft/chemistry/conformer_generation_equivalence_law_v1.py"
LAW_HASH = "sha256:d6416d06e430df2968693a6731723c2e2fea39397e2ff20c93270d8cd21330de"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_005_conformer_generation_equivalence_pre_source.json"
PRE_SOURCE_FILE_HASH = "sha256:bb428bc50ed3628cfe1864b0c5288eff60c72fe58a04217593836e872f0a4b31"
PRE_SOURCE_PAYLOAD_HASH = "sha256:1af4780a78bb418650ac93f057ca51b907333213a51cb00a0307699d22fff6ff"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_005_target_identities_v1.json"
IDENTITY_HASH = "sha256:7f148f0b99d0939aefb6023521d697dc00386a0de2f7a328d6b1220377965ad4"
TARGET_PATH = "experiments/external_sources/chemistry/org_005_withheld_targets_v1.json"
TARGET_HASH = "sha256:ed750adf9e52a8257fd3784f19fee213bca5c3a147cd72cb9488a2a4ec45c8f3"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-005-primary-records-v1.json"
PRIMARY_HASH = "sha256:a5eb356e0240a4e56457ba7265368cc7e06ca0396b38b103eac357e9ac186f10"

for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-005 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed != PRE_SOURCE_PAYLOAD_HASH
    or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("not_claimed_as_unknown_target_blind_prediction") is not True
    or _prediction.get("outcome_unopened_blind_target_count") != 0
):
    raise ValueError("ORG-005 observational derivation seal changed")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 4
    or _identity_document.get("development_observed_target_count") != 4
    or _identity_document.get("outcome_unopened_blind_target_count") != 0
    or len(_identity_rows) != 4
):
    raise ValueError("ORG-005 value-free identity boundary changed")
_target_rows = tuple(json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8")).get("rows", ()))
if len(_target_rows) != 4:
    raise ValueError("ORG-005 complete target vector changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        identity["target_id"],
        "::".join((identity["authority"], identity["source_id"], identity["source_record_role"], identity["custody_class"])),
        identity["registered_identity"], target["opened_snapshot_path"], target["opened_snapshot_sha256"],
    )
    for identity, target in zip(_identity_rows, _target_rows)
)

CONFORMER_GENERATION_EQUIVALENCE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005",
    title="Exact finite conformer generation and equivalence law",
    statement=(
        "For any positive finite connected molecular graph with a complete ordered rotor census and "
        "finite held torsion alphabets, every conformer assignment is generated exactly once by the "
        "Cartesian state product. Exact equivalence is the orbit relation of every exhaustively "
        "generated atom-type and bond-preserving graph automorphism; the disjoint orbit quotient is the "
        "complete conformer census, without coordinate tolerance, measured-energy selection or species rule."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, rotor, state generation, symmetry, equivalence, quotient, "
        "observation and extension alternatives; decide all 256 forms solely from admitted exact finite graph, "
        "combinatoric, order, process, molecular, isomeric and torsional-state dependencies."
    ),
    grammar_boundary=(
        "Every positive finite connected atom-labelled graph; every complete ordered four-site rotor; each "
        "positive finite held state alphabet with exact reversal involution; all Cartesian assignments; every "
        "atom-type and bond-preserving position bijection; all induced rotor actions; the complete disjoint orbit "
        "quotient; and the four frozen development-observed authority records."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One ordered rotor with three held states generates three assignments; identity and graph reversal force "
        "one self-equivalent anti class and one two-member opposed-gauche class, with no omitted assignment."
    ),
    induction_step=(
        "Append one complete rotor and its positive finite held alphabet. Take the exact Cartesian product with "
        "every prior assignment, exhaustively regenerate graph automorphisms and repartition by the same orbit "
        "relation; each assignment remains in exactly one nonempty class without a new rule."
    ),
    exclusions=(
        "no numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum tolerance fitted free or imported native parameter",
        "no measured energy molecular name coordinate library or selected conformer used to generate or quotient assignments",
        "no omitted graph automorphism rotor state or adverse external row",
        "all four external records are disclosed development-observed correspondence and are not called blind",
        "external signed decimal zero and absent inscriptions remain downstream records and never native arithmetic",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CONFORMER-GENERATION-EQUIVALENCE-005",
    expected_observation_label="complete-finite-conformer-generation-equivalence-and-small-molecule-census",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if an atom, bond, rotor, held state, Cartesian assignment or preserving graph bijection is "
        "omitted; if equivalence uses a coordinate tolerance or measured energy; if any assignment occurs in no "
        "class or more than one class; if the four-site witness does not generate three assignments, two graph "
        "actions and two classes of sizes one and two; if any of four authority records or any of the 19 tables "
        "and 105 CCCBDB rows is omitted; if Anti/Gauche is selected rather than compared after derivation; or if "
        "the adverse Gauche false-minimum row, signed values, conventional zeros or absent cells are erased."
    ),
)
CONFORMER_GENERATION_EQUIVALENCE_SPEC.validate()

__all__ = (
    "CONFORMER_GENERATION_EQUIVALENCE_SPEC", "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH", "IDENTITY_HASH", "IDENTITY_PATH", "PRE_SOURCE_PATH", "PRIMARY_HASH",
    "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
