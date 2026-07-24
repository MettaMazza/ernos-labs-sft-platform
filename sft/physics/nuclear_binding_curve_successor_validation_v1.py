"""Post-seal AMDC/AME2020 comparison for the nuclear binding curve."""

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
from sft.physics.nuclear_binding_curve_successor_laws_v1 import (
    NUCLEAR_BINDING_CURVE_TERMINAL_ID,
    binding_peak_certificate,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "AMDC-AME2020-MASS-1-BINDING-2021"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/nuclear-binding-curve-successor-source-record.json"
SOURCE_HASH = "sha256:d10a9474253b2d29fac71ee21352039659f2e5f4b7d75395416d361878a18ddc"
RAW_PATH = "experiments/external_sources/physics/snapshots/ame2020-mass_1.mas20"
RAW_HASH = "sha256:e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
MEASURED_LABEL = (
    "sealed-zero-parameter-binding-ledger-uniquely-predicts-A62-Z28-N34"
    "__complete-AME2020-2548-positive-composite-row-census-identifies-Ni62-global-binding-per-nucleon-maximum"
    "__Ni62-lower-uncertainty-bound-exceeds-every-rival-upper-bound"
    "__light-anchor-rise-and-heavy-anchor-fall-close-an-interior-iron-nickel-maximum"
    "__unqualified-iron-only-maximum-replaced-by-exact-nickel62-coordinate"
)


def authoritative_record(root: Path) -> dict[str, object]:
    record_path = root / SOURCE_PATH
    raw_path = root / RAW_PATH
    if hash_file(record_path) != SOURCE_HASH or hash_file(raw_path) != RAW_HASH:
        raise ValueError("AME2020 binding source identity changed")
    payload = json.loads(record_path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "development_targets_already_known": True,
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "no_fitted_mass_formula_coefficient": True,
        "irrational_radius_not_admitted": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("AME2020 binding custody disclosure changed")
    census = payload["complete_numeric_binding_census"]
    if census["raw_numeric_row_count"] != 2550 or census["positive_composite_row_count"] != 2548:
        raise ValueError("AME2020 registered binding census changed")
    boundary = census["singleton_empty_binding_boundary_rows"]
    if len(boundary) != 2 or any(row["mass_number"] != 1 or row["binding_energy_per_nucleon_keV"] != "0.0" for row in boundary):
        raise ValueError("AME2020 singleton empty-binding boundary changed")
    return payload


def measured_binding_rows(root: Path) -> tuple[dict[str, object], ...]:
    authoritative_record(root)
    rows: list[dict[str, object]] = []
    for line in (root / RAW_PATH).read_text(encoding="utf-8").splitlines():
        if len(line) < 79:
            continue
        try:
            neutrons = int(line[4:9])
            charge = int(line[9:14])
            mass = int(line[14:19])
        except ValueError:
            continue
        if mass < 2:
            continue
        binding_raw = line[54:67].strip()
        uncertainty_raw = line[68:78].strip()
        if not binding_raw or binding_raw == "*" or "#" in binding_raw:
            continue
        try:
            binding = Fraction(binding_raw)
            uncertainty = Fraction(uncertainty_raw)
        except (ValueError, ZeroDivisionError):
            continue
        lower = positive_take(binding, uncertainty)
        rows.append({
            "mass_number": mass,
            "charge_count": charge,
            "neutron_count": neutrons,
            "element": line[20:23].strip(),
            "binding_energy_per_nucleon_keV": binding,
            "standard_uncertainty_keV": uncertainty,
            "lower_keV": lower,
            "upper_keV": binding + uncertainty,
        })
    if len(rows) != 2548:
        raise ValueError("complete AME2020 numeric binding census changed")
    return tuple(rows)


def row_by_coordinate(root: Path, mass: int, charge: int) -> dict[str, object]:
    matches = tuple(
        row for row in measured_binding_rows(root)
        if row["mass_number"] == mass and row["charge_count"] == charge
    )
    if len(matches) != 1:
        raise ValueError("AME2020 coordinate is absent or duplicated")
    return matches[0]


def measurement_analysis(root: Path) -> dict[str, object]:
    rows = measured_binding_rows(root)
    ranked = sorted(rows, key=lambda row: row["binding_energy_per_nucleon_keV"], reverse=True)
    peak = ranked[0]
    rival_upper = max(row["upper_keV"] for row in rows if row is not peak)
    anchors = {
        "deuterium": row_by_coordinate(root, 2, 1),
        "helium4": row_by_coordinate(root, 4, 2),
        "carbon12": row_by_coordinate(root, 12, 6),
        "iron56": row_by_coordinate(root, 56, 26),
        "iron58": row_by_coordinate(root, 58, 26),
        "nickel62": row_by_coordinate(root, 62, 28),
        "lead208": row_by_coordinate(root, 208, 82),
        "uranium238": row_by_coordinate(root, 238, 92),
    }
    light_rise = (
        anchors["deuterium"]["upper_keV"] < anchors["helium4"]["lower_keV"]
        < anchors["carbon12"]["lower_keV"] < anchors["iron56"]["lower_keV"]
        < anchors["nickel62"]["lower_keV"]
    )
    heavy_fall = (
        anchors["lead208"]["upper_keV"] < anchors["nickel62"]["lower_keV"]
        and anchors["uranium238"]["upper_keV"] < anchors["lead208"]["lower_keV"]
    )
    return {
        "complete_measured_row_count": len(rows),
        "global_maximum": {
            "mass_number": peak["mass_number"],
            "charge_count": peak["charge_count"],
            "neutron_count": peak["neutron_count"],
            "element": peak["element"],
            "binding_energy_per_nucleon_keV": str(peak["binding_energy_per_nucleon_keV"]),
            "standard_uncertainty_keV": str(peak["standard_uncertainty_keV"]),
            "lower_keV": str(peak["lower_keV"]),
            "upper_keV": str(peak["upper_keV"]),
        },
        "runner_up": {
            "mass_number": ranked[1]["mass_number"],
            "charge_count": ranked[1]["charge_count"],
            "element": ranked[1]["element"],
            "binding_energy_per_nucleon_keV": str(ranked[1]["binding_energy_per_nucleon_keV"]),
            "standard_uncertainty_keV": str(ranked[1]["standard_uncertainty_keV"]),
        },
        "global_rival_upper_keV": str(rival_upper),
        "peak_interval_separated_from_every_rival": peak["lower_keV"] > rival_upper,
        "light_curve_rises_to_peak": light_rise,
        "heavy_curve_falls_from_peak": heavy_fall,
        "anchor_intervals_keV": {
            name: [str(row["lower_keV"]), str(row["upper_keV"])] for name, row in anchors.items()
        },
        "formal_coordinate_matches_measurement": (
            binding_peak_certificate()["mass_number"],
            binding_peak_certificate()["charge_count"],
            binding_peak_certificate()["neutron_count"],
        ) == (peak["mass_number"], peak["charge_count"], peak["neutron_count"]),
        "iron_only_shortcut_rejected": peak["element"] == "Ni" and ranked[1]["element"] == "Fe",
    }


def nuclear_binding_curve_classification(root: Path) -> str:
    analysis = measurement_analysis(root)
    if analysis["complete_measured_row_count"] != 2548:
        raise ValueError("complete AME2020 measured vector was not retained")
    if analysis["global_maximum"] != {
        "mass_number": 62,
        "charge_count": 28,
        "neutron_count": 34,
        "element": "Ni",
        "binding_energy_per_nucleon_keV": "17589111/2000",
        "standard_uncertainty_keV": "69/10000",
        "lower_keV": "43972743/5000",
        "upper_keV": "10993203/1250",
    }:
        raise ValueError("AME2020 nickel-62 maximum row changed")
    if not all(analysis[key] is True for key in (
        "peak_interval_separated_from_every_rival",
        "light_curve_rises_to_peak",
        "heavy_curve_falls_from_peak",
        "formal_coordinate_matches_measurement",
        "iron_only_shortcut_rejected",
    )):
        raise ValueError("AME2020 binding-curve comparison failed")
    return MEASURED_LABEL


NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=NUCLEAR_BINDING_CURVE_TERMINAL_ID,
    title="Terminal nuclear binding curve post-seal AME2020 comparison",
    statement=(
        "Observation informed the explicit successor, but the AMDC AME2020 mass table remains capability-closed "
        "until the zero-parameter ledger, exact all-mass maximum and tail induction seal. After release, all 2,548 "
        "positive composite rows and uncertainties are retained; the two free-singleton zero-binding inscriptions "
        "remain explicit external empty-binding boundaries and never become proof values."
    ),
    dependencies=(
        NUCLEAR_BINDING_CURVE_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete post-seal coordinate, 2,548-positive-composite-row AME census, two singleton boundary rows, uncertainty, curve-direction, custody and unfavorable-iron-shortcut product.",
    grammar_boundary="Every positive composite AME2020 binding-energy-per-nucleon row, its reported standard uncertainty, both free-singleton empty-binding boundary inscriptions, the complete global ranking, registered light/heavy anchors, source identity and custody state.",
    dimensions=empirical_dimensions(
        "sealed-A62-Z28-N34-coordinate-versus-complete-AME2020-binding-census",
        "Every positive composite row participates in the global maximum test; both singleton boundary rows and all anchor/adverse iron-only statements remain visible.",
    ),
    exact_result=(
        "The complete 2,548-row positive-composite AME2020 census places nickel-62 at 8794.5555 +/- 0.0069 keV per "
        "nucleon. Its lower uncertainty endpoint exceeds every rival upper endpoint. The independently sealed "
        "A=62, Z=28, N=34 coordinate matches exactly; light anchors rise and lead-208/uranium-238 fall from the "
        "interior iron-nickel region."
    ),
    induction_base="One sealed coordinate is compared with one complete authoritative measured row and its outward exact uncertainty interval.",
    induction_step="Each additional AME row enters the same exact global ranking and anchor-direction census without altering the sealed ledger or omitting an unfavorable rival.",
    exclusions=(
        "no AME row, nuclide name or measured energy readable by the executable law",
        "no semi-empirical coefficient fitted to the AME table",
        "no floating-point interval decision or evaluated irrational radius",
        "no omitted numeric rival, uncertainty, heavy anchor or adverse iron-only control",
        "no measurement-to-formal-survivor flow",
    ),
    operational_witnesses=((
        "target-free-exact-coordinate",
        "The exact A=62, Z=28, N=34 coordinate and rational score separation exist before source release.",
        binding_peak_certificate()["mass_number"] == 62
        and binding_peak_certificate()["charge_count"] == 28
        and binding_peak_certificate()["neutron_count"] == 34,
    ),),
    experiment_id="SFT-EXP-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("AME2020-COMPLETE-BINDING-CENSUS", SOURCE_ID, "AME2020 mass_1.mas20 complete 2,548 positive composite rows plus two singleton empty-binding boundary rows", MEASURED_LABEL),
        ExternalTargetRow("AME2020-GLOBAL-MAXIMUM", SOURCE_ID, "AME2020 complete binding-energy-per-nucleon ranking with reported uncertainties", MEASURED_LABEL),
        ExternalTargetRow("AME2020-LIGHT-TO-IRON-NICKEL-RISE", SOURCE_ID, "AME2020 deuterium, helium-4, carbon-12, iron-56/58 and nickel-62 rows", MEASURED_LABEL),
        ExternalTargetRow("AME2020-HEAVY-FALL", SOURCE_ID, "AME2020 lead-208 and uranium-238 rows", MEASURED_LABEL),
        ExternalTargetRow("AME2020-IRON-ONLY-ADVERSE", SOURCE_ID, "AME2020 nickel-62 versus iron-58/56 ranking", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if the complete measured table has another maximum, the predicted coordinate differs, "
        "uncertainty intervals erase the separation, either curve direction fails, any numeric rival is omitted, "
        "or target access precedes the formal seal."
    ),
)


class NuclearBindingCurveValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(
            self.root, NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC
        ).validate(sealed)
        if nuclear_binding_curve_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("nuclear binding curve authoritative classification changed")
        return validation


NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC.validate()


__all__ = (
    "MEASURED_LABEL",
    "NUCLEAR_BINDING_CURVE_EMPIRICAL_SPEC",
    "NuclearBindingCurveValidator",
    "RAW_HASH",
    "RAW_PATH",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "measured_binding_rows",
    "measurement_analysis",
    "nuclear_binding_curve_classification",
)
