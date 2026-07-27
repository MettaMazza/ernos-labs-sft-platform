"""Post-seal complete dimer/cluster validation for Chemistry PROP-011."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.intermolecular_binding_batch_v1 import (
    IDENTITY_HASH,
    IDENTITY_PATH,
    INTERMOLECULAR_BINDING_SPEC,
    ION_CLUSTER_HASH,
    ION_CLUSTER_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
    WATER_CLUSTER_HASH,
    WATER_CLUSTER_PATH,
)
from sft.claim_evidence import (
    EMPTY_ONE,
    CapabilityClosedFoldInterpreter,
    CrossPlatformCustodyExchange,
    EmptyOne,
    FoldTable,
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


def _pair(record: dict[str, object]) -> PositiveRatio:
    return PositiveRatio.from_pair(int(record["numerator"]), int(record["denominator"]))


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("PROP-011 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "value_inscription_kJ_per_mol", "value_inscription_cm_inverse", "uncertainty_inscription_cm_inverse",
        "central_cm_inverse", "uncertainty_cm_inverse", "lower_cm_inverse", "upper_cm_inverse",
        "external_orientation", "absolute_inscribed_magnitude_kJ_per_mol",
    }
    if (
        document.get("schema") != "sft-v3-intermolecular-binding-identities/1"
        or document.get("all_binding_values_absent") is not True
        or len(rows) != 1299
        or any(row.get("target_value_absent") is not True or forbidden.intersection(row) for row in rows)
    ):
        raise ValueError("PROP-011 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    """Seal every external identity and the exact law without a binding value."""

    instructions: list[dict[str, object]] = [
        {"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}
    ]
    table_arguments: list[str] = []
    identity_fields = (
        ("dimer_formula", "bound-composite-formula"),
        ("dimer_name", "bound-composite-name"),
        ("donor_formula", "molecular-constituent"),
        ("acceptor_formula", "molecular-constituent"),
        ("source_class", "external-evidence-class"),
        ("source_id", "external-source-identity"),
    )
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"binding-row-{ordinal}"
        instructions.append({
            "opcode": "label", "destination": prefix + "-target",
            "arguments": ["target-id", str(row["target_id"])],
        })
        registers = ["premise"]
        for number, (key, family) in enumerate(identity_fields, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            registers.append(destination)
        for key, family in (("method_id", "calculation-method-id"), ("basis_id", "calculation-basis-id")):
            destination = f"{prefix}-{key}"
            if key in row:
                instructions.append({"opcode": "label", "destination": destination, "arguments": [family, str(row[key])]})
            else:
                instructions.append({"opcode": "empty_one", "destination": destination, "arguments": ["structural-empty-One"]})
            registers.append(destination)
        for family, label in (
            ("constituent-composition-law", "exact-positive-named-constituent-state-composition"),
            ("separation-organization", "finite-held-separated-constituent-endpoint"),
            ("binding-law", "ordered-positive-separated-Take-bound"),
            ("absence-law", "strict-bound-order-or-structural-EmptyOne"),
            ("extension-law", "shared-constituent-extension-preserves-exact-Take"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table_arguments.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-intermolecular-binding-vector", "arguments": table_arguments},
        {"opcode": "emit", "destination": "", "arguments": ["complete-intermolecular-binding-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": INTERMOLECULAR_BINDING_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {
        "experiment_id": INTERMOLECULAR_BINDING_SPEC.experiment_id,
        "claim_id": INTERMOLECULAR_BINDING_SPEC.claim_id,
        "provenance": "observational_derivation",
        "frozen_relation": INTERMOLECULAR_BINDING_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "normalized_primary_records": (PRIMARY_PATH, PRIMARY_HASH),
        "water_cluster_source": (WATER_CLUSTER_PATH, WATER_CLUSTER_HASH),
        "ion_cluster_scope_source": (ION_CLUSTER_PATH, ION_CLUSTER_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in INTERMOLECULAR_BINDING_SPEC.target_rows),
        "all_1299_binding_values_and_orientations_absent_from_prediction": True,
        "computed_measured_adverse_and_scope_classes_separate": True,
        "falsification_condition": INTERMOLECULAR_BINDING_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 1299:
        raise ValueError("PROP-011 prediction is not the complete 1,299-row table")
    resolved: dict[str, FoldWord] = {}
    for entry in output.entries:
        if not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id":
            raise ValueError("PROP-011 prediction lost a target identity")
        if not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 14:
            raise ValueError("PROP-011 prediction lost its complete binding carrier")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 1299:
        raise ValueError("PROP-011 prediction duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict[str, object], ...]:
    for path, expected in (
        (TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH),
        (WATER_CLUSTER_PATH, WATER_CLUSTER_HASH), (ION_CLUSTER_PATH, ION_CLUSTER_HASH),
    ):
        if hash_file(root / path) != expected:
            raise ValueError(f"PROP-011 registered source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    targets = tuple(document.get("rows", ()))
    if (
        document.get("schema") != "sft-v3-intermolecular-binding-withheld-targets/1"
        or document.get("all_target_values_separate_from_identities") is not True
        or document.get("complete_row_count") != 1299
        or len(targets) != 1299
    ):
        raise ValueError("PROP-011 withheld registry changed")
    resolved: list[dict[str, object]] = []
    identity_keys = (
        "target_id", "dimer_id", "dimer_formula", "dimer_name", "donor_formula", "donor_name",
        "acceptor_formula", "acceptor_name", "source_id", "source_class", "source_locator", "snapshot_path",
    )
    for identity, target in zip(identities, targets):
        if tuple(identity.get(key) for key in identity_keys) != tuple(target.get(key) for key in identity_keys):
            raise ValueError("PROP-011 identity and withheld source rows differ")
        if target["source_class"] == "authoritative-calculated-benchmark":
            inscription = Fraction(str(target["value_inscription_kJ_per_mol"]))
            stored = _pair(target["absolute_inscribed_magnitude_kJ_per_mol"])
            if stored.fraction != abs(inscription) or inscription == 0:
                raise ValueError("PROP-011 calculated inscription reconstruction changed")
            value = stored if inscription > 0 else EMPTY_ONE
            result_class = "exact-positive-calculated-binding" if inscription > 0 else "signed-adverse-source-record-structural-EmptyOne"
        elif target["source_class"] == "reported-experimental-cluster-dissociation-value":
            central = _pair(target["central_cm_inverse"])
            uncertainty = _pair(target["uncertainty_cm_inverse"])
            lower = _pair(target["lower_cm_inverse"])
            upper = _pair(target["upper_cm_inverse"])
            if not lower.fraction < central.fraction < upper.fraction or central.fraction - uncertainty.fraction != lower.fraction or central.fraction + uncertainty.fraction != upper.fraction:
                raise ValueError("PROP-011 experimental interval reconstruction changed")
            value = central
            result_class = "exact-positive-reported-experimental-cluster-dissociation"
        else:
            raise ValueError("PROP-011 source class changed")
        resolved.append({**target, "vault_value": value, "result_class": result_class})
    if (
        len(resolved) != 1299
        or sum(isinstance(row["vault_value"], PositiveRatio) for row in resolved) != 1203
        or sum(isinstance(row["vault_value"], EmptyOne) for row in resolved) != 96
    ):
        raise ValueError("PROP-011 complete positive/adverse partition changed")
    return tuple(resolved)


class IntermolecularBindingValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = INTERMOLECULAR_BINDING_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(
            self.spec.experiment_id,
            {"registered-premise": sha256_identity(inputs["registered-premise"])},
            tuple(row.target_id for row in self.spec.target_rows),
            sealed.seal_hash,
            registration_hash,
        )
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, package_audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not package_audit.passed:
            raise ValueError("PROP-011 prediction package changed")
        predicted = _prediction_map(execution.output)

        # First target-value and source-orientation access occurs after the complete identity seal.
        source_rows = _source_rows(self.root)
        target_values = {str(row["target_id"]): row["vault_value"] for row in source_rows}
        vault = TargetVault(
            experiment_id=self.spec.experiment_id,
            custodian_id=self.spec.experiment_id + "-NIST-target-custodian",
            targets=target_values,
            custody_nonce=sha256_identity((registration_hash, TARGET_HASH)),
            expected_envelope_hash=sha256_identity(envelope),
        )
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)

        comparisons = []
        for row in source_rows:
            target_id = str(row["target_id"])
            word = predicted[target_id]
            released = release.targets[target_id]
            identity_match = (
                isinstance(word.cells[1], HeldLabel) and word.cells[1].label == row["dimer_formula"]
                and isinstance(word.cells[2], HeldLabel) and word.cells[2].label == row["dimer_name"]
                and isinstance(word.cells[3], HeldLabel) and word.cells[3].label == row["donor_formula"]
                and isinstance(word.cells[4], HeldLabel) and word.cells[4].label == row["acceptor_formula"]
                and isinstance(word.cells[5], HeldLabel) and word.cells[5].label == row["source_class"]
                and isinstance(word.cells[6], HeldLabel) and word.cells[6].label == row["source_id"]
            )
            value_match = released == row["vault_value"]
            comparisons.append({
                "target_id": target_id,
                "dimer_id": row["dimer_id"],
                "source_class": row["source_class"],
                "result_class": row["result_class"],
                "source_value_inscription": row.get("value_inscription_kJ_per_mol", row.get("value_inscription_cm_inverse")),
                "identity_match": identity_match,
                "exact_value_or_structural_absence_match": value_match,
                "passed": identity_match and value_match,
            })

        first_positive = next(row for row in source_rows if isinstance(row["vault_value"], PositiveRatio))
        first_adverse = next(row for row in source_rows if isinstance(row["vault_value"], EmptyOne))
        tampered = PositiveRatio.from_pair(
            first_positive["vault_value"].numerator.value + first_positive["vault_value"].denominator.value,
            first_positive["vault_value"].denominator.value,
        )
        controls = {
            "tampered_positive_value_rejected": tampered != release.targets[str(first_positive["target_id"])],
            "signed_adverse_cannot_become_negative_sft_number": isinstance(release.targets[str(first_adverse["target_id"])], EmptyOne),
            "missing_row_rejected": len(release.targets) == len(source_rows) == 1299,
            "complete_dimer_catalogue_retained": len({row["dimer_id"] for row in source_rows if row["source_class"] == "authoritative-calculated-benchmark"}) == 11,
            "computed_and_experimental_classes_not_conflated": {row["source_class"] for row in source_rows} == {"authoritative-calculated-benchmark", "reported-experimental-cluster-dissociation-value"},
            "all_96_signed_adverse_rows_retained": sum(isinstance(row["vault_value"], EmptyOne) for row in source_rows) == 96,
        }
        passed = all(bool(row["passed"]) for row in comparisons) and all(controls.values())
        isolation = seal_isolation_certificate(
            unsealed_isolation_certificate(
                executor_id=self.spec.experiment_id + "-prediction-executor",
                host_platform=platform.system() or "registered-host",
                python_implementation=platform.python_implementation(),
                interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
                program_hash=execution.program_hash,
                input_manifest_hash=execution.input_manifest_hash,
                registered_target_identity_hash=vault.commitment.target_identity_hash,
                comparison_implementation_identity_hash=sha256_identity((
                    "exact-positive-binding-or-structural-absence-complete-vector", self.spec.falsification_condition,
                )),
                prediction_seal_hash=prediction_seal.seal_hash,
                output_hash=execution.output_hash,
                trace_hash=execution.trace_hash,
            )
        )
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("PROP-011 released target differs from commitment")
        custody = seal_target_custody_certificate(
            unsealed_target_custody_certificate(
                custodian_id=release.custodian_id,
                experiment_registration_hash=registration_hash,
                registered_target_identity_hash=target_identity,
                prediction_seal_hash=prediction_seal.seal_hash,
                target_release_manifest_hash=release.release_hash,
            )
        )
        measurement_payload = {
            "experiment_registration_hash": registration_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "prediction_seal_hash": prediction_seal.seal_hash,
            "complete_1299_row_comparisons": comparisons,
            "controls": controls,
            "complete_trace_hash": execution.trace_hash,
        }
        return EmpiricalValidation(
            validated_seal_hash=sealed.seal_hash,
            experiment_registration_hash=registration_hash,
            isolation_certificate=isolation,
            target_custody_certificate=custody,
            evaluator_verified_seal=True,
            target_opened_after_seal=True,
            all_rows_preserved=True,
            data_source_ids=(
                "NIST-CCCBDB-SRD-101-DIMER-BINDING",
                "NIST-FARADAY-C8FD00092A-WATER-CLUSTER-DISSOCIATION",
                "NIST-JPCRD-1.555757-ION-CLUSTER-SCOPE",
            ),
            measurements=tuple(
                f"{row['target_id']}: {row['result_class']}; identity and exact post-seal result {row['passed']}"
                for row in comparisons
            ) + tuple(f"{name}: {result}" for name, result in controls.items()),
            measurement_receipt_hash=sha256_identity(measurement_payload),
            falsification_condition=self.spec.falsification_condition,
            passed=passed,
        )


__all__ = (
    "IntermolecularBindingValidator", "_prediction_map", "_source_rows",
    "experiment_registration_record", "prediction_program_document",
)
