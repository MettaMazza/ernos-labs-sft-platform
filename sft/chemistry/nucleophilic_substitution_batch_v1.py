"""Registered ORG-007 substitution law and complete external structure surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.nucleophilic_substitution_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"
LAW_PATH = "sft/chemistry/nucleophilic_substitution_law_v1.py"
LAW_HASH = "sha256:c4303edd24946ecb92eb1d6aaca5f3d14c2726cf41eaaba989abf9adbbe98185"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_007_nucleophilic_substitution_pre_source_v1.json"
PRE_SOURCE_FILE_HASH = "sha256:1cacce138902f43b84c89ced61f0ab83fc78e155f4dab47e1566ddd80ff6c1cd"
PRE_SOURCE_PAYLOAD_HASH = "sha256:70f38b8bb83b54b5613c9ea8f3639f15dc0382dd80afed58247b5e7a4add287e"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_007_target_identities_v1.json"
IDENTITY_HASH = "sha256:5dcb77e93b457fc4c02e93c3b8aac171d0813ecee72c8046e2cef36a2c585bff"
CORRECTION_PATH = "experiments/external_sources/chemistry/org_007_identity_hash_correction_v2.json"
CORRECTION_HASH = "sha256:eacf3538ee66081e9e3fc74a4641359c61224ce5dae087eb43c785247414bb9f"
CAPTURE_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-007-blind-v1/source-inventory-v1.json"
CAPTURE_INVENTORY_HASH = "sha256:750852bc6d3fa671127e7820c53a22e398dc023e31749e901176f139d829231d"
TARGET_PATH = "experiments/external_sources/chemistry/org_007_complete_targets_v1.json"
TARGET_HASH = "sha256:f5ab1d106f19f9d5a6208d0eec94cd5da2eb6d367cd4d3f9b1812fec145d7853"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-007-blind-v1/org-007-primary-record-v1.json"
PRIMARY_HASH = "sha256:7e95bf014c60356569972f5f16118fdd24750b39cc7932b5ceb9c214fb0768da"


for path, expected in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH), (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH), (LAW_PATH, LAW_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH), (IDENTITY_PATH, IDENTITY_HASH),
    (CORRECTION_PATH, CORRECTION_HASH), (CAPTURE_INVENTORY_PATH, CAPTURE_INVENTORY_HASH),
    (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"ORG-007 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed != PRE_SOURCE_PAYLOAD_HASH or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("exact_new_IUPAC_and_PubChem_payloads_opened_before_this_seal") is not False
    or _prediction.get("external_target_content_used_by_candidate_generator_or_eliminator") is not False
):
    raise ValueError("ORG-007 derivation and target seal changed")

_identities = tuple(json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))["rows"])
_targets = tuple(json.loads((ROOT / TARGET_PATH).read_text(encoding="utf-8"))["rows"])
if len(_identities) != 9 or len(_targets) != 9:
    raise ValueError("ORG-007 complete target cardinality changed")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        identity["target_id"],
        "::".join((identity["authority"], identity["source_id"], identity["source_record_role"], identity["custody_class"])),
        identity["registered_identity"], target["opened_snapshot_path"], target["opened_snapshot_sha256"],
    )
    for identity, target in zip(_identities, _targets)
)


NUCLEOPHILIC_SUBSTITUTION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007",
    title="Exact entering/leaving carrier substitution family law",
    statement=(
        "For every complete finite registered exchange carrier, one incoming held pair forms the unique centre-entering "
        "bond while the two occurrences of the displaced centre-leaving bond remain held on the leaving carrier. Every "
        "atom and electron occurrence is conserved. The complete generated path family consists of a one-transition "
        "exchange and cleavage followed by formation; formation before cleavage violates the unique exchange slot."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, source, support, change, path, record, observation and extension "
        "alternatives; decide all 256 forms only from admitted exact graph, conservation, bond and transition laws."
    ),
    grammar_boundary=(
        "Every positive finite complete exchange carrier with distinct centre, retained, entering and leaving occurrences; "
        "all source bonds and free pairs; every atom and held electron occurrence; the single exchange slot; both generated "
        "path orders; every source record and the complete nine-target external surface."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "A four-occurrence source with one retained bond, one displaced bond and one free entering pair forces one terminal "
        "with the retained bond, entering bond and displaced free pair through exactly one or two ordered transitions."
    ),
    induction_step=(
        "Append one fresh retained substrate occurrence and its complete held pair outside the exchange slot to every path "
        "state. Every prior atom, pair, bond change, state and transition remains unchanged without an extra rule."
    ),
    exclusions=(
        "no native numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary continuum fitted free random or imported native parameter",
        "no conventional nucleophilic SN1 SN2 rate energy solvent or substrate rule used to generate the survivor",
        "no external substrate product mechanism structure formula charge or source response opened before its applicable seal",
        "the two development-observed IUPAC records are disclosed and never relabelled blind",
        "all nine source rows and the V1 identity-hash transcription correction remain preserved",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-NUCLEOPHILIC-SUBSTITUTION-FAMILY-007",
    expected_observation_label="complete-entering-leaving-bond-change-path-and-postseal-structure-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any carrier, source bond, free pair, atom or electron occurrence is omitted; if more or fewer "
        "than one centre bond is replaced; if formation-before-cleavage is accepted; if either generated path family is "
        "omitted; if the census has other than 256 forms and one survivor; if any of nine external records is erased; if "
        "the post-seal IUPAC entering-group, substitution or heterolysis records fail their declared relations; if the "
        "PubChem source and terminal formula inventories differ; or if C-Br to C-O connectivity replacement is absent."
    ),
)
NUCLEOPHILIC_SUBSTITUTION_SPEC.validate()


__all__ = (
    "CAPTURE_INVENTORY_PATH", "CORRECTION_PATH", "FAMILY_BOUNDARY_PATH", "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH", "IDENTITY_HASH", "IDENTITY_PATH", "NUCLEOPHILIC_SUBSTITUTION_SPEC", "PRE_SOURCE_PATH",
    "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
