"""Post-seal Planck comparison for reconstructed cosmological values."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.physics.cosmology_prior_value_laws import DARK_BARYON_CLAIM_ID, dark_baryon_structure
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal


SOURCE_PATH = "experiments/external_sources/physics/snapshots/planck-2018-density-abstract-record.json"
SOURCE_HASH = "sha256:274e0189de5846ce0b8c2d7b83ae06c72587cf8325d4d2b2338e88dd0a74a88f"
SOURCE_ID = "PLANCK-2018-VI-ABSTRACT-DENSITIES"
EXPECTED_LABEL = "sealed-leading-and-native-deepened-ratios-inside-complete-planck-density-interval"


def density_ratio_interval(path: Path) -> tuple[Fraction, Fraction]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("source_id") != SOURCE_ID or payload.get("confidence_region") != "68 percent":
        raise ValueError("Planck density record identity or confidence boundary changed")
    rows = payload.get("reported_parameters", {})
    baryon = rows.get("baryon_density_omega_b_h2", {})
    dark = rows.get("cold_dark_matter_density_omega_c_h2", {})
    b = exact_decimal(baryon["central"])
    bu = exact_decimal(baryon["standard_uncertainty"])
    d = exact_decimal(dark["central"])
    du = exact_decimal(dark["standard_uncertainty"])
    if not (Fraction(0, 1) < bu < b and Fraction(0, 1) < du < d):
        raise ValueError("Planck density uncertainty does not preserve positive intervals")
    return (d - du) / (b + bu), (d + du) / (b - bu)


_lower, _upper = density_ratio_interval(Path(__file__).resolve().parents[2] / SOURCE_PATH)
_structure = dark_baryon_structure()

DARK_BARYON_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=DARK_BARYON_CLAIM_ID,
    title="Generation-cover dark-to-baryon fraction",
    statement="The sealed exact leading and native-deepened ratios are compared with the complete Planck 2018 cold-dark/baryon density interval.",
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
    generation_rule="Generate the complete post-seal relation, two-density-row, uncertainty, custody and no-extra-rule comparison product.",
    grammar_boundary="Both complete Planck abstract density rows and their reported 68-percent uncertainties.",
    dimensions=empirical_dimensions(
        "sealed-dark-baryon-ratios-versus-complete-planck-interval",
        "Both density intervals are retained and divided outward to form the complete ratio interval.",
    ),
    exact_result="Both 27/5 and 279/52 lie inside the complete Planck dark-to-baryon density interval.",
    induction_base="The baryon-density row retains central value, uncertainty and source identity.",
    induction_step="The cold-dark-density row is appended without dropping the baryon row; division propagates both intervals outward.",
    exclusions=("no Planck density in structural forcing", "no selected central-value ratio", "no floating comparison", "no omitted row or uncertainty"),
    operational_witnesses=(
        ("leading-inside", "The exact leading ratio is inside the complete interval.", _lower <= _structure["leading_ratio"] <= _upper),
        ("deepened-inside", "The exact native-deepened ratio is inside the complete interval.", _lower <= _structure["refined_ratio"] <= _upper),
        ("positive-complete-interval", "The exact ratio interval is positive and ordered.", Fraction(0, 1) < _lower < _upper),
    ),
    experiment_id="SFT-EXP-PHYS-COSMO-DARK-BARYON-FRACTION-001",
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(
        ExternalTargetRow("PLANCK-2018-BARYON-DENSITY", SOURCE_ID, "abstract baryon-density central value and 68-percent uncertainty", EXPECTED_LABEL),
        ExternalTargetRow("PLANCK-2018-COLD-DARK-DENSITY", SOURCE_ID, "abstract cold-dark-density central value and 68-percent uncertainty", EXPECTED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Either sealed ratio lies outside the complete density interval, either density row or uncertainty is omitted, source custody changes, or a tampered comparison is accepted.",
)


class DarkBaryonExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        lower, upper = density_ratio_interval(self.root / SOURCE_PATH)
        structure = dark_baryon_structure()
        if not all(lower <= structure[key] <= upper for key in ("leading_ratio", "refined_ratio")):
            raise ValueError("sealed dark/baryon ratio lies outside the complete Planck interval")
        return BlindExternalMeasurementValidator(self.root, DARK_BARYON_EMPIRICAL_SPEC).validate(sealed)


DARK_BARYON_EMPIRICAL_SPEC.validate()


__all__ = ("DARK_BARYON_EMPIRICAL_SPEC", "DarkBaryonExternalValidator", "density_ratio_interval")
