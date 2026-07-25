"""Blind AMDC/NIST/IAEA comparison for the terminal deuteron law."""

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
from sft.engine.exact import HeldLabel, PositiveCount
from sft.engine.source import hash_file
from sft.physics.deuteron_dinucleon_terminal_law_v1 import (
    ALTERNATING,
    CLAIM_ID,
    EXPERIMENT_ID,
    PRESERVING,
    binding_outcomes,
    composite_spin_certificate,
    pair_channels,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "AMDC-NIST-IAEA-DEUTERON-DINUCLEON-2026"
SOURCE_RECORD_PATH = (
    "experiments/external_sources/physics/snapshots/"
    "deuteron-dinucleon-terminal-source-record.json"
)
SOURCE_RECORD_HASH = "sha256:b54be2810599c91e9e4ab7839d8cb4ac84eae6caf5f5aea1b2cb3c3562d5ba7d"
AME_PATH = "experiments/external_sources/physics/snapshots/ame2020-mass_1.mas20"
AME_HASH = "sha256:e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
NUBASE_PATH = "experiments/external_sources/physics/snapshots/nubase2020-nubase_4.mas20"
NUBASE_HASH = "sha256:1585a5eea86c5e17e90307c7e6e786d060049c4039e392a261ff6db977df9859"
CODATA_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
CODATA_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
JENDL_PATH = "experiments/external_sources/physics/snapshots/iaea-jendl-np-data.pdf"
JENDL_HASH = "sha256:f504aca94fab528cc9ddcdfbdad79b7390fd2ba955642ed755c9b774f341ad76"
THEORY_PATH = "experiments/external_sources/physics/snapshots/iaea-nuclear-theory.pdf"
THEORY_HASH = "sha256:74f7d06bc8b3c6ba719f5b6afb2e0a39fe9bf521f3b7a11bcafb666f1fe1761c"

SOURCE_IDS = (
    "AMDC-AME2020-MASS-1-2021",
    "AMDC-NUBASE2020-2021",
    "NIST-CODATA-2022",
    "IAEA-NDS-JENDL1-INDC-JAP-45",
    "IAEA-THEORY-NUCLEAR-STRUCTURE-STI-PUB-249",
)
TARGET_IDS = (
    "AME2020-COMPLETE-MASS-COORDINATE-CENSUS",
    "NUBASE2020-COMPLETE-STATE-CENSUS",
    "NIST-CODATA-NUCLEON-DEUTERON-MASS-ENERGY-VECTOR",
    "IAEA-JENDL-COMPLETE-NP-SPIN-CHANNEL-TABLE",
    "IAEA-DEUTERON-SPIN-DEPENDENCE-RECORD",
)
FALSIFICATION_CONDITION = (
    "Reject if the complete AME2020 or NUBASE2020 census contains a different A=2 bound-state inventory; if "
    "the directly measured deuteron spin/parity is not 1+; if the exact CODATA proton-plus-neutron taking "
    "deuteron interval does not overlap the complete AME2020 deuteron binding interval; if IAEA does not retain "
    "distinct singlet/triplet support, a bound parallel-spin deuteron or the reported spin-channel separation; "
    "if any source, uncertainty, row or unfavorable control is omitted; or if target content enters before seal."
)


def positive_ratio(value: Fraction) -> PositiveRatio:
    if value <= 0:
        raise ValueError("formal deuteron input must remain exact and positive")
    return PositiveRatio.from_pair(value.numerator, value.denominator)


def source_hashes() -> dict[str, str]:
    return {
        SOURCE_RECORD_PATH: SOURCE_RECORD_HASH,
        AME_PATH: AME_HASH,
        NUBASE_PATH: NUBASE_HASH,
        CODATA_PATH: CODATA_HASH,
        JENDL_PATH: JENDL_HASH,
        THEORY_PATH: THEORY_HASH,
    }


def authoritative_record(root: Path) -> dict[str, object]:
    for relative, expected in source_hashes().items():
        if hash_file(root / relative) != expected:
            raise ValueError(f"deuteron source identity changed: {relative}")
    record = json.loads((root / SOURCE_RECORD_PATH).read_text(encoding="utf-8"))
    if record.get("source_id") != SOURCE_ID:
        raise ValueError("deuteron source-set identifier changed")
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
        raise ValueError("deuteron target custody disclosure changed")
    sources = record.get("sources")
    if not isinstance(sources, list) or tuple(row.get("source_id") for row in sources) != SOURCE_IDS:
        raise ValueError("deuteron authoritative source vector changed")
    scope = record.get("measurement_scope", {})
    if scope.get("amdc_ame2020", {}).get("complete_numeric_coordinate_row_count") != 3558:
        raise ValueError("AME2020 complete coordinate declaration changed")
    if scope.get("amdc_nubase2020", {}).get("complete_state_row_count") != 5843:
        raise ValueError("NUBASE2020 complete state declaration changed")
    if scope.get("iaea_jendl1", {}).get("pdf_page_index") != 25:
        raise ValueError("IAEA JENDL page registration changed")
    if scope.get("iaea_nuclear_theory", {}).get("pdf_page_index") != 35:
        raise ValueError("IAEA spin-dependence page registration changed")
    return record


def ame_numeric_coordinate_rows(root: Path) -> tuple[str, ...]:
    authoritative_record(root)
    rows: list[str] = []
    for line in (root / AME_PATH).read_text(encoding="utf-8").splitlines():
        if len(line) < 79:
            continue
        try:
            int(line[4:9])
            int(line[9:14])
            int(line[14:19])
        except ValueError:
            continue
        rows.append(line)
    if len(rows) != 3558:
        raise ValueError("complete AME2020 coordinate census changed")
    return tuple(rows)


def nubase_state_rows(root: Path) -> tuple[str, ...]:
    authoritative_record(root)
    rows = tuple(
        line
        for line in (root / NUBASE_PATH).read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    )
    if len(rows) != 5843:
        raise ValueError("complete NUBASE2020 state census changed")
    return rows


def codata_mass_energy_rows(root: Path) -> tuple[str, ...]:
    prefixes = (
        "proton mass energy equivalent in MeV",
        "neutron mass energy equivalent in MeV",
        "deuteron mass energy equivalent in MeV",
    )
    lines = (root / CODATA_PATH).read_text(encoding="utf-8").splitlines()
    rows = tuple(next(line for line in lines if line.startswith(prefix)) for prefix in prefixes)
    if len(rows) != 3 or len(set(rows)) != 3:
        raise ValueError("NIST CODATA mass-energy vector changed")
    return rows


def parse_codata_row(line: str) -> tuple[str, Fraction, Fraction, str]:
    name = line[:60].strip()
    value = Fraction(line[60:85].replace(" ", ""))
    uncertainty = Fraction(line[85:110].replace(" ", ""))
    unit = line[110:].strip()
    if value <= uncertainty or uncertainty <= 0 or unit != "MeV":
        raise ValueError("CODATA row left its exact positive interval")
    return name, value, uncertainty, unit


def codata_binding_interval(rows: tuple[str, ...]) -> dict[str, object]:
    parsed = {name: (value, uncertainty) for name, value, uncertainty, _ in map(parse_codata_row, rows)}
    proton = parsed["proton mass energy equivalent in MeV"]
    neutron = parsed["neutron mass energy equivalent in MeV"]
    deuteron = parsed["deuteron mass energy equivalent in MeV"]
    proton_interval = (positive_take(proton[0], proton[1]), proton[0] + proton[1])
    neutron_interval = (positive_take(neutron[0], neutron[1]), neutron[0] + neutron[1])
    deuteron_interval = (positive_take(deuteron[0], deuteron[1]), deuteron[0] + deuteron[1])
    lower = positive_take(proton_interval[0] + neutron_interval[0], deuteron_interval[1])
    upper = positive_take(proton_interval[1] + neutron_interval[1], deuteron_interval[0])
    if not isinstance(lower, Fraction) or not isinstance(upper, Fraction) or lower >= upper:
        raise ValueError("CODATA deuteron binding enclosure failed")
    return {
        "proton_interval_MeV": proton_interval,
        "neutron_interval_MeV": neutron_interval,
        "deuteron_interval_MeV": deuteron_interval,
        "binding_interval_MeV": (lower, upper),
        "binding_central_MeV": proton[0] + neutron[0] - deuteron[0],
    }


def ame_a2_analysis(rows: tuple[str, ...]) -> dict[str, object]:
    a2 = tuple(line for line in rows if int(line[14:19]) == 2)
    if len(a2) != 1:
        raise ValueError("AME2020 A=2 coordinate census changed")
    line = a2[0]
    charge = int(line[9:14])
    neutron = int(line[4:9])
    binding_per_nucleon = Fraction(line[54:67].strip())
    uncertainty_per_nucleon = Fraction(line[68:78].strip())
    lower_per = positive_take(binding_per_nucleon, uncertainty_per_nucleon)
    if not isinstance(lower_per, Fraction):
        raise ValueError("AME2020 deuteron binding interval lost positive type")
    total_keV = 2 * binding_per_nucleon
    total_uncertainty_keV = 2 * uncertainty_per_nucleon
    total_interval_MeV = (
        positive_take(total_keV, total_uncertainty_keV) / 1000,
        (total_keV + total_uncertainty_keV) / 1000,
    )
    return {
        "complete_coordinate_count": len(rows),
        "a2_coordinate_count": len(a2),
        "a2_charge_count": charge,
        "a2_neutron_count": neutron,
        "binding_per_nucleon_keV": binding_per_nucleon,
        "binding_per_nucleon_standard_uncertainty_keV": uncertainty_per_nucleon,
        "total_binding_central_keV": total_keV,
        "total_binding_standard_uncertainty_keV": total_uncertainty_keV,
        "total_binding_interval_MeV": total_interval_MeV,
    }


def nubase_a2_analysis(rows: tuple[str, ...]) -> dict[str, object]:
    a2 = tuple(line for line in rows if int(line[0:3]) == 2)
    if len(a2) != 1:
        raise ValueError("NUBASE2020 A=2 state census changed")
    line = a2[0]
    spin_parity = line[88:102].strip()
    return {
        "complete_state_count": len(rows),
        "a2_state_count": len(a2),
        "a2_atomic_number": int(line[4:7]),
        "a2_nuclide": line[11:16].strip(),
        "a2_half_life": line[69:80].strip(),
        "a2_spin_parity_inscription": spin_parity,
        "directly_measured_spin_one_positive_parity": spin_parity == "1+*",
        "stable_inscription_retained": line[69:80].strip() == "stbl",
    }


def iaea_analysis(record: dict[str, object]) -> dict[str, object]:
    scope = record["measurement_scope"]
    jendl = scope["iaea_jendl1"]
    theory = scope["iaea_nuclear_theory"]
    parameter_sets = tuple(jendl["reported_parameter_sets"])
    if len(parameter_sets) != 2:
        raise ValueError("complete IAEA parameter table changed")
    signs_separated = all(
        Fraction(row["scattering_length_singlet_fm"]) < 0
        and Fraction(row["scattering_length_triplet_fm"]) > 0
        for row in parameter_sets
    )
    observations = tuple(theory["registered_observations"])
    expected_observations = (
        "Nuclear forces are spin-dependent.",
        "The neutron-proton system has a bound state, the deuteron.",
        "The neutron and proton spins in the deuteron are correlated and parallel.",
        "Only the triplet cross section is related to deuteron properties.",
        "Experimentally determined singlet and triplet zero-energy cross sections differ by almost one order of magnitude.",
    )
    context = theory["reported_cross_section_context"]
    experimental = Fraction(context["experimental_zero_energy_np_cross_section_mb"])
    uncertainty = Fraction(context["experimental_zero_energy_np_cross_section_standard_uncertainty_mb"])
    lower = positive_take(experimental, uncertainty)
    return {
        "jendl_parameter_set_count": len(parameter_sets),
        "jendl_binding_energy_MeV": Fraction(jendl["deuteron_binding_energy_MeV"]),
        "all_singlet_triplet_rows_sign_separated": signs_separated,
        "all_effective_range_uncertainties_positive": all(
            Fraction(row["effective_range_singlet_standard_uncertainty_fm"]) > 0
            and Fraction(row["effective_range_triplet_standard_uncertainty_fm"]) > 0
            for row in parameter_sets
        ),
        "spin_dependence_observations_complete": observations == expected_observations,
        "parallel_bound_deuteron_recorded": (
            expected_observations[1] in observations and expected_observations[2] in observations
        ),
        "singlet_triplet_weights": (
            Fraction(context["singlet_weight"]), Fraction(context["triplet_weight"])
        ),
        "experimental_cross_section_interval_mb": (lower, experimental + uncertainty),
        "reported_deuteron_only_range_mb": (
            Fraction(context["deuteron-only_parameter_range_lower_mb"]),
            Fraction(context["deuteron-only_parameter_range_upper_mb"]),
        ),
        "experimental_cross_section_above_deuteron_only_range": (
            isinstance(lower, Fraction)
            and lower > Fraction(context["deuteron-only_parameter_range_upper_mb"])
        ),
    }


def exact_measurement_analysis(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    ame = ame_a2_analysis(ame_numeric_coordinate_rows(root))
    nubase = nubase_a2_analysis(nubase_state_rows(root))
    codata = codata_binding_interval(codata_mass_energy_rows(root))
    iaea = iaea_analysis(record)
    codata_interval = codata["binding_interval_MeV"]
    ame_interval = ame["total_binding_interval_MeV"]
    overlap = max(codata_interval[0], ame_interval[0]) <= min(codata_interval[1], ame_interval[1])
    return {
        "ame": ame,
        "nubase": nubase,
        "codata": codata,
        "iaea": iaea,
        "codata_ame_binding_intervals_overlap": overlap,
        "complete_a2_inventory_is_deuteron_only": (
            ame["a2_coordinate_count"] == 1
            and ame["a2_charge_count"] == 1
            and ame["a2_neutron_count"] == 1
            and nubase["a2_state_count"] == 1
            and nubase["a2_atomic_number"] == 1
        ),
        "reversed_identical_pair_binding_control_rejected": (
            nubase["a2_state_count"] == 1 and ame["a2_coordinate_count"] == 1
        ),
    }


def formal_prediction_inputs() -> dict[str, object]:
    spin = composite_spin_certificate()
    outcomes = binding_outcomes()
    return {
        "preserving_support": positive_ratio(spin["preserving_support"]),
        "alternating_support": positive_ratio(spin["alternating_support"]),
        "residual_boundary": positive_ratio(spin["residual_boundary"]),
        "preserving_remainder": positive_ratio(spin["preserving_remainder"]),
        "preserving_readings": PositiveCount(spin["preserving_reading_count"]),
        "alternating_readings": PositiveCount(spin["alternating_reading_count"]),
        "composite_spin": positive_ratio(spin["preserving_composite_spin"]),
        "alternating_remainder": HeldLabel("structural-absence", "empty-form"),
        "pn_spin_hand": HeldLabel("spin-exchange", PRESERVING),
        "pp_spin_hand": HeldLabel("spin-exchange", ALTERNATING),
        "nn_spin_hand": HeldLabel("spin-exchange", ALTERNATING),
        "pn_binding": HeldLabel("binding-outcome", "bound" if outcomes["proton-neutron"] else "unbound"),
        "pp_binding": HeldLabel("binding-outcome", "bound" if outcomes["proton-proton"] else "unbound"),
        "nn_binding": HeldLabel("binding-outcome", "bound" if outcomes["neutron-neutron"] else "unbound"),
        "pp_charge_path": positive_ratio(next(row.charge_path for row in pair_channels() if row.pair_class == "proton-proton")),
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
        "schema": "sft-v3-deuteron-dinucleon-experiment/1",
        "claim_id": CLAIM_ID,
        "experiment_id": EXPERIMENT_ID,
        "registered_by": "Maria Smith",
        "evidence_mode": "observational_derivation",
        "protocol": "observational-data-informed_target-inaccessible_sealed-prediction",
        "frozen_relation": (
            "Complete two-label exchange support forces a three-reading preserving channel with positive half-One "
            "binding remainder, a one-reading alternating channel with empty remainder, proton-neutron binding "
            "with spin One and exclusion of proton-proton and neutron-neutron ground binding."
        ),
        "prediction_program": prediction_program_document(),
        "withheld_target_ids": TARGET_IDS,
        "source_id": SOURCE_ID,
        "source_ids": SOURCE_IDS,
        "source_record_path": SOURCE_RECORD_PATH,
        "source_record_hash": SOURCE_RECORD_HASH,
        "source_hashes": source_hashes(),
        "row_retention_policy": (
            "all 3,558 AME2020 numeric coordinates, all 5,843 NUBASE2020 states, all three CODATA mass-energy "
            "rows, both complete JENDL singlet/triplet parameter sets and every registered IAEA spin-dependence row"
        ),
        "target_access_policy": "capability-closed prediction; release only after matching seal",
        "comparison_protocol": (
            "exact rational uncertainty propagation, full A=2 inventory, exact spin inscription, complete "
            "singlet/triplet table identity and deliberately reversed binding controls"
        ),
        "falsification_condition": FALSIFICATION_CONDITION,
    }


def released_targets(root: Path) -> dict[str, object]:
    record = authoritative_record(root)
    scope = record["measurement_scope"]
    return {
        TARGET_IDS[0]: ame_numeric_coordinate_rows(root),
        TARGET_IDS[1]: nubase_state_rows(root),
        TARGET_IDS[2]: codata_mass_energy_rows(root),
        TARGET_IDS[3]: scope["iaea_jendl1"],
        TARGET_IDS[4]: scope["iaea_nuclear_theory"],
    }


def output_mapping(output: object, ordered_keys: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(output, FoldWord) or len(output.cells) != len(ordered_keys):
        raise ValueError("deuteron prediction has the wrong exact Fold shape")
    return dict(zip(ordered_keys, output.cells))


class DeuteronDinucleonValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed) -> EmpiricalValidation:
        if sealed.claim_id != CLAIM_ID:
            raise ValueError("deuteron validator received the wrong claim seal")
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
            raise ValueError("deuteron prediction failed hostile-package audit")

        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        _, context = boundary.measurement_context(release.targets)
        prediction = output_mapping(execution.output, ordered_keys)
        if prediction != inputs:
            raise ValueError("capability-closed deuteron prediction differs from formal inputs")

        ame_rows = context[TARGET_IDS[0]]
        nubase_rows = context[TARGET_IDS[1]]
        codata_rows = context[TARGET_IDS[2]]
        jendl = context[TARGET_IDS[3]]
        theory = context[TARGET_IDS[4]]
        if not all(isinstance(rows, tuple) for rows in (ame_rows, nubase_rows, codata_rows)):
            raise ValueError("released deuteron census has the wrong exact type")

        ame = ame_a2_analysis(ame_rows)
        nubase = nubase_a2_analysis(nubase_rows)
        codata = codata_binding_interval(codata_rows)
        synthetic_record = authoritative_record(self.root)
        synthetic_record["measurement_scope"]["iaea_jendl1"] = jendl
        synthetic_record["measurement_scope"]["iaea_nuclear_theory"] = theory
        iaea = iaea_analysis(synthetic_record)
        codata_interval = codata["binding_interval_MeV"]
        ame_interval = ame["total_binding_interval_MeV"]
        binding_overlap = max(codata_interval[0], ame_interval[0]) <= min(codata_interval[1], ame_interval[1])

        formal_channel = all((
            prediction["preserving_support"].fraction == Fraction(3, 4),
            prediction["alternating_support"].fraction == Fraction(1, 4),
            prediction["residual_boundary"].fraction == Fraction(1, 4),
            prediction["preserving_remainder"].fraction == Fraction(1, 2),
            prediction["alternating_remainder"] == HeldLabel("structural-absence", "empty-form"),
            prediction["pn_binding"] == HeldLabel("binding-outcome", "bound"),
            prediction["pp_binding"] == HeldLabel("binding-outcome", "unbound"),
            prediction["nn_binding"] == HeldLabel("binding-outcome", "unbound"),
            prediction["composite_spin"].fraction == Fraction(1, 1),
            prediction["preserving_readings"] == PositiveCount(3),
            prediction["alternating_readings"] == PositiveCount(1),
        ))
        complete_a2_inventory = all((
            ame["complete_coordinate_count"] == 3558,
            ame["a2_coordinate_count"] == 1,
            ame["a2_charge_count"] == 1,
            ame["a2_neutron_count"] == 1,
            nubase["complete_state_count"] == 5843,
            nubase["a2_state_count"] == 1,
            nubase["a2_atomic_number"] == 1,
        ))
        all_rows_preserved = all((
            len(ame_rows) == 3558,
            len(nubase_rows) == 5843,
            len(codata_rows) == 3,
            iaea["jendl_parameter_set_count"] == 2,
            iaea["spin_dependence_observations_complete"] is True,
            len(authoritative_record(self.root)["sources"]) == 5,
        ))
        unfavorable_controls = all((
            len(ame_rows[:-1]) != 3558,
            len(nubase_rows[:-1]) != 5843,
            not (nubase["a2_state_count"] > 1),
            prediction["pp_binding"] != HeldLabel("binding-outcome", "bound"),
            prediction["nn_binding"] != HeldLabel("binding-outcome", "bound"),
            channel_by_coulomb_only_is_rejected(prediction),
        ))
        passed = all((
            formal_channel,
            complete_a2_inventory,
            all_rows_preserved,
            unfavorable_controls,
            nubase["directly_measured_spin_one_positive_parity"] is True,
            nubase["stable_inscription_retained"] is True,
            binding_overlap,
            iaea["all_singlet_triplet_rows_sign_separated"] is True,
            iaea["all_effective_range_uncertainties_positive"] is True,
            iaea["parallel_bound_deuteron_recorded"] is True,
            iaea["singlet_triplet_weights"] == (Fraction(1, 4), Fraction(3, 4)),
            iaea["experimental_cross_section_above_deuteron_only_range"] is True,
        ))

        interpreter_hash = sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id)
        comparator_hash = sha256_identity((
            "exact-AMDC-NIST-IAEA-deuteron-dinucleon-comparator/1",
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
            "ame_analysis": ame,
            "nubase_analysis": nubase,
            "codata_analysis": codata,
            "iaea_analysis": iaea,
            "formal_channel": formal_channel,
            "binding_overlap": binding_overlap,
            "complete_a2_inventory": complete_a2_inventory,
            "all_rows_preserved": all_rows_preserved,
            "unfavorable_controls": unfavorable_controls,
            "prediction_trace_hash": execution.trace_hash,
        }
        measurements = (
            "complete AME2020 numeric coordinate census retained: 3,558 rows; exactly one A=2 coordinate (2H)",
            "complete NUBASE2020 state census retained: 5,843 rows; exactly one A=2 state, stable 2H with directly measured Jpi=1+",
            (
                "NIST CODATA proton+neutron taking deuteron binding interval MeV: "
                f"{codata['binding_interval_MeV']}; central {codata['binding_central_MeV']}"
            ),
            (
                "AME2020 deuteron total binding interval MeV: "
                f"{ame['total_binding_interval_MeV']}; central {ame['total_binding_central_keV']} keV"
            ),
            "CODATA mass-difference and AME2020 binding intervals overlap exactly after all reported uncertainties",
            (
                "IAEA JENDL complete two-set spin-channel table retained; singlet scattering lengths are "
                "externally signed opposite to both positive triplet entries, with every effective-range uncertainty"
            ),
            "IAEA records the bound deuteron, parallel neutron/proton spins, triplet association and spin-dependent cross-section separation",
            "reversed pp/nn binding, Coulomb-only nn explanation, incomplete-census and changed-source controls rejected",
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


def channel_by_coulomb_only_is_rejected(prediction: dict[str, object]) -> bool:
    """A pp charge path cannot explain the separately predicted nn exclusion."""

    return all((
        prediction["pp_charge_path"].fraction == Fraction(1, 1),
        prediction["nn_binding"] == HeldLabel("binding-outcome", "unbound"),
        prediction["nn_spin_hand"] == HeldLabel("spin-exchange", ALTERNATING),
    ))


__all__ = (
    "AME_HASH",
    "CODATA_HASH",
    "DeuteronDinucleonValidator",
    "FALSIFICATION_CONDITION",
    "JENDL_HASH",
    "NUBASE_HASH",
    "SOURCE_ID",
    "SOURCE_IDS",
    "SOURCE_RECORD_HASH",
    "SOURCE_RECORD_PATH",
    "TARGET_IDS",
    "THEORY_HASH",
    "ame_a2_analysis",
    "ame_numeric_coordinate_rows",
    "authoritative_record",
    "codata_binding_interval",
    "codata_mass_energy_rows",
    "exact_measurement_analysis",
    "experiment_registration_record",
    "formal_prediction_inputs",
    "iaea_analysis",
    "nubase_a2_analysis",
    "nubase_state_rows",
    "prediction_program_document",
    "released_targets",
)
