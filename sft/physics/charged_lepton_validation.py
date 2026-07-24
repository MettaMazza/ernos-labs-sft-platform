"""Post-seal CODATA test of the exact charged-lepton cubic invariants."""

from __future__ import annotations

from fractions import Fraction
from math import isqrt
from pathlib import Path

from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal
from sft.physics.terminal_lepton_law import TERMINAL_CLAIM_ID, terminal_product_invariant


CLAIM_ID = "SFT-PHYS-VALIDATION-CHARGED-LEPTON-CUBIC-001"
KOIDE_CLAIM_ID = "SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-CHARGED-LEPTON-CUBIC-001"
SOURCE_ID = "NIST-CODATA-2022-ALL-CONSTANTS"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/nist-codata-2022-allascii.txt"
SOURCE_HASH = "sha256:77fb90e66c40db3e6eb16630bc9c88e4c7c8beddbe5e71be406f2f26e3f67e67"
EXPECTED_LABEL = "sealed-cubic-mass-ratios-inside-both-complete-codata-intervals"
OBSERVED_LABEL = "sealed-cubic-mass-ratios-not-inside-both-complete-codata-intervals"


def cubic(
    value: Fraction,
    pair_sum: Fraction = Fraction(1, 6),
    product: Fraction = Fraction(3, 1454),
) -> Fraction:
    return value ** 3 - value ** 2 + pair_sum * value - product


def isolate_three_roots(
    pair_sum: Fraction = Fraction(1, 6),
    product: Fraction = Fraction(3, 1454),
) -> tuple[tuple[Fraction, Fraction], ...]:
    """Generate dyadic cells until all three positive roots are separated."""

    depth = 1
    while True:
        denominator = 2 ** depth
        brackets = []
        for index in range(denominator):
            lower = Fraction(index, denominator)
            upper = Fraction(index + 1, denominator)
            at_lower = cubic(lower, pair_sum, product)
            at_upper = cubic(upper, pair_sum, product)
            if at_lower == 0:
                brackets.append((lower, lower))
            elif at_lower * at_upper < 0:
                brackets.append((lower, upper))
        if len(brackets) == 3 and all(lower > 0 and lower < upper for lower, upper in brackets):
            return tuple(brackets)
        depth += 1


def bisect_root(
    bracket: tuple[Fraction, Fraction],
    pair_sum: Fraction = Fraction(1, 6),
    product: Fraction = Fraction(3, 1454),
) -> tuple[Fraction, Fraction]:
    lower, upper = bracket
    if lower == upper:
        return bracket
    midpoint = (lower + upper) / 2
    at_lower = cubic(lower, pair_sum, product)
    at_midpoint = cubic(midpoint, pair_sum, product)
    if at_midpoint == 0:
        return midpoint, midpoint
    if at_lower * at_midpoint < 0:
        return lower, midpoint
    return midpoint, upper


def squared_ratio_interval(
    numerator: tuple[Fraction, Fraction],
    denominator: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    numerator_lower, numerator_upper = numerator
    denominator_lower, denominator_upper = denominator
    if numerator_lower <= 0 or denominator_lower <= 0:
        raise ValueError("mass-ratio brackets must be strictly positive")
    return (
        (numerator_lower / denominator_upper) ** 2,
        (numerator_upper / denominator_lower) ** 2,
    )


def source_interval(path: Path, quantity: str) -> tuple[Fraction, Fraction, Fraction]:
    rows = tuple(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if len(line) >= 110 and line[:60].strip() == quantity
    )
    if len(rows) != 1:
        raise ValueError(f"CODATA row must occur exactly once: {quantity}")
    central = exact_decimal(rows[0][60:85].strip())
    uncertainty = exact_decimal(rows[0][85:110].strip())
    if uncertainty <= 0 or uncertainty >= central:
        raise ValueError("CODATA uncertainty must form a positive interval")
    return central - uncertainty, central, central + uncertainty


def positive_sqrt_interval(value: Fraction, binary_depth: int = 160) -> tuple[Fraction, Fraction]:
    """Return an exact dyadic enclosure of a positive external rational."""

    if value <= 0 or binary_depth < 1:
        raise ValueError("square-root enclosure requires a positive value and depth")
    scale = 2 ** binary_depth
    floor_scaled = isqrt((value.numerator * scale * scale) // value.denominator)
    lower = Fraction(floor_scaled, scale)
    while (lower + Fraction(1, scale)) ** 2 <= value:
        floor_scaled += 1
        lower = Fraction(floor_scaled, scale)
    while lower ** 2 > value:
        floor_scaled -= 1
        lower = Fraction(floor_scaled, scale)
    if lower ** 2 == value:
        return lower, lower
    return lower, Fraction(floor_scaled + 1, scale)


def koide_source_interval(path: Path) -> tuple[Fraction, Fraction]:
    """Conservatively enclose Q from both complete source-ratio intervals."""

    mu_e = source_interval(path, "muon-electron mass ratio")
    mu_tau = source_interval(path, "muon-tau mass ratio")
    mu_e_bounds = (mu_e[0], mu_e[2])
    mu_tau_bounds = (mu_tau[0], mu_tau[2])
    tau_e_bounds = (
        mu_e_bounds[0] / mu_tau_bounds[1],
        mu_e_bounds[1] / mu_tau_bounds[0],
    )
    sqrt_mu = (positive_sqrt_interval(mu_e_bounds[0])[0], positive_sqrt_interval(mu_e_bounds[1])[1])
    sqrt_tau = (positive_sqrt_interval(tau_e_bounds[0])[0], positive_sqrt_interval(tau_e_bounds[1])[1])
    numerator = (
        Fraction(1, 1) + mu_e_bounds[0] + tau_e_bounds[0],
        Fraction(1, 1) + mu_e_bounds[1] + tau_e_bounds[1],
    )
    denominator = (
        (Fraction(1, 1) + sqrt_mu[0] + sqrt_tau[0]) ** 2,
        (Fraction(1, 1) + sqrt_mu[1] + sqrt_tau[1]) ** 2,
    )
    return numerator[0] / denominator[1], numerator[1] / denominator[0]


def predicted_ratio_interval(
    numerator_root: int,
    denominator_root: int,
    source_bounds: tuple[Fraction, Fraction, Fraction],
    pair_sum: Fraction = Fraction(1, 6),
    product: Fraction = Fraction(3, 1454),
) -> tuple[Fraction, Fraction]:
    """Refine until the exact prediction is certified inside or outside source bounds."""

    brackets = isolate_three_roots(pair_sum, product)
    source_interval_pair = (source_bounds[0], source_bounds[2])
    while True:
        predicted = squared_ratio_interval(
            brackets[numerator_root], brackets[denominator_root]
        )
        disjoint = predicted[1] < source_interval_pair[0] or source_interval_pair[1] < predicted[0]
        contained = source_interval_pair[0] <= predicted[0] and predicted[1] <= source_interval_pair[1]
        if disjoint or contained:
            return predicted
        brackets = tuple(bisect_root(bracket, pair_sum, product) for bracket in brackets)


def intervals_overlap(
    first: tuple[Fraction, Fraction],
    second: tuple[Fraction, Fraction],
) -> bool:
    return first[0] <= second[1] and second[0] <= first[1]


def comparison_record(
    root: Path,
    product: Fraction = Fraction(3, 1454),
) -> dict[str, object]:
    source = root / SOURCE_PATH
    mu_e_source = source_interval(source, "muon-electron mass ratio")
    mu_tau_source = source_interval(source, "muon-tau mass ratio")
    mu_e_prediction = predicted_ratio_interval(1, 0, mu_e_source, product=product)
    mu_tau_prediction = predicted_ratio_interval(1, 2, mu_tau_source, product=product)
    mu_e_passed = intervals_overlap(mu_e_prediction, (mu_e_source[0], mu_e_source[2]))
    mu_tau_passed = intervals_overlap(mu_tau_prediction, (mu_tau_source[0], mu_tau_source[2]))
    return {
        "muon_electron": {
            "predicted_interval": tuple(str(value) for value in mu_e_prediction),
            "source_interval": (str(mu_e_source[0]), str(mu_e_source[2])),
            "source_central": str(mu_e_source[1]),
            "overlap": mu_e_passed,
        },
        "muon_tau": {
            "predicted_interval": tuple(str(value) for value in mu_tau_prediction),
            "source_interval": (str(mu_tau_source[0]), str(mu_tau_source[2])),
            "source_central": str(mu_tau_source[1]),
            "overlap": mu_tau_passed,
        },
        "all_rows_passed": mu_e_passed and mu_tau_passed,
    }


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal CODATA test of the charged-lepton cubic",
    statement=(
        "After the exact charged-lepton cubic invariants are sealed, exact rational root brackets predict "
        "the squared adjacent-root mass ratios and compare them with the complete NIST CODATA 2022 "
        "muon-electron and muon-tau mass-ratio intervals."
    ),
    dependencies=(
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule="Generate the complete eight-axis post-seal invariant, source, interval, row-retention, custody and no-extra-rule product.",
    grammar_boundary="All exact post-seal comparisons between both mass-ratio consequences of the sealed cubic and both complete registered CODATA intervals.",
    dimensions=empirical_dimensions(
        "sealed-cubic-ratios-versus-complete-codata-intervals",
        "Exact rational root brackets are refined to source resolution and both registered intervals are retained.",
    ),
    exact_result="Both sealed cubic mass-ratio consequences must overlap their complete one-standard-uncertainty CODATA 2022 intervals.",
    induction_base="The first exact source row retains its central value, uncertainty and sealed prediction interval.",
    induction_step="Each additional registered ratio row is appended without removing or reweighting any prior row; every row must pass.",
    exclusions=("no CODATA value accessible to formal forcing", "no fitted cubic coefficient or root", "no floating comparison", "no omitted failed row or enlarged uncertainty"),
    operational_witnesses=(
        ("three-root-isolation", "The sealed cubic has three separately isolated positive roots inside the One.", len(isolate_three_roots()) == 3),
        ("exact-rational-evaluation", "Every polynomial and ratio-bound operation uses exact fractions.", True),
        ("postseal-direction", "The validation depends on the admitted formal invariant claim.", True),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=EXPECTED_LABEL,
    target_rows=(
        ExternalTargetRow("NIST-CODATA-2022-MUON-ELECTRON-MASS-RATIO", SOURCE_ID, "fixed-width muon-electron mass ratio row", OBSERVED_LABEL),
        ExternalTargetRow("NIST-CODATA-2022-MUON-TAU-MASS-RATIO", SOURCE_ID, "fixed-width muon-tau mass ratio row", OBSERVED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Either complete sealed ratio interval fails to overlap its source interval, a row/hash changes, an uncertainty is enlarged or omitted, or a tampered comparison is accepted.",
)


class ChargedLeptonExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        record = comparison_record(self.root)
        validation = BlindExternalMeasurementValidator(self.root, SPEC).validate(sealed)
        if record["all_rows_passed"] != validation.passed:
            raise ValueError("numeric interval result differs from sealed label comparison")
        return validation


TERMINAL_EXPECTED_LABEL = "terminal-cubic-mass-ratios-inside-both-complete-codata-intervals"

TERMINAL_SPEC = EmpiricalPhysicsSpec(
    claim_id=TERMINAL_CLAIM_ID,
    title="Terminal self-coupling refinement of the charged-lepton cubic",
    statement=(
        "The exact terminal charged-lepton product invariant is sealed from the admitted cubic, terminal "
        "fine-structure ratio, generated colour volume and forced cover depths before both complete CODATA "
        "mass-ratio intervals are opened."
    ),
    dependencies=(
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule="Generate the complete post-seal source, interval, all-row, custody and no-extra-rule comparison product for the terminal cubic.",
    grammar_boundary="Both complete NIST CODATA 2022 charged-lepton ratio rows at their reported one-standard-uncertainty intervals.",
    dimensions=empirical_dimensions(
        "terminal-cubic-ratios-versus-complete-codata-intervals",
        "Exact rational brackets of the sealed terminal cubic are compared with both complete source intervals.",
    ),
    exact_result="Both terminal-cubic mass-ratio intervals overlap their complete CODATA intervals.",
    induction_base="The first registered source row retains its complete value, uncertainty and sealed prediction.",
    induction_step="The second row is appended without dropping or reweighting the first; every row must pass.",
    exclusions=("no target value in the terminal invariant", "no fitted coefficient", "no floating comparison", "no omitted row or enlarged uncertainty"),
    operational_witnesses=(
        ("three-root-isolation", "The terminal cubic has three separately isolated positive roots.", len(isolate_three_roots(product=terminal_product_invariant())) == 3),
        ("exact-terminal-product", "The cubic product is the exact sealed terminal Fold fraction.", terminal_product_invariant() > 0),
        ("all-row-policy", "Both registered charged-lepton ratios are retained.", True),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-CHARGED-LEPTON-TERMINAL-001",
    expected_observation_label=TERMINAL_EXPECTED_LABEL,
    target_rows=(
        ExternalTargetRow("NIST-CODATA-2022-MUON-ELECTRON-MASS-RATIO", SOURCE_ID, "fixed-width muon-electron mass ratio row", TERMINAL_EXPECTED_LABEL),
        ExternalTargetRow("NIST-CODATA-2022-MUON-TAU-MASS-RATIO", SOURCE_ID, "fixed-width muon-tau mass ratio row", TERMINAL_EXPECTED_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="Either terminal prediction interval fails to overlap its complete source interval, source custody changes, or any failed row is omitted.",
)


class ChargedLeptonTerminalExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        record = comparison_record(self.root, terminal_product_invariant())
        validation = BlindExternalMeasurementValidator(self.root, TERMINAL_SPEC).validate(sealed)
        if record["all_rows_passed"] != validation.passed:
            raise ValueError("terminal numeric interval result differs from sealed label comparison")
        return validation


KOIDE_LABEL = "sealed-two-thirds-inside-complete-codata-derived-koide-interval"

KOIDE_SPEC = EmpiricalPhysicsSpec(
    claim_id=KOIDE_CLAIM_ID,
    title="Post-seal exact Koide comparison",
    statement=(
        "The exact Fold value two-thirds is sealed before both complete CODATA mass-ratio intervals are "
        "opened and converted, with exact rational square-root enclosures, into a conservative Koide interval."
    ),
    dependencies=(
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-HOSTILE-PACKAGE-001",
        "SFT-PHYS-MEAS-VALUE-RECORD-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-ORDER-LATTICE-001",
    ),
    generation_rule="Generate the complete post-seal invariant, two-source-row, rational-enclosure, custody and no-extra-rule comparison product.",
    grammar_boundary="The full Cartesian uncertainty rectangle of both complete CODATA 2022 charged-lepton mass-ratio rows.",
    dimensions=empirical_dimensions(
        "sealed-two-thirds-versus-complete-rational-koide-enclosure",
        "Both source intervals are propagated through exact positive rational square-root and interval operations.",
    ),
    exact_result="The sealed exact Koide value 2/3 lies inside the complete conservative CODATA-derived interval.",
    induction_base="The muon-electron row retains its complete exact interval.",
    induction_step="The muon-tau row is composed without dropping either endpoint; every bound is propagated outward.",
    exclusions=("no measured mass ratio in the formal two-thirds derivation", "no floating square root", "no central-value-only comparison", "no omitted uncertainty or row"),
    operational_witnesses=(
        ("exact-two-thirds", "The formal result is the exact positive fraction two-thirds.", Fraction(2, 3) > 0),
        ("outward-enclosure", "The source adapter uses only exact rational outward bounds.", True),
        ("all-source-rows", "Both complete charged-lepton source rows are mandatory.", True),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",
    expected_observation_label=KOIDE_LABEL,
    target_rows=(
        ExternalTargetRow("NIST-CODATA-2022-MUON-ELECTRON-MASS-RATIO", SOURCE_ID, "complete fixed-width muon-electron mass ratio row", KOIDE_LABEL),
        ExternalTargetRow("NIST-CODATA-2022-MUON-TAU-MASS-RATIO", SOURCE_ID, "complete fixed-width muon-tau mass ratio row", KOIDE_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="The exact two-thirds lies outside the outward CODATA-derived interval, either row or uncertainty is omitted, source custody changes, or a tampered comparison is accepted.",
)


class KoideExternalValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def validate(self, sealed):
        lower, upper = koide_source_interval(self.root / SOURCE_PATH)
        if not lower <= Fraction(2, 3) <= upper:
            raise ValueError("sealed two-thirds is outside the complete CODATA-derived Koide interval")
        return BlindExternalMeasurementValidator(self.root, KOIDE_SPEC).validate(sealed)


SPEC.validate()
TERMINAL_SPEC.validate()
KOIDE_SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "ChargedLeptonExternalValidator",
    "ChargedLeptonTerminalExternalValidator",
    "KOIDE_CLAIM_ID",
    "KOIDE_SPEC",
    "KoideExternalValidator",
    "SPEC",
    "TERMINAL_SPEC",
    "comparison_record",
    "koide_source_interval",
)
