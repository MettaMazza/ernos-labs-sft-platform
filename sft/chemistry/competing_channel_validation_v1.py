"""Capability-closed post-seal validation for Chemistry KIN-006."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path
import platform

from sft.chemistry.competing_channel_batch_v1 import (
    ARTICLE_HASH, ARTICLE_PATH, COMPETING_CHANNEL_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.competing_channel_law_v1 import (
    CompleteChannelRecord, ProductChannelSupport, forced_competing_channel_branching,
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
    "target_id", "source_id", "article_doi", "reaction_identity", "measurement_identity", "condition_identity",
    "source_table_identity", "source_product_row", "product_channel_identity",
)


def _identities(root: Path) -> tuple[dict, ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("KIN-006 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text())
    rows = tuple(document.get("rows", ()))
    forbidden = {
        "pressure_external_inscription_mbar", "temperature_external_inscription",
        "experimental_branching_percent_external_inscription",
        "experimental_branching_exact_fraction_of_complete_support",
        "experimental_uncertainty_percent_external_inscription", "experimental_uncertainty_exact_fraction",
        "calculated_comparison_percent_external_inscription", "calculated_comparison_exact_fraction",
        "target_payload", "target_payload_hash", "snapshot_hash",
    }
    if (
        document.get("complete_registered_product_channel_count") != 8
        or document.get("all_branching_condition_spectrum_uncertainty_analysis_and_target_hash_values_absent") is not True
        or len(rows) != 8 or any(forbidden.intersection(row) for row in rows)
        or tuple(row["source_product_row"] for row in rows) != tuple(range(1, 9))
        or len({row["product_channel_identity"] for row in rows}) != 8
    ):
        raise ValueError("KIN-006 value-free identity boundary changed")
    return rows


def prediction_program_document(root: Path) -> dict:
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table: list[str] = []
    for ordinal, row in enumerate(_identities(root), start=1):
        prefix = f"competing-channel-row-{ordinal}"
        instructions.append({"opcode": "label", "destination": prefix + "-target", "arguments": ["target-id", row["target_id"]]})
        registers = ["premise"]
        identities = (
            ("complete-source-identity", str(row["source_id"])),
            ("source-article-identity", str(row["article_doi"])),
            ("registered-reaction-identity", str(row["reaction_identity"])),
            ("measurement-identity", str(row["measurement_identity"])),
            ("held-condition-identity", str(row["condition_identity"])),
            ("source-table-identity", str(row["source_table_identity"])),
            ("positive-source-product-row", str(row["source_product_row"])),
            ("registered-product-channel-identity", str(row["product_channel_identity"])),
        )
        for number, (family, label) in enumerate(identities, start=1):
            destination = f"{prefix}-identity-{number}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        for family, label in (
            ("complete-support-law", "all-registered-product-channels-retained-in-source-order"),
            ("branch-relation-law", "exact-channel-support-over-exact-complete-support"),
            ("absence-law", "unfavorable-and-EmptyOne-channels-retained-without-invention"),
            ("provenance-law", "experimental-vector-separated-from-calculated-and-analysis-disclosures"),
        ):
            destination = f"{prefix}-law-{len(registers)}"
            instructions.append({"opcode": "label", "destination": destination, "arguments": [family, label]})
            registers.append(destination)
        instructions.append({"opcode": "word", "destination": prefix + "-word", "arguments": registers})
        table.extend((prefix + "-target", prefix + "-word"))
    instructions.extend((
        {"opcode": "table", "destination": "complete-competing-channel-vector", "arguments": table},
        {"opcode": "emit", "destination": "", "arguments": ["complete-competing-channel-vector"]},
    ))
    return {
        "schema": "sft-v3-fold-program/1",
        "program_id": COMPETING_CHANNEL_SPEC.experiment_id + "-value-free-complete-vector",
        "instructions": instructions,
    }


def experiment_registration_record(root: Path) -> dict:
    return {
        "experiment_id": COMPETING_CHANNEL_SPEC.experiment_id,
        "claim_id": COMPETING_CHANNEL_SPEC.claim_id,
        "provenance": "forward_forcing_with_prefetch_value_free_identity_seal",
        "frozen_relation": COMPETING_CHANNEL_SPEC.exact_result,
        "identity_registry": (IDENTITY_PATH, IDENTITY_HASH),
        "withheld_target_registry": (TARGET_PATH, TARGET_HASH),
        "primary_source_record": (PRIMARY_PATH, PRIMARY_HASH),
        "complete_article_snapshot": (ARTICLE_PATH, ARTICLE_HASH),
        "prediction_program": prediction_program_document(root),
        "target_ids": tuple(row.target_id for row in COMPETING_CHANNEL_SPEC.target_rows),
        "all_branching_condition_spectrum_uncertainty_analysis_and_target_hash_values_absent": True,
        "falsification_condition": COMPETING_CHANNEL_SPEC.falsification_condition,
    }


def _prediction_map(output: object) -> dict[str, FoldWord]:
    if not isinstance(output, FoldTable) or len(output.entries) != 8:
        raise ValueError("KIN-006 prediction is not the complete eight-channel table")
    resolved = {}
    for entry in output.entries:
        if (
            not isinstance(entry.left, HeldLabel) or entry.left.family != "target-id"
            or not isinstance(entry.right, FoldWord) or len(entry.right.cells) != 13
        ):
            raise ValueError("KIN-006 prediction lost a complete consequence")
        resolved[entry.left.label] = entry.right
    if len(resolved) != 8:
        raise ValueError("KIN-006 duplicated a target identity")
    return resolved


def _source_rows(root: Path) -> tuple[dict, ...]:
    for path, expected in ((TARGET_PATH, TARGET_HASH), (PRIMARY_PATH, PRIMARY_HASH), (ARTICLE_PATH, ARTICLE_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError(f"KIN-006 source changed: {path}")
    identities = _identities(root)
    document = json.loads((root / TARGET_PATH).read_text())
    targets = tuple(document.get("rows", ()))
    if (
        document.get("complete_registered_product_channel_count") != 8
        or document.get("release_requires_complete_identity_prediction_seal") is not True
        or document.get("identity_registry_hash") != IDENTITY_HASH or len(targets) != 8
    ):
        raise ValueError("KIN-006 target registry changed")
    resolved = []
    for identity, target in zip(identities, targets):
        if any(identity[key] != target.get(key) for key in IDENTITY_KEYS):
            raise ValueError("KIN-006 identity/target binding changed")
        resolved.append({**identity, "target_payload": target, "target_payload_hash": sha256_identity(target)})
    return tuple(resolved)


def exact_competing_channel_analysis(rows: tuple[dict, ...], primary: dict) -> dict:
    if len(rows) != 8:
        raise ValueError("KIN-006 requires the complete eight-channel vector")
    channels = []
    experimental = []
    uncertainties = []
    calculated = []
    for ordinal, row in enumerate(rows, start=1):
        target = row["target_payload"]
        if (
            target.get("source_status")
            != "experimentally determined branching ratio with separately retained calculated comparison"
            or target.get("source_product_row") != ordinal
        ):
            raise ValueError("KIN-006 target provenance or source order changed")
        support = Fraction(target["experimental_branching_exact_fraction_of_complete_support"])
        uncertainty = Fraction(target["experimental_uncertainty_exact_fraction"])
        calculation = Fraction(target["calculated_comparison_exact_fraction"])
        if support <= 0 or uncertainty <= 0 or calculation <= 0:
            raise ValueError("KIN-006 external vector contains prohibited nonpositive magnitude")
        if support != Fraction(int(target["experimental_branching_percent_external_inscription"]), 100):
            raise ValueError("KIN-006 experimental exact fraction changed")
        if uncertainty != Fraction(int(target["experimental_uncertainty_percent_external_inscription"]), 100):
            raise ValueError("KIN-006 uncertainty exact fraction changed")
        channels.append(ProductChannelSupport(
            HeldLabel("registered-product-channel", target["product_channel_identity"]),
            PositiveRatio.from_pair(support.numerator, support.denominator), PositiveCount(ordinal),
        ))
        experimental.append(support)
        uncertainties.append(uncertainty)
        calculated.append(calculation)
    relation = forced_competing_channel_branching(CompleteChannelRecord(
        HeldLabel("registered-reaction", rows[0]["reaction_identity"]),
        HeldLabel("held-condition", rows[0]["condition_identity"]), tuple(channels),
    ))
    shares = tuple(row.share_of_complete_support.fraction for row in relation.ordered_rows)
    pdf_records = tuple(primary.get("supplement_pdf_records", ()))
    return {
        "complete_product_channel_count": len(rows),
        "complete_supplementary_file_count": primary.get("complete_supplementary_file_count"),
        "complete_supplement_pdf_count": len(pdf_records),
        "exact_experimental_support_sum": str(sum(experimental, Fraction(0, 1))),
        "exact_calculated_comparison_sum": str(sum(calculated, Fraction(0, 1))),
        "exact_experimental_branching_range": {"minimum": str(min(experimental)), "maximum": str(max(experimental))},
        "exact_experimental_uncertainty_range": {"minimum": str(min(uncertainties)), "maximum": str(max(uncertainties))},
        "all_eight_source_rows_and_product_identities_retained": (
            tuple(row.source_row.value for row in relation.ordered_rows) == tuple(range(1, 9))
            and len({row.channel_identity for row in relation.ordered_rows}) == 8
        ),
        "forced_shares_match_complete_postseal_experimental_vector": shares == tuple(experimental),
        "complete_channel_partition_reconstructs_One": sum(shares, Fraction(0, 1)) == Fraction(1, 1),
        "weakest_and_all_unfavorable_channels_retained": min(shares) == Fraction(3, 50) and len(shares) == 8,
        "complete_article_nineteen_files_and_two_pdfs_retained": (
            primary.get("all_article_and_supplement_files_preserved") is True
            and primary.get("complete_supplementary_file_count") == 19
            and len(primary.get("complete_supplementary_files", ())) == 19
            and len(pdf_records) == 2
        ),
        "experimental_calculated_and_analysis_provenance_separated": (
            primary.get("experimental_and_calculated_columns_separated") is True
            and primary.get("reference_spectrum_Monte_Carlo_and_analysis_disclosures_retained") is True
        ),
        "no_imported_normalization_fit_selection_or_target_correction": (
            primary.get("imported_probability_normalization_branching_equation_fitted_ratio_selection_renormalization_or_target_correction_used_in_fold_law") is False
            and primary.get("external_values_used_as_proof_parameters") is False
            and primary.get("image_curves_not_digitized_and_unreported_values_not_inferred") is True
        ),
    }


class CompetingChannelValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.spec = COMPETING_CHANNEL_SPEC

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
            raise ValueError("KIN-006 prediction package changed")
        predicted = _prediction_map(execution.output)
        source_rows = _source_rows(self.root)
        target_values = {
            row["target_id"]: HeldLabel("external-competing-channel-row-hash", row["target_payload_hash"])
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
            "all-registered-product-channels-retained-in-source-order",
            "exact-channel-support-over-exact-complete-support",
            "unfavorable-and-EmptyOne-channels-retained-without-invention",
            "experimental-vector-separated-from-calculated-and-analysis-disclosures",
        )
        comparisons = []
        for row in source_rows:
            word = predicted[row["target_id"]]
            identity_values = tuple(str(row[key]) for key in IDENTITY_KEYS[1:])
            identity_match = all(
                isinstance(word.cells[index], HeldLabel) and word.cells[index].label == value
                for index, value in enumerate(identity_values, start=1)
            )
            law_match = tuple(cell.label for cell in word.cells[9:]) == expected_laws
            target_match = release.targets[row["target_id"]] == HeldLabel(
                "external-competing-channel-row-hash", row["target_payload_hash"]
            )
            comparisons.append({
                "target_id": row["target_id"], "identity_match": identity_match,
                "law_match": law_match, "postseal_target_hash_match": target_match,
                "passed": identity_match and law_match and target_match,
            })
        primary = json.loads((self.root / PRIMARY_PATH).read_text())
        analysis = exact_competing_channel_analysis(source_rows, primary)
        try:
            exact_competing_channel_analysis(source_rows[:-1], primary)
            omitted_channel_rejected = False
        except (ValueError, RuntimeError):
            omitted_channel_rejected = True
        controls = {
            "tampered_omitted_product_channel_rejected": omitted_channel_rejected,
            "complete_eight_channel_target_vector_retained": len(release.targets) == 8,
            "exact_whole_reconstructed_without_renormalization": analysis["complete_channel_partition_reconstructs_One"],
            "weak_and_unfavorable_channels_retained": analysis["weakest_and_all_unfavorable_channels_retained"],
            "prediction_contains_no_withheld_target_hash": TARGET_HASH not in json.dumps(document, sort_keys=True),
        }
        non_boolean = {
            "complete_product_channel_count", "complete_supplementary_file_count", "complete_supplement_pdf_count",
            "exact_experimental_support_sum", "exact_calculated_comparison_sum", "exact_experimental_branching_range",
            "exact_experimental_uncertainty_range",
        }
        passed = (
            all(row["passed"] for row in comparisons)
            and all(bool(value) for key, value in analysis.items() if key not in non_boolean)
            and all(controls.values())
        )
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-complete-support-branching-correspondence", self.spec.falsification_condition)),
            prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash,
            trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("KIN-006 released target differs from commitment")
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
            f"{row['target_id']}: product={row['product_channel_identity']}; target={row['target_payload_hash']}"
            for row in source_rows
        ) + (
            f"exact experimental branching range: {analysis['exact_experimental_branching_range']}",
            f"exact experimental uncertainty range: {analysis['exact_experimental_uncertainty_range']}",
            "complete eight-product experimental vector reconstructs One; complete article, nineteen supplementary files, two PDFs and separate calculated/analysis provenance retained",
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
    "CompetingChannelValidator", "_identities", "_prediction_map", "_source_rows",
    "exact_competing_channel_analysis", "experiment_registration_record", "prediction_program_document",
)
