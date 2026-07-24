"""Exact post-seal validation of terminal CKM and baryon transport.

The two formal relations are target-free.  The earlier adverse CKM comparison
was already visible during successor development, so this module preserves the
required observational-derivation disclosure.  It reads the registered target
only from ``validate`` after the engine has sealed the formal derivation.
"""

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
from sft.physics.matter_flavour_laws_v1 import (
    bisect_bracket,
    isolate_cubic_roots,
    quark_cubic_invariants,
)
from sft.physics.matter_flavour_terminal_ckm_laws_v1 import (
    TERMINAL_BARYON_PHOTON_ID,
    TERMINAL_CKM_ID,
    terminal_ckm_slope_contribution,
)


SOURCE_ID = "MATTER-FLAVOUR-TERMINAL-AUTHORITATIVE-2025-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/matter-flavour-terminal-source-record.json"
SOURCE_HASH = "sha256:652b186e29c835c9cf8fdfd3393fe19c6a81917666989331c5ca060dc789ae9e"

COMPONENT_HASHES = {
    "pdg-2025-ckm-matrix.pdf": "sha256:a0a78578971f38ff89c6fc5579bc608de41ec383a205dc25cba1d26f7145610a",
    "pdg-2025-bbang-cosmology.pdf": "sha256:2ea12893db3cdd33a67b6dbff98e74ca15b14ba2b2c3c2be5abcfdeffd98b543",
}

TERMINAL_CKM_LABEL = (
    "terminal-CKM-s12-s23-s13-and-J-all-overlap-complete-PDG-three-sigma-intervals"
    "__observational-derivation-disclosed"
)
TERMINAL_ETA_LABEL = (
    "terminal-baryon-to-photon-prediction-lies-inside-independent-PDG-BBN-and-"
    "Planck-derived-intervals__observational-derivation-disclosed"
)


def decimal(value: str) -> Fraction:
    return Fraction(value)


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("terminal matter/flavour source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    custody = payload.get("custody", {})
    required = {
        "development_target_already_known": True,
        "classification": "observational_derivation",
        "formal_relation_contains_measurement": False,
        "measurement_selects_formal_survivor": False,
        "engine_prediction_sealed_before_target_release_within_run": True,
        "blind_forward_discovery_claimed": False,
        "all_rows_and_uncertainties_retained": True,
    }
    if any(custody.get(key) != value for key, value in required.items()):
        raise ValueError("terminal matter/flavour custody disclosure changed")
    sources = payload.get("sources", ())
    if len(sources) != 2:
        raise ValueError("terminal matter/flavour source vector is incomplete")
    for item in sources:
        snapshot = item["snapshot_path"]
        name = snapshot.rsplit("/", 1)[-1]
        if name not in COMPONENT_HASHES or hash_file(root / snapshot) != COMPONENT_HASHES[name]:
            raise ValueError("terminal matter/flavour component identity changed")
    return payload


def source_rows(root: Path, source_id: str) -> dict[str, object]:
    for item in authoritative_record(root)["sources"]:
        if item["source_id"] == source_id:
            return item["rows"]
    raise ValueError(f"missing registered terminal source {source_id}")


def refined_quark_roots() -> dict[str, tuple[tuple[Fraction, Fraction], ...]]:
    result = {}
    resolution = Fraction(1, 10 ** 15)
    for name, values in quark_cubic_invariants().items():
        brackets = isolate_cubic_roots(values[1], values[2])
        while any(upper - lower > resolution for lower, upper in brackets):
            brackets = tuple(bisect_bracket(row, values[1], values[2]) for row in brackets)
        result[name] = brackets
    return result


def square_ratio_interval(
    numerator: tuple[Fraction, Fraction],
    denominator: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    return (numerator[0] / denominator[1]) ** 2, (numerator[1] / denominator[0]) ** 2


def overlaps(interval: tuple[Fraction, Fraction], target: tuple[Fraction, Fraction]) -> bool:
    return interval[0] <= target[1] and target[0] <= interval[1]


def terminal_ckm_prediction_intervals() -> dict[str, tuple[Fraction, Fraction]]:
    roots = refined_quark_roots()
    down, up = roots["down"], roots["up"]
    s12_sq = square_ratio_interval(down[0], down[1])
    down_slope = down[1][0] / down[2][1], down[1][1] / down[2][0]
    up_slope = up[1][0] / up[2][1], up[1][1] / up[2][0]
    addition = terminal_ckm_slope_contribution()
    s23 = down_slope[0] - up_slope[1] + addition, down_slope[1] - up_slope[0] + addition
    if s23[0] <= Fraction(1, 10 ** 9):
        raise ValueError("terminal CKM slope lost its positive separation")
    s23_sq = s23[0] ** 2, s23[1] ** 2
    s13_sq = s12_sq[0] * s23_sq[0] / 6, s12_sq[1] * s23_sq[1] / 6
    if not s12_sq[1] < Fraction(1, 2) or not s23_sq[1] < Fraction(1, 2) or not s13_sq[1] < Fraction(1, 3):
        raise ValueError("CKM endpoint monotonicity boundary changed")
    first = s12_sq[0] * (1 - s12_sq[0]), s12_sq[1] * (1 - s12_sq[1])
    second = s23_sq[0] * (1 - s23_sq[0]), s23_sq[1] * (1 - s23_sq[1])
    third = s13_sq[0] * (1 - s13_sq[1]) ** 2, s13_sq[1] * (1 - s13_sq[0]) ** 2
    j_sq = first[0] * second[0] * third[0], first[1] * second[1] * third[1]
    return {
        "s12_squared": s12_sq,
        "s23_squared": s23_sq,
        "s13_squared": s13_sq,
        "jarlskog_squared": j_sq,
    }


def three_sigma_squared(row: dict[str, str]) -> tuple[Fraction, Fraction]:
    centre = decimal(row["value"])
    lower = centre - 3 * decimal(row["lower_uncertainty"])
    upper = centre + 3 * decimal(row["upper_uncertainty"])
    if lower <= Fraction(1, 10 ** 12):
        raise ValueError("registered positive interval crossed its declared boundary")
    return lower ** 2, upper ** 2


def terminal_ckm_classification(root: Path) -> str:
    rows = source_rows(root, "PDG-2025-CKM-MATRIX")
    predictions = terminal_ckm_prediction_intervals()
    mapping = {
        "s12_squared": "sin_theta12",
        "s23_squared": "sin_theta23",
        "s13_squared": "sin_theta13",
        "jarlskog_squared": "jarlskog",
    }
    checks = {
        prediction: overlaps(predictions[prediction], three_sigma_squared(rows[source]))
        for prediction, source in mapping.items()
    }
    if not all(checks.values()):
        raise ValueError(f"terminal CKM complete comparison failed: {checks}")
    return TERMINAL_CKM_LABEL


def terminal_eta_prediction_interval() -> tuple[Fraction, Fraction]:
    j_sq = terminal_ckm_prediction_intervals()["jarlskog_squared"]
    return j_sq[0] / 2, j_sq[1] / 2


def terminal_eta_classification(root: Path) -> str:
    rows = source_rows(root, "PDG-2025-BIG-BANG-COSMOLOGY")
    prediction = terminal_eta_prediction_interval()
    bbn = rows["bbn_baryon_to_photon_ratio"]
    bbn_interval = decimal(bbn["strict_lower"]), decimal(bbn["strict_upper"])
    planck = rows["planck_derived_baryon_to_photon_ratio"]
    centre = decimal(planck["value"])
    uncertainty = decimal(planck["standard_uncertainty"])
    planck_interval = centre - uncertainty, centre + uncertainty
    if not (bbn_interval[0] < prediction[0] <= prediction[1] < bbn_interval[1]):
        raise ValueError("terminal baryon prediction left the independent BBN interval")
    if not overlaps(prediction, planck_interval):
        raise ValueError("terminal baryon prediction missed the PDG Planck-derived interval")
    return TERMINAL_ETA_LABEL


def empirical_dependencies(*formal_ids: str) -> tuple[str, ...]:
    return formal_ids + (
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    )


TERMINAL_CKM_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=TERMINAL_CKM_ID,
    title="Terminal CKM complete comparison",
    statement="The sealed terminal CKM relation is compared with every complete PDG CKM sine and Jarlskog interval, while its observational-derivation provenance remains explicit.",
    dependencies=empirical_dependencies(TERMINAL_CKM_ID),
    generation_rule="Generate the complete eight-axis post-seal terminal CKM comparison product.",
    grammar_boundary="All four registered PDG CKM rows with asymmetric uncertainty propagated to exact three-standard-uncertainty squared intervals.",
    dimensions=empirical_dimensions("sealed-terminal-CKM-versus-complete-PDG-vector", "Every CKM coordinate, uncertainty and provenance disclosure is retained."),
    exact_result="The target-free terminal CKM successor places s12, s23, s13 and J inside their complete registered PDG three-standard-uncertainty intervals.",
    induction_base="The first CKM row retains its sealed interval and complete source uncertainty.",
    induction_step="Each remaining CKM row is appended without selection, rescaling or removal of an earlier row.",
    exclusions=("no target value in the executable relation", "no fitted shift", "no blind-forward-discovery claim", "no omitted CKM row or enlarged uncertainty"),
    operational_witnesses=(("target-free-relation", "The exact terminal contribution is positive and generated without opening the target record.", terminal_ckm_slope_contribution() > Fraction(1, 10 ** 9)),),
    experiment_id="SFT-EXP-PHYS-MATTER-CKM-TERMINAL-004",
    expected_observation_label=TERMINAL_CKM_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-CKM-S12-COMPLETE", SOURCE_ID, "sin_theta12 complete row", TERMINAL_CKM_LABEL),
        ExternalTargetRow("PDG-CKM-S23-COMPLETE", SOURCE_ID, "sin_theta23 complete row", TERMINAL_CKM_LABEL),
        ExternalTargetRow("PDG-CKM-S13-COMPLETE", SOURCE_ID, "sin_theta13 complete row", TERMINAL_CKM_LABEL),
        ExternalTargetRow("PDG-CKM-J-COMPLETE", SOURCE_ID, "Jarlskog complete row", TERMINAL_CKM_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Any sealed CKM interval misses its complete registered source interval, a row is omitted, the target enters the relation, or observational provenance is hidden.",
)


TERMINAL_BARYON_EMPIRICAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=TERMINAL_BARYON_PHOTON_ID,
    title="Terminal baryon-to-photon complete comparison",
    statement="The sealed exact eta = J-terminal-squared/2 prediction is compared independently with the complete PDG BBN abundance interval and the PDG Planck-density translation.",
    dependencies=empirical_dependencies(TERMINAL_BARYON_PHOTON_ID, TERMINAL_CKM_ID),
    generation_rule="Generate the complete eight-axis post-seal terminal baryon-abundance comparison product.",
    grammar_boundary="Both registered baryon-to-photon comparison routes, including complete strict BBN bounds and the Planck-derived central value and uncertainty.",
    dimensions=empirical_dimensions("sealed-terminal-eta-versus-two-independent-PDG-routes", "Both BBN abundance and Planck-density routes are retained without selecting the formal value."),
    exact_result="The target-free terminal eta prediction lies strictly inside the PDG BBN interval and overlaps the complete PDG Planck-derived interval.",
    induction_base="The direct BBN abundance interval is retained as the first independent comparison.",
    induction_step="The Planck-density translation and its complete uncertainty are appended without replacing or reweighting the BBN comparison.",
    exclusions=("no baryon abundance in the executable relation", "no free efficiency", "no fitted normalization", "no omitted comparison route", "no blind-forward-discovery claim"),
    operational_witnesses=(("half-One-transport", "The sealed target-free relation retains exactly one half of terminal J squared.", terminal_eta_prediction_interval()[0] > Fraction(1, 10 ** 12)),),
    experiment_id="SFT-EXP-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",
    expected_observation_label=TERMINAL_ETA_LABEL,
    target_rows=(
        ExternalTargetRow("PDG-BBN-ETA-COMPLETE", SOURCE_ID, "BBN strict abundance interval", TERMINAL_ETA_LABEL),
        ExternalTargetRow("PDG-PLANCK-ETA-COMPLETE", SOURCE_ID, "Planck-derived value and uncertainty", TERMINAL_ETA_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="The sealed eta prediction leaves either complete registered interval, a route is omitted, or a measured abundance enters the law.",
)


EMPIRICAL_SPEC_BY_ID = {
    TERMINAL_CKM_ID: TERMINAL_CKM_EMPIRICAL_SPEC,
    TERMINAL_BARYON_PHOTON_ID: TERMINAL_BARYON_EMPIRICAL_SPEC,
}


class TerminalRecordValidator:
    def __init__(self, root: Path, spec: EmpiricalPhysicsSpec):
        self.root = root.resolve()
        self.spec = spec

    def validate(self, sealed):
        # This call creates and seals the target-inaccessible prediction before
        # the target vault is released.  Exact numerical recomputation follows.
        validation = BlindExternalMeasurementValidator(self.root, self.spec).validate(sealed)
        observed = {
            TERMINAL_CKM_ID: terminal_ckm_classification,
            TERMINAL_BARYON_PHOTON_ID: terminal_eta_classification,
        }[self.spec.claim_id](self.root)
        if observed != self.spec.expected_observation_label or not validation.passed:
            raise ValueError("terminal matter/flavour authoritative classification changed")
        return validation


VALIDATOR_BY_ID = {
    claim_id: (lambda root, item=spec: TerminalRecordValidator(root, item))
    for claim_id, spec in EMPIRICAL_SPEC_BY_ID.items()
}

for _spec in EMPIRICAL_SPEC_BY_ID.values():
    _spec.validate()


__all__ = (
    "EMPIRICAL_SPEC_BY_ID",
    "SOURCE_HASH",
    "SOURCE_PATH",
    "TERMINAL_CKM_LABEL",
    "TERMINAL_ETA_LABEL",
    "VALIDATOR_BY_ID",
    "authoritative_record",
    "terminal_ckm_classification",
    "terminal_ckm_prediction_intervals",
    "terminal_eta_classification",
    "terminal_eta_prediction_interval",
)
