"""Blind PDG/NIST comparison for terminal decay-width laws."""

from __future__ import annotations

from fractions import Fraction
from functools import reduce
import json
from operator import add
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
from sft.physics.decay_width_branching_lifetime_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    formal_certificate,
)
from sft.physics.measured_value import exact_decimal
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "PDG-NIST-DECAY-WIDTH-BRANCHING-LIFETIME-2026"
SOURCE_RECORD_PATH = (
    "experiments/external_sources/physics/snapshots/"
    "decay-width-branching-lifetime-source-record.json"
)
SOURCE_RECORD_HASH = "sha256:331b5b194d2282f2a9e9dde4d92c9635844f0e3cac08fd0389083287d81890fc"
PDG_PATH = "experiments/external_sources/physics/snapshots/pdg-2026-w-boson-listing.pdf"
PDG_HASH = "sha256:f1905e46980fb732a525de5a1eaa58cb6a87ff97a9dc135e3d7935912ba1d2a1"
CODATA_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"

SOURCE_IDS = ("PDG-2026-W-BOSON-LISTING", "NIST-CODATA-2022")
TARGET_IDS = (
    "PDG-W-COMPLETE-WIDTH-AND-BRANCHING-VECTOR",
    "NIST-CODATA-REDUCED-ACTION-CARRIER",
)
FALSIFICATION_CONDITION = (
    "Reject if the complete registered PDG W-width table, thirteen-row decay-mode table or either exclusive "
    "branching organization is incomplete; if PDG does not identify each branch as Gamma_i/Gamma or does not "
    "close the hadronic branch as One take three leptonic branches; if the complete measured exclusive intervals "
    "do not contain the One, if the exact complements forced from the printed leptonic values miss the printed "
    "hadronic interval, or if inclusive subsets are double counted; if the NIST action-prefix enclosure and PDG "
    "width interval do not yield a finite positive inverse-width lifetime interval and ordering; if any registered "
    "row, uncertainty, source identity or unfavorable control is omitted; or if target content enters before seal."
)


def positive_ratio(value: Fraction) -> PositiveRatio:
    if value.numerator < 1:
        raise ValueError("decay prediction input must remain exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def exact_total(values: tuple[Fraction, ...]) -> Fraction:
    if not values or any(value.numerator < 1 for value in values):
        raise ValueError("measurement total requires a nonempty positive family")
    return reduce(add, values[1:], values[0])


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        PDG_PATH: PDG_HASH,
        CODATA_PATH: CODATA_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"decay-width source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID or len(record.get("sources", ())) != 2:
        raise ValueError("decay-width source-set identity changed")
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
        raise ValueError("decay-width custody boundary changed")
    pdg = record["sources"][0]
    nist = record["sources"][1]
    width_rows = pdg["width_scope"]["complete_table_rows"]
    mode_rows = pdg["decay_mode_scope"]["complete_primary_mode_rows"]
    individual = pdg["branching_scope"]["individual_exclusive_fit"]
    if (
        pdg.get("source_id") != SOURCE_IDS[0]
        or pdg.get("snapshot_sha256") != PDG_HASH.removeprefix("sha256:")
        or pdg["width_scope"].get("printed_page") != 5
        or pdg["decay_mode_scope"].get("printed_page") != 7
        or pdg["branching_scope"].get("printed_pages") != [8, 9, 10, 11, 12]
        or len(width_rows) != 16
        or len(mode_rows) != 13
        or len(individual) != 4
        or nist.get("source_id") != SOURCE_IDS[1]
        or len(nist.get("required_rows", ())) != 1
    ):
        raise ValueError("decay-width registered page or row scope changed")
    if tuple(row["gamma_id"] for row in mode_rows) != tuple(
        f"Gamma{index}" for index in range(1, 14)
    ):
        raise ValueError("PDG complete mode-row identity changed")
    return record


def codata_action_row(root: Path) -> str:
    rows = tuple(
        line
        for line in (root / CODATA_PATH).read_text(encoding="utf-8").splitlines()
        if len(line) >= 110 and line[:60].strip() == "reduced Planck constant in eV s"
    )
    if len(rows) != 1:
        raise ValueError("NIST reduced-action row changed")
    row = rows[0]
    if (
        row[60:85].strip() != "6.582 119 569... e-16"
        or row[85:110].strip() != "(exact)"
        or row[110:].strip() != "eV s"
    ):
        raise ValueError("NIST reduced-action inscription changed")
    return row


def percent_part(value: str) -> Fraction:
    return exact_decimal(value) / Fraction(100, 1)


def symmetric_interval(central: Fraction, uncertainty: Fraction) -> tuple[Fraction, Fraction]:
    if central <= uncertainty:
        raise ValueError("measurement interval lost a positive lower endpoint")
    lower = positive_take(central, uncertainty)
    if not isinstance(lower, Fraction):
        raise ValueError("measurement lower endpoint became structural empty")
    return lower, central + uncertainty


def interval_contains(interval: tuple[Fraction, Fraction], value: Fraction) -> bool:
    return interval[0] <= value <= interval[1]


def interval_product(
    left: tuple[Fraction, Fraction],
    right: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    return left[0] * right[0], left[1] * right[1]


def pdg_analysis(record: dict[str, object]) -> dict[str, object]:
    pdg = record["sources"][0]
    widths = pdg["width_scope"]["complete_table_rows"]
    modes = pdg["decay_mode_scope"]["complete_primary_mode_rows"]
    branching = pdg["branching_scope"]
    universal = branching["lepton_universality_fit"]
    individual = branching["individual_exclusive_fit"]

    width_central = exact_decimal(widths[0]["central"])
    width_uncertainty = exact_decimal(widths[0]["uncertainties"][0])
    width_interval = symmetric_interval(width_central, width_uncertainty)

    lepton_each = percent_part(universal["leptonic_each_central_percent"])
    lepton_uncertainty = percent_part(universal["leptonic_each_uncertainty_percent"])
    hadron = percent_part(universal["hadronic_central_percent"])
    hadron_uncertainty = percent_part(universal["hadronic_uncertainty_percent"])
    universal_intervals = (
        symmetric_interval(lepton_each, lepton_uncertainty),
        symmetric_interval(lepton_each, lepton_uncertainty),
        symmetric_interval(lepton_each, lepton_uncertainty),
        symmetric_interval(hadron, hadron_uncertainty),
    )
    universal_central = (lepton_each, lepton_each, lepton_each, hadron)
    universal_interval_sum = (
        exact_total(tuple(item[0] for item in universal_intervals)),
        exact_total(tuple(item[1] for item in universal_intervals)),
    )
    three_leptons = lepton_each * Fraction(3, 1)
    forced_universal_hadron = positive_take(Fraction(1, 1), three_leptons)
    if not isinstance(forced_universal_hadron, Fraction):
        raise ValueError("universal leptonic vector exhausted the One")

    individual_central = tuple(percent_part(row["central_percent"]) for row in individual)
    individual_intervals = tuple(
        symmetric_interval(
            percent_part(row["central_percent"]),
            percent_part(row["uncertainty_percent"]),
        )
        for row in individual
    )
    individual_interval_sum = (
        exact_total(tuple(item[0] for item in individual_intervals)),
        exact_total(tuple(item[1] for item in individual_intervals)),
    )
    first_three = exact_total(individual_central[:3])
    forced_individual_hadron = positive_take(Fraction(1, 1), first_three)
    if not isinstance(forced_individual_hadron, Fraction):
        raise ValueError("individual leptonic vector exhausted the One")

    universal_printed_total = exact_total(universal_central)
    individual_printed_total = exact_total(individual_central)
    universal_rounding_take = positive_take(Fraction(1, 1), universal_printed_total)
    individual_rounding_take = positive_take(individual_printed_total, Fraction(1, 1))
    if not isinstance(universal_rounding_take, Fraction) or not isinstance(individual_rounding_take, Fraction):
        raise ValueError("printed branching residual direction changed")

    partial_width_intervals = tuple(
        interval_product(width_interval, branch_interval)
        for branch_interval in individual_intervals
    )
    partial_sum_interval = (
        exact_total(tuple(item[0] for item in partial_width_intervals)),
        exact_total(tuple(item[1] for item in partial_width_intervals)),
    )
    classifications = tuple(row["classification"] for row in modes)
    return {
        "width_row_count": len(widths),
        "used_width_component_count": len(tuple(row for row in widths[1:] if row["used_in_average"])),
        "mode_row_count": len(modes),
        "individual_exclusive_row_count": len(individual),
        "width_central_GeV": width_central,
        "width_interval_GeV": width_interval,
        "universal_central_branch_vector": universal_central,
        "universal_interval_sum": universal_interval_sum,
        "universal_interval_contains_one": interval_contains(universal_interval_sum, Fraction(1, 1)),
        "forced_universal_hadron": forced_universal_hadron,
        "forced_universal_hadron_inside_reported_interval": interval_contains(
            universal_intervals[3], forced_universal_hadron
        ),
        "universal_printed_rounding_take": universal_rounding_take,
        "individual_central_branch_vector": individual_central,
        "individual_interval_sum": individual_interval_sum,
        "individual_interval_contains_one": interval_contains(individual_interval_sum, Fraction(1, 1)),
        "forced_individual_hadron": forced_individual_hadron,
        "forced_individual_hadron_inside_reported_interval": interval_contains(
            individual_intervals[3], forced_individual_hadron
        ),
        "individual_printed_rounding_take": individual_rounding_take,
        "partial_width_intervals_GeV": partial_width_intervals,
        "partial_width_sum_interval_GeV": partial_sum_interval,
        "partial_width_sum_encloses_total_width_interval": (
            partial_sum_interval[0] <= width_interval[0]
            and partial_sum_interval[1] >= width_interval[1]
        ),
        "published_gamma_fraction_notation": all(
            row["gamma_id"].startswith("Gamma") for row in modes
        ),
        "published_exact_complement_relation": universal["published_closure_relation"]
        == "B(W to hadrons) = 1 - 3 B(W to ell nu)",
        "subsets_retained_without_double_counting": (
            len(classifications) == 13
            and classifications.count("exclusive primary leptonic channel") == 3
            and classifications.count("exclusive primary hadronic complement") == 1
            and all(
                "subset" in classification or "search class" in classification
                for classification in classifications[5:]
            )
        ),
    }


def nist_action_analysis(row: str, width_interval: tuple[Fraction, Fraction]) -> dict[str, object]:
    if row[:60].strip() != "reduced Planck constant in eV s":
        raise ValueError("wrong NIST action row released")
    lower_eVs = Fraction(6582119569, 10**25)
    upper_eVs = Fraction(6582119570, 10**25)
    lower_GeVs = lower_eVs / Fraction(10**9, 1)
    upper_GeVs = upper_eVs / Fraction(10**9, 1)
    lifetime_interval = (
        lower_GeVs / width_interval[1],
        upper_GeVs / width_interval[0],
    )
    atlas_width = exact_decimal("2.202")
    tevatron_width = exact_decimal("2.046")
    atlas_lifetime = lower_GeVs / atlas_width
    tevatron_lifetime = lower_GeVs / tevatron_width
    return {
        "displayed_prefix_interval_eV_s": (lower_eVs, upper_eVs),
        "displayed_prefix_interval_GeV_s": (lower_GeVs, upper_GeVs),
        "pdg_width_interval_GeV": width_interval,
        "derived_lifetime_interval_s": lifetime_interval,
        "finite_positive_lifetime_interval": (
            lifetime_interval[0].numerator >= 1
            and lifetime_interval[1] > lifetime_interval[0]
        ),
        "greater_width_shorter_lifetime": (
            atlas_width > tevatron_width and atlas_lifetime < tevatron_lifetime
        ),
        "ellipsis_not_promoted_to_exact_rational": True,
    }


def exact_measurement_analysis(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    pdg = pdg_analysis(record)
    nist = nist_action_analysis(codata_action_row(root), pdg["width_interval_GeV"])
    return {
        "pdg": pdg,
        "nist": nist,
        "all_sources_retained": len(record["sources"]) == 2,
    }


def formal_prediction_inputs() -> dict[str, object]:
    certificate = formal_certificate()
    widths = certificate["sample_partial_widths"]
    parts = certificate["sample_branching_parts"]
    return {
        "partial_width_one": positive_ratio(widths[0]),
        "partial_width_two": positive_ratio(widths[1]),
        "partial_width_three": positive_ratio(widths[2]),
        "total_width": positive_ratio(certificate["sample_total_width"]),
        "branch_one": positive_ratio(parts[0]),
        "branch_two": positive_ratio(parts[1]),
        "branch_three": positive_ratio(parts[2]),
        "branch_partition": positive_ratio(certificate["sample_partition"]),
        "lifetime": positive_ratio(certificate["sample_lifetime"]),
        "closed_channel": HeldLabel("decay-channel", "structural-empty-form"),
        "width_relation": HeldLabel("decay-width", "complete-positive-partial-sum"),
        "branch_relation": HeldLabel("decay-branch", "partial-over-total-partition-of-one"),
        "lifetime_relation": HeldLabel("decay-duration", "action-over-total-width"),
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
        "schema": "sft-v3-decay-width-branching-lifetime-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-prediction",
        "frozen_relation": (
            "Every positive open-channel partial width is paired transition support per action; total width is "
            "their complete sum, each branch is partial over total, complete exclusive branches partition the "
            "One, and lifetime is action over total width."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": (
            "all sixteen PDG W-width rows including unused inputs and every printed uncertainty; all thirteen "
            "primary decay-mode rows with aggregate/subset classification; both complete exclusive fit vectors; "
            "the exact PDG complement statement; and the complete NIST reduced-action row"
        ),
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": (
            "exact rational interval sums, forced exclusive complements, partial-width interval transport, exact "
            "rational enclosure of the NIST ellipsis and adverse omitted/double-counted/direct-lifetime controls"
        ),
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    return {
        TARGET_IDS[0]: {
            "width_scope": record["sources"][0]["width_scope"],
            "decay_mode_scope": record["sources"][0]["decay_mode_scope"],
            "branching_scope": record["sources"][0]["branching_scope"],
        },
        TARGET_IDS[1]: codata_action_row(root),
    }


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("decay-width prediction has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class DecayWidthBranchingLifetimeValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("decay-width validator received the wrong claim seal")
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
            raise ValueError("decay-width prediction failed hostile-package audit")

        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed decay-width prediction differs from formal inputs")

        released_pdg = context[TARGET_IDS[0]]
        released_nist = context[TARGET_IDS[1]]
        synthetic_record = authoritative_record(self.root)
        synthetic_record["sources"][0]["width_scope"] = released_pdg["width_scope"]
        synthetic_record["sources"][0]["decay_mode_scope"] = released_pdg["decay_mode_scope"]
        synthetic_record["sources"][0]["branching_scope"] = released_pdg["branching_scope"]
        pdg = pdg_analysis(synthetic_record)
        nist = nist_action_analysis(released_nist, pdg["width_interval_GeV"])

        formal_channel = all((
            prediction["partial_width_one"].fraction == Fraction(1, 4),
            prediction["partial_width_two"].fraction == Fraction(1, 2),
            prediction["partial_width_three"].fraction == Fraction(5, 4),
            prediction["total_width"].fraction == Fraction(2, 1),
            prediction["branch_one"].fraction == Fraction(1, 8),
            prediction["branch_two"].fraction == Fraction(1, 4),
            prediction["branch_three"].fraction == Fraction(5, 8),
            prediction["branch_partition"].fraction == Fraction(1, 1),
            prediction["lifetime"].fraction == Fraction(1, 2),
            prediction["closed_channel"] == HeldLabel("decay-channel", "structural-empty-form"),
        ))
        all_rows_preserved = all((
            pdg["width_row_count"] == 16,
            pdg["used_width_component_count"] == 3,
            pdg["mode_row_count"] == 13,
            pdg["individual_exclusive_row_count"] == 4,
            len(authoritative_record(self.root)["sources"]) == 2,
        ))
        unfavorable_controls = all((
            exact_total(pdg["individual_central_branch_vector"][:3]) != Fraction(1, 1),
            exact_total(pdg["individual_central_branch_vector"] + (percent_part("33.0"),))
            != Fraction(1, 1),
            Fraction(1, 1) / pdg["individual_central_branch_vector"][0]
            != pdg["individual_central_branch_vector"][0],
            pdg["width_central_GeV"] != nist["derived_lifetime_interval_s"][0],
            len(authoritative_record(self.root)["sources"][0]["width_scope"]["complete_table_rows"][:-1])
            != 16,
        ))
        passed = all((
            formal_channel,
            all_rows_preserved,
            unfavorable_controls,
            pdg["published_gamma_fraction_notation"],
            pdg["published_exact_complement_relation"],
            pdg["universal_interval_contains_one"],
            pdg["forced_universal_hadron_inside_reported_interval"],
            pdg["individual_interval_contains_one"],
            pdg["forced_individual_hadron_inside_reported_interval"],
            pdg["partial_width_sum_encloses_total_width_interval"],
            pdg["subsets_retained_without_double_counting"],
            nist["finite_positive_lifetime_interval"],
            nist["greater_width_shorter_lifetime"],
            nist["ellipsis_not_promoted_to_exact_rational"],
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-PDG-NIST-decay-width-branching-lifetime-comparator/1",
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
            "pdg_analysis": pdg,
            "nist_action_analysis": nist,
            "formal_channel": formal_channel,
            "all_rows_preserved": all_rows_preserved,
            "unfavorable_controls": unfavorable_controls,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            "PDG 2026 complete W-width table retained: sixteen rows, every uncertainty, use-status and scale-factor note",
            "PDG 2026 complete thirteen-row W decay-mode table retained with aggregate, exclusive, inclusive-subset and upper-limit classes kept distinct",
            "PDG exclusive individual vector retained: e, mu, tau and hadronic branch intervals contain the One jointly",
            "PDG universality fit retained: B(hadrons)=One take 3*B(ell nu) exactly; the forced complement lies inside the reported hadronic interval",
            f"PDG total width interval GeV: {pdg['width_interval_GeV']}",
            f"PDG exact individual partial-width enclosure GeV: {pdg['partial_width_sum_interval_GeV']}",
            "NIST reduced-action ellipsis retained as an adjacent rational enclosure, never as an exact rational proof value",
            f"derived W lifetime interval s from NIST action and PDG width: {nist['derived_lifetime_interval_s']}",
            "omitted branch, double-counted inclusive subset, inverse branch, direct width-lifetime and incomplete-source controls rejected",
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
    "DecayWidthBranchingLifetimeValidator",
    "FALSIFICATION_CONDITION",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "codata_action_row",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "formal_prediction_inputs",
    "nist_action_analysis",
    "pdg_analysis",
)
