"""Post-seal NIST/NBS comparison for atomic field splitting."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.atomic_field_splitting_successor_laws_v1 import (
    ATOMIC_FIELD_SPLITTING_TERMINAL_ID,
    linear_stark_magnitude,
    magnetic_sublevel_count,
    quadratic_stark_magnitude,
    zeeman_shift_magnitude,
)
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)


SOURCE_ID = "NIST-NBS-ATOMIC-FIELD-SPLITTING-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/atomic-field-splitting-successor-source-record.json"
SOURCE_HASH = "sha256:5093c824cec5438a98f82fd5e75460e737a001a11471d12dbd7cd67b930661df"
MEASURED_LABEL = (
    "sealed-two-J-plus-one-and-linear-Zeeman-match-NIST"
    "__degenerate-hydrogen-linear-Stark-matches-NBS"
    "__nondegenerate-cesium-quadratic-Stark-matches-NIST"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("atomic field-splitting source record identity changed")
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
        "complete_reported_resolution_and_uncertainty_status_retained": True,
        "linear_and_quadratic_stark_classes_separately_retained": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("atomic field-splitting custody disclosure changed")
    if set(payload.get("sources", {})) != {
        "nist_zeeman",
        "nbs_hydrogen_linear_stark",
        "nist_cesium_quadratic_stark",
    }:
        raise ValueError("atomic field-splitting source set changed")
    return payload


def field_splitting_classification(root: Path) -> str:
    sources = authoritative_record(root)["sources"]
    zeeman = sources["nist_zeeman"]["reported_record"]
    if zeeman["sublevel_count_relation"] != "2J+1":
        raise ValueError("NIST Zeeman multiplicity relation changed")
    if zeeman["weak_field_energy_relation"] != "delta-E=g*M*mu_B*B" or zeeman["field_order"] != "linear":
        raise ValueError("NIST weak-field Zeeman relation changed")
    if Fraction(zeeman["wavenumber_shift_coefficient_cm_inverse_per_tesla"]) != Fraction(23343, 50000):
        raise ValueError("NIST displayed Zeeman coefficient changed")
    if zeeman["coefficient_status"] != "NIST displayed value; no uncertainty reported on page":
        raise ValueError("NIST Zeeman uncertainty disclosure changed")

    hydrogen = sources["nbs_hydrogen_linear_stark"]["reported_record"]
    if hydrogen["response_order"] != "linear" or "linear energy shift" not in hydrogen["measurement_protocol"]:
        raise ValueError("NBS hydrogen linear-Stark record changed")

    cesium = sources["nist_cesium_quadratic_stark"]["reported_record"]
    if cesium["response_relation"] != "frequency-shift=(polarizability/2)*electric-field-squared":
        raise ValueError("NIST cesium quadratic-Stark relation changed")
    if cesium["response_order"] != "quadratic" or Fraction(cesium["polarizability_displayed_hz_per_field_squared"]) != Fraction(1, 2):
        raise ValueError("NIST cesium response class changed")
    field_v_per_m = Fraction(cesium["quadratic_voltage_range_V"]) / Fraction(cesium["electrode_spacing_m"])
    if field_v_per_m != 150000 or field_v_per_m / 100 != Fraction(cesium["first_level_crossing_field_V_per_cm"]):
        raise ValueError("NIST cesium voltage/spacing/field cross-check failed")
    if cesium["uncertainty_status"] != "no uncertainty reported for these displayed design values":
        raise ValueError("NIST cesium uncertainty disclosure changed")

    g_factor = Fraction(3, 2)
    field = Fraction(2, 5)
    if magnetic_sublevel_count(4) != 5:
        raise ValueError("sealed magnetic multiplicity witness failed")
    if zeeman_shift_magnitude(g_factor, 2, 2 * field) != 2 * zeeman_shift_magnitude(g_factor, 2, field):
        raise ValueError("sealed Zeeman linear scaling failed")
    if linear_stark_magnitude(Fraction(4, 7), 2 * field) != 2 * linear_stark_magnitude(Fraction(4, 7), field):
        raise ValueError("sealed degenerate Stark scaling failed")
    if quadratic_stark_magnitude(Fraction(4, 7), 2 * field) != 4 * quadratic_stark_magnitude(Fraction(4, 7), field):
        raise ValueError("sealed nondegenerate Stark scaling failed")
    return MEASURED_LABEL


ATOMIC_FIELD_SPLITTING_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=ATOMIC_FIELD_SPLITTING_TERMINAL_ID,
    title="Terminal atomic field-splitting post-seal NIST/NBS comparison",
    statement=(
        "Observation informed the explicit field-splitting successor. NIST weak-field Zeeman, NBS hydrogen "
        "linear-Stark and NIST nondegenerate cesium quadratic-Stark records remain capability-closed until the "
        "exact relation seals; post-seal comparison retains every displayed coefficient and uncertainty status."
    ),
    dependencies=(
        ATOMIC_FIELD_SPLITTING_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal multiplicity, field-order, degeneracy, source, custody and row-retention product.",
    grammar_boundary="The complete registered NIST Zeeman, NBS hydrogen linear-Stark and NIST cesium quadratic-Stark records, including displayed values, resolution status and exact operating cross-check.",
    dimensions=empirical_dimensions(
        "sealed-field-splitting-law-versus-complete-NIST-NBS-vector",
        "The sealed multiplicity, first/second field orders and degeneracy discriminator are compared with every registered row.",
    ),
    exact_result=(
        "The sealed 2J+1 multiplicity and linear Zeeman response equal the NIST weak-field law; retained "
        "degeneracy equals the NBS linear hydrogen Stark class; absent degeneracy equals the NIST quadratic "
        "cesium class, whose 750 V across 0.005 m exactly translates to 1500 V/cm."
    ),
    induction_base="One held noncentral orientation and one field act produce the first exact positive linear response.",
    induction_step="Appending an orientation preserves one common linear spacing, while closing the unpaired first electric act preserves the two-act quadratic successor at every finite support.",
    exclusions=(
        "no target readable by the executable law",
        "no measured coefficient selecting a formal survivor",
        "no numerical-zero central state or negative proof scalar",
        "no floating-point comparison",
        "no conflation of degenerate linear and nondegenerate quadratic Stark classes",
        "no omitted displayed coefficient, operating value or uncertainty-status row",
    ),
    operational_witnesses=((
        "target-free-field-orders",
        "The formal linear and quadratic scaling relations exist exactly before source release.",
        zeeman_shift_magnitude(Fraction(3, 2), 1, Fraction(2, 5)) == 2 * zeeman_shift_magnitude(Fraction(3, 2), 1, Fraction(1, 5))
        and quadratic_stark_magnitude(Fraction(4, 7), Fraction(2, 5)) == 4 * quadratic_stark_magnitude(Fraction(4, 7), Fraction(1, 5)),
    ),),
    experiment_id="SFT-EXP-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(
        ExternalTargetRow("NIST-WEAK-FIELD-ZEEMAN", SOURCE_ID, "NIST Atomic Spectroscopy Zeeman Effect page", MEASURED_LABEL),
        ExternalTargetRow("NBS-HYDROGEN-LINEAR-STARK", SOURCE_ID, "NBS Special Publication 617 hydrogen linear-Stark record", MEASURED_LABEL),
        ExternalTargetRow("NIST-CESIUM-QUADRATIC-STARK", SOURCE_ID, "NIST cesium-15s quadratic-Stark voltage-reference record", MEASURED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if multiplicity or a field order differs, the degeneracy discriminator fails, the exact "
        "voltage/spacing translation fails, a displayed value or uncertainty status changes, target access "
        "precedes sealing, or observational provenance is concealed."
    ),
)


class AtomicFieldSplittingValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, ATOMIC_FIELD_SPLITTING_EMPIRICAL_SPEC).validate(sealed)
        if field_splitting_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("atomic field-splitting authoritative classification changed")
        return validation


ATOMIC_FIELD_SPLITTING_EMPIRICAL_SPEC.validate()


__all__ = (
    "ATOMIC_FIELD_SPLITTING_EMPIRICAL_SPEC",
    "AtomicFieldSplittingValidator",
    "MEASURED_LABEL",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "field_splitting_classification",
)
