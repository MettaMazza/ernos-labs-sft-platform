"""Registered exact relation and blind NIST vector for Chemistry PROP-008."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.molecular_electron_affinity_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = "experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1/nist-cccbdb-electron-affinity-catalog.html"
CATALOG_HASH = "sha256:e501037192ac2b1a50efebf2cf11c95a60ca9a84f1cc52c9eef247d68ab7d987"
GUIDE_PATH = "experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1/nist-webbook-gas-phase-ion-thermochemistry.html"
GUIDE_HASH = "sha256:d5ff66aa2f3b1d6156e2e6f934da0decb2a8a05b94a370c1c44437c60ef69d4e"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1/molecular-electron-affinity-primary-records-v1.json"
PRIMARY_HASH = "sha256:a1fe2a76e293f97fed42e911b0daa423654479eb3d637f68fa6ce3e52941f589"
IDENTITY_PATH = "experiments/external_sources/chemistry/molecular_electron_affinity_target_identities_v1.json"
IDENTITY_HASH = "sha256:534bdc5572277948cd24ccac5a9bef92e5d31d21966f4dd261efa379f29eeecd"
TARGET_PATH = "experiments/external_sources/chemistry/molecular_electron_affinity_withheld_targets_v1.json"
TARGET_HASH = "sha256:4e7e66d57cd72991da1107d96086b5543cfc4efcf29a37d5a5158cba1abd3d9b"
PAGE_MANIFEST_PATH = "experiments/external_sources/chemistry/molecular_electron_affinity_source_page_manifest_v1.json"
PAGE_MANIFEST_HASH = "sha256:60b4c37ca8f23672de2c2af922a7cc91af4ca374007f1964ba4dac3e311046c6"


for _path, _hash in (
    (CATALOG_PATH, CATALOG_HASH),
    (GUIDE_PATH, GUIDE_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (PAGE_MANIFEST_PATH, PAGE_MANIFEST_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-008 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-molecular-electron-affinity-identities/1"
    or _identity_document.get("all_values_and_state_order_orientations_absent") is not True
    or _identity_document.get("complete_row_count") != 96
    or len(_identity_document.get("rows", ())) != 96
    or not all(row.get("target_value_and_orientation_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-008 identity registry is incomplete or contains a target")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=hash_file(ROOT / str(row["snapshot_path"])),
    )
    for row in _identity_document["rows"]
)


MOLECULAR_ELECTRON_AFFINITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-ELECTRON-AFFINITY-008",
    title="Exact molecular electron-affinity state-order and magnitude law",
    statement=(
        "Molecular electron affinity retains the complete neutral carrier, held electron-gain action and resulting "
        "anion state. Conventional sign is replaced by a held state-order orientation: a bound anion lies below "
        "the neutral-plus-electron state, while an unbound anion lies above it. In either orientation the magnitude "
        "is the exact positive higher-state Take lower-state; coincident states carry structural EmptyOne. The law "
        "and all 96 identities seal before the complete NIST experimental vector opens."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, gain, magnitude, boundary, prediction, record, uncertainty and "
        "extension forms; decide all 256 from admitted exact energy, order, ion, electron-transfer, state-transition "
        "and measurement-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent held-order plus positive-Take relation for every generated neutral/anion state pair, "
        "tested against every explicit experimental molecular electron-affinity record in the complete 192-row "
        "CCCBDB catalog after structurally excluding the 30 single-element atomic carriers: 162 molecular pages, "
        "96 measured molecular rows, 93 bound and three unbound orientations, with all 89 explicit uncertainties."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One retained neutral-plus-electron state and one retained anion state force exactly one of three structural "
        "orders: above, below or coincident; a strict order forces one positive higher Take lower magnitude, while "
        "coincidence forces EmptyOne."
    ),
    induction_step=(
        "Appending one generated molecular carrier preserves every earlier carrier, state order and exact magnitude; "
        "the same three-way order and positive-Take operation decides the appended pair without a species rule."
    ),
    exclusions=(
        "no numerical zero; coincident state heights use structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum proof value",
        "no conventional signed electron-affinity scalar as an SFT proof object",
        "no imported orbital theorem, wavefunction, Hamiltonian or fitted species coefficient",
        "no measured affinity magnitude, sign orientation or uncertainty in the law, grammar or prediction",
        "no favorable-sign selection, dropped unbound row, omitted uncertainty or atomic/molecular conflation",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-ELECTRON-AFFINITY-008",
    expected_observation_label="held-bound-or-unbound-state-order-with-exact-positive-affinity-magnitude",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if any retained neutral/anion pair cannot be represented by one held state-order orientation "
        "and an exact positive higher-state Take lower-state magnitude or structural EmptyOne; if any of the 192 "
        "catalog carriers, 30 atomic exclusions, 162 molecular pages, 96 measured molecular rows, 93 bound rows, "
        "three unbound rows or 89 explicit uncertainties changes or is omitted; if a source minus glyph enters as a "
        "negative SFT number; if a target orientation or magnitude is readable before sealing; or if an imported, "
        "fitted, species-specific or sign-correction rule is introduced."
    ),
)
MOLECULAR_ELECTRON_AFFINITY_SPEC.validate()


__all__ = (
    "CATALOG_HASH", "CATALOG_PATH", "GUIDE_HASH", "GUIDE_PATH", "IDENTITY_HASH", "IDENTITY_PATH",
    "MOLECULAR_ELECTRON_AFFINITY_SPEC", "PAGE_MANIFEST_HASH", "PAGE_MANIFEST_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH",
    "TARGET_REFERENCES",
)
