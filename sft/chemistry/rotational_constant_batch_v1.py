"""Registered held-axis recurrence law and blind NIST vector for Chemistry PROP-010."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.rotational_constant_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
LIST_SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/nist-cccbdb-complete-species-list.html"
LIST_SNAPSHOT_HASH = "sha256:bb76b24354857b06f9ef8b9c29406b4627e60d0dcde846932af56fd64a27fa64"
CHOICE_SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/nist-cccbdb-complete-rotational-choice-surface.html"
CHOICE_SNAPSHOT_HASH = "sha256:d54304bf3f790c204893f3bfcb27f56b4fb8d6b0919108273ea2ed40cc39e7a9"
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/nist-cccbdb-complete-rotational-constant-surface.html"
SNAPSHOT_HASH = "sha256:35d81c2d0230deee699c039c0dc9520cd69c2f4079b633991788f44d80d09253"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1/rotational-constant-primary-records-v1.json"
PRIMARY_HASH = "sha256:9b028e7a655d95d24feff86a9b1a9f457164296c1ebeec197af4302aad39f9b6"
IDENTITY_PATH = "experiments/external_sources/chemistry/rotational_constant_target_identities_v1.json"
IDENTITY_HASH = "sha256:bd8801129b8cc67b3c2000cf652a6778ef5088ba9e5271aeae752348329002d2"
TARGET_PATH = "experiments/external_sources/chemistry/rotational_constant_withheld_targets_v1.json"
TARGET_HASH = "sha256:da4d118b4451015e5399469cc6c9b03b492996052e1b20fdf2107a104fa9f264"


for _path, _hash in (
    (LIST_SNAPSHOT_PATH, LIST_SNAPSHOT_HASH),
    (CHOICE_SNAPSHOT_PATH, CHOICE_SNAPSHOT_HASH),
    (SNAPSHOT_PATH, SNAPSHOT_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-010 registered source changed: {_path}")


_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
_forbidden = {
    "measurement_present", "rotational_constant_inscription_cm_inverse",
    "exact_positive_axis_recurrence_ratio_per_centimeter", "external_measurement_absence",
}
if (
    _identity_document.get("schema") != "sft-v3-rotational-constant-identities/1"
    or _identity_document.get("all_rotational_constant_values_absent") is not True
    or _identity_document.get("complete_displayed_molecular_row_count") != 1005
    or _identity_document.get("complete_row_count") != 3015
    or len(_identity_document.get("rows", ())) != 3015
    or not all(
        row.get("target_value_absent") is True and not _forbidden.intersection(row)
        for row in _identity_document["rows"]
    )
):
    raise ValueError("PROP-010 identity registry is incomplete or contains a rotational target")


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


ROTATIONAL_CONSTANT_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ROTATIONAL-CONSTANT-010",
    title="Exact molecular held-axis rotational-constant law",
    statement=(
        "A molecular rotational constant is derived from a complete retained molecular state, finite generated "
        "geometry and held principal axis as the exact positive count of completed axis recurrences divided by a "
        "positive observation-interval count. Positive rotational ordinals force J(J+1) levels and adjacent 2J "
        "gaps; the unexcited form is structural EmptyOne. Every value-free identity from the complete official "
        "NIST list-to-choice-to-result route seals before 1,681 positive A/B/C measurements and 1,334 blank axis "
        "cells open. No rigid rotor, inertia equation, continuum angle or fitted molecular coefficient enters."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, axis, magnitude, ladder, translation, prediction, record and "
        "extension forms; decide all 256 candidates from admitted exact geometry, recurrence, spectroscopy, "
        "molecular composition and measurement-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent held-axis recurrence ratio and positive rotational ladder, tested against every "
        "row returned by all 1,193 elemental-composition queries generated from all 2,186 entries of the frozen "
        "official NIST complete species list: 1,832 returned charge/state choices, 1,005 displayed molecular "
        "property rows and all 3,015 A/B/C cells. The 83 listed compositions with no returned selectable row "
        "remain explicit and are not misreported as measured."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One positive recurrence on one held generated axis over one positive interval forces one exact constant; "
        "the first positive rotational ordinal forces multiplier two while the unexcited form remains EmptyOne."
    ),
    induction_step=(
        "Equal repetition scales recurrence and interval counts together and preserves their ratio; appending one "
        "positive rotational ordinal preserves prior levels and forces the next J(J+1) level and 2J gap; appending "
        "a distinct held axis preserves all preceding axis identities and applies the same recurrence law."
    ),
    exclusions=(
        "no numerical zero; missing source measurements and the unexcited form use structural EmptyOne",
        "no negative, irrational, imaginary, floating, signed or continuum proof value",
        "no rigid-rotor equation, freely rotating continuum body, trigonometric angle or imported moment of inertia",
        "no measured rotational constant in the law, grammar, candidate forcing or prediction",
        "no fitted geometry, inertia, molecular scale, species correction or residual",
        "no dropped blank A/B/C cell, unreturned composition, returned state or retrieval batch",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ROTATIONAL-CONSTANT-010",
    expected_observation_label="exact-positive-held-axis-recurrence-ratio-or-structural-EmptyOne-with-complete-source-custody",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if a generated molecular rotational constant cannot be reconstructed as a positive finite "
        "held-axis recurrence count over a positive interval while preserving molecular state and geometry; if "
        "equal repetition changes the ratio; if the J(J+1) level or 2J gap fails at any positive ordinal; if any "
        "of the 2,186 listed species, 1,193 composition queries, 1,832 returned choices, 83 unreturned composition "
        "boundaries, 1,005 displayed molecular rows, 1,681 measurements or 1,334 blank axis cells is concealed, "
        "duplicated or displaced; if any target opens before sealing; or if an imported, continuum, fitted or "
        "species-specific rule enters."
    ),
)
ROTATIONAL_CONSTANT_SPEC.validate()


__all__ = (
    "CHOICE_SNAPSHOT_HASH", "CHOICE_SNAPSHOT_PATH", "IDENTITY_HASH", "IDENTITY_PATH",
    "LIST_SNAPSHOT_HASH", "LIST_SNAPSHOT_PATH", "PRIMARY_HASH", "PRIMARY_PATH",
    "ROTATIONAL_CONSTANT_SPEC", "SNAPSHOT_HASH", "SNAPSHOT_PATH", "TARGET_HASH", "TARGET_PATH",
    "TARGET_REFERENCES",
)
