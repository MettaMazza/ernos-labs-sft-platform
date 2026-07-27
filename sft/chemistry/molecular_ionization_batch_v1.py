"""Registered exact relation and blind NIST vector for Chemistry PROP-007."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.molecular_ionization_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/molecular_ionization_target_identities_v1.json"
IDENTITY_HASH = "sha256:c14f627c7e247f01fc02243fce3d9cf6e06be5df92f1edf855787c0703f79c9c"
TARGET_PATH = "experiments/external_sources/chemistry/molecular_ionization_withheld_targets_v1.json"
TARGET_HASH = "sha256:f2e1f1fbfda163d5e13e5256ab74d2d519adcfc2ee04b21e4bf5b8906ca198f8"
GUIDE_PATH = "experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1/nist-webbook-gas-phase-ion-thermochemistry.html"
GUIDE_HASH = "sha256:3037004952cc27531f9ff87ed9f403e7dc2fd3c7293881a3ab3b7bfb9a5523d6"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1/molecular-ionization-primary-records-v1.json"
PRIMARY_HASH = "sha256:060293fa3a611e46a26fc0ac004a9933542c6b61ecc48c3a9e84bd320b755212"


for _path, _hash in (
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (GUIDE_PATH, GUIDE_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-007 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-molecular-ionization-identities/1"
    or _identity_document.get("all_ionization_values_absent") is not True
    or _identity_document.get("complete_row_count") != 9
    or len(_identity_document.get("rows", ())) != 9
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-007 identity registry is incomplete or contains a measurement")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _identity_document["rows"]
)


MOLECULAR_IONIZATION_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-IONIZATION-ENERGY-007",
    title="Exact molecular ionization-energy and terminal-state ordering law",
    statement=(
        "Molecular ionization retains the complete neutral carrier, held electron-removal orientation and "
        "resulting positive-ion state. Its required energy is the ordered positive Take from the bound initial "
        "state height to the separated ion-plus-electron terminal height. Adiabatic ionization is the least Take "
        "over complete generated terminal support; a vertical held-geometry terminal is a member of that support "
        "and therefore cannot lie below the adiabatic least Take. The relation and all nine identities seal before "
        "the NIST experimental energy vector opens."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, transformation, magnitude, path, order, prediction, record "
        "and extension forms; decide all 256 forms from admitted exact energy, state-transition, order, ion and "
        "measurement-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent ordered positive ionization Take and adiabatic/vertical terminal-state order, "
        "tested at the finite complete first-nine-neutral-diatomic boundary inherited value-free from PROP-006: "
        "D2, HD, H2, N2, CO, NO, O2, HF and F2, retaining initial state and conformation, resulting ionic state, "
        "held removed carrier, path, method, condition, units, uncertainty class and official source identity."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One complete neutral state and one strictly higher separated ion-plus-electron state force one exact "
        "positive terminal-from-initial Take; the least member of a nonempty finite terminal support exists."
    ),
    induction_step=(
        "Appending one generated ionic terminal preserves every earlier Take; the adiabatic value remains the "
        "least complete-support member or becomes the new smaller positive member, while every held-geometry "
        "vertical member remains not below the resulting least member."
    ),
    exclusions=(
        "no numerical zero, negative, irrational, imaginary, floating or continuum proof value",
        "no signed electron energy, negative orbital scalar or erased removal orientation",
        "no imported Koopmans theorem, orbital equality, wavefunction, Hamiltonian or fitted molecular coefficient",
        "no measured ionization energy, uncertainty or source inscription in the law, grammar or prediction",
        "no conflation of adiabatic and vertical terminal-state custody",
        "no erased neutral carrier, initial state, conformation, resulting ionic state, method or condition",
        "no selected isotope, favorable row, dropped uncertainty or species correction",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-IONIZATION-ENERGY-007",
    expected_observation_label="exact-positive-terminal-from-initial-ionization-Take-with-complete-state-custody",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a registered separated ion-plus-electron state does not lie at an exact positive Take "
        "from its retained neutral state; if a held-geometry vertical terminal lies below the least complete-support "
        "adiabatic terminal; if any of the nine post-seal NIST records is absent, duplicated, displaced, non-positive "
        "or detached from its initial and resulting states, method, condition, units and uncertainty class; if a "
        "target value is readable before sealing; or if a signed, continuum, imported, fitted or species-specific "
        "correction rule is introduced."
    ),
)
MOLECULAR_IONIZATION_SPEC.validate()


__all__ = (
    "GUIDE_HASH", "GUIDE_PATH", "IDENTITY_HASH", "IDENTITY_PATH", "MOLECULAR_IONIZATION_SPEC",
    "PRIMARY_HASH", "PRIMARY_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
