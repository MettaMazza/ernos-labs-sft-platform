"""Registered ELEC-002 molecular electron-count and held-spin specification."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.electron_count_spin_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
INPUT_REGISTRY_PATH = "experiments/external_sources/chemistry/electron_spin_inputs_v1.json"
TARGET_REGISTRY_PATH = "experiments/external_sources/chemistry/electron_spin_withheld_targets_v1.json"
INPUT_REGISTRY_HASH = "sha256:9972d91da982bdae04b8a19e6eeb2c6d22e145b5597e0ca6ba613bae0150b54b"
TARGET_REGISTRY_HASH = "sha256:b7a58ce1a399e415d13def0e22de48f9a90c913840554598864a20d334de48bb"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025"


if hash_file(ROOT / INPUT_REGISTRY_PATH) != INPUT_REGISTRY_HASH:
    raise ValueError("registered electron/spin prediction inputs changed")
if hash_file(ROOT / TARGET_REGISTRY_PATH) != TARGET_REGISTRY_HASH:
    raise ValueError("withheld electron/spin target registry changed")


_inputs = json.loads((ROOT / INPUT_REGISTRY_PATH).read_text(encoding="utf-8"))
if _inputs.get("schema") != "sft-v3-electron-spin-inputs/1" or len(_inputs.get("rows", ())) != 22:
    raise ValueError("electron/spin input registry is incomplete")


TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["row_id"]),
        source_id=SOURCE_ID,
        source_locator=str(row["source_url"]) + " :: Constants of diatomic molecules :: X state",
        snapshot_path=str(row["snapshot_path"]),
        snapshot_hash=str(row["snapshot_hash"]),
    )
    for row in _inputs["rows"]
)


ELECTRON_COUNT_SPIN_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELECTRON-COUNT-SPIN-002",
    title="Exact molecular electron count and held-spin organization",
    statement=(
        "For every positive finite molecular nuclear support, the complete electron occurrence count is forced by "
        "atomic-number occurrences and a held adjoin/remove transfer; every occurrence then has exactly one of two "
        "held spin fibres, same-fibre same-cell doubling is excluded, and the support decomposes uniquely at a declared "
        "spin width into complementary pairs plus unmatched held fibres."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal Cartesian product of nuclear support, charge representation, electron census, spin "
        "carrier, cell occupation, pair/surplus decomposition, observable width and extension choices. Decide every "
        "one of the 256 forms solely by preservation of admitted exact arithmetic, atomic-number, ion, spin, "
        "indistinguishability, exclusion, information and molecular-state laws."
    ),
    grammar_boundary=(
        "Every positive finite molecular multiset of admitted atomic-number occurrences, structural empty-One or a "
        "positive held electron-transfer count that leaves positive support, and every positive spin width. Closure is "
        "depth-independent: adjoining one nucleus, electron occurrence, complementary pair or unmatched fibre repeats "
        "the same local census, two-fibre, exclusion and complete-support checks."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One admitted nucleus supplies its positive atomic-number occurrence support. After any lawful held transfer, "
        "one retained electron occurrence requires one named support cell, one of two spin fibres and spin width two."
    ),
    induction_step=(
        "Adjoining one admitted nucleus expands support by its exact atomic-number count; adjoining or removing one "
        "held charge occurrence changes support by one without a signed scalar; adjoining a complementary fibre pair "
        "preserves width, while adjoining one unmatched fibre advances width by one. No species rule or measurement "
        "enters any successor."
    ),
    exclusions=(
        "no numerical-zero, negative, irrational, imaginary or floating proof value",
        "no signed charge or signed-spin proof coordinate",
        "no imported orbital occupation table, Hamiltonian, wavefunction or ground-state solver",
        "no measured state term or multiplicity in the derivation, candidate generator or prediction inputs",
        "no fitted, learned, species-specific or target-derived parameter",
        "no omitted, selected or silently corrected external row",
        "external state terms open only after the complete prediction vector is sealed",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELECTRON-COUNT-SPIN-002",
    expected_observation_label="exact-electron-count-and-spin-width-parity-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_REGISTRY_PATH,
    falsification_condition=(
        "The claim fails if electron occurrence support differs from the complete atomic-number/held-transfer census; "
        "if a same-fibre duplicate occupies one cell; if complete support cannot be decomposed into complementary pairs "
        "and unmatched held fibres; if any NIST X-state multiplicity violates the sealed count/width parity; if any "
        "registered neutral, cation or anion row is omitted; or if a changed charge, state width, source byte, target "
        "row, prediction trace or adverse control is accepted."
    ),
)


ELECTRON_COUNT_SPIN_SPEC.validate()


__all__ = (
    "ELECTRON_COUNT_SPIN_SPEC",
    "INPUT_REGISTRY_HASH",
    "INPUT_REGISTRY_PATH",
    "SOURCE_ID",
    "TARGET_REGISTRY_HASH",
    "TARGET_REGISTRY_PATH",
    "TARGET_REFERENCES",
)
