"""Post-seal Planck curvature test without signed SFT proof scalars."""

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
from sft.physics.measured_value import exact_decimal
from sft.physics.spatial_flatness_law import SPATIAL_FLATNESS_CLAIM_ID


SOURCE_PATH = "experiments/external_sources/physics/snapshots/planck-2018-curvature-record.json"
SOURCE_HASH = "sha256:97d4c8210c7de6cc8b406d96f3d0136ef3535a96e5a9874bcceca1c875185873"
SOURCE_ID = "PLANCK-2018-VI-CURVATURE-47B"
EXPECTED_LABEL = "sealed-empty-curvature-remainder-inside-complete-planck-bao-signed-interval"


def planck_interval_contains_absence(path: Path) -> bool:
    """Test interval crossing using orientation and positive magnitudes only."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "source_id": SOURCE_ID,
        "central_orientation": "positive",
        "confidence_region": "68 percent",
        "data_combination": "Planck TT,TE,EE+lowE+lensing+BAO",
        "equation_reference": "47b",
    }
    if any(payload.get(key) != value for key, value in required.items()):
        raise ValueError("Planck curvature record identity or boundary changed")
    central_magnitude = exact_decimal(payload["central_magnitude"])
    uncertainty_magnitude = exact_decimal(payload["reported_standard_uncertainty_magnitude"])
    return uncertainty_magnitude >= central_magnitude


_contains_absence = planck_interval_contains_absence(
    Path(__file__).resolve().parents[2] / SOURCE_PATH
)

SPATIAL_FLATNESS_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=SPATIAL_FLATNESS_CLAIM_ID,
    title="Complete-partition spatial flatness and absent curvature remainder",
    statement=(
        "The sealed empty-One curvature remainder is tested against the complete Planck 2018 plus BAO "
        "signed curvature interval using a held orientation and exact positive magnitudes."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule="Generate the complete post-seal absence, signed-orientation, magnitude, uncertainty, custody and no-extra-rule comparison product.",
    grammar_boundary="The complete Planck equation 47b central orientation and magnitude, symmetric 68-percent uncertainty magnitude and full data-combination identity.",
    dimensions=empirical_dimensions(
        "empty-remainder-versus-oriented-positive-magnitude-interval",
        "The signed external record is held as orientation plus positive magnitudes; absence is inside exactly when uncertainty reaches beyond the central magnitude.",
    ),
    exact_result="The empty-One curvature remainder is inside the complete Planck TT,TE,EE+lowE+lensing+BAO 68-percent interval reported in equation 47b.",
    induction_base="The external central record retains one positive magnitude and its positive orientation label.",
    induction_step="The complete symmetric uncertainty magnitude is appended; reaching beyond the central magnitude makes the interval contain structural absence without constructing a signed proof scalar.",
    exclusions=(
        "no Planck value in the structural derivation",
        "no numerical zero or negative SFT proof scalar",
        "no omitted sign orientation, uncertainty, confidence region or data-combination identity",
        "no claim that this parameter analysis alone proves the physical mechanism",
    ),
    operational_witnesses=(
        ("complete-interval-contains-absence", "The reported uncertainty magnitude exceeds the reported central magnitude.", _contains_absence),
        ("orientation-retained", "The positive central orientation remains a held external record rather than a signed proof scalar.", True),
        ("empty-result-not-numerical-zero", "The structural prediction is named as empty-One absence.", "empty" in EXPECTED_LABEL),
    ),
    experiment_id="SFT-EXP-PHYS-COSMO-SPATIAL-FLATNESS-001",
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(
        ExternalTargetRow(
            "PLANCK-2018-BAO-CURVATURE-47B",
            SOURCE_ID,
            "equation 47b central orientation/magnitude and complete 68-percent uncertainty",
            EXPECTED_LABEL,
        ),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The complete registered curvature interval excludes structural absence; its orientation, central "
        "magnitude, uncertainty, confidence region or data combination is omitted; source custody changes; "
        "or a tampered comparison is accepted."
    ),
)


class SpatialFlatnessExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        if not planck_interval_contains_absence(self.root / SOURCE_PATH):
            raise ValueError("complete Planck curvature interval excludes the sealed absence result")
        return BlindExternalMeasurementValidator(
            self.root, SPATIAL_FLATNESS_EMPIRICAL_SPEC
        ).validate(sealed)


SPATIAL_FLATNESS_EMPIRICAL_SPEC.validate()


__all__ = (
    "SPATIAL_FLATNESS_EMPIRICAL_SPEC",
    "SpatialFlatnessExternalValidator",
    "planck_interval_contains_absence",
)
