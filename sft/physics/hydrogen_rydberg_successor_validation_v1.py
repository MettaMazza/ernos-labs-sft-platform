"""Post-seal NIST comparison for terminal hydrogen Rydberg completion."""

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
from sft.physics.hydrogen_rydberg_successor_laws_v1 import (
    HYDROGEN_RYDBERG_TERMINAL_ID,
    terminal_hydrogen_scale_interval,
)
from sft.physics.prior_value_laws import positive_take


SOURCE_ID = "NIST-HYDROGEN-RYDBERG-SUCCESSOR-2022-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/hydrogen-rydberg-successor-source-record.json"
SOURCE_HASH = "sha256:2bbdc82b1ff35fce2b486fe1c26fc8341faeca13fbba201ceffa64ee731ac448"
COMPONENT_HASHES = {
    "rydberg": "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67",
    "hydrogen_ionization": "sha256:cc54c774518d62cbb7e95f17b3b7fcd9d1faf0aa90043a607b91dff0a43e2087",
    "hydrogen_lines": "sha256:86ccaeb875fcdb4445e727618509621ceee656e5dc02295140ecdb6e1d2dd443",
}
MEASURED_LABEL = (
    "terminal-hydrogen-reduced-mass-and-radiative-scale-contained-in-NIST-ionization-Rydberg-ratio"
    "__absolute-ionization-Lyman-Balmer-vector-passed"
)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("hydrogen Rydberg source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "development_targets_already_known": True,
        "classification": "observational_derivation",
        "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
        "empirical_prediction_protocol": True,
        "target_inaccessible_during_prediction_execution": True,
        "formal_relations_contain_measurement": False,
        "measurements_select_formal_survivors": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "complete_reported_uncertainties_retained": True,
        "displayed_resolution_separately_labelled_where_no_uncertainty_is_reported": True,
        "earlier_hydrogen_and_proton_receipts_preserved": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("hydrogen Rydberg custody disclosure changed")
    sources = payload.get("sources", {})
    if set(sources) != set(COMPONENT_HASHES):
        raise ValueError("hydrogen Rydberg source set changed")
    for key, expected in COMPONENT_HASHES.items():
        row = sources[key]
        component = root / row.get("snapshot_path", "missing")
        if row.get("snapshot_hash") != expected or hash_file(component) != expected:
            raise ValueError(f"hydrogen Rydberg component identity changed: {key}")
    if payload.get("comparison_policy", {}).get("provenance") != (
        "Observation informed the explicit frozen successor relation. The executable law module contains none of these values and cannot open this record. Complete grammar enumeration, unique selection and sealing precede target release."
    ):
        raise ValueError("hydrogen Rydberg comparison provenance changed")
    return payload


def symmetric_interval(value: str, spread: str) -> tuple[Fraction, Fraction]:
    centre, half_width = Fraction(value), Fraction(spread)
    return positive_take(centre, half_width), centre + half_width


def rydberg_interval(root: Path) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"]["rydberg"]["row"]
    return symmetric_interval(row["value_cm_inverse"], row["standard_uncertainty_cm_inverse"])


def ionization_target_interval(root: Path) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"]["hydrogen_ionization"]["row"]
    return symmetric_interval(row["value_cm_inverse"], row["last_inscribed_digit_half_width_cm_inverse"])


def line_target_interval(root: Path, kind: str) -> tuple[Fraction, Fraction]:
    row = authoritative_record(root)["sources"]["hydrogen_lines"]["rows"][kind]
    return symmetric_interval(row["value_cm_inverse"], row["standard_uncertainty_cm_inverse"])


def outward_ratio_interval(
    numerator: tuple[Fraction, Fraction],
    denominator: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    if numerator[0] <= 0 or denominator[0] <= 0:
        raise ValueError("hydrogen Rydberg ratio requires positive endpoints")
    return numerator[0] / denominator[1], numerator[1] / denominator[0]


def predicted_ionization_interval(root: Path) -> tuple[Fraction, Fraction]:
    scale, rydberg = terminal_hydrogen_scale_interval(), rydberg_interval(root)
    return scale[0] * rydberg[0], scale[1] * rydberg[1]


def predicted_line_interval(root: Path, gap: Fraction) -> tuple[Fraction, Fraction]:
    ionization = predicted_ionization_interval(root)
    return gap * ionization[0], gap * ionization[1]


def intervals_overlap(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> bool:
    return left[0] <= right[1] and right[0] <= left[1]


def hydrogen_rydberg_classification(root: Path) -> str:
    scale = terminal_hydrogen_scale_interval()
    target_scale = outward_ratio_interval(ionization_target_interval(root), rydberg_interval(root))
    if not target_scale[0] <= scale[0] <= scale[1] <= target_scale[1]:
        raise ValueError("terminal hydrogen/Rydberg scale left the complete registered interval")
    ionization = predicted_ionization_interval(root)
    if not ionization_target_interval(root)[0] <= ionization[0] <= ionization[1] <= ionization_target_interval(root)[1]:
        raise ValueError("terminal hydrogen ionization left the displayed-resolution enclosure")
    lines = {
        "lyman_alpha": predicted_line_interval(root, Fraction(3, 4)),
        "balmer_alpha": predicted_line_interval(root, Fraction(5, 36)),
    }
    for kind, prediction in lines.items():
        if not intervals_overlap(prediction, line_target_interval(root, kind)):
            raise ValueError(f"terminal hydrogen line left the complete NIST interval: {kind}")
    return MEASURED_LABEL


HYDROGEN_RYDBERG_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=HYDROGEN_RYDBERG_TERMINAL_ID,
    title="Terminal hydrogen reduced-mass and Rydberg post-seal NIST comparison",
    statement=(
        "Observation informed the explicit terminal hydrogen scale.  The complete NIST Rydberg, hydrogen "
        "ionization, Lyman-alpha and Balmer-alpha rows remain capability-closed while the engine exhausts the "
        "formal grammar and seals the exact reduced-mass/radiative relation; post-seal exact interval propagation "
        "contains the ionization ratio and absolute ionization and overlaps both complete line intervals."
    ),
    dependencies=(
        HYDROGEN_RYDBERG_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal terminal hydrogen Rydberg comparison product.",
    grammar_boundary="The complete registered CODATA Rydberg row, NIST H-I ionization row, both Kramida line intervals, immutable predecessors, disclosed observational development and sealed target-inaccessible terminal relation.",
    dimensions=empirical_dimensions(
        "sealed-terminal-hydrogen-scale-versus-complete-NIST-Rydberg-ionization-and-line-vector",
        "Every exact relation, uncertainty, displayed-resolution label, source identity and predecessor receipt remains visible while post-seal interval decisions remain exact.",
    ),
    exact_result=(
        "The exact terminal H/R-infinity interval is contained in the registered NIST ionization/Rydberg interval; "
        "its absolute ionization interval is contained at displayed resolution, and its immutable Lyman and Balmer "
        "gaps overlap both complete NIST line intervals."
    ),
    induction_base="The source record retains the complete Rydberg, ionization and first two line rows beside the immutable sealed scale.",
    induction_step="Every later metrology revision creates a new comparison receipt and cannot rewrite the relation, any component snapshot or predecessor evidence.",
    exclusions=(
        "no target readable by the executable law",
        "no measured value selecting the formal survivor",
        "no hidden development provenance or uncertainty reinterpretation",
        "no floating-point interval decision",
        "no omitted line or rewritten predecessor receipt",
    ),
    operational_witnesses=((
        "target-free-exact-scale",
        "The terminal hydrogen scale is an exact positive interval before source release.",
        Fraction(99, 100) < terminal_hydrogen_scale_interval()[0] < terminal_hydrogen_scale_interval()[1] < 1,
    ),),
    experiment_id="SFT-EXP-PHYS-ATOMIC-HYDROGEN-RYDBERG-TERMINAL-005",
    expected_observation_label=MEASURED_LABEL,
    target_rows=(ExternalTargetRow(
        "NIST-HYDROGEN-RYDBERG-IONIZATION-LINE-COMPLETE-VECTOR",
        SOURCE_ID,
        "CODATA 2022 Rydberg row; NIST ASD H-I ionization row; Kramida Tables 10 and 11 Balmer/Lyman rows",
        MEASURED_LABEL,
    ),),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "The claim fails if the sealed scale leaves the complete ionization/Rydberg interval, its translated "
        "ionization leaves the displayed-resolution enclosure, either line misses its full interval, any source "
        "hash or uncertainty changes, target access precedes sealing, development provenance is hidden, or a "
        "predecessor receipt is rewritten."
    ),
)


class HydrogenRydbergValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        validation = BlindExternalMeasurementValidator(self.root, HYDROGEN_RYDBERG_EMPIRICAL_SPEC).validate(sealed)
        if hydrogen_rydberg_classification(self.root) != MEASURED_LABEL or not validation.passed:
            raise ValueError("terminal hydrogen Rydberg authoritative classification changed")
        return validation


HYDROGEN_RYDBERG_EMPIRICAL_SPEC.validate()


__all__ = (
    "HYDROGEN_RYDBERG_EMPIRICAL_SPEC",
    "HydrogenRydbergValidator",
    "MEASURED_LABEL",
    "SOURCE_HASH",
    "SOURCE_ID",
    "SOURCE_PATH",
    "authoritative_record",
    "hydrogen_rydberg_classification",
    "ionization_target_interval",
    "line_target_interval",
    "predicted_ionization_interval",
    "predicted_line_interval",
    "rydberg_interval",
)
