"""Registered exact relation and blind NIST vector for Chemistry PROP-006."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_polarizability_law_v1 import (
    DEPENDENCIES,
    DIMENSIONS,
    EXACT_RESULT,
    OPERATIONAL_WITNESSES,
)
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
IDENTITY_PATH = "experiments/external_sources/chemistry/molecular_polarizability_target_identities_v1.json"
IDENTITY_HASH = "sha256:fccda61ada2280f7e84a80e10e6184f476a8c40b583e9f5f0dc63e8a652ef1d6"
TARGET_PATH = "experiments/external_sources/chemistry/molecular_polarizability_withheld_targets_v1.json"
TARGET_HASH = "sha256:10d6771a8ceaf1cfff2a0fa6e6789d29dcbf01687d62441d7945341ba61889ed"
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/prop-006-nist-cccbdb-experimental-polarizabilities-v1.html"
SNAPSHOT_HASH = "sha256:179fbbdd73c90635dd695919f5b0d63de980f9f792d1ec9d3ac9ccf9e8dfef7f"
PRIMARY_PATH = "experiments/external_sources/chemistry/snapshots/prop-006-molecular-polarizability-primary-records-v1.json"
PRIMARY_HASH = "sha256:0b55742a205927a3954805e8917722dfadd35ee308a39019164849c26695a829"


for _path, _hash in (
    (IDENTITY_PATH, IDENTITY_HASH),
    (TARGET_PATH, TARGET_HASH),
    (SNAPSHOT_PATH, SNAPSHOT_HASH),
    (PRIMARY_PATH, PRIMARY_HASH),
):
    if hash_file(ROOT / _path) != _hash:
        raise ValueError(f"PROP-006 registered source changed: {_path}")

_identity_document = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))
if (
    _identity_document.get("schema") != "sft-v3-molecular-polarizability-identities/1"
    or _identity_document.get("all_polarizability_values_absent") is not True
    or _identity_document.get("complete_molecular_row_count") != 252
    or len(_identity_document.get("rows", ())) != 252
    or not all(row.get("target_value_absent") is True for row in _identity_document["rows"])
):
    raise ValueError("PROP-006 identity registry is incomplete or contains a measurement")

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


MOLECULAR_POLARIZABILITY_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-MOLECULAR-POLARIZABILITY-006",
    title="Exact molecular polarizability response and isotropic-composition law",
    statement=(
        "A molecular polarizability component is the exact positive ratio between a retained induced-dipole "
        "distinction and the retained external electric distinction that causes it. Repeating equal field acts "
        "preserves this ratio at every generated depth. At the admitted three-axis boundary, the isotropic "
        "response is the exact one-third Junction of the three held component responses. The complete identity "
        "and relation vector seals before every one of the 252 NIST molecular alpha inscriptions opens."
    ),
    dependencies=DEPENDENCIES,
    generation_rule=(
        "Generate the literal product of carrier, response, orientation, composition, successor, prediction, "
        "record-completeness and extension forms; decide all 256 forms from admitted exact response, electric "
        "distinction, three-axis composition and measurement-custody laws."
    ),
    grammar_boundary=(
        "The depth-independent exact response-ratio and three-axis isotropic-composition laws, tested at the "
        "finite complete NIST CCCBDB non-atomic boundary: all 252 molecular rows in source order, retaining "
        "formula, name, molecular state, conformation, field-response definition, method, condition, units, "
        "reference and comment. All alpha inscriptions remain withheld until after relation sealing."
    ),
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base=(
        "One positive electric distinction producing one positive induced molecular dipole distinction forces "
        "their exact positive response ratio; three distinct held axes force their exact one-third Junction."
    ),
    induction_step=(
        "Appending one equal electric act adds one equal field part and one equal response part, so numerator "
        "and denominator acquire the same positive count and the exact response ratio is unchanged at every "
        "finite depth; appending a molecular record changes no law or prior record."
    ),
    exclusions=(
        "no numerical zero, negative, irrational, imaginary, floating or continuum proof value",
        "no signed Cartesian component, continuum derivative, tensor calculus or perturbation series in proof",
        "no imported wavefunction, Hamiltonian, molecular model, basis set or fitted response coefficient",
        "no measured alpha, source inscription, reference value or table score in the law, grammar or prediction",
        "no erased formula, name, state, conformation, field definition, method, condition, unit or reference",
        "no selected species, source cohort, favorable subset or dropped comment row",
        "no numerical prediction for an ungenerated molecule and no claim beyond the registered static-response boundary",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-MOLECULAR-POLARIZABILITY-006",
    expected_observation_label="positive-exact-molecular-response-record-under-one-depth-independent-ratio-law",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if the exact response ratio changes under any generated equal-field successor; if the "
        "isotropic carrier is not exactly the one-third Junction of three distinct held positive components; if "
        "any of the 252 post-seal NIST molecular alpha records is absent, duplicated, displaced, non-positive or "
        "not bound to its formula, state, conformation, units, reference and source row; if target content is "
        "readable before sealing; or if a signed, irrational, continuum, imported, fitted or species-specific "
        "correction rule is introduced."
    ),
)
MOLECULAR_POLARIZABILITY_SPEC.validate()


__all__ = (
    "IDENTITY_HASH", "IDENTITY_PATH", "MOLECULAR_POLARIZABILITY_SPEC", "PRIMARY_HASH",
    "PRIMARY_PATH", "SNAPSHOT_HASH", "SNAPSHOT_PATH", "TARGET_HASH", "TARGET_PATH",
    "TARGET_REFERENCES",
)
