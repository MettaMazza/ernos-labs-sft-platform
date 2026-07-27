"""Capability-closed post-seal validation for Chemistry KIN-004."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.activation_barrier_batch_v1 import (
    ACTIVATION_BARRIER_SPEC, IDENTITY_HASH, IDENTITY_PATH, INDEX_HASH, INDEX_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.activation_barrier_law_v1 import (
    BarrierPathRecord, BarrierPathState, external_nonnegative_support, external_positive_magnitude,
    forced_activation_barrier, forced_barrier_collection,
)
from sft.claim_evidence import (
    CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, EmptyOne, FoldTable, FoldWord,
    HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree,
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


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-004 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "barrier_kJ_mol_minus1_external_inscription", "barrier_kJ_mol_minus1_exact_fraction",
        "barrier_cm_minus1_external_inscription", "complete_source_ordered_path_states",
        "complete_source_reference_record", "snapshot_hash", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_index_species_count") != 41 or document.get("complete_detail_target_count") != 44
        or document.get("all_species_path_state_identities_retained") is not True
        or document.get("all_barrier_unit_uncertainty_method_note_and_target_hash_values_absent") is not True
        or len(rows) != 44 or any(forbidden.intersection(row) for row in rows)
        or any("=" in row["source_reference_identity"] for row in rows)
    ):
        raise ValueError("KIN-004 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"activation-barrier-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        identity_coordinates = (
            ("complete-source-identity", row["source_id"]),
            ("positive-source-detail-ordinal", str(row["source_detail_ordinal"])),
            ("registered-species-name", row["species_name"]),
            ("source-formula-identity", row["formula_external_inscription"]),
            ("source-cas-identity", row["casno_source_identity"]),
            ("source-torsion-identity", row["torsion_index_source_identity"]),
            ("source-torsion-atom-identity", row["torsion_atom_identity"]),
            ("source-rotor-type-identity", row["rotor_type_identity"]),
            ("source-reference-identity", row["source_reference_identity"]),
        )
        for number, (family, label) in enumerate(identity_coordinates, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("path-law", "complete-generated-discrete-path-with-held-state-identities"),
            ("barrier-law", "greatest-exact-positive-support-relative-to-structural-least-state"),
            ("record-law", "complete-source-profile-reference-absence-and-unresolved-retention"),
            ("prediction-law", "value-free-complete-collection-without-fit-selection-or-correction"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-activation-barrier-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-activation-barrier-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": ACTIVATION_BARRIER_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": ACTIVATION_BARRIER_SPEC.experiment_id,
        "claim_id": ACTIVATION_BARRIER_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": ACTIVATION_BARRIER_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_index_snapshot": (INDEX_PATH, INDEX_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in ACTIVATION_BARRIER_SPEC.target_rows),
        "all_barrier_profile_value_unit_note_and_target_hash_values_absent": True,
        "falsification_condition": ACTIVATION_BARRIER_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 44:
        raise ValueError("KIN-004 prediction is not the complete forty-four-target table")
    resolved = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id" or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 14:
            raise ValueError("KIN-004 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 44:
        raise ValueError("KIN-004 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (INDEX_PATH, INDEX_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-004 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_index_species_count") != 41 or document.get("complete_detail_target_count") != 44
        or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 44
    ):
        raise ValueError("KIN-004 target registry changed")
    keys = (
        "target_id", "source_id", "source_detail_ordinal", "species_name", "formula_external_inscription",
        "casno_source_identity", "torsion_index_source_identity", "torsion_atom_identity", "rotor_type_identity",
        "source_reference_identity",
    )
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in keys):
            raise ValueError("KIN-004 identity/target binding changed")
        if hash_file(root / target["snapshot_path"]) != target["snapshot_hash"]:
            raise ValueError("KIN-004 detail snapshot changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_activation_barrier_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    law_paths = []
    barrier_values = []
    wavenumber_values = []
    complete_state_count = 0
    explicit_zero_glyph_count = 0
    missing_reference_count = 0
    missing_least_state_count = 0
    for target_ordinal, row in enumerate(rows, start=1):
        target = row["target_payload"]
        if (
            target.get("source_status") != "NIST CCCBDB experimental barrier collection with complete cited-source identity"
            or target.get("fitted_barrier_or_absolute_energy_origin_used_in_fold_law") is not False
            or target.get("uncertainty_support") != "EmptyOne"
            or target.get("measurement_method_support") != "EmptyOne"
        ):
            raise ValueError("KIN-004 external source status or structural-absence boundary changed")
        states = []
        source_states = tuple(target.get("complete_source_ordered_path_states", ()))
        if not source_states or len(source_states) != target.get("complete_path_state_count"):
            raise ValueError("KIN-004 complete path-state record changed")
        for state in source_states:
            support = external_nonnegative_support(state["energy_kJ_mol_minus1_fold_support"])
            external = state["energy_kJ_mol_minus1_external_inscription"]
            if isinstance(support, EmptyOne):
                if external not in {"0", "0.0", "0.00", "EmptyOne"}:
                    raise ValueError("KIN-004 EmptyOne is not source-bound to zero displacement or absence")
                if external != "EmptyOne":
                    explicit_zero_glyph_count += 1
            states.append(BarrierPathState(
                HeldLabel("generated-path-state", f"state-{state['source_state_ordinal']}-angle-label-{state['external_angle_state_label']}"),
                support,
            ))
        if not any(isinstance(state.relative_support, EmptyOne) for state in states):
            states.insert(0, BarrierPathState(HeldLabel("generated-path-state", "source-least-state-coordinate-absent"), EmptyOne()))
            missing_least_state_count += 1
        source_reference = (
            EmptyOne() if target["source_reference_identity"] == "EmptyOne"
            else HeldLabel("source-reference", target["source_reference_identity"])
        )
        if isinstance(source_reference, EmptyOne):
            missing_reference_count += 1
        path = BarrierPathRecord(
            HeldLabel("registered-species", f"{target['casno_source_identity']}:{target['species_name']}"),
            HeldLabel(
                "generated-reaction-path",
                f"torsion-{target['torsion_index_source_identity']}-atoms-{target['torsion_atom_identity']}-rotor-{target['rotor_type_identity']}",
            ),
            tuple(states), PositiveCount(target_ordinal), source_reference, EmptyOne(), EmptyOne(),
        )
        forced = forced_activation_barrier(path)
        declared = external_positive_magnitude(target["barrier_kJ_mol_minus1_external_inscription"])
        declared_fraction = Fraction(target["barrier_kJ_mol_minus1_exact_fraction"])
        if forced.barrier_support.fraction != declared.fraction or declared.fraction != declared_fraction:
            raise ValueError("KIN-004 forced path boundary does not match the post-seal external barrier")
        law_paths.append(path)
        barrier_values.append(declared_fraction)
        wavenumber_values.append(Fraction(target["barrier_cm_minus1_exact_fraction"]))
        complete_state_count += len(source_states)
    relation = forced_barrier_collection(tuple(law_paths))
    detail_pages = tuple(primary.get("complete_detail_pages", ()))
    unresolved_rows = tuple(primary.get("complete_unresolved_path_rows", ()))
    return {
        "complete_target_count": len(rows),
        "complete_index_species_count": len({row["casno_source_identity"] for row in rows}),
        "complete_detail_page_count": len(detail_pages),
        "complete_path_state_count": complete_state_count + sum(
            len(row["complete_source_ordered_path_states"]) for row in unresolved_rows
        ),
        "complete_explicit_zero_glyph_count_translated_to_EmptyOne": explicit_zero_glyph_count,
        "source_reference_EmptyOne_count": missing_reference_count,
        "source_least_state_coordinate_EmptyOne_count": missing_least_state_count,
        "complete_unresolved_path_row_count": len(unresolved_rows),
        "exact_barrier_range_kJ_mol_minus1": {"minimum": str(min(barrier_values)), "maximum": str(max(barrier_values))},
        "exact_barrier_range_cm_minus1": {"minimum": str(min(wavenumber_values)), "maximum": str(max(wavenumber_values))},
        "all_forty_four_targets_retained_in_source_order": tuple(row[4].value for row in relation.ordered_rows) == tuple(range(1, 45)),
        "all_forty_one_species_retained": len({row["casno_source_identity"] for row in rows}) == 41,
        "all_seven_hundred_eighty_two_path_states_retained": (
            complete_state_count + sum(len(row["complete_source_ordered_path_states"]) for row in unresolved_rows) == 782
        ),
        "unresolved_source_row_preserved": len(unresolved_rows) == 1,
        "all_detail_pages_and_index_preserved": len(detail_pages) == 41 and primary.get("complete_index_species_count") == 41,
        "structural_absence_and_missing_provenance_preserved": missing_reference_count == 12 and missing_least_state_count == 2,
        "no_imported_fitted_or_selected_barrier_law": (
            primary.get("transition_state_saddle_continuum_arrhenius_prefactor_fitted_activation_absolute_origin_selection_average_or_target_correction_used_in_law") is False
            and primary.get("external_values_used_as_proof_parameters") is False
        ),
    }


class ActivationBarrierValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = ACTIVATION_BARRIER_SPEC

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
            raise ValueError("KIN-004 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-activation-barrier-row-hash", row["target_payload_hash"])
            for row in source_rows
        }
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-complete-target-custodian",
            targets=target_values, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        expected_laws = (
            "complete-generated-discrete-path-with-held-state-identities",
            "greatest-exact-positive-support-relative-to-structural-least-state",
            "complete-source-profile-reference-absence-and-unresolved-retention",
            "value-free-complete-collection-without-fit-selection-or-correction",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = (
                row["source_id"], str(row["source_detail_ordinal"]), row["species_name"],
                row["formula_external_inscription"], row["casno_source_identity"],
                row["torsion_index_source_identity"], row["torsion_atom_identity"], row["rotor_type_identity"],
                row["source_reference_identity"],
            )
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[10:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-activation-barrier-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_activation_barrier_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        states = [dict(state) for state in payload["complete_source_ordered_path_states"]]
        states[0]["energy_kJ_mol_minus1_fold_support"] = "-1"
        payload["complete_source_ordered_path_states"] = states
        tampered[0] = {**tampered[0], "target_payload": payload}
        try:
            exact_activation_barrier_analysis(tuple(tampered), primary)
            tamper_rejected = False
        except (ValueError, RuntimeError):
            tamper_rejected = True
        controls = {
            "tampered_negative_path_support_rejected": tamper_rejected,
            "complete_forty_four_target_vector_retained": len(release.targets) == 44,
            "source_order_species_and_paths_retained": (
                analysis["all_forty_four_targets_retained_in_source_order"]
                and analysis["all_forty_one_species_retained"]
                and analysis["all_seven_hundred_eighty_two_path_states_retained"]
            ),
            "structural_absences_unresolved_row_index_and_detail_pages_retained": (
                analysis["structural_absence_and_missing_provenance_preserved"]
                and analysis["unresolved_source_row_preserved"]
                and analysis["all_detail_pages_and_index_preserved"]
            ),
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_target_count", "complete_index_species_count", "complete_detail_page_count",
            "complete_path_state_count", "complete_explicit_zero_glyph_count_translated_to_EmptyOne",
            "source_reference_EmptyOne_count", "source_least_state_coordinate_EmptyOne_count",
            "complete_unresolved_path_row_count", "exact_barrier_range_kJ_mol_minus1",
            "exact_barrier_range_cm_minus1",
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
            comparison_implementation_identity_hash=sha256_identity(("exact-activation-barrier-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-004 released target differs from commitment")
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
            f"{row['target_id']}: species={row['species_name']}; torsion={row['torsion_index_source_identity']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            f"exact barrier range kJ mol^-1: {analysis['exact_barrier_range_kJ_mol_minus1']}",
            f"exact barrier range cm^-1: {analysis['exact_barrier_range_cm_minus1']}",
            "complete NIST SRD 101 experimental surface: forty-one species, forty-four torsion targets, seven hundred eighty-two path states and one unresolved row; no imported or fitted barrier law",
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
    "ActivationBarrierValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_activation_barrier_analysis", "experiment_registration_record", "prediction_program_document",
)
