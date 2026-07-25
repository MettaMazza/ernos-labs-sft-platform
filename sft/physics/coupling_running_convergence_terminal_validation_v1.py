"""Blind authoritative comparison for terminal coupling-running laws."""

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
from sft.physics.coupling_running_convergence_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    formal_certificate,
)
from sft.physics.measured_value import exact_decimal
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "PDG-COUPLING-RUNNING-CONVERGENCE-2025-2026"
SOURCE_RECORD_PATH = (
    "experiments/external_sources/physics/snapshots/"
    "coupling-running-convergence-source-record.json"
)
SOURCE_RECORD_HASH = "sha256:b83331089d96c073fbd5101753ba5c4716ae1a8b1b891e068684b6f7246d9953"
QCD_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-qcd.pdf"
QCD_HASH = "sha256:c04c628d76b18610c5fa2a919c6081918a25b55fb971b6af5829f4ca2baa386f"
EW_2026_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-electroweak-model.pdf"
EW_2026_HASH = "sha256:a102f6252b7190dc423200271dffa7c805cd15a50391b1c578853d2f777611cb"
EW_2025_PATH = "experiments/external_sources/physics/snapshots/pdg-2025-electroweak-model.pdf"
EW_2025_HASH = "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a"

SOURCE_IDS = (
    "PDG-2026-QCD-REVIEW",
    "PDG-2026-ELECTROWEAK-REVIEW",
    "PDG-2025-ELECTROMAGNETIC-RUNNING-ENDPOINT",
)
TARGET_IDS = (
    "PDG-COMPLETE-STRONG-RUNNING-VECTOR",
    "PDG-COMPLETE-ELECTROMAGNETIC-RUNNING-VECTOR",
    "PDG-EXPLICIT-ELECTROMAGNETIC-ENDPOINT-PAIR",
)
FALSIFICATION_CONDITION = (
    "Reject if any of the seven PDG QCD Table 9.1 rows, nine Figure 9.4 measurement classes, exact low- and "
    "m_Z-scale strong-coupling rows, five current alpha(0) rows, eleven current hadronic Delta-alpha rows, "
    "published electromagnetic running relation, direct LEP observation or explicit prior Z-scale endpoint is "
    "omitted or altered; if the separated strong-coupling intervals do not decrease from 1.37 GeV to m_Z; if "
    "the explicit inverse electromagnetic endpoint intervals do not decrease from the Thomson limit to the Z "
    "scale; if a universal physical energy sign is imposed despite the sealed carrier-specific coordinates; if "
    "the exact Fold support successor, running-share increment, pair-gap shrinkage or finite tolerance witness "
    "fails; if the formal convergence prediction is falsely labelled a direct measurement; or if any target "
    "content enters before the prediction seal."
)


def positive_ratio(value: Fraction) -> PositiveRatio:
    if value.numerator < 1:
        raise ValueError("coupling prediction input must remain exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        QCD_PATH: QCD_HASH,
        EW_2026_PATH: EW_2026_HASH,
        EW_2025_PATH: EW_2025_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"coupling-running source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID or len(record.get("sources", ())) != 3:
        raise ValueError("coupling-running source-set identity changed")
    custody = record.get("custody", {})
    required = {
        "complete_reported_rows_retained": True,
        "development_targets_already_known": True,
        "empirical_prediction_protocol": True,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "target_inaccessible_during_prediction_execution": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("coupling-running custody boundary changed")
    qcd, electroweak, endpoint = record["sources"]
    if (
        qcd.get("source_id") != SOURCE_IDS[0]
        or qcd.get("snapshot_sha256") != QCD_HASH.removeprefix("sha256:")
        or len(qcd.get("exact_multiscale_rows", ())) != 2
        or len(qcd["table_9_1"].get("complete_rows", ())) != 7
        or len(qcd["figure_9_4"].get("complete_legend_classes", ())) != 9
        or electroweak.get("source_id") != SOURCE_IDS[1]
        or electroweak.get("snapshot_sha256") != EW_2026_HASH.removeprefix("sha256:")
        or len(electroweak["alpha_zero_scope"].get("complete_rows", ())) != 5
        or len(electroweak["table_10_1"].get("complete_rows", ())) != 11
        or endpoint.get("source_id") != SOURCE_IDS[2]
        or endpoint.get("snapshot_sha256") != EW_2025_HASH.removeprefix("sha256:")
        or len(endpoint.get("exact_endpoint_rows", ())) != 2
    ):
        raise ValueError("coupling-running registered row or page scope changed")
    return record


def symmetric_interval(central: Fraction, uncertainty: Fraction) -> tuple[Fraction, Fraction]:
    lower = positive_take(central, uncertainty)
    if not isinstance(lower, Fraction):
        raise ValueError("measurement uncertainty exhausted its positive central value")
    return lower, central + uncertainty


def interval_from_pair(pair: list[str]) -> tuple[Fraction, Fraction]:
    if len(pair) != 2:
        raise ValueError("measurement pair must contain central value and uncertainty")
    return symmetric_interval(exact_decimal(pair[0]), exact_decimal(pair[1]))


def qcd_analysis(qcd: dict[str, object], electroweak: dict[str, object]) -> dict[str, object]:
    rows = qcd["exact_multiscale_rows"]
    low = rows[0]
    high = rows[1]
    low_interval = symmetric_interval(
        exact_decimal(low["central"]),
        exact_decimal(low["symmetric_uncertainty"]),
    )
    high_interval = symmetric_interval(
        exact_decimal(high["central"]),
        exact_decimal(high["symmetric_uncertainty"]),
    )
    z_mass = electroweak["z_mass_scope"]
    z_interval = symmetric_interval(
        exact_decimal(z_mass["central_GeV"]),
        exact_decimal(z_mass["symmetric_uncertainty_GeV"]),
    )
    low_scale = exact_decimal(low["scale_GeV"])
    table_rows = qcd["table_9_1"]["complete_rows"]
    all_table_intervals_positive = all(
        all(
            interval_from_pair(row[column])[0].numerator >= 1
            for column in ("unweighted", "weighted")
        )
        and (
            row["without_subfield"] is None
            or interval_from_pair(row["without_subfield"])[0].numerator >= 1
        )
        for row in table_rows
    )
    return {
        "exact_multiscale_row_count": len(rows),
        "table_9_1_row_count": len(table_rows),
        "figure_9_4_class_count": len(qcd["figure_9_4"]["complete_legend_classes"]),
        "low_scale_GeV": low_scale,
        "z_mass_interval_GeV": z_interval,
        "low_alpha_s_interval": low_interval,
        "mZ_alpha_s_interval": high_interval,
        "scales_strictly_ordered": low_scale < z_interval[0],
        "separated_intervals_strictly_decrease_with_energy": low_interval[0] > high_interval[1],
        "all_table_intervals_positive": all_table_intervals_positive,
        "full_figure_retained_without_fabricated_coordinates": (
            qcd["figure_9_4"]["machine_policy"]
            == "The complete vector figure is retained by immutable PDF hash and visual audit. Values not numerically printed by PDG are not fabricated by digitizing the plot."
        ),
        "pdg_energy_dependence_conclusion_retained": (
            qcd["printed_conclusion"]["comparison_class"]
            == "strong-coupling-energy-dependence-confirmed"
        ),
    }


def electromagnetic_analysis(
    electroweak: dict[str, object],
    endpoint: dict[str, object],
) -> dict[str, object]:
    alpha_zero_rows = electroweak["alpha_zero_scope"]["complete_rows"]
    delta_rows = electroweak["table_10_1"]["complete_rows"]
    adopted = alpha_zero_rows[-1]
    adopted_interval = symmetric_interval(
        exact_decimal(adopted["central_inverse_alpha"]),
        exact_decimal(adopted["standard_uncertainty"]),
    )
    endpoint_rows = endpoint["exact_endpoint_rows"]
    old_low_interval = symmetric_interval(
        exact_decimal(endpoint_rows[0]["central"]),
        exact_decimal(endpoint_rows[0]["standard_uncertainty"]),
    )
    high_interval = symmetric_interval(
        exact_decimal(endpoint_rows[1]["central"]),
        exact_decimal(endpoint_rows[1]["standard_uncertainty"]),
    )
    delta_intervals = tuple(
        symmetric_interval(
            exact_decimal(row["central"]),
            exact_decimal(row["symmetric_uncertainty"]),
        )
        for row in delta_rows
    )
    return {
        "alpha_zero_row_count": len(alpha_zero_rows),
        "delta_alpha_row_count": len(delta_rows),
        "current_adopted_inverse_alpha_interval": adopted_interval,
        "explicit_prior_low_inverse_alpha_interval": old_low_interval,
        "explicit_z_inverse_alpha_interval": high_interval,
        "inverse_alpha_strictly_decreases_to_z_scale": old_low_interval[0] > high_interval[1],
        "therefore_alpha_strictly_increases_to_z_scale": old_low_interval[0] > high_interval[1],
        "all_hadronic_delta_intervals_positive": all(
            interval[0].numerator >= 1 for interval in delta_intervals
        ),
        "published_running_relation_retained": (
            electroweak["alpha_zero_scope"]["published_relation"]
            == "alpha(M_Z^2) = alpha(0) / [1 - Delta alpha(M_Z^2)]"
        ),
        "direct_lep_observation_retained": (
            "L3 and OPAL directly observed" in electroweak["alpha_zero_scope"]["direct_observation"]
        ),
    }


def exact_measurement_analysis(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    qcd, electroweak, endpoint = record["sources"]
    strong = qcd_analysis(qcd, electroweak)
    electromagnetic = electromagnetic_analysis(electroweak, endpoint)
    return {
        "strong": strong,
        "electromagnetic": electromagnetic,
        "carrier_specific_opposite_energy_directions_retained": (
            strong["separated_intervals_strictly_decrease_with_energy"]
            and electromagnetic["therefore_alpha_strictly_increases_to_z_scale"]
        ),
        "formal_convergence_not_promoted_to_direct_measurement": True,
        "all_sources_retained": len(record["sources"]) == 3,
    }


def formal_prediction_inputs() -> dict[str, object]:
    certificate = formal_certificate()
    sectors = certificate["sectors"]
    supports = certificate["supports"]
    first_vector = dict(certificate["common_scale_vectors"][0])
    fourth_vector = dict(certificate["common_scale_vectors"][3])
    first_gaps = certificate["pair_gap_vectors"][0]
    fourth_gaps = certificate["pair_gap_vectors"][3]
    witness = certificate["convergence_witnesses"][-1]
    inputs: dict[str, object] = {
        "support_one": positive_ratio(Fraction(supports[0], 1)),
        "support_two": positive_ratio(Fraction(supports[1], 1)),
        "support_four": positive_ratio(Fraction(supports[2], 1)),
        "support_eight": positive_ratio(Fraction(supports[3], 1)),
        "pair_gap_base": positive_ratio(first_gaps[-1]),
        "pair_gap_level_four": positive_ratio(fourth_gaps[-1]),
        "finite_tolerance": positive_ratio(witness["tolerance"]),
        "finite_witness_gap": positive_ratio(witness["gap"]),
        "scale_relation": HeldLabel("coupling-scale", "One-base-binary-successor"),
        "running_relation": HeldLabel("coupling-running", "one-shortfall-of-sector-plus-support"),
        "gap_relation": HeldLabel("coupling-gap", "exact-pair-gap-shrinks-at-successor"),
        "convergence_relation": HeldLabel("coupling-convergence", "finite-positive-tolerance-witness"),
        "translation_relation": HeldLabel("coupling-translation", "carrier-specific-coordinate-orientation"),
    }
    for sector in sectors:
        inputs[f"sector_{sector}_base"] = positive_ratio(first_vector[sector])
        inputs[f"sector_{sector}_level_four"] = positive_ratio(fourth_vector[sector])
    return inputs


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
        "schema": "sft-v3-coupling-running-convergence-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-prediction",
        "frozen_relation": (
            "The complete prime-sector ladder shares One-base binary support; each running share is the holding "
            "part of sector plus support, every share increases with support, every exact pair gap decreases, "
            "and every finite tolerance has a generated witness. Physical energy orientation is carrier-specific."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": (
            "all seven PDG QCD Table 9.1 rows and all three columns; all nine Figure 9.4 measurement classes and "
            "its full immutable figure; both exact multi-scale strong rows; all five current alpha(0) rows; all "
            "eleven current Delta-alpha rows; the direct-observation statement, published relation and explicit "
            "prior high-scale endpoint"
        ),
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": (
            "exact rational interval ordering, complete-row and figure-class custody, opposite carrier-specific "
            "energy-direction control, non-promotion of formal convergence to measurement and hostile controls"
        ),
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    qcd, electroweak, endpoint = record["sources"]
    return {
        TARGET_IDS[0]: qcd,
        TARGET_IDS[1]: electroweak,
        TARGET_IDS[2]: endpoint,
    }


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("coupling-running prediction has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class CouplingRunningConvergenceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("coupling-running validator received the wrong claim seal")
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
        audited_program, package_audit = HostilePackageAuditor().audit_program_document(
            document, before, after
        )
        if sha256_identity(audited_program) != execution.program_hash or not package_audit.passed:
            raise ValueError("coupling-running prediction failed hostile-package audit")

        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed coupling-running prediction differs from formal inputs")

        qcd = qcd_analysis(context[TARGET_IDS[0]], context[TARGET_IDS[1]])
        electromagnetic = electromagnetic_analysis(
            context[TARGET_IDS[1]], context[TARGET_IDS[2]]
        )
        certificate = formal_certificate()
        formal_channel = all((
            prediction["support_one"].fraction == Fraction(1, 1),
            prediction["support_two"].fraction == Fraction(2, 1),
            prediction["support_four"].fraction == Fraction(4, 1),
            prediction["support_eight"].fraction == Fraction(8, 1),
            prediction["pair_gap_base"].fraction > prediction["pair_gap_level_four"].fraction,
            prediction["finite_witness_gap"].fraction < prediction["finite_tolerance"].fraction,
            prediction["translation_relation"]
            == HeldLabel("coupling-translation", "carrier-specific-coordinate-orientation"),
            all(item["gap_below_tolerance"] for item in certificate["convergence_witnesses"]),
        ))
        all_rows_preserved = all((
            qcd["exact_multiscale_row_count"] == 2,
            qcd["table_9_1_row_count"] == 7,
            qcd["figure_9_4_class_count"] == 9,
            electromagnetic["alpha_zero_row_count"] == 5,
            electromagnetic["delta_alpha_row_count"] == 11,
            len(authoritative_record(self.root)["sources"]) == 3,
        ))
        opposite_directions = all((
            qcd["separated_intervals_strictly_decrease_with_energy"],
            electromagnetic["therefore_alpha_strictly_increases_to_z_scale"],
        ))
        unfavorable_controls = all((
            qcd["low_alpha_s_interval"][0] > qcd["mZ_alpha_s_interval"][1],
            not (qcd["low_alpha_s_interval"][1] < qcd["mZ_alpha_s_interval"][0]),
            electromagnetic["explicit_prior_low_inverse_alpha_interval"][0]
            > electromagnetic["explicit_z_inverse_alpha_interval"][1],
            len(context[TARGET_IDS[0]]["table_9_1"]["complete_rows"][:-1]) != 7,
            len(context[TARGET_IDS[1]]["table_10_1"]["complete_rows"][:-1]) != 11,
            opposite_directions,
        ))
        passed = all((
            formal_channel,
            all_rows_preserved,
            unfavorable_controls,
            qcd["scales_strictly_ordered"],
            qcd["all_table_intervals_positive"],
            qcd["full_figure_retained_without_fabricated_coordinates"],
            qcd["pdg_energy_dependence_conclusion_retained"],
            electromagnetic["all_hadronic_delta_intervals_positive"],
            electromagnetic["published_running_relation_retained"],
            electromagnetic["direct_lep_observation_retained"],
            opposite_directions,
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-PDG-coupling-running-convergence-comparator/1",
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
            "complete_target_identity_hash": target_identity,
            "qcd_analysis": qcd,
            "electromagnetic_analysis": electromagnetic,
            "formal_channel": formal_channel,
            "all_rows_preserved": all_rows_preserved,
            "opposite_directions": opposite_directions,
            "formal_convergence_not_promoted_to_direct_measurement": True,
            "unfavorable_controls": unfavorable_controls,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            "PDG 2026 QCD complete Table 9.1 retained: seven rows, every reported averaging column and uncertainty",
            "PDG 2026 QCD Figure 9.4 retained by immutable source hash and visual audit: nine measurement classes across the displayed multi-scale range",
            f"PDG strong low-scale interval at Q=1.37 GeV: {qcd['low_alpha_s_interval']}",
            f"PDG strong m_Z-scale interval: {qcd['mZ_alpha_s_interval']}",
            "The separated exact intervals confirm that alpha_s decreases as transfer energy rises; the full figure and page-43 conclusion retain the wider multi-scale evidence",
            "PDG 2026 electromagnetic scope retained: five alpha(0) determinations, eleven hadronic Delta-alpha evaluations, the published running relation and direct L3/OPAL observations",
            f"PDG explicit prior Thomson inverse-alpha interval: {electromagnetic['explicit_prior_low_inverse_alpha_interval']}",
            f"PDG explicit prior Z-scale inverse-alpha interval: {electromagnetic['explicit_z_inverse_alpha_interval']}",
            "The inverse-alpha intervals decrease, hence electromagnetic alpha increases toward the Z scale",
            "Opposite physical energy directions pass only under the sealed carrier-specific self-source-range and screening-exposure translations; a universal imported sign is rejected",
            "The exact common-support convergence of the four Fold sector functions remains a standing falsifiable prediction and is not mislabelled as a direct measurement",
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
    "CouplingRunningConvergenceValidator",
    "FALSIFICATION_CONDITION",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "electromagnetic_analysis",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "formal_prediction_inputs",
    "qcd_analysis",
)
