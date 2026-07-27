"""Capability-closed post-seal validation for Chemistry KIN-005."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.transition_boundary_batch_v1 import (
    ARTICLE_HASH, ARTICLE_PATH, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
    TRANSITION_BOUNDARY_SPEC,
)
from sft.chemistry.transition_boundary_law_v1 import (
    TransitionPath, TransitionPathState, external_barrier_signature, forced_boundary_collection,
    forced_transition_boundary,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldTable, FoldWord,
    HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree,
    target_identity_from_release,
)
from sft.engine import (
    EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate,
    unsealed_isolation_certificate, unsealed_target_custody_certificate,
)
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file


IDENTITY_KEYS = (
    "target_id", "source_id", "article_doi", "material_system_identity", "experimental_method_identity",
    "source_figure_identity", "isotopologue_identity", "exposure_identity",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-005 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "surface_coverage_external_inscription_ML", "temperature_range_K_external_inscription",
        "exposure_L_external_inscription", "uptake_temperature_order_signature",
        "apparent_barrier_external_signed_inscription_eV", "apparent_barrier_external_magnitude_exact_fraction_eV",
        "apparent_barrier_orientation", "uncertainty_external_inscription_eV", "uncertainty_exact_fraction_eV",
        "target_payload", "target_payload_hash", "snapshot_hash",
    }
    serialized = json.dumps(rows, sort_keys=True)
    if (
        document.get("complete_experimental_isotopologue_count") != 2
        or document.get("all_isotope_barrier_rate_temperature_exposure_uncertainty_caption_and_target_hash_values_absent") is not True
        or len(rows) != 2 or any(forbidden.intersection(row) for row in rows)
        or any(token in serialized for token in ("0.01", "0.023", "0.045", "0.005", "75", "193"))
        or tuple(row["isotopologue_identity"] for row in rows) != ("H2", "D2")
    ):
        raise ValueError("KIN-005 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"transition-boundary-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (family, key) in enumerate((
            ("complete-source-identity", "source_id"),
            ("source-article-identity", "article_doi"),
            ("material-system-identity", "material_system_identity"),
            ("experimental-method-identity", "experimental_method_identity"),
            ("source-figure-identity", "source_figure_identity"),
            ("held-isotopologue-identity", "isotopologue_identity"),
            ("exposure-record-identity", "exposure_identity"),
        ), start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, row[key]]})
            registers.append(destination)
        for family, label in (
            ("boundary-law", "finite-generated-path-unique-greatest-support-boundary"),
            ("partition-law", "complete-entry-boundary-exit-state-retention"),
            ("orientation-law", "positive-magnitude-plus-held-orientation-without-negative-number"),
            ("provenance-law", "experimental-targets-separated-from-calculated-and-fitted-disclosures"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-transition-boundary-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-transition-boundary-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": TRANSITION_BOUNDARY_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": TRANSITION_BOUNDARY_SPEC.experiment_id,
        "claim_id": TRANSITION_BOUNDARY_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": TRANSITION_BOUNDARY_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_article_snapshot": (ARTICLE_PATH, ARTICLE_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in TRANSITION_BOUNDARY_SPEC.target_rows),
        "all_isotope_barrier_rate_temperature_exposure_uncertainty_coverage_and_target_hash_values_absent": True,
        "falsification_condition": TRANSITION_BOUNDARY_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 2:
        raise ValueError("KIN-005 prediction is not the complete two-isotopologue table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 12
        ):
            raise ValueError("KIN-005 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 2:
        raise ValueError("KIN-005 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (ARTICLE_PATH, ARTICLE_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-005 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_experimental_isotopologue_count") != 2
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH or len(targets) != 2
    ):
        raise ValueError("KIN-005 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-005 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def _structural_path(ordinal: int, isotope: str) -> TransitionPath:
    return TransitionPath(
        HeldLabel("registered-reaction", "molecular-isotope-dissociative-activation"),
        HeldLabel("generated-reaction-path", f"complete-source-path-{ordinal}"),
        HeldLabel("held-isotopologue", isotope),
        (
            TransitionPathState(HeldLabel("generated-path-state", "entry-least-state"), EmptyOne()),
            TransitionPathState(HeldLabel("generated-path-state", "entry-positive-state"), PositiveRatio.from_pair(1, 1)),
            TransitionPathState(HeldLabel("generated-path-state", "unique-boundary-state"), PositiveRatio.from_pair(3, 1)),
            TransitionPathState(HeldLabel("generated-path-state", "exit-positive-state"), PositiveRatio.from_pair(2, 1)),
        ),
        PositiveCount(ordinal),
    )


def exact_transition_boundary_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 2:
        raise ValueError("KIN-005 requires the complete H2/D2 target pair")
    paths = []
    signatures = []
    for ordinal, row in enumerate(rows, start=1):
        target = row["target_payload"]
        if target.get("source_status") != "experimentally measured TPD uptake and source-reported apparent barrier":
            raise ValueError("KIN-005 nonexperimental record entered the measurement vector")
        path = _structural_path(ordinal, target["isotopologue_identity"])
        carrier = forced_transition_boundary(path)
        if (
            not isinstance(carrier.entry_word, tuple) or not isinstance(carrier.exit_word, tuple)
            or len(carrier.entry_word) != 2 or len(carrier.exit_word) != 1
            or carrier.isotopologue_identity.label != target["isotopologue_identity"]
        ):
            raise ValueError("KIN-005 finite path partition changed")
        signature = external_barrier_signature(
            target["apparent_barrier_external_signed_inscription_eV"],
            target["apparent_barrier_orientation"],
            target["uncertainty_external_inscription_eV"],
        )
        if (
            signature.positive_magnitude.fraction != Fraction(target["apparent_barrier_external_magnitude_exact_fraction_eV"])
            or signature.uncertainty.fraction != Fraction(target["uncertainty_exact_fraction_eV"])
        ):
            raise ValueError("KIN-005 exact post-seal barrier signature changed")
        paths.append(path)
        signatures.append(signature)
    collection = forced_boundary_collection(tuple(paths))
    orientations = tuple(signature.orientation.label for signature in signatures)
    target_orientations = tuple(row["target_payload"]["uptake_temperature_order_signature"] for row in rows)
    disclosure = primary.get("calculated_fitted_and_interpretive_records_retained_but_excluded_from_measurement_targets", {})
    return {
        "complete_experimental_target_count": len(rows),
        "complete_supplementary_file_count": primary.get("complete_supplementary_file_count"),
        "exact_measured_H2_apparent_barrier_magnitude_eV": str(signatures[0].positive_magnitude.fraction),
        "exact_measured_D2_apparent_barrier_magnitude_eV": str(signatures[1].positive_magnitude.fraction),
        "exact_measured_common_uncertainty_eV": str(signatures[0].uncertainty.fraction),
        "H2_external_barrier_orientation": orientations[0],
        "D2_external_barrier_orientation": orientations[1],
        "both_isotopologue_identities_retained": tuple(row[2].label for row in collection.ordered_rows) == ("H2", "D2"),
        "both_opposite_measured_temperature_directions_retained": target_orientations == (
            "uptake-decreases-as-temperature-is-raised", "uptake-increases-as-temperature-is-raised",
        ),
        "external_signed_barriers_translated_without_negative_proof_number": orientations == (
            "reverse-held-temperature-order", "held-temperature-order",
        ),
        "complete_finite_entry_boundary_exit_partitions_retained": all(
            isinstance(forced_transition_boundary(path).entry_word, tuple)
            and isinstance(forced_transition_boundary(path).exit_word, tuple)
            for path in paths
        ),
        "complete_article_and_thirteen_supplement_files_retained": (
            primary.get("all_article_and_supplement_files_preserved") is True
            and primary.get("complete_supplementary_file_count") == 13
            and len(primary.get("complete_supplementary_files", ())) == 13
        ),
        "experimental_and_calculated_provenance_separated": (
            primary.get("experimental_and_calculated_provenance_separated") is True
            and disclosure.get("source_discloses_systematic_model_parameter_adjustments_for_agreement") is True
            and disclosure.get("source_discloses_fitted_or_assumed_model_parameters_in_supplement_Table_S1") is True
            and disclosure.get("none_used_as_experimental_measurement_or_fold_law_parameter") is True
        ),
        "no_imported_saddle_KIE_fit_or_target_correction": (
            primary.get("transition_state_geometry_saddle_continuum_conventional_kie_equation_arrhenius_prefactor_fitted_barrier_selection_or_target_correction_used_in_fold_law") is False
            and primary.get("external_values_used_as_proof_parameters") is False
            and primary.get("negative_number_used_in_fold_proof") is False
        ),
    }


class TransitionBoundaryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = TRANSITION_BOUNDARY_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("KIN-005 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-transition-boundary-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "finite-generated-path-unique-greatest-support-boundary",
            "complete-entry-boundary-exit-state-retention",
            "positive-magnitude-plus-held-orientation-without-negative-number",
            "experimental-targets-separated-from-calculated-and-fitted-disclosures",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(row[key] for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[8:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-transition-boundary-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_transition_boundary_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["apparent_barrier_orientation"] = "held-temperature-order"
        tampered[0] = {**tampered[0], "target_payload": payload}
        try:
            exact_transition_boundary_analysis(tuple(tampered), primary)
            tamper_rejected = False
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_signed_orientation_mismatch_rejected": tamper_rejected,
            "complete_two_isotopologue_target_vector_retained": len(release.targets) == 2,
            "opposite_measured_H2_D2_signatures_retained": analysis["both_opposite_measured_temperature_directions_retained"],
            "calculated_and_fitted_disclosures_retained_but_not_measurements": analysis["experimental_and_calculated_provenance_separated"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_experimental_target_count", "complete_supplementary_file_count",
            "exact_measured_H2_apparent_barrier_magnitude_eV", "exact_measured_D2_apparent_barrier_magnitude_eV",
            "exact_measured_common_uncertainty_eV", "H2_external_barrier_orientation", "D2_external_barrier_orientation",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("finite-transition-boundary-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-005 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {
            "experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis,
            "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash,
        }
        measurements = tuple(
            f"{row['target_id']}: isotope={row['isotopologue_identity']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            f"measured H2 apparent-barrier magnitude/orientation: {analysis['exact_measured_H2_apparent_barrier_magnitude_eV']} eV; {analysis['H2_external_barrier_orientation']}",
            f"measured D2 apparent-barrier magnitude/orientation: {analysis['exact_measured_D2_apparent_barrier_magnitude_eV']} eV; {analysis['D2_external_barrier_orientation']}",
            "complete primary article and thirteen supplementary files preserved; fitted and calculated records disclosed but excluded from experimental targets",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash, experiment_registration_hash=registration_hash,
            isolation_certificate=isolation, target_custody_certificate=custody,
            evaluator_verified_seal=True, target_opened_after_seal=True, all_rows_preserved=True,
            data_source_ids=(source_rows[0]["source_id"],), measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition, passed=passed,
        )


__all__ = (
    "TransitionBoundaryValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_transition_boundary_analysis", "experiment_registration_record", "prediction_program_document",
)
