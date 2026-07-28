"""Registered ORG-002 law and sealed complete authority surface."""
from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.resonance_equivalent_representation_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
FAMILY_BOUNDARY_PATH = "audits/CHEMISTRY_ORG_001_016_FAMILY_BOUNDARY_2026-07-27.json"
FAMILY_BOUNDARY_HASH = "sha256:ccbc91e9873a84f31b50670c9a8f063ee6a6096d3dd216b5e7c3bf86521681b2"
FAMILY_REGISTRY_PATH = "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
FAMILY_INVENTORY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"
LAW_PATH = "sft/chemistry/resonance_equivalent_representation_law_v1.py"
LAW_HASH = "sha256:e07d2314e60bcbcf529716c67225c27ee5fd551bf8ebf465a8f49931c097dfd5"
PRE_SOURCE_PATH = "experiments/sealed_predictions/chemistry_org_002_resonance_equivalence_pre_source.json"
PRE_SOURCE_FILE_HASH = "sha256:bce7d5df7d0a84d4fe0c5d055ec5a3e37636ae2e9ead5893ac01894523f718ec"
PRE_SOURCE_PAYLOAD_HASH = "sha256:8e17d81cb943624e2778dd9536017265534e1166791d4794ea58d034b5f2cc9e"
IDENTITY_PATH = "experiments/external_sources/chemistry/org_002_target_identities_v1.json"
IDENTITY_HASH = "sha256:d90bb68121cb37ea8a2d85242fd0b3ba4673ec9e3eb01d151c79fb8118b0fbbc"
V1_TARGET_PATH = "experiments/external_sources/chemistry/org_002_withheld_targets_v1.json"
V1_TARGET_HASH = "sha256:18df21662ac89606b6d6e3cd2c7c80247b20cfe86156a97f85f1375f74185dbd"
V1_PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-002-primary-records-v1.json"
V1_PRIMARY_HASH = "sha256:f573789510a6349d997dc58ab4d2a2dbd6cbc361da7874f44c673e094540d8b5"
TARGET_PATH = "experiments/external_sources/chemistry/org_002_withheld_targets_v2.json"
TARGET_HASH = "sha256:873777e871d3b15278afd2502ac6fa4ad5b5083eb05192b06e16cf3b04d7be51"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-002-primary-records-v2.json"
PRIMARY_HASH = "sha256:0987db81474d56aacfeffa3b317e3380bfb4ec79b985ab09eed931594c366247"


for path, expected_hash in (
    (FAMILY_BOUNDARY_PATH, FAMILY_BOUNDARY_HASH),
    (FAMILY_REGISTRY_PATH, FAMILY_REGISTRY_HASH),
    (FAMILY_INVENTORY_PATH, FAMILY_INVENTORY_HASH),
    (LAW_PATH, LAW_HASH),
    (PRE_SOURCE_PATH, PRE_SOURCE_FILE_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (V1_TARGET_PATH, V1_TARGET_HASH),
    (V1_PRIMARY_PATH, V1_PRIMARY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / path) != expected_hash:
        raise ValueError(f"ORG-002 authority changed: {path}")

_prediction = json.loads((ROOT / PRE_SOURCE_PATH).read_text(encoding="utf-8"))
_claimed_prediction_hash = _prediction.pop("sealed_payload_hash", None)
if (
    _claimed_prediction_hash != PRE_SOURCE_PAYLOAD_HASH
    or sha256_identity(_prediction) != PRE_SOURCE_PAYLOAD_HASH
    or _prediction.get("external_target_content_opened_after_target_identity_seal") is not False
):
    raise ValueError("ORG-002 pre-source prediction seal changed")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_identity_rows = tuple(_identity_document.get("rows", ()))
if (
    _identity_document.get("complete_registered_target_count") != 4
    or _identity_document.get(
        "target_definitions_notes_examples_values_outcomes_presence_flags_or_payload_hashes_present"
    )
    is not False
    or len(_identity_rows) != 4
):
    raise ValueError("ORG-002 value-free identity boundary changed")

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

RESONANCE_EQUIVALENT_REPRESENTATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002",
    title="Exact one-carrier multiple-representation equivalence law",
    statement=(
        "A Fold representation-equivalence class retains exactly one molecular carrier, every "
        "atom occurrence and every adjacency while retaining at least two distinct encoding "
        "identities. In the minimal generated pair, every support incidence in the second encoding "
        "is the exact opposed Fold-fibre complement of the first; this relation creates neither a "
        "second species nor an equilibrium process."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, atom-support, adjacency, encoding-number, "
        "fibre-relation, identity, process and extension alternatives; decide all 256 forms from "
        "admitted form enforcement, exact graph, distinction, conservation, molecular identity, "
        "bond-order, electronic-state and conjugated-support dependencies."
    ),
    grammar_boundary=(
        "Every finite complete connected alternating molecular representation pair related by "
        "global Fold-fibre complement. Larger finite representation classes are generated by "
        "composition of exact local pair relations while retaining the same carrier, atoms and "
        "adjacency. The empirical boundary is the four complete preregistered IUPAC records."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "Three distinct atom occurrences, two complete incidences and their opposed global "
        "Fold-fibre assignments supply the first two-encoding one-carrier equivalence pair."
    ),
    induction_step=(
        "Append one fresh atom occurrence and one incidence to both encodings. The unique fibre "
        "opposed to each formerly terminal fibre preserves complete complement, identical atom "
        "support, identical adjacency and the single held carrier."
    ),
    exclusions=(
        "no numerical zero; structural absence is EmptyOne",
        "no negative irrational imaginary signed continuum fitted free or imported parameter",
        "no Lewis bond mark charge coefficient wavefunction or named resonance rule used to select the survivor",
        "no physical interconversion equilibrium time or stochastic mixing imported into representation equivalence",
        "no target definition note example or outcome opened to select the law",
        "the preserved V1 incomplete search-scope result cannot be hidden or treated as external absence",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-RESONANCE-EQUIVALENT-REPRESENTATION-002",
    expected_observation_label="complete-one-carrier-multiple-formal-representation-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if equivalent encodings change the carrier, atom occurrences or adjacency; "
        "if the minimal pair is not a complete opposed-fibre complement; if formal encodings are "
        "counted as multiple species or an equilibrium; if any of four complete records is omitted; "
        "if external wavefunction, coefficient or signed-charge language enters native forcing; if "
        "the V1 search-scope error is hidden; or if outcomes open before the value-free prediction seal."
    ),
)
RESONANCE_EQUIVALENT_REPRESENTATION_SPEC.validate()


__all__ = (
    "FAMILY_BOUNDARY_PATH",
    "FAMILY_INVENTORY_PATH",
    "FAMILY_REGISTRY_PATH",
    "IDENTITY_HASH",
    "IDENTITY_PATH",
    "PRE_SOURCE_PATH",
    "PRIMARY_HASH",
    "PRIMARY_PATH",
    "RESONANCE_EQUIVALENT_REPRESENTATION_SPEC",
    "TARGET_HASH",
    "TARGET_PATH",
    "TARGET_REFERENCES",
    "V1_PRIMARY_PATH",
    "V1_TARGET_PATH",
)
