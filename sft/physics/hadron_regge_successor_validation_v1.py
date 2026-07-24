"""Post-seal PDG comparison for light-hadron multiplets and Regge support."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.hadron_regge_successor_laws_v1 import (
    HADRON_REGGE_TERMINAL_ID,
    baryon_multiplet_partition,
    meson_multiplet_partition,
    normalized_regge_squared_support,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "PDG-HADRON-MULTIPLETS-REGGE-2025"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/hadron-regge-successor-source-record.json"
SOURCE_HASH = "sha256:c6e671212984fa6b6956a3d748c12c81879686b9198ca5a0818670fe63301358"
MEASURED_LABEL = (
    "sealed-nine-equals-eight-plus-one-and-twenty-seven-equals-ten-plus-eight-plus-eight-plus-one-match-PDG"
    "__complete-five-state-natural-parity-mass-vector-is-strictly-ordered"
    "__literal-common-squared-mass-step-is-rejected-by-complete-reported-intervals"
    "__exact-affine-Fold-law-retained-at-normalized-fixed-carrier-boundary"
    "__rho5-summary-omission-status-retained"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("hadron/Regge source record identity changed")
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
        "complete_trajectory_rows_retained": True,
        "unfavorable_exact_spacing_result_retained": True,
        "listing_status_retained": True,
    }
    custody = payload.get("custody", {})
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("hadron/Regge custody disclosure changed")
    if set(payload.get("sources", {})) != {
        "pdg_quark_model",
        "pdg_2025_meson_summary",
        "pdg_2025_rho5_listing",
    }:
        raise ValueError("hadron/Regge source set changed")
    return payload


def trajectory_rows(root: Path) -> tuple[dict[str, object], ...]:
    sources = authoritative_record(root)["sources"]
    summary = tuple(sources["pdg_2025_meson_summary"]["reported_record"])
    listing = dict(sources["pdg_2025_rho5_listing"]["reported_record"])
    rows = (*summary, listing)
    if tuple(row["spin_J"] for row in rows) != (1, 2, 3, 4, 5):
        raise ValueError("complete positive spin ordering changed")
    return rows


def exact_mass_interval(row: dict[str, object]) -> tuple[Fraction, Fraction]:
    centre = Fraction(str(row["mass_MeV"]))
    uncertainty = Fraction(str(row["standard_uncertainty_MeV"]))
    lower = positive_take(centre, uncertainty)
    if not isinstance(lower, Fraction):
        raise ValueError("reported mass interval exhausted its positive centre")
    return lower, centre + uncertainty


def squared_mass_interval_GeV2(row: dict[str, object]) -> tuple[Fraction, Fraction]:
    lower, upper = exact_mass_interval(row)
    unit = Fraction(1000, 1)
    return (lower / unit) ** 2, (upper / unit) ** 2


def successive_squared_mass_steps(root: Path) -> tuple[tuple[Fraction, Fraction], ...]:
    squares = tuple(squared_mass_interval_GeV2(row) for row in trajectory_rows(root))
    steps: list[tuple[Fraction, Fraction]] = []
    for previous, successor in zip(squares, squares[1:]):
        lower = positive_take(successor[0], previous[1])
        upper = positive_take(successor[1], previous[0])
        if not isinstance(lower, Fraction) or not isinstance(upper, Fraction) or lower > upper:
            raise ValueError("measured squared-mass ordering failed")
        steps.append((lower, upper))
    return tuple(steps)


def exact_common_step_exists(root: Path) -> bool:
    steps = successive_squared_mass_steps(root)
    return max(row[0] for row in steps) <= min(row[1] for row in steps)


def measurement_analysis(root: Path) -> dict[str, object]:
    rows = trajectory_rows(root)
    squares = tuple(squared_mass_interval_GeV2(row) for row in rows)
    steps = successive_squared_mass_steps(root)
    return {
        "trajectory_rows": [
            {
                "state": row["state"],
                "spin_J": row["spin_J"],
                "JPC": row["JPC"],
                "mass_kind": row["mass_kind"],
                "mass_interval_MeV": [str(value) for value in exact_mass_interval(row)],
                "squared_mass_interval_GeV2": [str(value) for value in square],
                "table_status": row["table_status"],
            }
            for row, square in zip(rows, squares)
        ],
        "successive_squared_mass_step_intervals_GeV2": [[str(value) for value in row] for row in steps],
        "common_step_intersection_exists": exact_common_step_exists(root),
        "classification": (
            "strict-order-and-Regge-scale-correspondence-with-literal-exact-equal-step-rejected-at-reported-interval-boundary"
        ),
        "no_fit_performed": True,
        "no_residual_correction_admitted": True,
    }


def hadron_regge_classification(root: Path) -> str:
    sources = authoritative_record(root)["sources"]
    model = sources["pdg_quark_model"]["reported_record"]
    if model["light_flavours"] != ["u", "d", "s"]:
        raise ValueError("PDG light-flavour support changed")
    if model["light_meson_combination_count"] != 9 or model["light_meson_partition"] != [8, 1]:
        raise ValueError("PDG meson multiplet record changed")
    if model["light_baryon_ordered_support_count"] != 27 or model["light_baryon_partition"] != [10, 8, 8, 1]:
        raise ValueError("PDG baryon multiplet record changed")
    if model["minimal_meson_content"] != "q-antiquark" or model["minimal_baryon_content"] != "qqq":
        raise ValueError("PDG minimal hadron composition record changed")
    if "non-minimal multiquark" not in model["exotic_boundary"]:
        raise ValueError("PDG exotic-composite boundary was omitted")
    if meson_multiplet_partition() != {"ordered_support": 9, "predecessor_multiplet": 8, "invariant_singlet": 1}:
        raise ValueError("sealed meson partition changed")
    if baryon_multiplet_partition() != {"ordered_support": 27, "symmetric": 10, "mixed_first_hand": 8, "mixed_second_hand": 8, "antisymmetric": 1}:
        raise ValueError("sealed baryon partition changed")
    if tuple(normalized_regge_squared_support(rank) for rank in range(1, 6)) != tuple(Fraction(rank, 1) for rank in range(1, 6)):
        raise ValueError("sealed normalized Regge support changed")

    rows = trajectory_rows(root)
    if tuple(row["JPC"] for row in rows) != ("1--", "2++", "3--", "4++", "5--"):
        raise ValueError("registered natural-parity sequence changed")
    intervals = tuple(exact_mass_interval(row) for row in rows)
    if any(successor[0] <= previous[1] for previous, successor in zip(intervals, intervals[1:])):
        raise ValueError("complete physical mass intervals are no longer strictly ordered")
    if rows[-1]["table_status"] != "OMITTED FROM SUMMARY TABLE":
        raise ValueError("rho5 omission status was concealed")
    if exact_common_step_exists(root):
        raise ValueError("registered adverse exact-spacing result changed")
    return MEASURED_LABEL


HADRON_REGGE_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=HADRON_REGGE_TERMINAL_ID,
    title="Terminal light-hadron multiplet and Regge post-seal PDG comparison",
    statement=(
        "Observation informed the explicit successor.  The complete PDG light-multiplet counts and five-state "
        "natural-parity trajectory remain capability-closed until the exact Fold partitions and affine support "
        "seal.  Post-seal comparison retains every mass, uncertainty and listing status, including the adverse "
        "finding that the four propagated squared-mass step intervals have no common intersection."
    ),
    dependencies=(
        HADRON_REGGE_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal multiplet, composition, trajectory, interval, status, custody, adverse-result and row-retention product.",
    grammar_boundary="The complete registered PDG nine-cell meson and twenty-seven-cell baryon partitions plus every mass, uncertainty, spin, parity and status row in the inherited five-state natural-parity trajectory.",
    dimensions=empirical_dimensions(
        "sealed-hadron-partitions-and-affine-support-versus-complete-PDG-vector",
        "Every multiplet, composition, mass interval, squared-mass step and unfavorable exact-spacing row remains visible.",
    ),
    exact_result=(
        "The independent Fold counts equal PDG's 9=8+1 and 27=10+8+8+1 organizations.  The five registered "
        "resonance mass intervals rise strictly with spin, but the four exact squared-mass step intervals have "
        "empty common intersection.  Therefore literal exact equal spacing of these reported masses is rejected; "
        "the exact theorem remains the normalized fixed-carrier affine support law, without a fitted correction."
    ),
    induction_base="The first positive rank carries one normalized squared-support unit and the first measured row supplies one complete positive mass interval only after sealing.",
    induction_step="Each structural successor adds one identical held carrier; each measurement successor appends its full source interval and status without rewriting the theorem or earlier rows.",
    exclusions=(
        "no target readable by the executable law",
        "no measured mass, slope or conventional multiplet selecting a formal survivor",
        "no fitted tension, intercept, residual or post-hoc trajectory subset",
        "no floating-point interval decision",
        "no omission of rho5 listing status or an unfavorable squared-step interval",
        "no conversion of approximate physical correspondence into a false exact measured equality",
    ),
    operational_witnesses=((
        "target-free-multiplets-and-affine-support",
        "The complete exact partitions and equal normalized successor already exist before source release.",
        meson_multiplet_partition()["ordered_support"] == 9
        and baryon_multiplet_partition()["ordered_support"] == 27
        and normalized_regge_squared_support(5) - normalized_regge_squared_support(4) == Fraction(1, 1),
    ),),
    experiment_id="SFT-EXP-PHYS-HADRON-REGGE-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-LIGHT-MESON-MULTIPLET", SOURCE_ID, "PDG 2025 Quark Model nine equals octet plus singlet record", MEASURED_LABEL),
        ExternalTargetRow("PDG-LIGHT-BARYON-MULTIPLETS", SOURCE_ID, "PDG 2025 Quark Model twenty-seven equals ten plus eight plus eight plus one record", MEASURED_LABEL),
        ExternalTargetRow("PDG-NATURAL-PARITY-TRAJECTORY", SOURCE_ID, "PDG 2025 rho/a summary rows and rho5 listing with complete uncertainties and status", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if either sealed partition differs, the normalized affine successor ceases to be exact, "
        "any registered mass/uncertainty/status row is lost, strict ordering changes, the exact common-step result "
        "is misstated, a fitted correction is introduced, or target access precedes sealing."
    ),
)


class HadronReggeValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, HADRON_REGGE_EMPIRICAL_SPEC).validate(sealed)
        if hadron_regge_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("hadron/Regge authoritative classification changed")
        return validation


HADRON_REGGE_EMPIRICAL_SPEC.validate()


__all__ = (
    "HADRON_REGGE_EMPIRICAL_SPEC",
    "HadronReggeValidator",
    "MEASURED_LABEL",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "exact_common_step_exists",
    "exact_mass_interval",
    "hadron_regge_classification",
    "measurement_analysis",
    "squared_mass_interval_GeV2",
    "successive_squared_mass_steps",
    "trajectory_rows",
)
