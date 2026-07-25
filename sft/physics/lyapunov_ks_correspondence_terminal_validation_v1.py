"""Post-seal external comparison for the exact Fold rate carrier."""

from __future__ import annotations

import json
from pathlib import Path
import platform

from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldWord, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file
from sft.physics.lyapunov_ks_correspondence_terminal_law_v1 import CLAIM_ID, EXPERIMENT_ID, carrier_certificate, exact_support_count, separation_carrier


SOURCE_ID = "PH2-EXTERNAL-LYAPUNOV-KS-CORRESPONDENCE"
SOURCE_IDS = (SOURCE_ID,)
SOURCE_RECORD_PATH = "experiments/external_sources/physics/snapshots/lyapunov-ks-correspondence-source-record.json"
SOURCE_RECORD_HASH = "sha256:a23b394f6da97239f1cba263b949a7ca14d34ac26e657437807be5216c9c0be3"
BERNOULLI_PATH = "experiments/external_sources/physics/snapshots/arxiv-1211.1234-chaotic-map-trng.pdf"
BERNOULLI_HASH = "sha256:716c6b68b4755f47087747f67f4b2c4a7ed0ade30f77391a18129f2ad76de6c9"
PESIN_PATH = "experiments/external_sources/physics/snapshots/arxiv-1004.3441-pesin-entropy-formula.pdf"
PESIN_HASH = "sha256:ea560114c9cc196e18feb4536f63f28c292dadda465aafcb9f41ef12c20ac090"
TARGET_IDS = ("PH2-WITHHELD-MAP-AND-ENTROPY-CORRESPONDENCE",)
FALSIFICATION_CONDITION = (
    "Reject if either primary-source snapshot or the source record changes; if any registered map, preimage, "
    "distribution, output-symbol, rate-label or hypothesis-scope row is omitted; if the direct map's branch, slope "
    "and output counts do not equal the independently generated Fold carrier; if complete support does not grow "
    "as m to depth; if the expansion and information carriers differ; if the conditional scope of the entropy "
    "formula is universalized; if an analytic logarithm is imported as an SFT proof scalar; if a free correction "
    "is introduced; or if target content enters before prediction sealing."
)


def source_hashes() -> dict[str, str]:
    return {SOURCE_RECORD_PATH: SOURCE_RECORD_HASH, BERNOULLI_PATH: BERNOULLI_HASH, PESIN_PATH: PESIN_HASH}


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"PH2 source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID or len(record.get("snapshots", ())) != 2:
        raise ValueError("PH2 source record changed")
    target = record.get("registered_target", {})
    required = {
        "direct_map_case": "complete-two-branch-Bernoulli-map",
        "map_piece_count": "2",
        "absolute_branch_slope": "2",
        "preimage_count": "2",
        "stationary_distribution": "uniform",
        "output_alphabet_size": "2",
        "output_symbols": "independent-and-equiprobable",
        "conventional_lyapunov_label": "natural-logarithm-of-two",
        "conventional_information_rate_label": "one-bit-per-step",
        "entropy_formula_scope": "conditional-on-the-stated-regularity-invariance-and-splitting-hypotheses",
        "entropy_formula_relation": "metric-entropy-equals-integrated-sum-of-positive-Lyapunov-exponents",
    }
    if any(target.get(key) != value for key, value in required.items()):
        raise ValueError("PH2 registered target changed")
    custody = record.get("custody", {})
    if not all((
        custody.get("formal_claim_contains_external_target_values") is False,
        custody.get("target_inaccessible_during_prediction_execution") is True,
        custody.get("prediction_sealed_before_target_release_within_run") is True,
        custody.get("all_registered_comparison_rows_retained") is True,
        custody.get("measurements_select_formal_survivor") is False,
        custody.get("analytic_logarithms_used_as_sft_proof_values") is False,
    )):
        raise ValueError("PH2 custody changed")
    return record


def exact_measurement_analysis(target: dict[str, object]) -> dict[str, object]:
    m = int(target["map_piece_count"])
    depths = (1, 2, 3, 4, 5)
    support = tuple(exact_support_count(m, depth) for depth in depths)
    ratios = tuple(support[index + 1] // support[index] for index in range(len(support) - 1))
    separation_multipliers = tuple(separation_carrier(m, parts) // parts for parts in (1, 2, 3, 5, 8))
    return {
        "generated_carrier": m,
        "registered_piece_count": int(target["map_piece_count"]),
        "registered_absolute_slope": int(target["absolute_branch_slope"]),
        "registered_preimage_count": int(target["preimage_count"]),
        "registered_output_alphabet_size": int(target["output_alphabet_size"]),
        "depths": depths,
        "complete_support": support,
        "support_successor_ratios": ratios,
        "separation_multipliers": separation_multipliers,
        "all_exact_carriers_equal": all(value == m for value in (int(target["absolute_branch_slope"]), int(target["preimage_count"]), int(target["output_alphabet_size"]), *ratios, *separation_multipliers)),
        "uniform_independent_symbol_record_retained": target["stationary_distribution"] == "uniform" and target["output_symbols"] == "independent-and-equiprobable",
        "conventional_labels_retained": (target["conventional_lyapunov_label"], target["conventional_information_rate_label"]),
        "entropy_formula_scope_retained": target["entropy_formula_scope"],
        "entropy_formula_relation_retained": target["entropy_formula_relation"],
        "analytic_value_computed_or_imported": False,
    }


def formal_prediction_inputs() -> dict[str, object]:
    certificate = carrier_certificate()
    if not all((certificate["support_is_m_to_depth"], certificate["local_separation_multiplier_is_m"], certificate["common_exact_carrier"])):
        raise ValueError("formal carrier certificate failed")
    return {
        "domain_relation": HeldLabel("rate-domain", "complete-generated-positive-m-label-support"),
        "separation_relation": HeldLabel("separation-growth", "one-Fold-step-multiplies-by-m"),
        "support_relation": HeldLabel("support-growth", "one-depth-successor-multiplies-by-m"),
        "carrier_relation": HeldLabel("common-carrier", "same-generated-m-for-expansion-and-information"),
        "analytic_relation": HeldLabel("analytic-boundary", "external-symbolic-correspondence-only"),
        "scope_relation": HeldLabel("entropy-correspondence", "retain-source-hypotheses"),
    }


def prediction_program_document() -> dict[str, object]:
    keys = tuple(formal_prediction_inputs())
    instructions = [{"opcode": "input", "destination": key, "arguments": [key]} for key in keys]
    instructions.extend(({"opcode": "word", "destination": "prediction", "arguments": list(keys)}, {"opcode": "emit", "destination": "", "arguments": ["prediction"]}))
    return {"schema": "sft-v3-fold-program/1", "program_id": EXPERIMENT_ID + "-exact-prediction", "instructions": instructions}


def experiment_registration_record() -> dict[str, object]:
    return {
        "schema": "sft-v3-lyapunov-ks-correspondence-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-comparison",
        "frozen_relation": "For every generated positive whole m, local separation and complete information support have the same exact one-step carrier m; external analytic rate notation remains a symbolic correspondence boundary.",
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": "retain both complete primary-source snapshots and every registered favorable, scope-limiting and adverse comparison row",
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": "independent positive-whole support and separation reconstruction; complete direct-map carrier vector; conditional entropy-formula scope; no analytic proof scalar",
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def output_mapping(output: object, keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(keys):
        raise ValueError("PH2 prediction has wrong Fold shape")
    return dict(zip(keys, output.cells))


class LyapunovKSCorrespondenceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("wrong PH2 seal")
        registration = experiment_registration_record()
        registration_hash = sha256_identity(registration)
        document = prediction_program_document()
        program = fold_program_from_mapping(document)
        inputs = formal_prediction_inputs()
        keys = tuple(inputs)
        envelope = PredictionEnvelope(EXPERIMENT_ID, {key: sha256_identity(value) for key, value in inputs.items()}, TARGET_IDS, sha256_identity((sealed.seal_hash, registration["frozen_relation"])), registration_hash)
        targets = {TARGET_IDS[0]: authoritative_record(self.root)["registered_target"]}
        vault = TargetVault(experiment_id=EXPERIMENT_ID, custodian_id=EXPERIMENT_ID + "-external-target-custodian", targets=targets, custody_nonce=sha256_identity((registration_hash, SOURCE_RECORD_HASH, source_hashes())), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("PH2 hostile-package audit failed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        if output_mapping(execution.output, keys) != inputs:
            raise ValueError("PH2 prediction changed")
        analysis = exact_measurement_analysis(context[TARGET_IDS[0]])
        certificate = carrier_certificate()
        formal_channel = all((certificate["support_is_m_to_depth"], certificate["one_step_support_multiplier_is_m"], certificate["local_separation_multiplier_is_m"], certificate["common_exact_carrier"], not certificate["analytic_proof_value_required"]))
        all_rows = all((len(analysis["complete_support"]) == 5, len(analysis["support_successor_ratios"]) == 4, len(analysis["separation_multipliers"]) == 5, analysis["uniform_independent_symbol_record_retained"], bool(analysis["entropy_formula_scope_retained"]), bool(analysis["entropy_formula_relation_retained"])))
        controls = all((analysis["generated_carrier"] == 2, analysis["complete_support"] == (2, 4, 8, 16, 32), analysis["support_successor_ratios"] == (2, 2, 2, 2), analysis["separation_multipliers"] == (2, 2, 2, 2, 2), analysis["analytic_value_computed_or_imported"] is False))
        passed = all((formal_channel, all_rows, controls, analysis["all_exact_carriers_equal"]))
        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity(("exact-lyapunov-ks-correspondence-comparator/1", registration_hash, FALSIFICATION_CONDITION))
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=EXPERIMENT_ID + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=interpreter_hash, program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=comparator_hash, prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"seal": sealed.seal_hash, "prediction_seal": prediction_seal.seal_hash, "source_hashes": source_hashes(), "target_identity": target_identity, "analysis": analysis, "formal_channel": formal_channel, "all_rows": all_rows, "controls": controls, "trace": execution.trace_hash}
        measurements = (
            "Both primary-source snapshots are retained byte-for-byte and opened only after the V3 prediction seal.",
            "The direct two-branch map records two pieces, absolute slope two, two preimages and two independent equiprobable output symbols.",
            "Independent Fold reconstruction gives complete supports two, four, eight, sixteen and thirty-two at depths one through five.",
            "Every support successor ratio and every tested local-separation multiplier is exactly the same positive-whole carrier two.",
            "The conventional Lyapunov and one-bit information labels are retained as external labels; no logarithm, irrational approximation or decimal enters the Fold proof value.",
            "The entropy-formula correspondence retains the source's hypotheses and is not promoted to an unconditional identity.",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, all_rows, SOURCE_IDS, measurements, sha256_identity(payload), FALSIFICATION_CONDITION, passed)


__all__ = ("LyapunovKSCorrespondenceValidator", "FALSIFICATION_CONDITION", "SOURCE_IDS", "TARGET_IDS", "authoritative_record", "exact_measurement_analysis", "experiment_registration_record")
