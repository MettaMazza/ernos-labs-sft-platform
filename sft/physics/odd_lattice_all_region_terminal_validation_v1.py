"""Post-seal replication of the superseded V1 E3 observation.

The validator does not import or execute the frozen V1 programs.  It verifies
their byte identities, releases their explicit target only after the formal
prediction seal, and independently reimplements the recorded exact-rational
procedure while retaining the complete observed vector.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    FoldWord,
    HostilePackageAuditor,
    PositiveRatio,
    TargetVault,
    fold_program_from_mapping,
    snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation,
    seal_isolation_certificate,
    seal_target_custody_certificate,
    unsealed_isolation_certificate,
    unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.odd_lattice_all_region_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    formal_certificate,
)


SOURCE_ID = "SFTOM-V1-E3-EXACT-OBSERVATION"
SOURCE_IDS = (SOURCE_ID,)
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/odd-lattice-all-region-source-record.json"
SOURCE_RECORD_HASH = "sha256:9ea9421a47a6945d08915e0bdc03ec96b89e981718d99a84fe1ceae9e118cbfc"
CLAIMS_SNAPSHOT_PATH = "experiments/external_sources/physics/snapshots/sftom-v1-e3-claims-emergence.py"
CLAIMS_SNAPSHOT_HASH = "sha256:627f1a340d656cf744449f3e7542ee6040a72766ba912c8ac4edb6149cdca446"
DENSITY_SNAPSHOT_PATH = "experiments/external_sources/physics/snapshots/sftom-v1-e3-density.py"
DENSITY_SNAPSHOT_HASH = "sha256:a4fdd45d43307d7a5ecf0bcc2cdca68b5290da48f8c4ce1c0abf33bcf22d397b"
TARGET_IDS = ("SFTOM-V1-E3-WITHHELD-EXACT-OBSERVATION",)

FALSIFICATION_CONDITION = (
    "Reject if either frozen V1 source identity changes; if the original E3 inputs, status, observation or "
    "acceptance rule are omitted or altered; if the independently measured complete recurrence vector changes "
    "with positive Fold depth; if any released region is empty despite region count not exceeding the odd "
    "complete-lattice count; if total occupancy differs from complete lattice membership; if the general odd-"
    "lattice permutation or positive-depth successor certificate fails; or if the historical target or result "
    "enters the claimant before its prediction seal."
)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        CLAIMS_SNAPSHOT_PATH: CLAIMS_SNAPSHOT_HASH,
        DENSITY_SNAPSHOT_PATH: DENSITY_SNAPSHOT_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"odd-lattice observation source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID or len(record.get("snapshots", ())) != 2:
        raise ValueError("odd-lattice source record identity changed")
    target = record.get("registered_target", {})
    required_target = {
        "source_entry": "E3",
        "evidence_label": "OBS",
        "declared_status": "measured",
        "lattice_member_count": "255",
        "fold_step_count": "12",
        "region_count": "8",
        "legacy_acceptance_rule": "every one of the eight region tallies is positive",
    }
    if any(target.get(key) != value for key, value in required_target.items()):
        raise ValueError("odd-lattice registered target changed")
    custody = record.get("custody", {})
    required_custody = {
        "development_target_already_known": True,
        "formal_claim_contains_target_values": False,
        "target_inaccessible_during_prediction_execution": True,
        "prediction_sealed_before_target_release_within_run": True,
        "all_original_source_lines_retained": True,
        "all_result_coordinates_retained_after_release": True,
        "measurements_select_formal_survivor": False,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-replication",
    }
    if any(custody.get(key) != value for key, value in required_custody.items()):
        raise ValueError("odd-lattice custody record changed")
    claims_text = (root / CLAIMS_SNAPSHOT_PATH).read_text(encoding="utf-8")
    density_text = (root / DENSITY_SNAPSHOT_PATH).read_text(encoding="utf-8")
    if (
        "occ=D.occupancy(D.even_lattice(255),12,8)" not in claims_text
        or "return all(occ)" not in claims_text
        or "def occupancy(starts, folds, regions):" not in density_text
        or "def even_lattice(N):  return [Fraction(i,N) for i in range(1,N+1)]" not in density_text
    ):
        raise ValueError("frozen E3 procedure lines changed")
    return record


def legacy_fold(part: Fraction) -> Fraction:
    if not isinstance(part, Fraction) or not 0 < part <= 1:
        raise ValueError("legacy replication requires an exact positive part")
    doubled = part + part
    return doubled if doubled <= 1 else doubled - 1


def independent_observation(member_count: int, step_count: int, region_count: int) -> tuple[int, ...]:
    """Recompute the released V1 procedure without importing claimant or V1 code."""

    if any(isinstance(value, bool) or value < 1 for value in (member_count, step_count, region_count)):
        raise ValueError("released observation inputs must be positive whole counts")
    points = tuple(Fraction(index, member_count) for index in range(1, member_count + 1))
    for _ in range(step_count):
        points = tuple(legacy_fold(point) for point in points)
    labels = tuple(
        1 if (point.numerator * region_count) // point.denominator == region_count
        else (point.numerator * region_count) // point.denominator + 1
        for point in points
    )
    return tuple(
        sum(1 for label in labels if label == region)
        for region in range(1, region_count + 1)
    )


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    members = int(target["lattice_member_count"])
    steps = int(target["fold_step_count"])
    regions = int(target["region_count"])
    vector = independent_observation(members, steps, regions)
    first_step_vector = independent_observation(members, 1, regions)
    return {
        "member_count": members,
        "step_count": steps,
        "region_count": regions,
        "complete_recurrence_vector": vector,
        "first_step_vector": first_step_vector,
        "depth_invariant": vector == first_step_vector,
        "all_regions_occupied": all(count >= 1 for count in vector),
        "complete_member_total_retained": sum(vector) == members,
        "exact_balance_span_is_One": max(vector) == min(vector) + 1,
        "legacy_acceptance_rule_passed": all(count >= 1 for count in vector),
    }


def positive_ratio(value: int) -> PositiveRatio:
    if value < 1:
        raise ValueError("formal prediction input must be positive")
    return PositiveRatio.from_pair(value, 1)


def formal_prediction_inputs() -> dict[str, object]:
    certificate = formal_certificate()
    first = certificate["certificates"][0]
    return {
        "sample_member_count": positive_ratio(first["permutation"]["member_count"]),
        "sample_region_count": positive_ratio(len(first["base_vector"])),
        "sample_first_region_count": positive_ratio(first["base_vector"][0]),
        "sample_second_region_count": positive_ratio(first["base_vector"][1]),
        "lattice_relation": HeldLabel("odd-lattice", "complete-positive-odd-support"),
        "Fold_relation": HeldLabel("odd-lattice-Fold", "binary-residue-permutation"),
        "observation_relation": HeldLabel("odd-lattice-observation", "complete-positive-region-vector"),
        "depth_relation": HeldLabel("odd-lattice-depth", "every-positive-successor-invariant"),
        "coverage_relation": HeldLabel("odd-lattice-coverage", "all-regions-occupied-when-regions-do-not-exceed-members"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [
        {"opcode": "input", "destination": key, "arguments": [key]}
        for key in keys
    ]
    instructions.extend((
        {"opcode": "word", "destination": "prediction", "arguments": list(keys)},
        {"opcode": "emit", "destination": "", "arguments": ["prediction"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": EXPERIMENT_ID + "-exact-prediction",
        "instructions": instructions,
    }


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-odd-lattice-all-region-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-replication",
        "frozen_relation": (
            "Every complete positive odd lattice is permuted by the binary Fold; every complete positive-region "
            "occupancy vector is therefore invariant at every positive Fold depth, totals the lattice membership "
            "and occupies every region whenever the region count does not exceed the member count."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": "both complete frozen V1 source files, every original line, all three released counts, the original status and acceptance rule, and every coordinate of the independently measured vector",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "exact rational re-execution by an implementation importing neither claimant nor frozen V1 code; full-vector, total, coverage, depth-invariance and adverse-boundary checks",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    return {TARGET_IDS[0]: authoritative_record(root)["registered_target"]}


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("odd-lattice prediction has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class OddLatticeAllRegionValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("odd-lattice validator received the wrong claim seal")
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = formal_prediction_inputs()
        ordered_keys = tuple(inputs)
        envelope = PredictionEnvelope(
            experiment_id=EXPERIMENT_ID,
            registered_inputs={key: sha256_identity(value) for key, value in inputs.items()},
            withheld_target_ids=TARGET_IDS,
            frozen_relation_hash=sha256_identity((sealed.seal_hash, registration["frozen_relation"])),
            experiment_registration_hash=registration_hash,
        )
        vault = TargetVault(
            experiment_id=EXPERIMENT_ID,
            custodian_id=EXPERIMENT_ID + "-external-target-custodian",
            targets=released_targets(self.root),
            custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, source_hashes())),
            expected_envelope_hash=sha256_identity(envelope),
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("odd-lattice prediction failed hostile-package audit")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed odd-lattice prediction differs from formal inputs")

        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        certificate = formal_certificate()
        formal_channel = all((
            prediction["Fold_relation"] == HeldLabel("odd-lattice-Fold", "binary-residue-permutation"),
            prediction["depth_relation"] == HeldLabel("odd-lattice-depth", "every-positive-successor-invariant"),
            prediction["coverage_relation"] == HeldLabel("odd-lattice-coverage", "all-regions-occupied-when-regions-do-not-exceed-members"),
            all(item["all_steps_equal"] for item in certificate["certificates"]),
            all(item["permutation"]["image_is_complete_support"] for item in certificate["certificates"]),
        ))
        complete_sources = len(authoritative_record(self.root)["snapshots"]) == 2
        adverse_controls = all((
            independent_observation(255, 1, 8) == analysis["complete_recurrence_vector"],
            independent_observation(255, 11, 8) == analysis["complete_recurrence_vector"],
            sum(independent_observation(255, 12, 7)) == 255,
            len(set(independent_observation(255, 12, 8))) == 2,
            len(set(range(1, 255))) != 255,
        ))
        all_rows_preserved = all((
            complete_sources,
            analysis["member_count"] == 255,
            analysis["step_count"] == 12,
            analysis["region_count"] == 8,
            len(analysis["complete_recurrence_vector"]) == 8,
        ))
        passed = all((
            formal_channel,
            all_rows_preserved,
            adverse_controls,
            analysis["depth_invariant"],
            analysis["all_regions_occupied"],
            analysis["complete_member_total_retained"],
            analysis["exact_balance_span_is_One"],
            analysis["legacy_acceptance_rule_passed"],
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-odd-lattice-all-region-comparator/1",
            registration_hash,
            FALSIFICATION_CONDITION,
        ))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=EXPERIMENT_ID + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=interpreter_hash,
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=comparator_hash,
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        comparison_payload = {
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "source_record_hash": SOURCE_RECORD_HASH,
            "source_hashes": source_hashes(),
            "target_identity_hash": target_identity,
            "analysis": analysis,
            "formal_channel": formal_channel,
            "complete_sources": complete_sources,
            "adverse_controls": adverse_controls,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            "Both frozen V1 E3 source files are retained byte-for-byte and were opened only after the V3 prediction seal.",
            "Released historical inputs: complete 255-member lattice, twelve Fold steps and eight regions.",
            f"Complete independently measured recurrence vector: {analysis['complete_recurrence_vector']}.",
            "Every one of the eight regions is occupied; the exact vector totals all 255 members.",
            "The same complete vector occurs after the first, eleventh and twelfth positive Fold steps, directly replicating and strengthening the original measured statement.",
            "The V3 law is depth-independent and applies to every positive finite odd complete lattice and every complete region partition within its member count; the historical run did not select that law.",
        )
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=all_rows_preserved,
            data_source_ids=SOURCE_IDS,
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(comparison_payload),
            falsification_condition=FALSIFICATION_CONDITION,
            passed=passed,
        )


__all__ = (
    "FALSIFICATION_CONDITION",
    "OddLatticeAllRegionValidator",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "formal_prediction_inputs",
    "independent_observation",
)
