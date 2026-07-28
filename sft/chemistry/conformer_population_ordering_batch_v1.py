"""Registered ORG-006 exact population law and complete external surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.conformer_population_ordering_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
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
LAW_PATH = "sft/chemistry/conformer_population_ordering_law_v1.py"
LAW_HASH = "sha256:d929d1c74c84048f7b341e3b972ec745867a675cd56507842a6f4d1249d049d0"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v5.json"
PRE_SOURCE_FILE_HASH = "sha256:76b38b99801d4c158eb32d9568202012f671e3834150fa6af3690ab7dd9d6202"
PRE_SOURCE_PAYLOAD_HASH = "sha256:937757ab2e2cb928be4d1e779b0d19ee1c15bf38022acddf971f3c87b3dc1121"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_006_complete_target_identities_v1.json"
IDENTITY_HASH = "sha256:ba488c309eb8a3081959b7f1ae6850bd43c0db50abdf3d351532d9da76c69d17"
TARGET_PATH = "experiments/external_sources/chemistry/org_006_complete_targets_v1.json"
TARGET_HASH = "sha256:992fd64ac240c750753fce9fabeb0487e88e6a5efadd843313f2dc96c93b3d0e"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-006-core-direct-v5/org-006-primary-record-v1.json"
PRIMARY_HASH = "sha256:9d44c07e1f26a5dbbac7abff49187ac26feb6cd08413c6b5469e301cd0b99eb7"

for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-006 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("exact_download_outcomes_payloads_temperatures_energies_probabilities_tables_and_figures_opened_before_v5_value_seal") is not False
):
    raise ValueError("ORG-006 value-blind derivation seal changed")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
_target_document = json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))
_target_rows = tuple(_target_document.get("rows", ()))
if len(_identity_rows) != 14 or len(_target_rows) != 14 or _identity_document.get("external_values_or_outcomes_used_to_select_identity") is not False:
    raise ValueError("ORG-006 complete target boundary changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        identity["target_id"],
        "::".join((identity["authority"], identity["source_id"], identity["source_record_role"], identity["custody_class"])),
        identity["registered_identity"], target["opened_snapshot_path"], target["opened_snapshot_sha256"],
    )
    for identity, target in zip(_identity_rows, _target_rows)
)

CONFORMER_POPULATION_ORDERING_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-CONFORMER-POPULATION-ORDERING-006",
    title="Exact conditioned conformer population and ordering law",
    statement=(
        "For every complete finite conformer quotient, retained observation condition and positive finite trace, "
        "each conformer population is exactly its deterministic class-occurrence count divided by the complete "
        "trace boundary. An unobserved class is structural EmptyOne. Relative energy order uses structural least "
        "state plus positive exact Take, while every condition and observation-timescale remains retained."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, condition, finite boundary, population, absence, order, "
        "observation and extension alternatives; decide all 256 forms solely from admitted Fold and ORG-005 dependencies."
    ),
    grammar_boundary=(
        "Every positive finite conformer equivalence census; every positive finite deterministic observation trace; "
        "one held condition and timescale; exact occurrence fractions; structural EmptyOne for no occurrence; positive "
        "relative-energy magnitudes and ordered Take; all fourteen frozen external target identities and every preserved response."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "At one retained four-observation boundary, three occurrences of one ORG-005 class and one of the other force "
        "exact populations three-fourths and one-fourth; structural least energy precedes one positive energy."
    ),
    induction_step=(
        "Append exactly one already generated assignment, retain the complete prior trace and condition, increase the "
        "positive boundary once and recompute every class count over that boundary without a smoothing or random rule."
    ),
    exclusions=(
        "no native numerical zero; structural absence and the least-state reference are EmptyOne",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no Boltzmann exponential measured temperature species label energy or population used to generate the law",
        "all external signed zero negative decimal uncertainty and rounded inscriptions remain downstream evidence",
        "no condition observation-timescale source response failed capture adverse row or rounding discrepancy omitted",
        "no external result opened before its applicable value-free source and prediction seal",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-CONFORMER-POPULATION-ORDERING-006",
    expected_observation_label="complete-conditioned-conformer-population-energy-order-and-blind-value-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any ORG-005 conformer class, observation, condition, timescale or source response is omitted; "
        "if a probability is fitted, randomized, imported or detached from its exact positive finite boundary; if native "
        "numerical zero or signed energy subtraction is used; if the 256-form census has other than one survivor; if the "
        "blind 298.5 K population vector, 22-spectrum condition surface, printed energy vector, all 224 ACS measurement "
        "rows, failed provider routes or the isotropic 201/200 rounded-display adverse row is erased or altered."
    ),
)
CONFORMER_POPULATION_ORDERING_SPEC.validate()

__all__ = (
    "CONFORMER_POPULATION_ORDERING_SPEC", "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH", "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH", "IDENTITY_PATH", "PRE_SOURCE_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
