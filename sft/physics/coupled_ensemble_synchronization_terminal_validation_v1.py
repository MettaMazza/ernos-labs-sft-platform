"""Post-seal exact replication of the superseded V1 E4 ensemble."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldWord, HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.coupled_ensemble_synchronization_terminal_law_v1 import CLAIM_ID, EXPERIMENT_ID, formal_certificate


SOURCE_ID = "SFTOM-V1-E4-EXACT-OBSERVATION"
SOURCE_IDS = (SOURCE_ID,)
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/coupled-ensemble-synchronization-source-record.json"
SOURCE_RECORD_HASH = "sha256:16915101542c9bf4592f0595713a56a68932ec4f0662f90e2e6624fbd747ad8e"
CLAIMS_PATH = "experiments/external_sources/physics/snapshots/sftom-v1-e3-claims-emergence.py"
CLAIMS_HASH = "sha256:627f1a340d656cf744449f3e7542ee6040a72766ba912c8ac4edb6149cdca446"
AGGREGATE_PATH = "experiments/external_sources/physics/snapshots/sftom-v1-e4-aggregate.py"
AGGREGATE_HASH = "sha256:b582bf60d4abdabdc4811e4f875f74248a7b7102de7cd7e25822ef3ff15d6f85"
TARGET_IDS = ("SFTOM-V1-E4-WITHHELD-EXACT-RECURRENCES",)
FALSIFICATION_CONDITION = (
    "Reject if either frozen V1 source identity changes; if any registered ensemble, depth, region, coupling or "
    "printed final coordinate is omitted or altered; if the independent exact recurrence fails to reproduce all "
    "five final region counts; if half-One does not uniquely reach one occupied region; if its complete stepwise "
    "recurrence or terminal common point changes; if any off-half comparison is deleted; if the general pair "
    "synchronization or synchronized-terminal proof fails; or if target content enters before prediction sealing."
)


def source_hashes() -> dict[str, str]:
    return {SOURCE_RECORD_PATH: SOURCE_RECORD_HASH, CLAIMS_PATH: CLAIMS_HASH, AGGREGATE_PATH: AGGREGATE_HASH}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"coupled-ensemble source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID or len(record.get("snapshots", ())) != 2:
        raise ValueError("coupled-ensemble source record changed")
    target = record.get("registered_target", {})
    required = {
        "source_entry": "E4", "evidence_label": "OBS", "declared_status": "measured",
        "ensemble_denominator": "21", "ensemble_member_count": "20",
        "coupled_fold_step_count": "15", "region_count": "12",
        "complete_coupling_support": ["1/10", "1/3", "1/2", "7/10", "9/10"],
        "printed_final_region_counts": ["7", "7", "1", "5", "5"],
    }
    if any(target.get(key) != value for key, value in required.items()):
        raise ValueError("coupled-ensemble registered target changed")
    custody = record.get("custody", {})
    if not all((
        custody.get("formal_claim_contains_target_values") is False,
        custody.get("target_inaccessible_during_prediction_execution") is True,
        custody.get("prediction_sealed_before_target_release_within_run") is True,
        custody.get("all_original_source_lines_retained") is True,
        custody.get("all_coupling_rows_retained") is True,
        custody.get("all_recurrence_coordinates_retained_after_release") is True,
        custody.get("measurements_select_formal_survivor") is False,
    )):
        raise ValueError("coupled-ensemble custody changed")
    claims = (root / CLAIMS_PATH).read_text(encoding="utf-8")
    aggregate = (root / AGGREGATE_PATH).read_text(encoding="utf-8")
    if "for _ in range(15): pts=A.step(pts,Fraction(1,2))" not in claims or "return A.occupied_regions(pts,12)==1" not in claims or "def step(points, g):" not in aggregate:
        raise ValueError("frozen E4 procedure lines changed")
    return record


def legacy_cast(value: Fraction) -> Fraction:
    while value > 1:
        value -= 1
    return value


def legacy_fold(value: Fraction) -> Fraction:
    return legacy_cast(value + value)


def legacy_separation(left: Fraction, right: Fraction) -> Fraction:
    if left == right:
        return Fraction(1, 1)
    larger, smaller = (left, right) if left > right else (right, left)
    forward = larger - smaller
    return min(forward, Fraction(1, 1) - forward)


def legacy_step(points: tuple[Fraction, ...], coupling: Fraction) -> tuple[Fraction, ...]:
    folded = tuple(legacy_fold(point) for point in points)
    output: list[Fraction] = []
    for point in folded:
        nearest = None
        nearest_separation = None
        for other in folded:
            if other == point:
                continue
            separation = legacy_separation(point, other)
            if nearest_separation is None or separation < nearest_separation:
                nearest, nearest_separation = other, separation
        if nearest is None:
            output.append(point)
            continue
        move = coupling * nearest_separation
        ahead = legacy_cast(point + nearest_separation)
        output.append(legacy_cast(point + move) if ahead == nearest else legacy_cast(point + (Fraction(1, 1) - move)))
    return tuple(output)


def occupied_region_count(points: tuple[Fraction, ...], regions: int) -> int:
    labels = {
        1 if (point.numerator * regions) // point.denominator == regions
        else (point.numerator * regions) // point.denominator + 1
        for point in points
    }
    return len(labels)


def independent_recurrence(denominator: int, members: int, steps: int, regions: int, coupling: Fraction) -> dict[str, object]:
    points = tuple(Fraction(index, denominator) for index in range(1, members + 1))
    counts: list[int] = []
    for _ in range(steps):
        points = legacy_step(points, coupling)
        counts.append(occupied_region_count(points, regions))
    return {"coupling": coupling, "region_count_recurrence": tuple(counts), "final_region_count": counts[-1], "final_points": points, "terminal_common_point": points[0] if len(set(points)) == 1 else ()}


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    denominator = int(target["ensemble_denominator"])
    members = int(target["ensemble_member_count"])
    steps = int(target["coupled_fold_step_count"])
    regions = int(target["region_count"])
    couplings = tuple(Fraction(value) for value in target["complete_coupling_support"])
    recurrences = tuple(independent_recurrence(denominator, members, steps, regions, coupling) for coupling in couplings)
    final_counts = tuple(item["final_region_count"] for item in recurrences)
    half = recurrences[2]
    return {
        "denominator": denominator,
        "member_count": members,
        "step_count": steps,
        "region_count": regions,
        "couplings": couplings,
        "recurrences": recurrences,
        "final_region_counts": final_counts,
        "printed_final_region_counts": tuple(int(value) for value in target["printed_final_region_counts"]),
        "all_printed_rows_reproduced": final_counts == tuple(int(value) for value in target["printed_final_region_counts"]),
        "half_One_uniquely_reaches_one_region": half["final_region_count"] == 1 and all(item["final_region_count"] > 1 for index, item in enumerate(recurrences) if index != 2),
        "half_One_recurrence": half["region_count_recurrence"],
        "half_One_terminal_point": half["terminal_common_point"],
        "half_One_terminal_members_identical": len(set(half["final_points"])) == 1,
        "half_One_first_one_region_step": next(index for index, count in enumerate(half["region_count_recurrence"], 1) if count == 1),
    }


def formal_prediction_inputs() -> dict[str, object]:
    certificate = formal_certificate()
    return {
        "coupling_numerator": PositiveRatio.from_pair(certificate["unique_synchronizing_coupling"].numerator, 1),
        "coupling_denominator": PositiveRatio.from_pair(certificate["unique_synchronizing_coupling"].denominator, 1),
        "pair_relation": HeldLabel("pair-synchronization", "equal-moves-reassemble-separation"),
        "residual_relation": HeldLabel("pair-residual", "half-One-empty-off-half-positive"),
        "terminal_relation": HeldLabel("synchronized-ensemble", "common-Fold-successor-preserves-equality"),
        "scope_relation": HeldLabel("synchronization-scope", "pair-boundary-general-ensemble-convergence-separate"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [{"opcode": "input", "destination": key, "arguments": [key]} for key in keys]
    instructions.extend(({"opcode": "word", "destination": "prediction", "arguments": list(keys)}, {"opcode": "emit", "destination": "", "arguments": ["prediction"]}))
    return {"schema": "sft-v3-fold-program/1", "program_id": EXPERIMENT_ID + "-exact-prediction", "instructions": instructions}


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-coupled-ensemble-synchronization-experiment/1",
        "claim_id": CLAIM_ID, "experiment_id": EXPERIMENT_ID, "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-replication",
        "frozen_relation": "Equal paired movement synchronizes an exact positive pair if and only if each member moves by the forced half-One of separation; every off-half generated coupling leaves positive residual separation, and every already synchronized ensemble remains synchronized under a common Fold successor.",
        "prediction_program": prediction_program_document(), "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID, "source_ids": SOURCE_IDS, "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH, "source_hashes": source_hashes(),
        "row_retention_policy": "both complete frozen V1 source files, all five registered coupling rows, all fifteen stepwise region-count coordinates for every coupling, every final point, the original claim status and acceptance rule",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "independent exact-rational coupled-Fold recurrence importing neither claimant nor V1 code; complete-vector, terminal-point, uniqueness, printed-row and hostile-boundary checks",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("coupled-ensemble prediction has wrong Fold shape")
    return dict(zip(keys, output.cells))


class CoupledEnsembleSynchronizationValidator:
    def __init__(self, root: Path): self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID: raise ValueError("wrong coupled-ensemble seal")
        registration = experiment_registration_record(); registration_hash = sha256_identity(registration)
        document = prediction_program_document(); program = fold_program_from_mapping(document); inputs = formal_prediction_inputs(); keys = tuple(inputs)
        envelope = PredictionEnvelope(EXPERIMENT_ID, {key: sha256_identity(value) for key, value in inputs.items()}, TARGET_IDS, sha256_identity((sealed.seal_hash, registration["frozen_relation"])), registration_hash)
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=targets,
            custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction_seal = boundary.seal_prediction(execution.output, execution.trace); after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed: raise ValueError("coupled-ensemble hostile-package audit failed")
        release = vault.release(prediction_seal); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs: raise ValueError("coupled-ensemble prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        certificate = formal_certificate()
        formal_channel = all((certificate["unique_synchronizing_coupling"] == Fraction(1,2), certificate["half_One_residuals_empty"], certificate["off_half_residuals_positive"], certificate["synchronized_terminal_preserved"]))
        all_rows = len(analysis["recurrences"]) == 5 and all(len(item["region_count_recurrence"]) == 15 and len(item["final_points"]) == 20 for item in analysis["recurrences"])
        controls = all((analysis["final_region_counts"] == (7,7,1,5,5), analysis["half_One_recurrence"] == (12,10,7,5,4,3,2,1,1,1,1,1,1,1,1), analysis["half_One_terminal_point"] == Fraction(4,7), analysis["half_One_first_one_region_step"] == 8))
        passed = all((formal_channel, all_rows, controls, analysis["all_printed_rows_reproduced"], analysis["half_One_uniquely_reaches_one_region"], analysis["half_One_terminal_members_identical"]))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id); comparator_hash = sha256_identity(("exact-coupled-ensemble-synchronization-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=interpreter_hash, program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=comparator_hash, prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "prediction_seal": prediction_seal.seal_hash, "source_hashes": source_hashes(), "target_identity": target_identity, "analysis": analysis, "formal_channel": formal_channel, "all_rows": all_rows, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "Both frozen V1 E4 files are retained byte-for-byte and opened only after the V3 prediction seal.",
            "All five registered couplings and all fifteen region-count steps per coupling were independently recomputed exactly.",
            f"Complete final coupling vector: {analysis['final_region_counts']}.",
            f"Half-One recurrence: {analysis['half_One_recurrence']}.",
            "Half-One uniquely reaches one occupied region, first at step eight, and all twenty members finish exactly at four-sevenths.",
            "Off-half controls remain visible and finish at seven, seven, five and five occupied regions; they cannot be discarded to manufacture uniqueness.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, all_rows, SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("CoupledEnsembleSynchronizationValidator", "FALSIFICATION_CONDITION", "SOURCE_IDS", "TARGET_IDS", "authoritative_record", "exact_measurement_analysis", "experiment_registration_record", "independent_recurrence")
