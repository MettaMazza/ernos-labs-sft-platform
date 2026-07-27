"""Registered KIN-001 law and complete declared elementary-rate surface."""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.elementary_transition_rate_law_v1 import DEPENDENCIES, DIMENSIONS, EXACT_RESULT, OPERATIONAL_WITNESSES
from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.source import hash_file


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_ROOT = "experiments/external_sources/chemistry/snapshots/kin-001-elementary-transition-rate-v1"
SPEC_PATH = "experiments/external_sources/chemistry/elementary_transition_rate_capture_spec_v1.json"
SPEC_HASH = "sha256:1274bb6d4768a49627ce2629d951df65405105cfe5b7cd6123e06b504371e29f"
PRIMARY_PATH = f"{SNAPSHOT_ROOT}/elementary-transition-rate-primary-records-v1.json"
PRIMARY_HASH = "sha256:9adbf7bae394a5edc6859973519fd0b4b57f8a50396535a16a18edf9e5d1d766"
IDENTITY_PATH = "experiments/external_sources/chemistry/elementary_transition_rate_target_identities_v1.json"
IDENTITY_HASH = "sha256:e7cfae2a24ff1d52a4fe2d9704b0a608dee95fb15442bb17e5636d20a044cda3"
TARGET_PATH = "experiments/external_sources/chemistry/elementary_transition_rate_withheld_targets_v1.json"
TARGET_HASH = "sha256:6044024fe4650e8e99c66d992b12aff3cf12d2332b82ff2b6749e967e3499343"
SOURCE_FILES = (
    (f"{SNAPSHOT_ROOT}/nist-srd17-1972tin-koo3-15.html", "sha256:68562ee063103f727b882119f3e76c100aa4f59d6bee0aec0da96f26b669b3ba"),
    (f"{SNAPSHOT_ROOT}/nist-srd17-1967wil2017-1.html", "sha256:6986b45f216c45e26dbbc1532b94d4005946e83dbf5c2cb5e69f3355bf249ccd"),
    (f"{SNAPSHOT_ROOT}/nist-srd17-1967avr-kra501-503-1.html", "sha256:8318565032c709a5990eaab78ca570d551bca536b931632990eebee279b8c8c6"),
    (f"{SNAPSHOT_ROOT}/nist-srd17-1962ash-bur685-691-1.html", "sha256:f41bc74df29304de470c805b3d51a753889da9990e6c4f316168048be23b08ec"),
)


for path, expected in ((SPEC_PATH, SPEC_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), *SOURCE_FILES):
    if hash_file(ROOT / path) != expected:
        raise ValueError(f"KIN-001 registered source changed: {path}")

_primary = json.loads((ROOT / PRIMARY_PATH).read_text())
_identities = json.loads((ROOT / IDENTITY_PATH).read_text())
if (
    _primary.get("complete_source_count") != 4
    or _primary.get("complete_target_count") != 46
    or _primary.get("source_declared_order_row_counts") != {"1": 4, "2": 24, "3": 18}
    or _primary.get("all_declared_source_pages_and_rate_rows_preserved") is not True
    or _identities.get("complete_target_count") != 46
    or _identities.get("all_reaction_state_condition_method_expression_temperature_rate_value_and_target_hash_values_absent") is not True
    or len(_identities.get("rows", ())) != 46
):
    raise ValueError("KIN-001 complete source boundary changed")

_source_path_by_id = {
    row["source_id"]: row["snapshot_path"] for row in _primary["source_summaries"]
}
_source_hash_by_id = {
    row["source_id"]: row["snapshot_hash"] for row in _primary["source_summaries"]
}
TARGET_REFERENCES = tuple(
    ChemistryTargetReference(
        target_id=row["target_id"], source_id=row["source_id"],
        source_locator=f"NIST SRD 17 record {row['record_id']} rate-table row {row['source_row_ordinal']}",
        snapshot_path=_source_path_by_id[row["source_id"]], snapshot_hash=_source_hash_by_id[row["source_id"]],
    ) for row in _identities["rows"]
)


ELEMENTARY_TRANSITION_RATE_SPEC = EmpiricalChemistrySpec(
    claim_id="SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    title="Exact elementary-transition rate relation",
    statement=(
        "An elementary chemical transition rate is the exact positive count of completed instances of one registered "
        "transition between distinct retained molecular states per positive reference tick and observation support, with "
        "conditions held and direction represented as a label. The declared NIST rate inscriptions are opened only after "
        "the complete identity vector and native relation seal."
    ),
    dependencies=DEPENDENCIES,
    generation_rule="Generate the literal product of carrier, state, event, recurrence, boundary, magnitude, prediction and extension forms; decide all 256 candidates only from admitted state-transition, conservation, exact-resource, molecular-state, mechanism, statistical-support, EmptyOne and finite-successor laws.",
    grammar_boundary="Every finite registered elementary chemical transition between distinct molecular states with complete conditions, positive completed-event count, positive tick count and positive observation support. External testing preserves all 46 rate rows from four complete declared NIST SRD 17 experimental records.",
    dimensions=DIMENSIONS,
    exact_result=EXACT_RESULT,
    induction_base="One registered elementary transition completed once on one positive tick and one positive observation support supplies the least rate record.",
    induction_step="Appending a complete condition or measurement record preserves all earlier distinctions; common completed-event/tick replication preserves the exact quotient without refitting.",
    exclusions=(
        "no numerical zero; absent external coordinates are structural EmptyOne",
        "no negative, irrational, imaginary, logarithmic, floating, signed or continuum SFT proof value",
        "no imported mass-action equation, reaction order, Arrhenius form, fitted rate constant, concentration derivative or continuum time",
        "no interpolation, regression, selected reaction/state/condition/method/source/row or target-derived correction",
        "no reaction, state, condition, method, expression, temperature, rate value or target hash before prediction seal",
        "source-reported Arrhenius tabulations remain post-seal external records and are not described as raw event counts",
    ),
    operational_witnesses=OPERATIONAL_WITNESSES,
    experiment_id="SFT-EXP-CHEM-ELEMENTARY-TRANSITION-RATE-001",
    expected_observation_label="complete-declared-elementary-transition-rate-vector",
    target_rows=TARGET_REFERENCES,
    observation_registry_path=TARGET_PATH,
    falsification_condition=(
        "The claim fails if reaction identity, either molecular endpoint, condition, completed event, tick, observation "
        "support or direction is erased; if a prohibited number or imported conventional/fitted law enters; if target "
        "content opens before all 46 row identities seal; if any declared NIST page or rate row is omitted; if an "
        "Arrhenius tabulation is mislabeled as a raw event count; or if any target is tampered."
    ),
)
ELEMENTARY_TRANSITION_RATE_SPEC.validate()


__all__ = (
    "ELEMENTARY_TRANSITION_RATE_SPEC", "IDENTITY_HASH", "IDENTITY_PATH", "PRIMARY_HASH", "PRIMARY_PATH",
    "SOURCE_FILES", "SPEC_HASH", "SPEC_PATH", "TARGET_HASH", "TARGET_PATH", "TARGET_REFERENCES",
)
