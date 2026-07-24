"""Post-seal exact interval test for the Hubble calibration reconstruction."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.hubble_calibration_law import (
    HUBBLE_CALIBRATION_CLAIM_ID,
    hubble_calibration_structure,
)
from sft.physics.measured_value import exact_decimal


SOURCE_PATH = "experiments/external_sources/physics/snapshots/planck-shoes-hubble-abstract-record.json"
SOURCE_HASH = "sha256:4f5bc28ad7a691b9b1fb64bb68a30546f5c82ea7f2e9797f4ade713cad498c04"
SOURCE_ID = "PLANCK-2018-SHOES-2022-HUBBLE-ABSTRACTS"
PLANCK_SOURCE_ID = "PLANCK-2018-VI-HUBBLE"
SHOES_SOURCE_ID = "SHOES-2022-BASELINE-HUBBLE"
EXPECTED_LABEL = "sealed-leading-and-depth-seven-ratios-inside-complete-planck-shoes-ratio-interval"


def hubble_ratio_interval(path: Path) -> tuple[Fraction, Fraction]:
    """Propagate both complete source intervals outward through late/early."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("source_id") != SOURCE_ID:
        raise ValueError("Hubble source record identity changed")
    publications = payload.get("publications", {})
    early = publications.get("early_route", {})
    late = publications.get("late_route", {})
    if early.get("route") != "CMB inference assuming base Lambda-CDM":
        raise ValueError("Planck route qualification changed")
    if late.get("route") != "Cepheid-SN Ia distance ladder baseline result":
        raise ValueError("SH0ES route qualification changed")
    if early.get("unit") != late.get("unit"):
        raise ValueError("Hubble source units differ")

    early_central = exact_decimal(early["central"])
    early_uncertainty = exact_decimal(early["standard_uncertainty"])
    late_central = exact_decimal(late["central"])
    late_uncertainty = exact_decimal(late["standard_uncertainty"])
    if not (
        Fraction(0, 1) < early_uncertainty < early_central
        and Fraction(0, 1) < late_uncertainty < late_central
    ):
        raise ValueError("Hubble uncertainty does not preserve positive intervals")
    return (
        (late_central - late_uncertainty) / (early_central + early_uncertainty),
        (late_central + late_uncertainty) / (early_central - early_uncertainty),
    )


_lower, _upper = hubble_ratio_interval(Path(__file__).resolve().parents[2] / SOURCE_PATH)
_structure = hubble_calibration_structure()

HUBBLE_CALIBRATION_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=HUBBLE_CALIBRATION_CLAIM_ID,
    title="Fold calibration ratio between early and late expansion routes",
    statement=(
        "The sealed exact leading and depth-seven Fold calibration ratios are compared with the complete "
        "outward-propagated ratio interval from Planck 2018 and the SH0ES 2022 baseline result."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule=(
        "Generate the complete post-seal relation, two-route, two-uncertainty, custody and no-extra-rule "
        "comparison product."
    ),
    grammar_boundary=(
        "The complete Planck 2018 base-Lambda-CDM Hubble interval and complete SH0ES 2022 baseline "
        "distance-ladder interval, propagated outward through late divided by early."
    ),
    dimensions=empirical_dimensions(
        "sealed-ratios-versus-complete-planck-shoes-interval",
        "Both route intervals are retained and divided outward before either sealed ratio is tested.",
    ),
    exact_result=(
        "Both exact predictions 13/12 and 3305/3048 lie inside the complete one-standard-uncertainty "
        "late/early interval formed from the registered Planck and SH0ES records."
    ),
    induction_base="The Planck row retains route qualification, central value, uncertainty, unit and source identity.",
    induction_step=(
        "The SH0ES row is appended with the same complete fields; outward interval division retains every "
        "endpoint and no central-value-only tolerance."
    ),
    exclusions=(
        "no Planck or SH0ES value in structural forcing",
        "no claim that CMB inference and local distance-ladder measurement are the same procedure",
        "no central-value-only comparison, fitted tolerance or floating arithmetic",
        "no omitted uncertainty, route qualification or source row",
    ),
    operational_witnesses=(
        ("leading-inside", "The exact leading ratio is inside the complete source interval.", _lower <= _structure["leading_ratio"] <= _upper),
        ("refined-inside", "The exact depth-seven ratio is inside the complete source interval.", _lower <= _structure["refined_ratio"] <= _upper),
        ("positive-complete-interval", "The exact ratio interval is positive and ordered.", Fraction(0, 1) < _lower < _upper),
    ),
    experiment_id="SFT-EXP-PHYS-COSMO-HUBBLE-CALIBRATION-001",
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(
        ExternalTargetRow(
            "PLANCK-2018-HUBBLE-INTERVAL",
            PLANCK_SOURCE_ID,
            "abstract base-Lambda-CDM Hubble central value and 68-percent uncertainty",
            EXPECTED_LABEL,
        ),
        ExternalTargetRow(
            "SHOES-2022-HUBBLE-INTERVAL",
            SHOES_SOURCE_ID,
            "abstract baseline Cepheid-SN Ia central value and total reported uncertainty",
            EXPECTED_LABEL,
        ),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Either sealed exact ratio lies outside the complete outward-propagated late/early interval; either "
        "route, central value, uncertainty, unit or qualification is omitted; source custody changes; or a "
        "tampered comparison is accepted."
    ),
)


class HubbleCalibrationExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        lower, upper = hubble_ratio_interval(self.root / SOURCE_PATH)
        structure = hubble_calibration_structure()
        if not all(lower <= structure[key] <= upper for key in ("leading_ratio", "refined_ratio")):
            raise ValueError("sealed Hubble calibration ratio lies outside the complete source interval")
        return BlindExternalMeasurementValidator(
            self.root, HUBBLE_CALIBRATION_EMPIRICAL_SPEC
        ).validate(sealed)


HUBBLE_CALIBRATION_EMPIRICAL_SPEC.validate()


__all__ = (
    "HUBBLE_CALIBRATION_EMPIRICAL_SPEC",
    "HubbleCalibrationExternalValidator",
    "hubble_ratio_interval",
)
