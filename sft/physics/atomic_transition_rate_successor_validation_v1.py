"""Post-seal NIST comparison for terminal atomic transition rates."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.atomic_transition_rate_successor_laws_v1 import (
    ATOMIC_TRANSITION_RATE_TERMINAL_ID,
    electric_multipole_exponent,
    exact_lifetime,
)
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "NIST-ATOMIC-TRANSITION-RATE-LIFETIME-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/atomic-transition-rate-successor-source-record.json"
SOURCE_HASH = "sha256:77bb5da60432c1dd9d5979e952254ace888073af666605ecce7c8f5fda4eb5a4"
NIST_ATSPEC_HASH = "sha256:35f4c76e7ed640958c6ef184cb731fc91c540608bda87bab7ab63130abb7f7a2"
MEASURED_LABEL = (
    "sealed-E1-gap-cube-E2-gap-five-and-reciprocal-lifetime-match-NIST-equations"
    "__hydrogenic-rate-four-cross-locks__complete-metastable-lifetime-vector-passed"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("atomic transition-rate source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
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
        "adverse_universal_forbidden_ordering_retained": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("atomic transition-rate custody disclosure changed")
    sources = payload.get("sources", {})
    if set(sources) != {"nist_atomic_spectroscopy", "nist_argon_metastable", "nist_aluminium_clock"}:
        raise ValueError("atomic transition-rate source set changed")
    atspec = sources["nist_atomic_spectroscopy"]
    component = root / atspec["snapshot_path"]
    if atspec["snapshot_hash"] != NIST_ATSPEC_HASH or hash_file(component) != NIST_ATSPEC_HASH:
        raise ValueError("NIST atomic-spectroscopy snapshot changed")
    if payload.get("comparison_policy", {}).get("adverse_boundary") != (
        "NIST M1 and E1 relations both have cubic gap exponent, so channel naming alone cannot lawfully force every forbidden transition below every E1 transition. Distinct line strength and weight carriers remain explicit."
    ):
        raise ValueError("atomic transition-rate adverse boundary changed")
    return payload


def measured_interval(root: Path, source_key: str) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"][source_key]["reported_record"]
    centre = Fraction(row["lifetime_seconds"])
    spread = Fraction(row["standard_uncertainty_seconds"])
    return positive_take(centre, spread), centre + spread


def allowed_example_lifetime(root: Path) -> Fraction:
    row = authoritative_record(root)["sources"]["nist_atomic_spectroscopy"]["reported_record"]["allowed_helium_example"]
    return exact_lifetime((Fraction(1, 1) * int(row["transition_probability_per_second"]),))


def transition_rate_classification(root: Path) -> str:
    record = authoritative_record(root)
    row = record["sources"]["nist_atomic_spectroscopy"]["reported_record"]
    if row["E1_gap_exponent"] != electric_multipole_exponent(1):
        raise ValueError("sealed E1 exponent differs from NIST")
    if row["E2_gap_exponent"] != electric_multipole_exponent(2):
        raise ValueError("sealed E2 exponent differs from NIST")
    if row["M1_gap_exponent"] != electric_multipole_exponent(1):
        raise ValueError("NIST M1 adverse exponent boundary changed")
    if row["lifetime_relation"] != "tau_k=(sum_i A_ki)^-1":
        raise ValueError("NIST lifetime reciprocal relation changed")
    gap_power = row["hydrogenic_gap_scaling_exponent"]
    if gap_power * electric_multipole_exponent(1) != 6:
        raise ValueError("hydrogenic gap-cube composition failed")
    if row["hydrogenic_strength_scaling"] != "inverse-square" or row["hydrogenic_rate_scaling_exponent"] != 4:
        raise ValueError("hydrogenic rate exponent cross-lock failed")
    allowed = allowed_example_lifetime(root)
    for source_key in ("nist_argon_metastable", "nist_aluminium_clock"):
        if measured_interval(root, source_key)[0] <= allowed:
            raise ValueError("registered metastable lifetime does not exceed the allowed example")
    return MEASURED_LABEL


ATOMIC_TRANSITION_RATE_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=ATOMIC_TRANSITION_RATE_TERMINAL_ID,
    title="Terminal transition-rate and lifetime post-seal NIST comparison",
    statement=(
        "Observation informed the explicit transition-rate successor.  NIST equations, the complete allowed "
        "helium example and both metastable lifetime intervals remain capability-closed until the exact relation "
        "seals.  Post-seal comparison exactly matches the E1 cubic, E2 fifth-power and reciprocal-lifetime laws, "
        "cross-locks hydrogenic rate exponent four, and preserves M1's cubic adverse boundary."
    ),
    dependencies=(
        ATOMIC_TRANSITION_RATE_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal transition-rate, exponent, lifetime, source, adverse-boundary and row-retention product.",
    grammar_boundary="The full registered NIST E1/E2/M1 exponent and lifetime equations, hydrogenic scaling rows, allowed helium record, Ar9+ and Al27+ metastable intervals, source identities and adverse M1 boundary.",
    dimensions=empirical_dimensions(
        "sealed-rate-lifetime-multipole-law-versus-complete-NIST-vector",
        "Every formal exponent, NIST equation, numerical example, uncertainty and adverse same-exponent M1 row remains visible.",
    ),
    exact_result=(
        "The sealed E1 exponent three, E2 exponent five and reciprocal total-rate lifetime equal the NIST laws; "
        "gap-squared hydrogenic scaling cubed with inverse-square strength gives NIST rate exponent four; both "
        "complete metastable lower endpoints exceed the allowed-example implied lifetime."
    ),
    induction_base="The source record retains electric rank One, its complete allowed example and the sealed cubic rate before release.",
    induction_step="Each later source revision appends a new comparison receipt and cannot rewrite the relation, component hash, uncertainty, adverse boundary or predecessor evidence.",
    exclusions=(
        "no target readable by the executable law",
        "no measured rate, strength or lifetime selecting the survivor",
        "no universal forbidden-rate ordering that erases M1's cubic exponent",
        "no floating-point interval decision",
        "no omitted equation, uncertainty, numerical example or adverse row",
    ),
    operational_witnesses=((
        "target-free-exponents",
        "The formal electric exponents exist exactly before source release.",
        electric_multipole_exponent(1) == 3 and electric_multipole_exponent(2) == 5,
    ),),
    experiment_id="SFT-EXP-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("NIST-ATSPEC-RATE-LIFETIME-EQUATIONS", SOURCE_ID, "NIST Atomic Spectroscopy equations 19, 21, 27 and forbidden-transition table", MEASURED_LABEL),
        ExternalTargetRow("NIST-AR9-M1-METASTABLE-LIFETIME", SOURCE_ID, "NIST 2018 Ar9+ complete 9.39 +/- 0.09 ms row", MEASURED_LABEL),
        ExternalTargetRow("NIST-AL27-CLOCK-METASTABLE-LIFETIME", SOURCE_ID, "NIST 2007 Al+ complete 20.6 +/- 1.4 s row", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if a sealed exponent or lifetime relation differs, hydrogenic exponent four does not "
        "cross-lock, either complete metastable interval fails, M1's adverse boundary is erased, a source hash "
        "or uncertainty changes, target access precedes sealing, or observational provenance is concealed."
    ),
)


class AtomicTransitionRateValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, ATOMIC_TRANSITION_RATE_EMPIRICAL_SPEC).validate(sealed)
        if transition_rate_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("atomic transition-rate authoritative classification changed")
        return validation


ATOMIC_TRANSITION_RATE_EMPIRICAL_SPEC.validate()


__all__ = (
    "ATOMIC_TRANSITION_RATE_EMPIRICAL_SPEC",
    "AtomicTransitionRateValidator",
    "MEASURED_LABEL",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "allowed_example_lifetime",
    "authoritative_record",
    "measured_interval",
    "transition_rate_classification",
)
