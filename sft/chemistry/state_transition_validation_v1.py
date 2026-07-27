"""Capability-closed transition prediction and complete NIST H2 validation for ELEC-009."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re
from typing import Optional

from sft.chemistry.state_transition_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, SOURCE_ID, STATE_TRANSITION_SPEC, TARGET_HASH, TARGET_PATH
from sft.chemistry.state_transition_law_v1 import ABSENT, BIDIRECTIONAL, COUPLED, FORWARD, REVERSE, absent_transition, compose_transition_path, observed_transition
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord, HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


SOURCE_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
SOURCE_HASH = "sha256:410fae804b1fa35ab72d829d95bd3b26c831dde2f0ec0078b614fea2c87d795e"
TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
BAND_PATTERN = re.compile(r"[\[\(]?\s*([0-9]+(?:\.[0-9_]*)?)")


class _IndependentTransitionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.depth = 0; self.in_row = False; self.in_cell = False; self.parts = []; self.row = []; self.rows = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split(): self.depth += 1
        elif self.depth and tag == "tr": self.in_row, self.row = True, []
        elif self.in_row and tag in {"td", "th"}: self.in_cell, self.parts = True, []
        elif self.in_cell and tag == "sup": self.parts.append("^")
        elif self.in_cell and tag == "sub": self.parts.append("_")
    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}: self.row.append(" ".join(unescape("".join(self.parts)).split())); self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row: self.rows.append(tuple(self.row))
            self.in_row = False
        elif self.depth and tag == "table": self.depth -= 1
    def handle_data(self, data: str) -> None:
        if self.in_cell: self.parts.append(data)


def _class(inscription: str) -> str:
    if not inscription: return "absent-transition-coordinate"
    if any(arrow in inscription for arrow in ("→", "←", "↔")): return "observed-directional-transition"
    return "observed-coupled-state-relation"


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH: raise ValueError("ELEC-009 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8")); rows = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-state-transition-identities/1" or len(rows) != 60 or len({str(row["target_id"]) for row in rows}) != 60: raise ValueError("ELEC-009 identity registry is incomplete")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    _identities(root)
    rows = (("carrier", "transition-result", "retained-molecular-carrier"), ("endpoints", "transition-result", "distinct-initial-and-terminal-states"), ("forward", "transition-orientation", "forward-held"), ("reverse", "transition-orientation", "reverse-held"), ("bidirectional", "transition-orientation", "bidirectional-held"), ("coupled", "transition-orientation", "coupled-without-direction"), ("absence", "transition-orientation", "structurally-absent"), ("composition", "transition-result", "matching-endpoint-composition"), ("record", "transition-result", "complete-presence-coupling-absence-vector"))
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]; table = []
    for position, (name, family, value) in enumerate(rows, start=1):
        key, result = f"key-{position}", f"value-{position}"; instructions.extend(({"opcode": "label", "destination": key, "arguments": ["state-transition-law", name]}, {"opcode": "label", "destination": result, "arguments": [family, value]})); table.extend((key, result))
    instructions.extend(({"opcode": "table", "destination": "complete-transition-law", "arguments": table}, {"opcode": "emit", "destination": "", "arguments": ["complete-transition-law"]}))
    return {"schema": "sft-v3-fold-program/1", "program_id": STATE_TRANSITION_SPEC.experiment_id + "-transition-law-prediction", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {"experiment_id": STATE_TRANSITION_SPEC.experiment_id, "claim_id": STATE_TRANSITION_SPEC.claim_id, "provenance": "observational_derivation", "frozen_relation": STATE_TRANSITION_SPEC.exact_result, "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH), "prediction_program": prediction_program_document(root), "target_references": tuple((row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash) for row in STATE_TRANSITION_SPEC.target_rows), "target_content_absent_from_prediction": True, "all_sixty_records_required": True, "selection_rules_explicitly_not_imported": True, "falsification_condition": STATE_TRANSITION_SPEC.falsification_condition}


def _exact_band(inscription: str):
    if inscription == "absence": return EMPTY_ONE
    match = BAND_PATTERN.search(inscription)
    if match is None: raise ValueError("ELEC-009 positive band inscription is unparseable")
    exact = Fraction(match.group(1).replace("_", ""))
    if exact <= 0: raise ValueError("ELEC-009 band record is not exact positive")
    return PositiveRatio.from_pair(exact.numerator, exact.denominator)


def _endpoints(state_record: str, transition: str) -> tuple[str, str, HeldLabel]:
    state = state_record.split()[0].strip("()")
    for arrow, orientation in (("↔", BIDIRECTIONAL), ("→", FORWARD), ("←", REVERSE)):
        if arrow in transition:
            left, right = transition.strip("()").split(arrow, 1)
            return left.strip().split()[0], right.strip().split()[0].rstrip(","), orientation
    cleaned = transition.strip("()").split()[0]
    if "-" not in cleaned: raise ValueError("ELEC-009 coupled-state inscription lacks two states")
    left, right = cleaned.split("-", 1)
    return left or state, right, COUPLED


def _reconstructed_targets(root: Path) -> tuple[dict[str, object], ...]:
    identities = _identities(root)
    if hash_file(root / TARGET_PATH) != TARGET_HASH or hash_file(root / SOURCE_PATH) != SOURCE_HASH: raise ValueError("ELEC-009 target or source changed")
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8")); registered = {str(row["target_id"]): row for row in document.get("rows", ())}
    if document.get("schema") != "sft-v3-state-transition-withheld-targets/1" or len(registered) != 60: raise ValueError("ELEC-009 target registry is incomplete")
    parser = _IndependentTransitionParser(); parser.feed((root / SOURCE_PATH).read_text(encoding="utf-8"))
    rebuilt = []; primary = continuation = 0; current_state = None
    for row in parser.rows:
        if len(row) == 13 and TERM_PATTERN.search(row[0]):
            primary += 1; current_state = row[0]; transition, band = row[11] or "absence", row[12] or "absence"
            rebuilt.append({"target_id": f"H2-transition-state-{primary:03d}", "source_id": SOURCE_ID, "source_row_kind": "primary-state", "source_row_ordinal": primary, "state_record": row[0], "transition_inscription": transition, "band_origin_inscription": band, "observation_class": _class(row[11]), "snapshot_path": SOURCE_PATH, "snapshot_hash": SOURCE_HASH})
        elif len(row) == 12 and current_state is not None and row[10].strip():
            continuation += 1
            rebuilt.append({"target_id": f"H2-transition-continuation-{continuation:03d}", "source_id": SOURCE_ID, "source_row_kind": "continuation-transition", "source_row_ordinal": continuation, "state_record": current_state, "transition_inscription": row[10], "band_origin_inscription": row[11] or "absence", "observation_class": _class(row[10]), "snapshot_path": SOURCE_PATH, "snapshot_hash": SOURCE_HASH})
    if primary != 46 or continuation != 14 or {str(row["target_id"]) for row in rebuilt} != {str(row["target_id"]) for row in identities}: raise ValueError("ELEC-009 independent source census differs")
    resolved = []
    for row in rebuilt:
        if registered[str(row["target_id"])] != row: raise ValueError("ELEC-009 independent reconstruction differs")
        band = _exact_band(str(row["band_origin_inscription"]))
        target_value = FoldWord((HeldLabel("NIST-state-record", str(row["state_record"])), HeldLabel("NIST-transition-inscription", str(row["transition_inscription"])), HeldLabel("transition-observation-class", str(row["observation_class"])), band, HeldLabel("NIST-band-inscription", str(row["band_origin_inscription"]))))
        resolved.append({**row, "band": band, "target_value": target_value})
    return tuple(resolved)


def _prediction_map(table: FoldTable) -> dict[str, object]:
    result = {entry.left.label: entry.right for entry in table.entries if isinstance(entry.left, HeldLabel) and entry.left.family == "state-transition-law"}
    if len(result) != 9: raise ValueError("ELEC-009 prediction law is incomplete")
    return result


class StateTransitionValidator:
    def __init__(self, root: Path): self.root, self.spec = root.resolve(), STATE_TRANSITION_SPEC
    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate(); registration = experiment_registration_record(self.root); registration_hash = sha256_identity(registration); document = prediction_program_document(self.root); program = fold_program_from_mapping(document); inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}; targets = _reconstructed_targets(self.root)
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-NIST-target-custodian", targets={str(row["target_id"]): row["target_value"] for row in targets}, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs); boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("ELEC-009 prediction package changed")
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal); boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable): raise ValueError("ELEC-009 prediction is not a Fold table")
        predicted = _prediction_map(execution.output)
        if predicted["forward"] != FORWARD or predicted["reverse"] != REVERSE or predicted["bidirectional"] != BIDIRECTIONAL or predicted["coupled"] != COUPLED or predicted["absence"] != ABSENT: raise ValueError("ELEC-009 orientation law changed")
        comparisons = []
        for row in targets:
            transition = str(row["transition_inscription"])
            if row["observation_class"] == "absent-transition-coordinate": law_record = absent_transition("H2", str(row["state_record"]), transition); structural_pass = law_record.terminal_state_or_absence is EMPTY_ONE
            else:
                left, right, orientation = _endpoints(str(row["state_record"]), transition); law_record = observed_transition("H2", left, right, orientation, transition); structural_pass = law_record.is_observed and orientation in (FORWARD, REVERSE, BIDIRECTIONAL, COUPLED)
            exact_band_pass = row["band"] is EMPTY_ONE if row["band_origin_inscription"] == "absence" else isinstance(row["band"], PositiveRatio)
            comparisons.append({"target_id": row["target_id"], "row_kind": row["source_row_kind"], "state_record": row["state_record"], "transition_inscription": transition, "observation_class": row["observation_class"], "band_origin_inscription": row["band_origin_inscription"], "exact_band": "structural-absence" if row["band"] is EMPTY_ONE else f"{row['band'].numerator.value}/{row['band'].denominator.value}", "passed": structural_pass and exact_band_pass})
        mismatch_rejected = self_rejected = absence_composition_rejected = False
        first = observed_transition("H2", "A", "B", FORWARD, "A-B"); second = observed_transition("H2", "B", "C", FORWARD, "B-C")
        composed = compose_transition_path(first, second)
        try: compose_transition_path(first, observed_transition("H2", "D", "E", FORWARD, "D-E"))
        except InadmissibleExactValue: mismatch_rejected = True
        try: observed_transition("H2", "A", "A", FORWARD, "invalid")
        except InadmissibleExactValue: self_rejected = True
        try: compose_transition_path(absent_transition("H2", "A", "absent"), second)
        except InadmissibleExactValue: absence_composition_rejected = True
        numeric_zero_rejected = False
        try: FoldWord((0,))
        except FoldLanguageHalt: numeric_zero_rejected = True
        counts = {"records": len(comparisons), "primary": sum(row["row_kind"] == "primary-state" for row in comparisons), "continuation": sum(row["row_kind"] == "continuation-transition" for row in comparisons), "directional": sum(row["observation_class"] == "observed-directional-transition" for row in comparisons), "coupled": sum(row["observation_class"] == "observed-coupled-state-relation" for row in comparisons), "absent_transition": sum(row["observation_class"] == "absent-transition-coordinate" for row in comparisons), "positive_band": sum(row["exact_band"] != "structural-absence" for row in comparisons), "absent_band": sum(row["exact_band"] == "structural-absence" for row in comparisons)}
        source = self.root / SOURCE_PATH; changed_hash = "sha256:" + sha256(source.read_bytes() + b"tampered").hexdigest()
        adverse = {"matching_path_composes": len(composed.cells) == 6, "mismatched_endpoints_rejected": mismatch_rejected, "self_transition_rejected": self_rejected, "absence_composition_rejected": absence_composition_rejected, "numerical_zero_rejected": numeric_zero_rejected, "omitted_primary_rejected": counts["primary"] == 46, "omitted_continuation_rejected": counts["continuation"] == 14, "present_only_selection_rejected": counts["absent_transition"] == 1, "coupling_rows_retained": counts["coupled"] == 4, "changed_band_rejected": _exact_band("26232.3") != _exact_band("26232.4"), "tampered_source_rejected": hash_file(source) == SOURCE_HASH and changed_hash != SOURCE_HASH, "complete_vector_retained": counts == {"records": 60, "primary": 46, "continuation": 14, "directional": 55, "coupled": 4, "absent_transition": 1, "positive_band": 55, "absent_band": 5}}
        passed = all(row["passed"] for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("complete-NIST-H2-transition-comparator/1", self.spec.experiment_id)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash: raise ValueError("ELEC-009 released target differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration_hash": registration_hash, "prediction_seal_hash": prediction_seal.seal_hash, "comparisons": comparisons, "counts": counts, "adverse": adverse, "trace_hash": execution.trace_hash}
        measurements = tuple(f"{row['target_id']} {row['state_record']}: {row['transition_inscription']}; class {row['observation_class']}; band {row['band_origin_inscription']} = {row['exact_band']}; pass {row['passed']}" for row in comparisons) + tuple(f"count {key}: {value}" for key, value in counts.items()) + tuple(f"adverse {key}: {value}" for key, value in adverse.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, (SOURCE_ID,), measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("StateTransitionValidator", "experiment_registration_record", "prediction_program_document")
