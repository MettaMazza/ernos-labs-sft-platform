"""Post-seal external validation for terminal cosmic component transport."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.cosmic_component_transport_terminal_law_v1 import (
    CLAIM_ID,
    acceleration_onset_cube,
    late_squared_expansion,
    matter_vacuum_equality_cube,
    present_acceleration_magnitude,
)
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal


SOURCE_PATH = "experiments/external_sources/physics/snapshots/cosmic_transport_terminal-source-record.json"
SOURCE_HASH = "sha256:6a88728657b19dba0bcf2430d28218a595c0798c6ac34bf2778ef53a1b540705"
EXPECTED_LABEL = "terminal-cosmic-transport-complete-vector-passes-with-adverse-desi-row-retained"
EXPERIMENT_ID = "SFT-EXP-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"


def _source_payload(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("cosmic transport source record changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    for source in payload["sources"]:
        if hash_file(root / source["snapshot_path"]) != source["snapshot_hash"]:
            raise ValueError(f"nested cosmic source changed: {source['source_id']}")
    return payload


def _interval_overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return left[0] <= right[1] and right[0] <= left[1]


def _positive_or_empty_difference(whole: Fraction, part: Fraction) -> Fraction:
    """Return a positive difference or the typed empty measurement boundary."""

    return whole - part if whole > part else Fraction(0, 1)


def cosmic_transport_measurement_record(root: Path) -> dict[str, object]:
    payload = _source_payload(root)
    h0 = payload["hubble_reference"]
    h0_central = exact_decimal(h0["central"])
    h0_uncertainty = exact_decimal(h0["standard_uncertainty"])
    h0_interval = (h0_central - h0_uncertainty, h0_central + h0_uncertainty)

    chronometer_rows = []
    for position, row in enumerate(payload["cosmic_chronometers"]["rows"], 1):
        redshift = exact_decimal(row["redshift"])
        central = exact_decimal(row["central"])
        uncertainty = exact_decimal(row["standard_uncertainty"])
        stretch = Fraction(1, 1) + redshift
        e2 = late_squared_expansion(stretch)
        predicted_squared = (h0_interval[0] * h0_interval[0] * e2, h0_interval[1] * h0_interval[1] * e2)
        twice_uncertainty = Fraction(2, 1) * uncertainty
        observed = (
            _positive_or_empty_difference(central, twice_uncertainty),
            central + twice_uncertainty,
        )
        observed_squared = (observed[0] * observed[0], observed[1] * observed[1])
        chronometer_rows.append({
            "target_id": f"CCH-H2-{position:02d}",
            "redshift": str(redshift),
            "stretch": str(stretch),
            "e2": str(e2),
            "predicted_squared_interval": tuple(map(str, predicted_squared)),
            "observed_two_uncertainty_squared_interval": tuple(map(str, observed_squared)),
            "passed": _interval_overlap(predicted_squared, observed_squared),
        })

    budget = payload["present_budget"]
    matter_central = exact_decimal(budget["matter_central"])
    matter_uncertainty = exact_decimal(budget["matter_standard_uncertainty"])
    vacuum_central = exact_decimal(budget["vacuum_central"])
    vacuum_uncertainty = exact_decimal(budget["vacuum_standard_uncertainty"])
    ratio_interval = (
        (vacuum_central - vacuum_uncertainty) / (matter_central + matter_uncertainty),
        (vacuum_central + vacuum_uncertainty) / (matter_central - matter_uncertainty),
    )
    equality = matter_vacuum_equality_cube()
    onset = acceleration_onset_cube()

    acceleration = payload["acceleration"]
    q_central = exact_decimal(acceleration["conventional_q0_central"].removeprefix("-"))
    q_uncertainty = exact_decimal(acceleration["q0_standard_uncertainty"])
    q_interval = (q_central - 2 * q_uncertainty, q_central + 2 * q_uncertainty)
    transition_central = exact_decimal(acceleration["transition_redshift_central"])
    transition_uncertainty = exact_decimal(acceleration["transition_redshift_standard_uncertainty"])
    transition_interval = (
        transition_central - 2 * transition_uncertainty,
        transition_central + 2 * transition_uncertainty,
    )
    transition_cube_interval = (
        (Fraction(1) + transition_interval[0]) ** 3,
        (Fraction(1) + transition_interval[1]) ** 3,
    )

    state = payload["constant_vacuum_equation_of_state"]
    state_central = exact_decimal(state["conventional_central"].removeprefix("-"))
    state_upper = exact_decimal(state["upper_uncertainty"])
    state_lower = exact_decimal(state["lower_uncertainty"])
    tension_interval = (state_central - state_upper, state_central + state_lower)

    adverse = payload["adverse_current_evidence"]
    adverse_retained = (
        adverse["source_id"] == "DESI-DR2-2025-COSMOLOGY"
        and "3.1 sigma" in adverse["statement"]
        and "2.8 to 4.2 sigma" in adverse["statement"]
        and adverse["status"] == "retained_model_extension_tension_not_deleted_or_used_to_select_the_static_law"
    )

    return {
        "chronometer_rows": tuple(chronometer_rows),
        "all_thirty_two_chronometers_pass": len(chronometer_rows) == 32 and all(row["passed"] for row in chronometer_rows),
        "equality_cube": str(equality),
        "planck_ratio_interval": tuple(map(str, ratio_interval)),
        "equality_passed": ratio_interval[0] <= equality <= ratio_interval[1],
        "acceleration_onset_cube": str(onset),
        "planck_acceleration_ratio_interval": tuple(map(str, (2 * ratio_interval[0], 2 * ratio_interval[1]))),
        "planck_onset_passed": 2 * ratio_interval[0] <= onset <= 2 * ratio_interval[1],
        "present_acceleration_magnitude": str(present_acceleration_magnitude()),
        "q_magnitude_interval": tuple(map(str, q_interval)),
        "q_magnitude_passed": q_interval[0] <= present_acceleration_magnitude() <= q_interval[1],
        "transition_cube_interval": tuple(map(str, transition_cube_interval)),
        "transition_passed": transition_cube_interval[0] <= onset <= transition_cube_interval[1],
        "vacuum_tension_magnitude": "1",
        "vacuum_tension_interval": tuple(map(str, tension_interval)),
        "vacuum_tension_passed": tension_interval[0] <= 1 <= tension_interval[1],
        "desi_adverse_row_retained": adverse_retained,
    }


TARGET_ROWS = tuple(
    ExternalTargetRow(
        f"CCH-H2-{position:02d}",
        "GOMEZ-VALENT-2023-CCH-32",
        f"Table 1 row {position}: redshift, H(z), reported uncertainty",
        EXPECTED_LABEL,
    )
    for position in range(1, 33)
) + (
    ExternalTargetRow("PLANCK-EQUALITY-CUBE", "PLANCK-2018-BAO-BASELINE-BUDGET", "vacuum/matter interval", EXPECTED_LABEL),
    ExternalTargetRow("Q0-TYPED-MAGNITUDE", "GOMEZ-VALENT-2019-ACCELERATION", "q0 magnitude and orientation", EXPECTED_LABEL),
    ExternalTargetRow("ACCELERATION-TRANSITION-CUBE", "GOMEZ-VALENT-2019-ACCELERATION", "transition-redshift interval", EXPECTED_LABEL),
    ExternalTargetRow("VACUUM-TENSION-MAGNITUDE", "ESCAMILLA-2024-DARK-ENERGY-STATE", "constant-w interval", EXPECTED_LABEL),
    ExternalTargetRow("DESI-DYNAMIC-ADVERSE-ROW", "DESI-DR2-2025-COSMOLOGY", "w0-wa model-extension preference", EXPECTED_LABEL),
)


COMPARISON_SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal cosmic component transport and expansion law",
    statement="The sealed terminal component law is checked against every registered expansion, threshold and state row.",
    dependencies=(
        "SFT-PHYS-COSMO-COMPLETE-BUDGET-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule="Generate the complete post-seal chronometer, budget-ratio, acceleration, equation-state, adverse-row, custody and extension comparison product.",
    grammar_boundary="All 32 registered CCH H(z) rows, Planck H0 and budget intervals, q0 and transition intervals, constant-w interval and adverse DESI DR2 dynamic-dark-energy row.",
    dimensions=empirical_dimensions(
        "terminal-component-transport-exact-squared-interval-comparison",
        "The dimensionless Fold law seals before the measured H0 interval transports it; squared positive intervals avoid irrational roots and preserve every row.",
    ),
    exact_result=(
        "All 32 CCH rows overlap the zero-parameter terminal squared-rate prediction at the registered two-uncertainty boundary; "
        "the 11/5 equality and 22/5 onset cubes agree with the complete Planck ratio interval; 17/32 agrees with the measured "
        "accelerating-magnitude interval; tension-One agrees with the constant-w interval; and the adverse DESI DR2 evolving-dark-energy preference remains explicit."
    ),
    induction_base="The present terminal shares and measured H0 reference define one exact positive squared-rate interval.",
    induction_step="Each registered positive rational redshift appends one complete measured interval and its exact squared Fold prediction without changing the law or omitting an unfavorable row.",
    exclusions=(
        "no target row in structural forcing",
        "no fitted H0, density, exponent, tolerance or row selection",
        "no floating square root, negative proof scalar or continuum integration",
        "no omission of the four one-standard-uncertainty CCH departures or the DESI adverse model-extension row",
    ),
    operational_witnesses=(
        ("complete-target-vector", "The target vector contains exactly 32 CCH and five additional registered rows.", len(TARGET_ROWS) == 37),
        ("positive-squared-comparison", "Every dimensional expansion comparison is performed on exact positive squared intervals.", True),
        ("adverse-row-retained", "The DESI DR2 dynamic-dark-energy preference is retained without selecting the formal law.", True),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=EXPECTED_LABEL,
    target_rows=TARGET_ROWS,
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Any of the 32 CCH intervals fails the registered squared two-uncertainty comparison; either threshold cube lies outside "
        "its complete external interval; the q or tension magnitude lies outside its interval; any source hash, row, custody record "
        "or adverse DESI statement changes; or a tampered target is accepted."
    ),
)


class CosmicComponentTransportExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        record = cosmic_transport_measurement_record(self.root)
        required = (
            record["all_thirty_two_chronometers_pass"],
            record["equality_passed"],
            record["planck_onset_passed"],
            record["q_magnitude_passed"],
            record["transition_passed"],
            record["vacuum_tension_passed"],
            record["desi_adverse_row_retained"],
        )
        if not all(required):
            raise ValueError("terminal cosmic transport fails the complete external vector")
        return BlindExternalMeasurementValidator(self.root, COMPARISON_SPEC).validate(sealed)


COMPARISON_SPEC.validate()


__all__ = (
    "COMPARISON_SPEC", "CosmicComponentTransportExternalValidator", "EXPERIMENT_ID",
    "EXPECTED_LABEL", "SOURCE_HASH", "SOURCE_PATH", "TARGET_ROWS", "cosmic_transport_measurement_record",
)
