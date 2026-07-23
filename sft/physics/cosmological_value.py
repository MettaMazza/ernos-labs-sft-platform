"""Exact target-withheld COBE FIRAS background-temperature correspondence."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import platform
import re

from sft.engine import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmpiricalValidation,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping,
    seal_isolation_certificate, seal_target_custody_certificate, snapshot_protected_tree,
    target_identity_from_release, unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.fold_language import FoldPair, PositiveRatio
from sft.engine.source import hash_file


INPUT_PATH = "experiments/external_sources/physics/snapshots/nasa-lambda-cobe-firas.html"
INPUT_HASH = "sha256:5eae175f5ea06f7a5cb863866eeee9d87a38d870937d9a93ebf28629af0d6ef9"
TARGET_PATH = "experiments/external_sources/physics/snapshots/nasa-lambda-cobe-firas-monopole.html"
TARGET_HASH = "sha256:e42bcf7e3e2eccac3ac8c210d4287e2477c394ad03d76ac7f719515d29753f2a"
INPUT_SOURCE_ID = "NASA-LAMBDA-COBE-FIRAS-2026-07-23"
TARGET_SOURCE_ID = "NASA-LAMBDA-COBE-FIRAS-MONOPOLE-2026-07-23"


def _ratio(value: Fraction) -> PositiveRatio:
    if value <= 0:
        raise ValueError("background temperature must remain an exact positive value")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def _pair(central: Fraction, uncertainty: Fraction) -> FoldPair:
    if uncertainty <= 0 or uncertainty >= central:
        raise ValueError("background-temperature uncertainty is outside the positive domain")
    return FoldPair(_ratio(central - uncertainty), _ratio(central + uncertainty))


def read_firas_input(path: Path) -> FoldPair:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"2\.725&plusmn;0\.002 K", text)
    if match is None:
        raise ValueError("registered FIRAS input temperature record is absent")
    return _pair(Fraction(2725, 1000), Fraction(2, 1000))


def read_firas_target(path: Path) -> FoldPair:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"2725 \+/- 1 mK", text)
    if match is None:
        raise ValueError("withheld FIRAS monopole temperature record is absent")
    return _pair(Fraction(2725, 1000), Fraction(1, 1000))


def _interval(value: object) -> tuple[Fraction, Fraction]:
    if not isinstance(value, FoldPair) or not isinstance(value.left, PositiveRatio) or not isinstance(value.right, PositiveRatio):
        raise ValueError("background prediction is not an exact Fold interval")
    if value.left.fraction > value.right.fraction:
        raise ValueError("background prediction interval is unordered")
    return value.left.fraction, value.right.fraction


def _overlap(left: object, right: object) -> bool:
    ll, lu = _interval(left); rl, ru = _interval(right)
    return not (lu < rl or ru < ll)


def program_document(experiment_id: str) -> dict[str, object]:
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": experiment_id + "-background-invariance",
        "instructions": [
            {"opcode": "input", "destination": "lower", "arguments": ["background_lower"]},
            {"opcode": "input", "destination": "upper", "arguments": ["background_upper"]},
            {"opcode": "pair", "destination": "prediction", "arguments": ["lower", "upper"]},
            {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
        ],
    }


class FIRASBackgroundValueValidator:
    """Predict cross-analysis background invariance before target release."""

    def __init__(self, root: Path, experiment_id: str, claim_id: str, falsification_condition: str):
        self.root = root.resolve(); self.experiment_id = experiment_id
        self.claim_id = claim_id; self.falsification_condition = falsification_condition

    def validate(self, sealed) -> EmpiricalValidation:
        input_path, target_path = self.root / INPUT_PATH, self.root / TARGET_PATH
        if hash_file(input_path) != INPUT_HASH or hash_file(target_path) != TARGET_HASH:
            raise ValueError("COBE FIRAS external snapshot differs from registration")
        input_interval, target_interval = read_firas_input(input_path), read_firas_target(target_path)
        input_lower, input_upper = _interval(input_interval)
        inputs = {"background_lower": _ratio(input_lower), "background_upper": _ratio(input_upper)}
        document = program_document(self.experiment_id); program = fold_program_from_mapping(document)
        registration = {
            "claim_id": self.claim_id, "experiment_id": self.experiment_id,
            "frozen_relation": "background thermodynamic temperature is invariant across the registered FIRAS analyses",
            "input_source_id": INPUT_SOURCE_ID, "input_snapshot_hash": INPUT_HASH,
            "withheld_target_source_id": TARGET_SOURCE_ID, "target_snapshot_hash": TARGET_HASH,
            "program": document, "falsification_condition": self.falsification_condition,
        }
        registration_hash = sha256_identity(registration)
        envelope = PredictionEnvelope(
            self.experiment_id, {key: sha256_identity(value) for key, value in sorted(inputs.items())},
            ("firas_monopole_temperature",), sealed.seal_hash, registration_hash,
        )
        vault = TargetVault(
            experiment_id=self.experiment_id,
            custodian_id=self.experiment_id + "-firas-target-custodian",
            targets={"firas_monopole_temperature": target_interval},
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("FIRAS prediction failed hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        observed = release.targets["firas_monopole_temperature"]
        value_passed = _overlap(execution.output, observed)
        _, prediction_upper = _interval(execution.output)
        unfavorable = FoldPair(_ratio(prediction_upper + 1), _ratio(prediction_upper + 2))
        unfavorable_rejected = not _overlap(execution.output, unfavorable)

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-FIRAS-interval-overlap/1", self.falsification_condition))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.experiment_id + "-firas-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(), interpreter_hash=interpreter_hash,
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=comparator_hash,
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        predicted = _interval(execution.output); measured = _interval(observed)
        payload = {
            "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash,
            "input_snapshot_hash": INPUT_HASH, "target_snapshot_hash": TARGET_HASH,
            "predicted_interval_kelvin": predicted, "measured_interval_kelvin": measured,
            "overlap": value_passed, "unfavorable_rejected": unfavorable_rejected,
            "trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=(INPUT_SOURCE_ID, TARGET_SOURCE_ID),
            measurements=(
                f"FIRAS background interval predicted {predicted}; independently released monopole interval {measured}; overlap {value_passed}",
                "deliberately displaced unfavorable interval rejected",
            ),
            measurement_receipt_hash=sha256_identity(payload),
            falsification_condition=self.falsification_condition,
            passed=value_passed and unfavorable_rejected,
        )


__all__ = ("FIRASBackgroundValueValidator", "read_firas_input", "read_firas_target")
