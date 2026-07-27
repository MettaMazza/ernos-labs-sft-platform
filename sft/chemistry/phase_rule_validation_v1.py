"""Post-seal complete IUPAC/NIST phase-rule structure validation for THERMO-011."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import platform

from sft.chemistry.phase_rule_batch_v1 import (
    IDENTITY_HASH, IDENTITY_PATH, IUPAC_HASH, IUPAC_PATH, NIST_HASH, NIST_PATH,
    NIST_TEXT_HASH, NIST_TEXT_PATH, PHASE_RULE_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.phase_rule_law_v1 import PhaseRuleAccount, independent_degree_support
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
        raise ValueError("THERMO-011 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "degree_support_external_inscription", "sft_degree_support_state", "external_relation_record",
        "iupac_definition_fragments", "target_payload", "target_payload_hash",
    }
    if (
        document.get("complete_target_count") != 18
        or document.get("all_degree_support_outcome_source_fragment_and_target_hash_values_absent") is not True
        or len(rows) != 18
        or any(forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("THERMO-011 value-free identity boundary changed")
    return rows


def _account(component_count: int, phase_count: int) -> PhaseRuleAccount:
    return PhaseRuleAccount(
        tuple(HeldLabel("chemical-component", f"component-{index}") for index in range(1, component_count + 1)),
        tuple(HeldLabel("chemical-phase", f"phase-{index}") for index in range(1, phase_count + 1)),
        (
            HeldLabel("phase-environment-coordinate", "temperature"),
            HeldLabel("phase-environment-coordinate", "pressure"),
        ),
    )


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"phase-rule-row-{ordinal}"
        component_count = int(row["component_count_identity"])
        phase_count = int(row["phase_count_identity"])
        support = independent_degree_support(_account(component_count, phase_count))
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        for number, (key, family) in enumerate(
            (("iupac_source_id", "iupac-source"), ("nist_source_id", "nist-source")), start=1
        ):
            destination = f"{prefix}-source-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, row[key]]})
            registers.append(destination)
        for name, value in (("component-count", component_count), ("phase-count", phase_count)):
            destination = f"{prefix}-{name}"
            instructions.append({"opcode": "count", "destination": destination, "arguments": [str(value)]})
            registers.append(destination)
        degree_destination = prefix + "-degree-support"
        if isinstance(support.count, EmptyOne):
            instructions.append({"opcode": "empty_one", "destination": degree_destination, "arguments": ["structural-empty-One"]})
        else:
            instructions.append({"opcode": "count", "destination": degree_destination, "arguments": [str(support.count.value)]})
        registers.append(degree_destination)
        for family, label in (
            ("phase-rule-law", "one-carrier-cancelled-per-coexisting-phase"),
            ("record-law", "complete-component-phase-environment-account-retained"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-phase-rule-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-phase-rule-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": PHASE_RULE_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": PHASE_RULE_SPEC.experiment_id,
        "claim_id": PHASE_RULE_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": PHASE_RULE_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "iupac_source": (IUPAC_PATH, IUPAC_HASH),
        "nist_source": (NIST_PATH, NIST_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in PHASE_RULE_SPEC.target_rows),
        "all_degree_support_outcome_source_fragment_and_target_hash_values_absent": True,
        "falsification_condition": PHASE_RULE_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 18:
        raise ValueError("THERMO-011 prediction is not the complete 18-row table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 8
        ):
            raise ValueError("THERMO-011 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 18:
        raise ValueError("THERMO-011 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (IUPAC_PATH, IUPAC_HASH),
        (NIST_PATH, NIST_HASH), (NIST_TEXT_PATH, NIST_TEXT_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"THERMO-011 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if document.get("complete_target_count") != 18 or document.get("release_requires_complete_identity_prediction_seal") is not True or len(targets) != 18:
        raise ValueError("THERMO-011 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if (
            identity["target_id"] != target.get("target_id")
            or identity["component_count_identity"] != target.get("component_count_external_inscription")
            or identity["phase_count_identity"] != target.get("phase_count_external_inscription")
        ):
            raise ValueError("THERMO-011 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_phase_rule_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    component_counts: Counter[int] = Counter()
    positive_degree_states = 0
    empty_degree_states = 0
    for row in rows:
        target = row["target_payload"]
        component_count = int(target["component_count_external_inscription"])
        phase_count = int(target["phase_count_external_inscription"])
        degree_inscription = int(target["degree_support_external_inscription"])
        if component_count < 1 or phase_count < 1:
            raise ValueError("THERMO-011 external identity is not positive")
        if target.get("external_relation_record", "").replace("−", "-") != "F = C - P + 2":
            raise ValueError("THERMO-011 IUPAC relation record changed")
        if degree_inscription == 0:
            if target.get("sft_degree_support_state") != "EmptyOne" or component_count + 2 != phase_count:
                raise ValueError("THERMO-011 invariant external glyph was consumed as a number")
            empty_degree_states += 1
        elif degree_inscription > 0:
            if (
                target.get("sft_degree_support_state") != "exact-positive-degree-support"
                or component_count + 2 != phase_count + degree_inscription
            ):
                raise ValueError("THERMO-011 positive degree support breaks exact carrier balance")
            positive_degree_states += 1
        else:
            raise ValueError("THERMO-011 external degree inscription is negative")
        component_counts[component_count] += 1
    return {
        "complete_target_count": len(rows),
        "component_class_counts": dict(component_counts),
        "positive_degree_support_count": positive_degree_states,
        "EmptyOne_degree_support_count": empty_degree_states,
        "all_18_component_phase_rows_retained": len(rows) == 18,
        "complete_one_through_four_component_classes_retained": dict(component_counts) == {1: 3, 2: 4, 3: 5, 4: 6},
        "all_14_positive_degree_supports_retained": positive_degree_states == 14,
        "all_four_external_zero_glyphs_translated_only_to_EmptyOne": empty_degree_states == 4,
        "complete_iupac_source_retained": primary.get("iupac_snapshot_hash") == IUPAC_HASH,
        "complete_32_page_nist_source_retained": primary.get("nist_snapshot_hash") == NIST_HASH and primary.get("nist_complete_page_count") == 32,
        "all_sources_and_rows_preserved": primary.get("all_complete_sources_and_component_phase_degree_rows_preserved") is True,
        "no_external_equation_or_degree_used_as_proof_parameter": primary.get("external_equation_or_degree_value_used_as_proof_parameter") is False,
        "no_subtraction_signed_count_or_numerical_zero_imported": primary.get("subtraction_signed_count_or_numerical_zero_imported_into_sft_derivation") is False,
    }


class PhaseRuleValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = PHASE_RULE_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("THERMO-011 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {}
        for row in source_rows:
            target = row["target_payload"]
            if target["sft_degree_support_state"] == "EmptyOne":
                target_values[row["target_id"]] = EmptyOne()
            else:
                target_values[row["target_id"]] = PositiveCount(int(target["degree_support_external_inscription"]))
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
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            sources_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["iupac_source_id"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["nist_source_id"]
            )
            counts_match = (
                isinstance(word.cells[3], PositiveCount) and word.cells[3].value == int(row["component_count_identity"])
                and isinstance(word.cells[4], PositiveCount) and word.cells[4].value == int(row["phase_count_identity"])
            )
            target_match = word.cells[5] == release.targets[row["target_id"]]
            laws_match = tuple(cell.label for cell in word.cells[6:]) == (
                "one-carrier-cancelled-per-coexisting-phase",
                "complete-component-phase-environment-account-retained",
            )
            comparisons.append({"target_id": row["target_id"], "identity_match": sources_match and counts_match, "postseal_degree_support_match": target_match, "law_match": laws_match, "passed": sources_match and counts_match and target_match and laws_match})
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_phase_rule_analysis(source_rows, primary)
        tampered = [dict(row) for row in source_rows]
        payload = dict(tampered[0]["target_payload"])
        payload["degree_support_external_inscription"] = "9"
        tampered[0] = {**tampered[0], "target_payload": payload}
        tamper_rejected = False
        try:
            exact_phase_rule_analysis(tuple(tampered), primary)
        except ValueError:
            tamper_rejected = True
        controls = {
            "tampered_degree_support_rejected": tamper_rejected,
            "complete_18_row_vector_retained": len(release.targets) == 18,
            "all_14_positive_targets_retained": analysis["all_14_positive_degree_supports_retained"],
            "all_four_EmptyOne_boundaries_retained": analysis["all_four_external_zero_glyphs_translated_only_to_EmptyOne"],
            "complete_sources_retained": analysis["complete_iupac_source_retained"] and analysis["complete_32_page_nist_source_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {"complete_target_count", "component_class_counts", "positive_degree_support_count", "EmptyOne_degree_support_count"}
        passed = all(row["passed"] for row in comparisons) and all(bool(value) for key, value in analysis.items() if key not in non_boolean) and all(controls.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host",
            python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash,
            input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-phase-rule-structure-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash,
            output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("THERMO-011 released target differs from commitment")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id,
            experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity,
            prediction_seal_hash=prediction_seal.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        measurement_payload = {"experiment_registration_hash": registration_hash, "derivation_seal_hash": sealed.seal_hash, "prediction_seal_hash": prediction_seal.seal_hash, "analysis": analysis, "comparisons": comparisons, "controls": controls, "trace": execution.trace_hash}
        measurements = tuple(
            f"{row['target_id']}: components={row['target_payload']['component_count_external_inscription']}; phases={row['target_payload']['phase_count_external_inscription']}; degree support={row['target_payload']['sft_degree_support_state'] if row['target_payload']['sft_degree_support_state'] == 'EmptyOne' else row['target_payload']['degree_support_external_inscription']}"
            for row in source_rows
        ) + (
            "complete structure vector: 18 component/phase identities across one through four components",
            "degree support: 14 exact positive outcomes and four external zero glyphs translated only to EmptyOne",
            "complete sources: IUPAC Gold Book P04533 and the byte-preserved 32-page NIST phase-diagram glossary",
        ) + tuple(f"{key}: {value}" for key, value in controls.items())
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=("IUPAC-GOLDBOOK-P04533-PHASE-RULE", "NIST-PHASE-DIAGRAM-GENERAL-DISCUSSION-GLOSSARY"),
            measurements=measurements,
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "PhaseRuleValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_phase_rule_analysis", "experiment_registration_record", "prediction_program_document",
)
