"""Post-seal authoritative checks of terminal Physics precision laws.

The formal claims are immutable before this module opens the registered source
snapshots.  Every comparison uses exact rational interval arithmetic.  The
electroweak record deliberately retains the current PDG all-input W-mass
tension as well as the favorable on-shell and compatible-input comparisons.
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
from sft.physics.measured_value import exact_decimal
from sft.physics.precision_value_laws_v1 import (
    ELECTROWEAK_TERMINAL_ID,
    PROTON_PLANCK_TERMINAL_ID,
    terminal_electroweak_cos_squared,
    terminal_electroweak_sin_squared,
    terminal_proton_planck_squared_ratio,
)


ELECTROWEAK_VALIDATION_ID = "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003"
HIERARCHY_VALIDATION_ID = "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003"

PDG_RECORD_PATH = "experiments/external_sources/physics/snapshots/pdg-electroweak-precision-source-record.json"
PDG_RECORD_HASH = "sha256:1eb3111d343f411a1788120d394899c03ea75279bbea68a0c8284a58f6af89bd"
NIST_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
NIST_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"

PDG_LABEL = "on-shell-pass__compatible-w-mass-pass__all-input-w-mass-tension-retained"
HIERARCHY_LABEL = "terminal-squared-hierarchy-inside-complete-codata-mass-interval"


def interval(central: str, uncertainty: str) -> tuple[Fraction, Fraction]:
    middle = exact_decimal(central)
    width = exact_decimal(uncertainty)
    if middle <= width or width <= 0:
        raise ValueError("source interval must remain strictly positive")
    return middle - width, middle + width


def intervals_overlap(first: tuple[Fraction, Fraction], second: tuple[Fraction, Fraction]) -> bool:
    return first[0] <= second[1] and second[0] <= first[1]


def squared_ratio_interval(
    numerator: tuple[Fraction, Fraction],
    denominator: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    if numerator[0] <= 0 or denominator[0] <= 0:
        raise ValueError("squared ratio requires positive source intervals")
    return (numerator[0] / denominator[1]) ** 2, (numerator[1] / denominator[0]) ** 2


def pdg_rows(root: Path) -> dict[str, tuple[Fraction, Fraction]]:
    path = root / PDG_RECORD_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("record_id") != "PDG-ELECTROWEAK-PRECISION-2024-2025":
        raise ValueError("PDG precision record identity changed")
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 2:
        raise ValueError("PDG precision record must retain both source documents")
    expected_hashes = {
        "pdg-2025-electroweak-model.pdf": "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a",
        "pdg-2024-w-boson-listing.pdf": "sha256:91cb466bfea8fa49b53ae53d2168797189c14a5a114f30d7cc926f64c4c1e772",
    }
    rows: dict[str, tuple[Fraction, Fraction]] = {}
    for source in sources:
        snapshot = source["snapshot"]
        expected = expected_hashes.get(snapshot)
        if expected is None or hash_file(path.parent / snapshot) != expected:
            raise ValueError("PDG source snapshot differs from its registered identity")
        for row in source["rows"]:
            rows[row["quantity"]] = interval(row["central"], row["standard_uncertainty"])
    required = {
        "on-shell sin-squared theta-W",
        "Z mass",
        "W mass, world average using all measurements through 2023",
        "W mass, PDG evaluation excluding the incompatible CDF 2022 input",
    }
    if set(rows) != required:
        raise ValueError("PDG precision rows are missing or additional")
    return rows


def electroweak_comparison(root: Path) -> dict[str, object]:
    rows = pdg_rows(root)
    weak = terminal_electroweak_sin_squared()
    weak_interval = rows["on-shell sin-squared theta-W"]
    z_interval = rows["Z mass"]
    all_wz = squared_ratio_interval(rows["W mass, world average using all measurements through 2023"], z_interval)
    compatible_wz = squared_ratio_interval(rows["W mass, PDG evaluation excluding the incompatible CDF 2022 input"], z_interval)
    cos_value = terminal_electroweak_cos_squared()
    outcomes = {
        "on_shell_weak_share_inside": weak_interval[0] <= weak <= weak_interval[1],
        "compatible_input_wz_inside": compatible_wz[0] <= cos_value <= compatible_wz[1],
        "all_input_wz_inside": all_wz[0] <= cos_value <= all_wz[1],
    }
    classification = (
        PDG_LABEL
        if outcomes == {
            "on_shell_weak_share_inside": True,
            "compatible_input_wz_inside": True,
            "all_input_wz_inside": False,
        }
        else "electroweak-comparison-classification-changed"
    )
    return {
        "prediction_sin_squared": str(weak),
        "prediction_cos_squared": str(cos_value),
        "on_shell_interval": tuple(str(value) for value in weak_interval),
        "compatible_wz_interval": tuple(str(value) for value in compatible_wz),
        "all_input_wz_interval": tuple(str(value) for value in all_wz),
        "outcomes": outcomes,
        "classification": classification,
    }


def codata_row(path: Path, quantity: str) -> tuple[Fraction, Fraction]:
    matches = tuple(
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if len(line) >= 110 and line[:60].strip() == quantity
    )
    if len(matches) != 1:
        raise ValueError(f"CODATA row must occur exactly once: {quantity}")
    return interval(matches[0][60:85].strip(), matches[0][85:110].strip())


def codata_hierarchy_interval(root: Path) -> tuple[Fraction, Fraction]:
    source = root / NIST_PATH
    planck = codata_row(source, "Planck mass")
    proton = codata_row(source, "proton mass")
    return squared_ratio_interval(planck, proton)


_root = Path(__file__).resolve().parents[2]
_ew = electroweak_comparison(_root)
_hierarchy_interval = codata_hierarchy_interval(_root)


ELECTROWEAK_SPEC = EmpiricalPhysicsSpec(
    claim_id=ELECTROWEAK_VALIDATION_ID,
    title="Blind PDG test of the terminal electroweak Fold share",
    statement=(
        "After the exact terminal weak share is sealed, it is compared with the PDG on-shell weak angle and "
        "with squared W/Z mass intervals from both the all-input world average and PDG's separately published "
        "compatible-input evaluation. The resulting pass/pass/tension vector is retained whole."
    ),
    dependencies=(
        ELECTROWEAK_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal relation, source provenance, custody, exact interval, complete-row, successor and no-extra-rule product.",
    grammar_boundary="All exact post-seal comparisons of the immutable terminal sin-squared and cos-squared shares with every registered PDG weak-angle and W/Z mass interval, including the unfavorable all-input result.",
    dimensions=empirical_dimensions("sealed-terminal-share-versus-complete-pdg-vector", "All four source rows are propagated exactly and the complete pass/pass/tension classification is the measured result."),
    exact_result="The sealed terminal share must lie inside the PDG on-shell interval and compatible-input W/Z interval while the all-input W/Z tension is retained, not silently discarded.",
    induction_base="The first registered source row retains its exact central value, stated uncertainty, source identity and immutable prediction.",
    induction_step="Every additional PDG row is appended and classified without deleting, widening or reweighting earlier rows.",
    exclusions=("no PDG value accessible before the formal seal", "no fitted digit or uncertainty widening", "no deletion of the unfavorable all-input row", "no floating-point interval decision"),
    operational_witnesses=(
        ("on-shell-pass", "The sealed sin-squared share lies inside the exact PDG on-shell interval.", _ew["outcomes"]["on_shell_weak_share_inside"] is True),
        ("compatible-wz-pass", "The sealed complement lies inside the compatible-input W/Z squared interval.", _ew["outcomes"]["compatible_input_wz_inside"] is True),
        ("all-input-tension-retained", "The all-input W/Z squared interval is disjoint and remains explicit.", _ew["outcomes"]["all_input_wz_inside"] is False),
        ("complete-classification", "The exact three-way classification is stable.", _ew["classification"] == PDG_LABEL),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
    expected_observation_label=PDG_LABEL,
    target_rows=(ExternalTargetRow("PDG-ELECTROWEAK-COMPLETE-VECTOR", "PDG-ELECTROWEAK-PRECISION-2024-2025", "all four registered rows in both hashed PDG documents", PDG_LABEL),),
    source_snapshot_path=PDG_RECORD_PATH,
    source_snapshot_hash=PDG_RECORD_HASH,
    falsification_condition="The sealed weak share leaves the on-shell interval, leaves the compatible-input W/Z interval, enters the presently disjoint all-input interval without a source revision, any registered row/hash changes, or an unfavorable row is omitted.",
)


HIERARCHY_SPEC = EmpiricalPhysicsSpec(
    claim_id=HIERARCHY_VALIDATION_ID,
    title="Blind CODATA test of the terminal proton-to-Planck hierarchy",
    statement=(
        "After the exact terminal squared hierarchy is sealed, the complete CODATA 2022 Planck-mass and "
        "proton-mass intervals are propagated outward through an exact positive squared ratio and tested "
        "without forming an irrational root."
    ),
    dependencies=(
        PROTON_PLANCK_TERMINAL_ID,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal relation, source provenance, custody, exact interval, complete-row, successor and no-extra-rule product.",
    grammar_boundary="All exact post-seal outward interval propagation from the complete registered CODATA Planck-mass and proton-mass rows to the immutable squared hierarchy.",
    dimensions=empirical_dimensions("sealed-terminal-hierarchy-versus-complete-codata-mass-interval", "Both source uncertainties are propagated monotonically through the squared positive ratio before interval membership is decided."),
    exact_result="The sealed terminal squared hierarchy lies inside the complete outward-propagated CODATA 2022 Planck/proton mass interval.",
    induction_base="The two source masses retain exact printed central values, uncertainties, units and source identity.",
    induction_step="Any future authoritative revision is a new registered snapshot and comparison; it cannot rewrite this sealed result or remove the earlier row.",
    exclusions=("no CODATA value accessible before the formal seal", "no fitted hierarchy exponent or correction", "no floating-point comparison", "no omitted source uncertainty", "no irrational square-root proof value"),
    operational_witnesses=(
        ("exact-outward-interval", "The terminal exact squared hierarchy lies inside both propagated endpoints.", _hierarchy_interval[0] <= terminal_proton_planck_squared_ratio() <= _hierarchy_interval[1]),
        ("both-source-rows", "Both complete CODATA source rows contribute to the interval.", True),
        ("squared-domain", "No irrational mass-ratio root is formed.", True),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003",
    expected_observation_label=HIERARCHY_LABEL,
    target_rows=(ExternalTargetRow("NIST-CODATA-2022-PLANCK-PROTON-HIERARCHY", "NIST-CODATA-2022-ALL-CONSTANTS", "complete Planck mass and proton mass fixed-width rows", HIERARCHY_LABEL),),
    source_snapshot_path=NIST_PATH,
    source_snapshot_hash=NIST_HASH,
    falsification_condition="The sealed squared hierarchy lies outside the complete propagated CODATA interval, either source row or hash changes, an uncertainty is omitted, or a tampered comparison is accepted.",
)


class ElectroweakExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        if electroweak_comparison(self.root)["classification"] != PDG_LABEL:
            raise ValueError("sealed electroweak result differs from the complete PDG classification")
        return BlindExternalMeasurementValidator(self.root, ELECTROWEAK_SPEC).validate(sealed)


class HierarchyExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        source_interval = codata_hierarchy_interval(self.root)
        if not source_interval[0] <= terminal_proton_planck_squared_ratio() <= source_interval[1]:
            raise ValueError("sealed terminal hierarchy is outside the complete CODATA interval")
        return BlindExternalMeasurementValidator(self.root, HIERARCHY_SPEC).validate(sealed)


VALIDATION_SPECS = (ELECTROWEAK_SPEC, HIERARCHY_SPEC)
VALIDATOR_BY_ID = {
    ELECTROWEAK_VALIDATION_ID: ElectroweakExternalValidator,
    HIERARCHY_VALIDATION_ID: HierarchyExternalValidator,
}

for _spec in VALIDATION_SPECS:
    _spec.validate()


__all__ = (
    "VALIDATION_SPECS",
    "VALIDATOR_BY_ID",
    "electroweak_comparison",
    "codata_hierarchy_interval",
)
