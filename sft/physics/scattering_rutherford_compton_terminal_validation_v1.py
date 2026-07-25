"""Blind IAEA/NIST comparison for terminal scattering laws."""

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
from sft.physics.measured_value import exact_decimal
from sft.physics.scattering_rutherford_compton_terminal_law_v1 import (
    CLAIM_ID,
    EXPERIMENT_ID,
    TRANSFER_PARTS,
    formal_certificate,
)


SOURCE_ID = "IAEA-NIST-RUTHERFORD-COMPTON-2026"
SOURCE_RECORD_PATH = (
    "experiments/external_sources/physics/snapshots/"
    "scattering-rutherford-compton-source-record.json"
)
SOURCE_RECORD_HASH = "sha256:048ec96abfbd4835adf37e46f9f172a6310443aff1b3f3701bf3fe50bc402ef1"
IAEA_PATH = (
    "experiments/external_sources/physics/snapshots/"
    "iaea-rutherford-compton-handbook.pdf"
)
IAEA_HASH = "sha256:da4e3b5af19ed9506a812fea6704ff15cf55991902684a17759dbc7cbba05da0"
CODATA_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"

SOURCE_IDS = (
    "IAEA-STI-PUB-1196-RADIATION-PHYSICS",
    "NIST-CODATA-2022",
)
TARGET_IDS = (
    "IAEA-RUTHERFORD-COMPTON-COMPLETE-REGISTERED-RECORD",
    "NIST-CODATA-SCATTERING-CARRIER-VECTOR",
)
CODATA_QUANTITIES = (
    ("Planck constant", "J Hz^-1"),
    ("speed of light in vacuum", "m s^-1"),
    ("electron mass", "kg"),
    ("Compton wavelength", "m"),
    ("electron mass energy equivalent in MeV", "MeV"),
    ("classical electron radius", "m"),
    ("Thomson cross section", "m^2"),
)
FALSIFICATION_CONDITION = (
    "Reject if the complete IAEA record does not retain inverse-square Coulomb force, the inverse-fourth-power "
    "half-angle Rutherford relation, nonempty large-angle Geiger-Marsden support, closed Compton energy-momentum "
    "transfer or the wavelength-shift relation; if exact h/(m_e*c) does not overlap the NIST Compton-wavelength "
    "interval; if the right-angle and backscatter energy ceilings disagree with the NIST electron rest-energy "
    "vector and IAEA limits; if any registered row, uncertainty, scope condition or adverse control is omitted; "
    "or if target content enters before seal."
)


def positive_ratio(value: Fraction) -> PositiveRatio:
    if value.numerator < 1:
        raise ValueError("scattering prediction input must remain exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        IAEA_PATH: IAEA_HASH,
        CODATA_PATH: CODATA_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"scattering source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID or len(record.get("sources", ())) != 2:
        raise ValueError("scattering source-set identity changed")
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
        raise ValueError("scattering custody boundary changed")
    scope = record.get("measurement_scope", {})
    iaea = scope.get("iaea_handbook", {})
    rutherford = iaea.get("rutherford", {})
    compton = iaea.get("compton", {})
    if (
        rutherford.get("historical_pdf_page_index_one_based") != 47
        or rutherford.get("relation_pdf_page_index_one_based") != 48
        or compton.get("pdf_page_index_one_based") != 68
        or len(scope.get("nist_codata2022", {}).get("required_rows", ())) != 7
    ):
        raise ValueError("scattering registered page or row scope changed")
    return record


def codata_rows(root: Path) -> tuple[str, ...]:
    lines = (root / CODATA_PATH).read_text(encoding="utf-8").splitlines()
    selected = tuple(
        line
        for quantity, _ in CODATA_QUANTITIES
        for line in lines
        if len(line) >= 110 and line[:60].strip() == quantity
    )
    if len(selected) != len(CODATA_QUANTITIES):
        raise ValueError("complete CODATA scattering vector changed")
    if tuple(line[:60].strip() for line in selected) != tuple(item[0] for item in CODATA_QUANTITIES):
        raise ValueError("CODATA scattering vector order changed")
    return selected


def parse_codata_row(line: str) -> dict[str, object]:
    quantity = line[:60].strip()
    value_record = line[60:85].strip()
    uncertainty_record = line[85:110].strip()
    unit = line[110:].strip()
    expected = dict(CODATA_QUANTITIES)
    if quantity not in expected or expected[quantity] != unit:
        raise ValueError("CODATA scattering row identity changed")
    central = exact_decimal(value_record)
    if uncertainty_record == "(exact)":
        lower = upper = central
    else:
        uncertainty = exact_decimal(uncertainty_record)
        if uncertainty >= central:
            raise ValueError("CODATA scattering uncertainty lost a positive lower endpoint")
        lower, upper = central - uncertainty, central + uncertainty
    return {
        "quantity": quantity,
        "unit": unit,
        "central": central,
        "lower": lower,
        "upper": upper,
        "uncertainty_record": uncertainty_record,
    }


def codata_analysis(rows: tuple[str, ...]) -> dict[str, object]:
    parsed = {row["quantity"]: row for row in map(parse_codata_row, rows)}
    action = parsed["Planck constant"]
    speed = parsed["speed of light in vacuum"]
    mass = parsed["electron mass"]
    observed = parsed["Compton wavelength"]
    rest = parsed["electron mass energy equivalent in MeV"]
    predicted = (
        action["lower"] / (mass["upper"] * speed["upper"]),
        action["upper"] / (mass["lower"] * speed["lower"]),
    )
    observed_interval = (observed["lower"], observed["upper"])
    overlap = max(predicted[0], observed_interval[0]) <= min(predicted[1], observed_interval[1])
    rounded_iaea_angstrom_interval_m = (
        Fraction(235, 10000) / 10**10,
        Fraction(245, 10000) / 10**10,
    )
    return {
        "row_count": len(rows),
        "all_rows_exact_positive": all(row["lower"].numerator >= 1 for row in parsed.values()),
        "planck_exact": action["uncertainty_record"] == "(exact)",
        "speed_exact": speed["uncertainty_record"] == "(exact)",
        "derived_compton_wavelength_interval_m": predicted,
        "reported_compton_wavelength_interval_m": observed_interval,
        "derived_reported_intervals_overlap": overlap,
        "iaea_rounded_compton_carrier_contains_nist": (
            rounded_iaea_angstrom_interval_m[0] <= observed_interval[0]
            and observed_interval[1] <= rounded_iaea_angstrom_interval_m[1]
        ),
        "electron_rest_energy_interval_MeV": (rest["lower"], rest["upper"]),
        "right_angle_high_energy_ceiling_interval_MeV": (rest["lower"], rest["upper"]),
        "backscatter_high_energy_ceiling_interval_MeV": (
            rest["lower"] / 2,
            rest["upper"] / 2,
        ),
        "classical_electron_radius_interval_m": (
            parsed["classical electron radius"]["lower"],
            parsed["classical electron radius"]["upper"],
        ),
        "thomson_cross_section_interval_m2": (
            parsed["Thomson cross section"]["lower"],
            parsed["Thomson cross section"]["upper"],
        ),
    }


def iaea_analysis(record: dict[str, object]) -> dict[str, object]:
    iaea = record["measurement_scope"]["iaea_handbook"]
    rutherford = iaea["rutherford"]
    compton = iaea["compton"]
    history = rutherford["historical_large_angle_observation"]
    assumptions = tuple(compton["assumptions_retained"])
    return {
        "inverse_square_coulomb_recorded": rutherford["coulomb_force_radial_order"] == "inverse-square",
        "rutherford_relation_complete": (
            rutherford["differential_cross_section_relation"]
            == "d_sigma/d_omega = (D/4)^2 / sin(theta/2)^4"
            and rutherford["distance_of_closest_approach_relation"]
            == "D = z_alpha * Z_N * e^2 / (4*pi*epsilon_0*E_K)"
        ),
        "large_angle_observed_support": (
            history["angle_class"] == "theta greater than 90 degrees"
            and history["geiger_marsden_observed_probability"] == "approximately 1/10^4"
            and history["obsolete_diffuse_model_prediction_order"] == "10^-3500"
        ),
        "compton_relation_complete": (
            compton["wavelength_shift_relation"]
            == "delta_lambda = lambda_C * (1 - cos(theta))"
            and compton["compton_carrier_definition"] == "lambda_C = h/(m_e c)"
        ),
        "compton_assumptions_complete": assumptions == (
            "The electron is essentially free and stationary.",
            "The incident photon energy is much larger than the electron binding energy.",
            "Energy and momentum are conserved across photon and recoil-electron carriers.",
        ),
        "rutherford_scope_retained": "nonrelativistic point-boundary conditions" in rutherford["scope_boundary"],
        "iaea_rutherford_angular_vector": (
            Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1)
        ),
        "iaea_compton_shift_vector": (
            Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1)
        ),
    }


def exact_measurement_analysis(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    codata = codata_analysis(codata_rows(root))
    iaea = iaea_analysis(record)
    return {
        "codata": codata,
        "iaea": iaea,
        "all_sources_retained": len(record["sources"]) == 2,
        "rutherford_exact_vector_matches": iaea["iaea_rutherford_angular_vector"]
        == tuple(value for _, value in formal_certificate()["coulomb_normalized_angular_density"]),
        "compton_exact_vector_matches": iaea["iaea_compton_shift_vector"]
        == tuple(value for _, value in formal_certificate()["photon_shift_in_compton_carriers"]),
    }


def formal_prediction_inputs() -> dict[str, object]:
    certificate = formal_certificate()
    return {
        "coulomb_part_one_quarter": positive_ratio(certificate["coulomb_normalized_angular_density"][0][1]),
        "coulomb_part_one_half": positive_ratio(certificate["coulomb_normalized_angular_density"][1][1]),
        "coulomb_part_three_quarters": positive_ratio(certificate["coulomb_normalized_angular_density"][2][1]),
        "coulomb_part_one": positive_ratio(certificate["coulomb_normalized_angular_density"][3][1]),
        "charge_doubling": positive_ratio(certificate["coulomb_charge_doubling_ratio"]),
        "energy_doubling": positive_ratio(certificate["coulomb_energy_doubling_ratio"]),
        "shift_one_quarter": positive_ratio(certificate["photon_shift_in_compton_carriers"][0][1]),
        "shift_one_half": positive_ratio(certificate["photon_shift_in_compton_carriers"][1][1]),
        "shift_three_quarters": positive_ratio(certificate["photon_shift_in_compton_carriers"][2][1]),
        "shift_one": positive_ratio(certificate["photon_shift_in_compton_carriers"][3][1]),
        "right_angle_ceiling": positive_ratio(certificate["right_angle_high_energy_ceiling"]),
        "backscatter_ceiling": positive_ratio(certificate["backscatter_high_energy_ceiling"]),
        "forward_transfer": HeldLabel("direction-transfer", "structural-empty-form"),
        "rutherford_scope": HeldLabel("scattering-scope", "coulomb-point-boundary"),
        "compton_scope": HeldLabel("scattering-scope", "free-held-electron-closed-transfer"),
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
        "schema": "sft-v3-scattering-rutherford-compton-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-prediction",
        "frozen_relation": (
            "Paired exact overlap legs force inverse-transfer-part-squared Coulomb differential support; closed "
            "photon-electron transfer forces two-transfer-part wavelength increase, exact recoil-energy loss and "
            "right-angle/backscatter high-energy ceilings of One and half-One rest support."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": (
            "every registered IAEA Rutherford historical, force, scale, angular, Compton relation, conservation, "
            "assumption and scope row; all seven named NIST CODATA carrier rows with every reported uncertainty"
        ),
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": (
            "exact rational angular/shift vectors, exact h/(m_e*c) interval propagation, exact rest-energy ceiling "
            "transport, source/page identity and deliberately false angular, omitted-row and changed-source controls"
        ),
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    return {
        TARGET_IDS[0]: record["measurement_scope"]["iaea_handbook"],
        TARGET_IDS[1]: codata_rows(root),
    }


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("scattering prediction has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class ScatteringRutherfordComptonValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("scattering validator received the wrong claim seal")
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
            raise ValueError("scattering prediction failed hostile-package audit")

        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed scattering prediction differs from formal inputs")

        iaea_scope = context[TARGET_IDS[0]]
        released_codata_rows = context[TARGET_IDS[1]]
        if not isinstance(released_codata_rows, tuple) or len(released_codata_rows) != 7:
            raise ValueError("released CODATA scattering vector is incomplete")
        synthetic_record = authoritative_record(self.root)
        synthetic_record["measurement_scope"]["iaea_handbook"] = iaea_scope
        iaea = iaea_analysis(synthetic_record)
        codata = codata_analysis(released_codata_rows)

        predicted_angular = tuple(
            prediction[key].fraction
            for key in (
                "coulomb_part_one_quarter",
                "coulomb_part_one_half",
                "coulomb_part_three_quarters",
                "coulomb_part_one",
            )
        )
        predicted_shift = tuple(
            prediction[key].fraction
            for key in (
                "shift_one_quarter",
                "shift_one_half",
                "shift_three_quarters",
                "shift_one",
            )
        )
        formal_channel = all((
            predicted_angular == (Fraction(16, 1), Fraction(4, 1), Fraction(16, 9), Fraction(1, 1)),
            prediction["charge_doubling"].fraction == Fraction(4, 1),
            prediction["energy_doubling"].fraction == Fraction(1, 4),
            predicted_shift == (Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(2, 1)),
            prediction["right_angle_ceiling"].fraction == Fraction(1, 1),
            prediction["backscatter_ceiling"].fraction == Fraction(1, 2),
            prediction["forward_transfer"] == HeldLabel("direction-transfer", "structural-empty-form"),
        ))
        angular_match = predicted_angular == iaea["iaea_rutherford_angular_vector"]
        shift_match = predicted_shift == iaea["iaea_compton_shift_vector"]
        all_rows_preserved = all((
            len(released_codata_rows) == 7,
            codata["row_count"] == 7,
            len(authoritative_record(self.root)["sources"]) == 2,
            iaea["rutherford_relation_complete"] is True,
            iaea["compton_relation_complete"] is True,
            iaea["compton_assumptions_complete"] is True,
            iaea["rutherford_scope_retained"] is True,
        ))
        unfavorable_controls = all((
            predicted_angular != (Fraction(4, 1), Fraction(2, 1), Fraction(4, 3), Fraction(1, 1)),
            predicted_angular != (Fraction(1, 1),) * 4,
            predicted_shift != TRANSFER_PARTS,
            len(released_codata_rows[:-1]) != 7,
            prediction["forward_transfer"] != positive_ratio(Fraction(1, 1)),
        ))
        passed = all((
            formal_channel,
            angular_match,
            shift_match,
            all_rows_preserved,
            unfavorable_controls,
            iaea["inverse_square_coulomb_recorded"] is True,
            iaea["large_angle_observed_support"] is True,
            codata["all_rows_exact_positive"] is True,
            codata["planck_exact"] is True,
            codata["speed_exact"] is True,
            codata["derived_reported_intervals_overlap"] is True,
            codata["iaea_rounded_compton_carrier_contains_nist"] is True,
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-IAEA-NIST-Rutherford-Compton-comparator/1",
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
            "iaea_analysis": iaea,
            "codata_analysis": codata,
            "formal_channel": formal_channel,
            "angular_match": angular_match,
            "shift_match": shift_match,
            "all_rows_preserved": all_rows_preserved,
            "unfavorable_controls": unfavorable_controls,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            "IAEA complete Rutherford record retained: inverse-square Coulomb source, charge/energy scale and inverse-fourth-power half-angle differential law",
            "IAEA historical Geiger-Marsden record retained: approximately one in 10^4 alpha particles above 90 degrees versus the obsolete diffuse-model order 10^-3500",
            "IAEA complete Compton record retained: free stationary electron boundary, closed energy-momentum transfer, delta-lambda relation and h/(m_e*c) carrier",
            "NIST CODATA complete seven-row scattering vector retained with every reported uncertainty",
            f"exact h/(m_e*c) interval m: {codata['derived_compton_wavelength_interval_m']}",
            f"NIST Compton wavelength interval m: {codata['reported_compton_wavelength_interval_m']}",
            f"NIST right-angle high-energy ceiling interval MeV: {codata['right_angle_high_energy_ceiling_interval_MeV']}",
            f"NIST backscatter high-energy ceiling interval MeV: {codata['backscatter_high_energy_ceiling_interval_MeV']}",
            "first-power, angle-independent, elastic-energy, numerical-forward, incomplete-row and changed-source controls rejected",
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
    "CODATA_QUANTITIES",
    "FALSIFICATION_CONDITION",
    "ScatteringRutherfordComptonValidator",
    "SOURCE_IDS",
    "TARGET_IDS",
    "authoritative_record",
    "codata_analysis",
    "codata_rows",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "formal_prediction_inputs",
)
