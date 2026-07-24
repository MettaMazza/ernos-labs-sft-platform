"""Post-seal PDG/NIST comparison for residual nuclear interaction and range."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator, EmpiricalPhysicsSpec, ExternalTargetRow, empirical_dimensions
from sft.physics.nuclear_residual_force_successor_laws_v1 import (
    NUCLEAR_RESIDUAL_FORCE_TERMINAL_ID,
    inverse_mass_order,
    mediator_range,
    neutral_composite_exchange,
    residual_boundary_support,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "PDG-NIST-NUCLEAR-RESIDUAL-RANGE-2025-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/nuclear-residual-force-successor-source-record.json"
SOURCE_HASH = "sha256:898f2c17eaadb3419aa5ee9be4519b21eeeaf5523045111bb0a04017d18a11d1"
MEASURED_LABEL = (
    "sealed-neutral-leading-closure-and-quarter-second-order-residual"
    "__positive-NIST-neutron-hydrogen-and-deuterium-scattering-support-nonempty-external-interaction"
    "__disjoint-channel-cross-sections-reject-universal-quarter-strength-identification"
    "__complete-PDG-pion-rho-omega-mass-order-forces-pion-longest-reciprocal-range"
    "__NIST-context-retains-pion-long-range-component-and-range-scale-not-hard-cutoff"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("nuclear residual-force source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "classification": "observational_derivation",
        "development_targets_already_known": True,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "interaction_strength_channel_dependence_retained": True,
        "one_quarter_not_conflated_with_measured_cross_section": True,
        "range_is_scale_not_hard_cutoff": True,
    }
    custody = payload.get("custody", {})
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("nuclear residual-force custody disclosure changed")
    if set(payload.get("sources", {})) != {
        "pdg_mediator_masses",
        "nist_hbar_c",
        "nist_neutron_scattering",
        "nist_pion_exchange_context",
    }:
        raise ValueError("nuclear residual-force source set changed")
    return payload


def exact_interval(centre: str, uncertainty: str) -> tuple[Fraction, Fraction]:
    c, u = Fraction(centre), Fraction(uncertainty)
    lower = positive_take(c, u)
    if not isinstance(lower, Fraction):
        raise ValueError("reported interval exhausted its positive centre")
    return lower, c + u


def mediator_mass_intervals(root: Path) -> dict[str, tuple[Fraction, Fraction]]:
    rows = authoritative_record(root)["sources"]["pdg_mediator_masses"]["reported_record"]
    return {row["mediator"]: exact_interval(row["mass_MeV"], row["standard_uncertainty_MeV"]) for row in rows}


def mediator_range_intervals_fm(root: Path) -> dict[str, tuple[Fraction, Fraction]]:
    sources = authoritative_record(root)["sources"]
    conversion = sources["nist_hbar_c"]["reported_record"]
    hbar_lower = Fraction(conversion["displayed_value_MeV_fm"])
    hbar_upper = Fraction(conversion["displayed_resolution_upper_MeV_fm"])
    result = {}
    for name, mass in mediator_mass_intervals(root).items():
        result[name] = hbar_lower / mass[1], hbar_upper / mass[0]
    return result


def scattering_intervals_barn(root: Path) -> dict[str, tuple[Fraction, Fraction]]:
    row = authoritative_record(root)["sources"]["nist_neutron_scattering"]["reported_record"]
    return {
        "natural-hydrogen": exact_interval(row["natural_hydrogen_total_scattering_cross_section_barn"], row["natural_hydrogen_cross_section_uncertainty_barn"]),
        "deuterium": exact_interval(row["deuterium_total_scattering_cross_section_barn"], row["deuterium_cross_section_uncertainty_barn"]),
    }


def measurement_analysis(root: Path) -> dict[str, object]:
    masses = mediator_mass_intervals(root)
    ranges = mediator_range_intervals_fm(root)
    scattering = scattering_intervals_barn(root)
    return {
        "mediator_mass_intervals_MeV": {key: [str(value) for value in row] for key, row in masses.items()},
        "mediator_reciprocal_range_enclosures_fm": {key: [str(value) for value in row] for key, row in ranges.items()},
        "scattering_cross_section_intervals_barn": {key: [str(value) for value in row] for key, row in scattering.items()},
        "pion_range_envelope_fm": [str(ranges["charged-pion"][0]), str(ranges["neutral-pion"][1])],
        "vector_range_envelope_fm": [str(ranges["omega"][0]), str(ranges["rho-neutral"][1])],
        "all_scattering_intervals_positive": all(row[0] > 0 for row in scattering.values()),
        "channel_strength_intervals_disjoint": scattering["natural-hydrogen"][0] > scattering["deuterium"][1],
        "one_quarter_is_structural_order_not_cross_section": True,
        "range_is_finite_scale_not_numerical_zero_cutoff": True,
    }


def nuclear_residual_force_classification(root: Path) -> str:
    sources = authoritative_record(root)["sources"]
    if residual_boundary_support() != Fraction(1, 4) or neutral_composite_exchange()["leading_external_label"] != ():
        raise ValueError("sealed residual structure changed")

    masses = mediator_mass_intervals(root)
    order = ("neutral-pion", "charged-pion", "rho-neutral", "omega")
    if any(masses[successor][0] <= masses[previous][1] for previous, successor in zip(order, order[1:])):
        raise ValueError("complete PDG mediator mass intervals no longer order")
    if any(not inverse_mass_order(masses[previous][1], masses[successor][0]) for previous, successor in zip(order, order[1:])):
        raise ValueError("sealed reciprocal range ordering failed")
    ranges = mediator_range_intervals_fm(root)
    if ranges["charged-pion"][0] <= ranges["rho-neutral"][1]:
        raise ValueError("complete pion/vector range envelopes overlap")
    if any(mediator_range(row[0]) <= mediator_range(row[1]) for row in masses.values()):
        raise ValueError("mass uncertainty did not reverse under reciprocal range")

    scattering = scattering_intervals_barn(root)
    if any(row[0] <= 0 for row in scattering.values()):
        raise ValueError("registered NIST scattering support ceased to be positive")
    if scattering["natural-hydrogen"][0] <= scattering["deuterium"][1]:
        raise ValueError("NIST channel dependence was lost")
    scattering_record = sources["nist_neutron_scattering"]["reported_record"]
    if scattering_record["evaluation_speed_m_per_s"] != "2200" or "channel-dependent" not in scattering_record["comparison_status"]:
        raise ValueError("NIST scattering boundary changed")

    context = sources["nist_pion_exchange_context"]["reported_record"]
    if context["context_statement"] != "pion exchange mediates the only long-range component of the interaction":
        raise ValueError("NIST pion context changed")
    conversion = sources["nist_hbar_c"]["reported_record"]
    if conversion["uncertainty_status"] != "exact defining conversion; NIST table displays an ellipsis after the recorded digits":
        raise ValueError("NIST conversion disclosure changed")
    return MEASURED_LABEL


NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=NUCLEAR_RESIDUAL_FORCE_TERMINAL_ID,
    title="Terminal residual nuclear interaction post-seal PDG/NIST comparison",
    statement=(
        "Observation informed the explicit successor. PDG mediator masses, the NIST defining conversion, NIST "
        "neutron scattering and NIST pion-exchange context remain capability-closed until the neutral-boundary, "
        "quarter-order and reciprocal-range laws seal. Every uncertainty and the unfavorable universal-strength "
        "control is retained after release."
    ),
    dependencies=(
        NUCLEAR_RESIDUAL_FORCE_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal residual, mass, reciprocal range, scattering, channel, source, custody and row-retention product.",
    grammar_boundary="Every registered PDG pion/rho/omega mass interval, the complete NIST displayed hbar-c resolution enclosure, both NIST hydrogen/deuterium scattering intervals, their evaluation speed and the NIST pion-exchange context statement.",
    dimensions=empirical_dimensions(
        "sealed-residual-order-and-reciprocal-range-versus-complete-PDG-NIST-vector",
        "Every mediator mass/range, scattering interval, channel-dependence and unfavorable universal-strength row remains visible.",
    ),
    exact_result=(
        "Positive NIST hydrogen and deuterium scattering support a nonempty residual interaction outside neutral "
        "nucleon boundaries, while their disjoint intervals reject identifying structural quarter-One with one "
        "universal measured strength. Complete PDG mass intervals force pion reciprocal ranges above rho/omega "
        "ranges; the post-seal NIST conversion places the pion envelope at a finite femtometre scale."
    ),
    induction_base="One sealed neutral pair supplies exact quarter-order support; one registered positive mass interval supplies one reciprocal range enclosure after release.",
    induction_step="Each additional mediator interval reverses order exactly under reciprocation; each scattering channel appends its full interval without changing the sealed structural order.",
    exclusions=(
        "no target readable by the executable law",
        "no measured mass, cross section, force range or conventional exchange model selecting the survivor",
        "no identification of one-quarter with a universal measured cross section or coupling",
        "no floating-point interval decision",
        "no hidden uncertainty, channel difference, conversion resolution or context scope",
        "no fitted exponential, hard numerical-zero cutoff or selected mediator subset",
    ),
    operational_witnesses=((
        "target-free-residual-and-range-order",
        "Quarter-order neutral exchange and exact reciprocal ordering exist before source release.",
        residual_boundary_support() == Fraction(1, 4)
        and inverse_mass_order(Fraction(3, 7), Fraction(5, 7)),
    ),),
    experiment_id="SFT-EXP-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-MEDIATOR-MASS-RANGE", SOURCE_ID, "PDG 2025 pion, rho and omega complete mass intervals", MEASURED_LABEL),
        ExternalTargetRow("NIST-HBAR-C-RANGE-TRANSLATION", SOURCE_ID, "NIST CODATA 2022 displayed exact hbar-c conversion", MEASURED_LABEL),
        ExternalTargetRow("NIST-NEUTRON-SCATTERING", SOURCE_ID, "NIST NCNR hydrogen and deuterium scattering intervals at 2200 m/s", MEASURED_LABEL),
        ExternalTargetRow("NIST-PION-LONG-RANGE-CONTEXT", SOURCE_ID, "NIST Journal of Research pion-exchange long-range context", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if neutral leading closure or quarter order changes, reciprocal ordering fails, the "
        "complete pion and vector ranges overlap, either scattering interval ceases to be positive, channel "
        "dependence is erased, one-quarter is relabelled as a measured strength, or target access precedes sealing."
    ),
)


class NuclearResidualForceValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC).validate(sealed)
        if nuclear_residual_force_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("nuclear residual-force authoritative classification changed")
        return validation


NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC.validate()


__all__ = (
    "MEASURED_LABEL",
    "NUCLEAR_RESIDUAL_FORCE_EMPIRICAL_SPEC",
    "NuclearResidualForceValidator",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "mediator_mass_intervals",
    "mediator_range_intervals_fm",
    "measurement_analysis",
    "nuclear_residual_force_classification",
    "scattering_intervals_barn",
)
