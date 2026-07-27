"""Registered exact recurrence law and blind NIST vector for Chemistry PROP-009."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.vibrational_frequency_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/prop-009-vibrational-frequency-v1/nist-cccbdb-complete-paired-fundamental-frequency-surface.html"
SNAPSHOT_HASH = "sha256:f74cc33252361160595a571e19a22ab5196fe51ede9b021231ffd9ee046c747a"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-009-vibrational-frequency-v1/vibrational-frequency-primary-records-v1.json"
PRIMARY_HASH = "sha256:e437a6ecb62f7d1303556276caa28823d09be8230d4efa3632c76aad83a5f063"
IDENTITY_PATH = "experiments/external_sources/chemistry/vibrational_frequency_target_identities_v1.json"
IDENTITY_HASH = "sha256:b81b78c1ef2ffaa62cf8d4da76a0c6a47e04a948dffa0e77921be490ea3d136a"
TARGET_PATH = "experiments/external_sources/chemistry/vibrational_frequency_withheld_targets_v1.json"
TARGET_HASH = "sha256:a2d26c4c8dcf397c76cbf871b439522beeb528f31cc8c628d7ce466de0b9a0d9"


for _path, _hash in (
    (SNAPSHOT_PATH, SNAPSHOT_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-009 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-vibrational-frequency-identities/1"
    or _identity_document.get("all_frequency_values_absent") is not True
    or _identity_document.get("complete_displayed_molecule_count") != 145
    or _identity_document.get("complete_row_count") != 2009
    or len(_identity_document.get("rows", ())) != 2009
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-009 identity registry is incomplete or contains a frequency target")

TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=str(row["target_id"]),
        source_id=str(row["source_id"]),
        source_locator=str(row["source_locator"]),
        snapshot_path=SNAPSHOT_PATH,
        snapshot_hash=SNAPSHOT_HASH,
    )
    for row in _identity_document["rows"]
)


VIBRATIONAL_FREQUENCY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-VIBRATIONAL-FREQUENCY-009",
    title="Exact molecular vibrational recurrence-frequency law",
    statement=(
        "A molecular vibrational frequency is derived from a complete retained molecule, mode and symmetry carrier "
        "as the exact positive count of finite recurrences divided by a positive observation-interval count. A "
        "conventional reciprocal-centimeter inscription is a held unit translation applied only after that ratio "
        "exists. All 2,009 displayed NIST mode identities seal before 1,984 positive measurements and 25 structural "
        "measurement absences open; theoretical frequencies, ratios and fitted scale factors are excluded."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, recurrence, magnitude, mode, translation, prediction, record and "
        "extension forms; decide all 256 from admitted exact arithmetic, recurrence, wave-frequency, spectroscopy, "
        "molecular-transition and measurement-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent exact recurrence-count/positive-interval relation for every generated finite mode, "
        "tested against the complete 2,009-row table actually displayed by the frozen official NIST CCCBDB page: "
        "145 displayed molecules, 1,984 positive experimental frequencies and 25 displayed absences. The page's "
        "advertised 164 molecules/2,452 vibrations and its undisplayed difference of 19/443 remain explicit."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One positive recurrence over one positive observation interval forces one exact positive ratio while "
        "retaining molecule, mode, symmetry and transition identity."
    ),
    induction_step=(
        "Appending an equal positive observation interval and its corresponding finite recurrence count scales "
        "numerator and denominator together and preserves the exact frequency; appending a distinct mode preserves "
        "all preceding mode identities and applies the same ratio law."
    ),
    exclusions=(
        "no numerical zero; missing source measurements use structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum proof value",
        "no continuum sinusoid, differential equation or harmonic-oscillator premise",
        "no theoretical frequency, experimental/theoretical ratio, fitted scale factor or species residual",
        "no measured frequency in the law, grammar, candidate forcing or prediction",
        "no dropped source absence or concealed advertised/displayed source-count discrepancy",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-VIBRATIONAL-FREQUENCY-009",
    expected_observation_label="exact-positive-finite-recurrence-ratio-with-held-mode-and-unit-translation",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a generated molecular vibrational frequency cannot be reconstructed as a positive finite "
        "recurrence count over a positive interval while retaining molecule, mode and symmetry; if equal-interval "
        "repetition changes that ratio; if any of the 2,009 displayed rows, 145 molecules, 1,984 measured values or "
        "25 displayed absences is omitted, duplicated or displaced; if the advertised 164/2,452 versus displayed "
        "145/2,009 boundary is hidden; if any target opens before sealing; or if a continuum, theoretical, fitted, "
        "scaled or species-specific rule enters."
    ),
)
VIBRATIONAL_FREQUENCY_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH", "SNAPSHOT_HASH", "SNAPSHOT_PATH",
    "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES", "VIBRATIONAL_FREQUENCY_SPEC",
)
