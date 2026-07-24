"""Complete four-row Planck+BAO test for the refined cosmic budget."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.physics.cosmic_budget_law import COSMIC_BUDGET_CLAIM_ID, cosmic_budget_structure
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal


SOURCE_PATH = "experiments/external_sources/physics/snapshots/planck-2018-bao-budget-record.json"
SOURCE_HASH = "sha256:a8525585688e7ba818f8650fc0f8b73a449823d5e199a8be36e37b8e73a0e612"
SOURCE_ID = "PLANCK-2018-BAO-BASELINE-BUDGET"
EXPECTED_LABEL = "sealed-refined-four-part-budget-inside-all-complete-planck-bao-intervals"


def _direct_interval(row: dict[str, str]) -> tuple[Fraction, Fraction]:
    central = exact_decimal(row["central"])
    uncertainty = exact_decimal(row["standard_uncertainty"])
    if uncertainty >= central:
        raise ValueError("budget uncertainty does not preserve a positive interval")
    return central - uncertainty, central + uncertainty


def planck_budget_intervals(path: Path) -> dict[str, tuple[Fraction, Fraction]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("source_id") != SOURCE_ID or payload.get("confidence_region") != "68 percent":
        raise ValueError("Planck budget source identity or confidence boundary changed")
    if payload.get("data_combination") != "Planck 2018 plus BAO baseline parameter table":
        raise ValueError("Planck budget data-combination identity changed")
    rows = payload.get("parameters", {})
    matter = _direct_interval(rows["matter_fraction_omega_m"])
    vacuum = _direct_interval(rows["dark_energy_fraction_omega_lambda"])
    hubble = _direct_interval(rows["hubble_constant"])
    baryon_physical = _direct_interval(rows["baryon_physical_density_omega_b_h2"])
    dark_physical = _direct_interval(rows["cold_dark_physical_density_omega_c_h2"])
    hundred = Fraction(100, 1)
    h_lower, h_upper = hubble[0] / hundred, hubble[1] / hundred
    baryon = baryon_physical[0] / (h_upper * h_upper), baryon_physical[1] / (h_lower * h_lower)
    cold_dark = dark_physical[0] / (h_upper * h_upper), dark_physical[1] / (h_lower * h_lower)
    return {"vacuum": vacuum, "matter": matter, "baryon": baryon, "cold_dark": cold_dark}


def all_inside(values: dict[str, Fraction], intervals: dict[str, tuple[Fraction, Fraction]]) -> bool:
    return all(intervals[key][0] <= values[key] <= intervals[key][1] for key in intervals)


_intervals = planck_budget_intervals(Path(__file__).resolve().parents[2] / SOURCE_PATH)
_refined = cosmic_budget_structure()
_leading = {
    "vacuum": Fraction(2, 3),
    "matter": Fraction(1, 3),
    "baryon": Fraction(5, 96),
    "cold_dark": Fraction(9, 32),
}

COSMIC_BUDGET_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=COSMIC_BUDGET_CLAIM_ID,
    title="Depth-five Fold cosmic energy budget",
    statement=(
        "The four sealed refined budget values are tested jointly against the complete Planck+BAO vacuum, "
        "matter, baryon-density, cold-dark-density and Hubble rows with exact outward interval propagation."
    ),
    dependencies=(
        "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
        "SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule="Generate the complete post-seal four-component, five-source-row, uncertainty, conversion, custody and no-extra-rule comparison product.",
    grammar_boundary="All five Planck+BAO baseline rows required to test vacuum, total matter, baryon and cold-dark fractions at their complete 68-percent interval boundary.",
    dimensions=empirical_dimensions(
        "sealed-four-budget-values-versus-five-complete-planck-bao-rows",
        "Vacuum and matter use their direct intervals; both physical densities are divided outward by the complete squared reduced-Hubble interval.",
    ),
    exact_result="All four refined values 11/16, 5/16, 25/512 and 135/512 lie inside their complete Planck+BAO intervals; all four earlier leading values lie outside their respective intervals.",
    induction_base="The vacuum and total-matter rows retain both central values and both uncertainties.",
    induction_step="The Hubble, baryon physical-density and cold-dark physical-density rows are appended and propagated outward; no row or endpoint is selected away.",
    exclusions=(
        "no Planck value in structural forcing",
        "no central-value-only conversion, fitted tolerance or floating comparison",
        "no omitted component, Hubble conversion row, uncertainty or data-combination identity",
        "no erasure or false admission of the earlier leading four-value comparison",
    ),
    operational_witnesses=(
        ("refined-all-inside", "All four refined exact values lie inside all four complete intervals.", all_inside(_refined, _intervals)),
        ("leading-all-rejected", "Every earlier leading exact value lies outside its corresponding complete interval.", all(not (_intervals[key][0] <= value <= _intervals[key][1]) for key, value in _leading.items())),
        ("four-components-retained", "The comparison contains exactly the four registered component identities.", set(_intervals) == {"vacuum", "matter", "baryon", "cold_dark"}),
    ),
    experiment_id="SFT-EXP-PHYS-COSMO-COMPLETE-BUDGET-001",
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(
        ExternalTargetRow("PLANCK-BAO-VACUUM-FRACTION", SOURCE_ID, "complete direct vacuum interval", EXPECTED_LABEL),
        ExternalTargetRow("PLANCK-BAO-MATTER-FRACTION", SOURCE_ID, "complete direct matter interval", EXPECTED_LABEL),
        ExternalTargetRow("PLANCK-BAO-BARYON-FRACTION", SOURCE_ID, "physical baryon density divided by complete squared reduced-Hubble interval", EXPECTED_LABEL),
        ExternalTargetRow("PLANCK-BAO-COLD-DARK-FRACTION", SOURCE_ID, "physical cold-dark density divided by complete squared reduced-Hubble interval", EXPECTED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Any refined component lies outside its complete interval; any earlier leading component is falsely labelled as passing; any required source row or uncertainty is omitted; custody changes; or a tampered comparison is accepted.",
)


class CosmicBudgetExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        intervals = planck_budget_intervals(self.root / SOURCE_PATH)
        if not all_inside(cosmic_budget_structure(), intervals):
            raise ValueError("refined cosmic budget fails at least one complete Planck+BAO interval")
        if any(intervals[key][0] <= value <= intervals[key][1] for key, value in _leading.items()):
            raise ValueError("leading budget failure record changed")
        return BlindExternalMeasurementValidator(self.root, COSMIC_BUDGET_EMPIRICAL_SPEC).validate(sealed)


COSMIC_BUDGET_EMPIRICAL_SPEC.validate()


__all__ = ("COSMIC_BUDGET_EMPIRICAL_SPEC", "CosmicBudgetExternalValidator", "planck_budget_intervals")
