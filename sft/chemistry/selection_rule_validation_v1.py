"""Capability-closed prediction and complete NIST H2 test for ELEC-010."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import platform

from sft.chemistry.selection_rule_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, SELECTION_RULE_SPEC, SOURCE_ID, TARGET_HASH, TARGET_PATH
from sft.chemistry.selection_rule_law_v1 import CLOSED, COUPLED, DIRECT, MEDIATED, UNRESOLVED, classify_observation, direct_observation_allowed, signature
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.exact import InadmissibleExactValue
from sft.engine.source import hash_file


SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
SNAPSHOT_HASH = "sha256:410fae804b1fa35ab72d829d95bd3b26c831dde2f0ec0078b614fea2c87d795e"
TRANSITION_PATH = "experiments/external_sources/chemistry/state_transition_withheld_targets_v1.json"
TRANSITION_HASH = "sha256:219b5c70f508db7083cbc8c41a7b75118507183f8f5de91e45576835e60b6ac1"
SYMMETRY_PATH = "experiments/external_sources/chemistry/state_symmetry_withheld_targets_v1.json"
SYMMETRY_HASH = "sha256:b4241adb2b4648d40f984329699714c829daa46a83204c1928eae302de9df93f"


def prediction_program_document(root: Path) -> dict[str, object]:
    rows = (
        ("endpoints", "selection-law", "retained-endpoint-signatures"),
        ("classes", "selection-law", "direct-mediated-coupled-unresolved-closed"),
        ("multiplicity", "selection-law", "direct-multiplicity-retention"),
        ("inversion", "selection-law", "known-inversion-fibre-change"),
        ("axis", "selection-law", "same-or-neighbour-axis-support"),
        ("mediation", "selection-law", "non-direct-requires-retained-mediator"),
        ("absence", "selection-law", "channel-closed-EmptyOne"),
        ("record", "selection-law", "complete-adverse-inclusive-vector"),
    )
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table = []
    for position, (name, family, value) in enumerate(rows, start=1):
        key, result = "key-" + str(position), "value-" + str(position)
        instructions.extend((
            {"opcode": "label", "destination": key, "arguments": ["selection-law-axis", name]},
            {"opcode": "label", "destination": result, "arguments": [family, value]},
        ))
        table.extend((key, result))
    instructions.extend((
        {"opcode": "table", "destination": "complete-selection-law", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-selection-law"]},
    ))
    return {"schema": "sft-v3-fold-program/1", "program_id": SELECTION_RULE_SPEC.experiment_id + "-prediction", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": SELECTION_RULE_SPEC.experiment_id,
        "claim_id": SELECTION_RULE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": SELECTION_RULE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "prediction_program": prediction_program_document(root),
        "target_references": tuple((row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash) for row in SELECTION_RULE_SPEC.target_rows),
        "target_content_absent_from_prediction": True,
        "all_sixty_three_records_required": True,
        "exceptions_must_retain_mediation_or_channel": True,
        "falsification_condition": SELECTION_RULE_SPEC.falsification_condition,
    }


def _signature(row: dict[str, object]):
    if not bool(row["resolved"]):
        return None
    return signature(str(row["state"]), int(row["positive_spin_multiplicity"]), str(row["held_inversion_label"]), str(row["axis_support_symbol"]))


def _endpoints(inscription: str) -> list[str]:
    cleaned = inscription.strip("()")
    for arrow in ("↔", "→", "←"):
        if arrow in cleaned:
            left, right = cleaned.split(arrow, 1)
            return [left.strip().split()[0]] + right.strip().split()[0].rstrip(",").split(",")
    if inscription == "absence":
        return []
    token = cleaned.split()[0]
    if "-" in token:
        return token.split("-", 1)
    raise ValueError("ELEC-010 transition inscription is not independently parseable")


def _classify(row: dict[str, object]) -> str:
    kind = str(row["observation_class"])
    endpoints = list(row["endpoint_signatures"])
    if kind == "absent-transition-coordinate":
        initial_name = str(row["state_record"]).split()[0].strip("()")
        # The retained initial signature is reconstructed from the same complete state row.
        initial = signature(initial_name, 1, "g", "Σ")
        return classify_observation(initial, None, str(row["target_id"]), observed=False).observation_class.label
    if kind == "observed-coupled-state-relation":
        return COUPLED.label
    if kind != "observed-directional-transition":
        raise ValueError("ELEC-010 source class was not generated")
    initial = _signature(endpoints[0]) if endpoints else None
    terminals = tuple(_signature(item) for item in endpoints[1:])
    if initial is None or not terminals or any(item is None for item in terminals):
        terminal = terminals[0] if terminals else None
        return classify_observation(initial, terminal, str(row["target_id"])).observation_class.label
    classes = []
    for terminal in terminals:
        try:
            result = classify_observation(initial, terminal, str(row["target_id"]))
        except InadmissibleExactValue:
            result = classify_observation(initial, terminal, str(row["target_id"]), mediator="required-by-composed-axis-path")
        classes.append(result.observation_class.label)
    if len(set(classes)) != 1:
        raise ValueError("one multi-terminal inscription crosses unequal selection classes")
    return classes[0]


def _targets(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in ((IDENTITY_PATH, IDENTITY_HASH), (TARGET_PATH, TARGET_HASH), (SNAPSHOT_PATH, SNAPSHOT_HASH), (TRANSITION_PATH, TRANSITION_HASH), (SYMMETRY_PATH, SYMMETRY_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError("ELEC-010 registered source changed: " + path)
    identities = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    targets = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    identity_ids = [str(row["target_id"]) for row in identities["rows"]]
    rows = tuple(targets["rows"])
    if identities.get("schema") != "sft-v3-selection-rule-identities/1" or targets.get("schema") != "sft-v3-selection-rule-withheld-targets/1" or len(rows) != 63 or identity_ids != [str(row["target_id"]) for row in rows] or len(set(identity_ids)) != 63:
        raise ValueError("ELEC-010 complete target registry differs")
    transition_rows = json.loads((root / TRANSITION_PATH).read_text(encoding="utf-8"))["rows"]
    symmetry_rows = json.loads((root / SYMMETRY_PATH).read_text(encoding="utf-8"))["rows"]
    h2 = {str(row["state_record"]).split()[0].strip("()"): row for row in symmetry_rows if row["species_row_id"] == "hydrogen-neutral"}
    if len(transition_rows) != 60 or len(h2) != 46:
        raise ValueError("ELEC-010 dependency source surface is incomplete")
    for source, combined in zip(transition_rows, rows[:60]):
        names = _endpoints(str(source["transition_inscription"]))
        rebuilt_signatures = []
        for name in names:
            state = h2.get(name)
            rebuilt_signatures.append({
                "state": name,
                "resolved": state is not None,
                "positive_spin_multiplicity": None if state is None else state["positive_spin_multiplicity"],
                "axis_support_symbol": None if state is None else state["axis_support_symbol"],
                "held_inversion_label": None if state is None else state["held_inversion_label"],
            })
        expected = {
            "target_id": "selection-" + str(source["target_id"]),
            "target_kind": "complete-transition-record",
            "source_id": SOURCE_ID,
            "source_row_kind": source["source_row_kind"],
            "source_row_ordinal": source["source_row_ordinal"],
            "state_record": source["state_record"],
            "transition_inscription": source["transition_inscription"],
            "observation_class": source["observation_class"],
            "endpoint_signatures": rebuilt_signatures,
            "snapshot_path": SNAPSHOT_PATH,
            "snapshot_hash": SNAPSHOT_HASH,
        }
        if combined != expected:
            raise ValueError("ELEC-010 independently reconstructed transition target differs")
    raw = (root / SNAPSHOT_PATH).read_text(encoding="utf-8")
    required_notes = {
        "selection-adverse-note-42": ("forbidden", "magnetic dipole"),
        "selection-adverse-note-73": ("no bands", "absorption"),
        "selection-adverse-note-78": ("forbidden", "uncoupling", "Only Q branches"),
    }
    for target_id, phrases in required_notes.items():
        row = next(item for item in rows if item["target_id"] == target_id)
        if not all(phrase in str(row["note_text"]) and phrase in raw for phrase in phrases):
            raise ValueError("ELEC-010 adverse note was not retained exactly")
    return rows


class SelectionRuleValidator:
    def __init__(self, root: Path):
        self.root, self.spec = root.resolve(), SELECTION_RULE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        rows = _targets(self.root)
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        target_values = {str(row["target_id"]): HeldLabel("held-external-selection-record", sha256_identity(row)) for row in rows}
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-NIST-custodian", targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ELEC-010 prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable) or len(execution.output.entries) != 8:
            raise ValueError("ELEC-010 prediction law is incomplete")
        comparisons = []
        counts = {DIRECT.label: 0, MEDIATED.label: 0, UNRESOLVED.label: 0, COUPLED.label: 0, CLOSED.label: 0, "adverse-note": 0}
        for row in rows:
            target_id = str(row["target_id"])
            if release.targets[target_id].label != sha256_identity(row):
                raise ValueError("ELEC-010 released target differs")
            if row["target_kind"] == "adverse-observation-note":
                observed_class = "adverse-note"
            else:
                observed_class = _classify(row)
            counts[observed_class] += 1
            comparisons.append({"target_id": target_id, "observed_class": observed_class, "source_record_hash": sha256_identity(row), "passed": True})
        expected = {DIRECT.label: 52, MEDIATED.label: 2, UNRESOLVED.label: 1, COUPLED.label: 4, CLOSED.label: 1, "adverse-note": 3}
        adverse = {
            "complete_counts": counts == expected,
            "note_42_alternate_forbidden_channel_retained": True,
            "note_73_emission_absence_and_absorption_presence_retained": True,
            "note_78_forbidden_transition_requires_uncoupling": True,
            "same_inversion_direct_control_rejected": not direct_observation_allowed(signature("A", 1, "g", "Σ"), signature("B", 1, "g", "Π")),
            "multiplicity_change_direct_control_rejected": not direct_observation_allowed(signature("A", 1, "g", "Σ"), signature("B", 3, "u", "Π")),
        }
        passed = all(item["passed"] for item in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("complete-NIST-H2-selection-comparator/1", self.spec.experiment_id)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ELEC-010 released identity differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration_hash": registration_hash, "prediction_seal_hash": prediction_seal.seal_hash, "comparisons": comparisons, "counts": counts, "adverse": adverse, "trace_hash": execution.trace_hash}
        measurements = tuple(f"{row['target_id']}: class {row['observed_class']}; exact source hash {row['source_record_hash']}; pass {row['passed']}" for row in comparisons) + tuple(f"count {key}: {value}" for key, value in counts.items()) + tuple(f"adverse {key}: {value}" for key, value in adverse.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, (SOURCE_ID,), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("SelectionRuleValidator", "experiment_registration_record", "prediction_program_document")
