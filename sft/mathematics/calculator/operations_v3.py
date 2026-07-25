"""Expanded exact scientific operation surface for calculator claim 005."""

from __future__ import annotations

from fractions import Fraction

from .operations import *  # noqa: F401,F403 - preserved admitted exact kernels
from .operations import (
    absolute,
    add,
    as_interval,
    cos_enclosure,
    divide,
    exp_enclosure,
    ln_enclosure,
    multiply,
    negate,
    nth_root,
    reciprocal,
    require_scalar,
    sin_enclosure,
    subtract,
    whole_power,
)
from .operations_v2 import circle_constant_enclosure
from .values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    Scalar,
    Value,
    add_scalar,
    compare_scalar,
    counter,
    forward,
    scalar_from_projection,
    scalar_to_fraction_for_projection,
)


def _whole_gcd(left: int, right: int) -> int:
    """Finite exact remainder descent on positive whole host counters."""

    a, b = abs(left), abs(right)
    while b:
        a, b = b, a % b
    return a


def _ordered_interval(lower: Scalar, upper: Scalar, certificate: tuple[str, ...]) -> CertifiedInterval:
    return CertifiedInterval(lower, upper, certificate)


def _interval_hull(*intervals: CertifiedInterval, certificate: str) -> CertifiedInterval:
    lowers = tuple(item.lower for item in intervals)
    uppers = tuple(item.upper for item in intervals)
    lower = min(lowers, key=scalar_to_fraction_for_projection)
    upper = max(uppers, key=scalar_to_fraction_for_projection)
    trace = tuple(part for item in intervals for part in item.certificate) + (certificate,)
    return CertifiedInterval(lower, upper, trace)


def rational_power(base: Value, exponent: Value, places: int = 18) -> Value:
    """Exact rational exponent as counted root then counted composition."""

    if isinstance(exponent, ComplexFibre):
        raise CalculatorHalt("orthogonal-fibre exponents are outside the declared scientific surface")
    if isinstance(exponent, CertifiedInterval) or isinstance(base, CertifiedInterval):
        base_interval = base if isinstance(base, CertifiedInterval) else as_interval(require_scalar(base))
        if compare_scalar(base_interval.lower, EMPTY_ONE) <= 0:
            raise CalculatorHalt("a non-rational exponent requires a strictly forward-held base enclosure")
        exponent_value: Value = exponent
        result = exp_value(multiply(exponent_value, ln_value(base_interval, places + 6)), places)
        return result
    power = require_scalar(exponent)
    if isinstance(power, EmptyOne):
        return forward(1)
    numerator = power.magnitude.numerator
    denominator = power.magnitude.denominator
    rooted = nth_root(base, denominator)
    result = whole_power(rooted, forward(numerator))
    return result if power.is_forward else reciprocal(result)


def root_value(value: Value, degree: int) -> Value:
    if not isinstance(value, CertifiedInterval):
        return nth_root(value, degree)
    if compare_scalar(value.lower, EMPTY_ONE) < 0:
        raise CalculatorHalt("an interval root must remain on one admitted nonnegative branch")
    lower_root = nth_root(value.lower, degree)
    upper_root = nth_root(value.upper, degree)
    if isinstance(lower_root, ComplexFibre) or isinstance(upper_root, ComplexFibre):
        raise CalculatorHalt("orthogonal interval roots are outside the declared surface")
    lower = lower_root.lower if isinstance(lower_root, CertifiedInterval) else lower_root
    upper = upper_root.upper if isinstance(upper_root, CertifiedInterval) else upper_root
    return CertifiedInterval(
        lower,
        upper,
        value.certificate
        + ((lower_root.certificate if isinstance(lower_root, CertifiedInterval) else ("exact-lower-root",)))
        + ((upper_root.certificate if isinstance(upper_root, CertifiedInterval) else ("exact-upper-root",)))
        + (f"monotone-root-degree:{degree}",),
    )


def exp_value(value: Value, places: int = 18) -> CertifiedInterval:
    if isinstance(value, CertifiedInterval):
        lower = exp_enclosure(value.lower, places)
        upper = exp_enclosure(value.upper, places)
        return CertifiedInterval(
            lower.lower,
            upper.upper,
            value.certificate + lower.certificate + upper.certificate + ("monotone-exp-interval",),
        )
    if isinstance(value, ComplexFibre):
        raise CalculatorHalt("complex exponential is outside the declared two-fibre scientific surface")
    return exp_enclosure(value, places)


def ln_value(value: Value, places: int = 18) -> CertifiedInterval:
    if isinstance(value, CertifiedInterval):
        if compare_scalar(value.lower, EMPTY_ONE) <= 0:
            raise CalculatorHalt("ln interval must remain strictly forward-held")
        lower = ln_enclosure(value.lower, places)
        upper = ln_enclosure(value.upper, places)
        return CertifiedInterval(
            lower.lower,
            upper.upper,
            value.certificate + lower.certificate + upper.certificate + ("monotone-ln-interval",),
        )
    if isinstance(value, ComplexFibre):
        raise CalculatorHalt("complex logarithm is outside the declared two-fibre scientific surface")
    return ln_enclosure(value, places)


def log_base(value: Value, base: Value, places: int = 18) -> CertifiedInterval:
    base_scalar = require_scalar(base)
    if isinstance(base_scalar, EmptyOne) or not base_scalar.is_forward or base_scalar.magnitude == 1:
        raise CalculatorHalt("logarithm base must be positive and distinct from One")
    result = divide(ln_value(value, places + 5), ln_value(base, places + 5))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("logarithm enclosure construction failed")
    return result


def _atan_small(value: Scalar, places: int, max_terms: int = 4096) -> CertifiedInterval:
    if isinstance(value, EmptyOne):
        return as_interval(EMPTY_ONE, "atan-empty-One")
    magnitude = value.magnitude
    if magnitude > Fraction(1, 2):
        raise CalculatorHalt("internal arctangent recurrence requires magnitude at most half-One")
    positive, held = Fraction(0), Fraction(0)
    tolerance = Fraction(1, 10 ** places)
    for index in range(max_terms):
        term = magnitude ** (2 * index + 1) / (2 * index + 1)
        if index % 2:
            held += term
        else:
            positive += term
        next_term = magnitude ** (2 * index + 3) / (2 * index + 3)
        if next_term <= tolerance:
            partial = positive - held
            count = index + 1
            if count % 2:
                lower, upper = partial - next_term, partial
            else:
                lower, upper = partial, partial + next_term
            interval = CertifiedInterval(
                forward(lower),
                forward(upper),
                (f"atan-small-terms:{count}", f"next-term-bound:{next_term}", "parity-checked:v3"),
            )
            return interval if value.is_forward else negate(interval)  # type: ignore[return-value]
    raise CalculatorHalt("arctangent certificate did not close inside the declared term bound")


def atan_value(value: Value, places: int = 18) -> CertifiedInterval:
    if isinstance(value, CertifiedInterval):
        left = atan_value(value.lower, places)
        right = atan_value(value.upper, places)
        return CertifiedInterval(
            left.lower,
            right.upper,
            value.certificate + left.certificate + right.certificate + ("monotone-atan-interval",),
        )
    scalar = require_scalar(value)
    if isinstance(scalar, EmptyOne):
        return as_interval(EMPTY_ONE, "atan-empty-One")
    if not scalar.is_forward:
        positive = atan_value(FoldScalar("forward-held", scalar.magnitude), places)
        return negate(positive)  # type: ignore[return-value]
    x = scalar.magnitude
    pi = circle_constant_enclosure(max(24, places + 8))
    if x <= Fraction(1, 2):
        return _atan_small(scalar, places)
    if x <= 1:
        transformed = FoldScalar("counter-held", (1 - x) / (1 + x)) if x < 1 else EMPTY_ONE
        result = add(divide(pi, forward(4)), _atan_small(transformed, places + 4))
    else:
        result = subtract(divide(pi, forward(2)), atan_value(forward(Fraction(1, 1) / x), places + 4))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("arctangent enclosure construction failed")
    return result


def asin_value(value: Value, places: int = 18) -> CertifiedInterval:
    scalar = require_scalar(value)
    if isinstance(scalar, EmptyOne):
        return as_interval(EMPTY_ONE, "asin-empty-One")
    if scalar.magnitude > 1:
        raise CalculatorHalt("asin requires a magnitude no greater than One")
    if scalar.magnitude == 1:
        half_pi = divide(circle_constant_enclosure(max(24, places + 8)), forward(2))
        return half_pi if scalar.is_forward else negate(half_pi)  # type: ignore[return-value]
    square = multiply(scalar, scalar)
    denominator = nth_root(subtract(forward(1), square), 2)
    return atan_value(divide(scalar, denominator), places)


def acos_value(value: Value, places: int = 18) -> CertifiedInterval:
    result = subtract(divide(circle_constant_enclosure(max(24, places + 8)), forward(2)), asin_value(value, places + 4))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("acos enclosure construction failed")
    return result


def _trig_interval(value: CertifiedInterval, cosine: bool, places: int) -> CertifiedInterval:
    lower_fraction = scalar_to_fraction_for_projection(value.lower)
    upper_fraction = scalar_to_fraction_for_projection(value.upper)
    midpoint = (lower_fraction + upper_fraction) / 2
    radius = (upper_fraction - lower_fraction) / 2
    centre = scalar_from_projection(midpoint)
    centre_interval = cos_enclosure(centre, places + 4) if cosine else sin_enclosure(centre, places + 4)
    lower = subtract(centre_interval.lower, forward(radius))
    upper = add(centre_interval.upper, forward(radius))
    if not isinstance(lower, (EmptyOne, FoldScalar)) or not isinstance(upper, (EmptyOne, FoldScalar)):
        raise CalculatorHalt("trigonometric interval expansion failed")
    return CertifiedInterval(
        lower,
        upper,
        value.certificate + centre_interval.certificate + ("unit-derivative-Lipschitz-enclosure",),
    )


def sin_value(value: Value, places: int = 18) -> CertifiedInterval:
    if isinstance(value, CertifiedInterval):
        return _trig_interval(value, False, places)
    return sin_enclosure(require_scalar(value), places)


def cos_value(value: Value, places: int = 18) -> CertifiedInterval:
    if isinstance(value, CertifiedInterval):
        return _trig_interval(value, True, places)
    return cos_enclosure(require_scalar(value), places)


def tan_value(value: Value, places: int = 18) -> CertifiedInterval:
    result = divide(sin_value(value, places + 4), cos_value(value, places + 4))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("tangent enclosure construction failed")
    return result


def to_radians(value: Value, mode: str) -> Value:
    if mode == "rad":
        return value
    if mode == "deg":
        return divide(multiply(value, circle_constant_enclosure()), forward(180))
    if mode == "grad":
        return divide(multiply(value, circle_constant_enclosure()), forward(200))
    raise CalculatorHalt("angle mode must be rad, deg or grad")


def from_radians(value: Value, mode: str) -> Value:
    if mode == "rad":
        return value
    if mode == "deg":
        return divide(multiply(value, forward(180)), circle_constant_enclosure())
    if mode == "grad":
        return divide(multiply(value, forward(200)), circle_constant_enclosure())
    raise CalculatorHalt("angle mode must be rad, deg or grad")


def sinh_value(value: Value, places: int = 18) -> CertifiedInterval:
    result = divide(subtract(exp_value(value, places + 4), exp_value(negate(value), places + 4)), forward(2))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("sinh enclosure construction failed")
    return result


def cosh_value(value: Value, places: int = 18) -> CertifiedInterval:
    result = divide(add(exp_value(value, places + 4), exp_value(negate(value), places + 4)), forward(2))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("cosh enclosure construction failed")
    return result


def tanh_value(value: Value, places: int = 18) -> CertifiedInterval:
    result = divide(sinh_value(value, places + 4), cosh_value(value, places + 4))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("tanh enclosure construction failed")
    return result


def asinh_value(value: Value, places: int = 18) -> CertifiedInterval:
    scalar = require_scalar(value)
    if isinstance(scalar, FoldScalar) and not scalar.is_forward:
        return negate(asinh_value(FoldScalar("forward-held", scalar.magnitude), places))  # type: ignore[return-value]
    result = ln_value(add(scalar, nth_root(add(multiply(scalar, scalar), forward(1)), 2)), places)
    return result


def acosh_value(value: Value, places: int = 18) -> CertifiedInterval:
    scalar = require_scalar(value)
    if isinstance(scalar, EmptyOne) or not scalar.is_forward or scalar.magnitude < 1:
        raise CalculatorHalt("acosh requires a forward-held magnitude at least One")
    return ln_value(add(scalar, nth_root(subtract(multiply(scalar, scalar), forward(1)), 2)), places)


def atanh_value(value: Value, places: int = 18) -> CertifiedInterval:
    scalar = require_scalar(value)
    if isinstance(scalar, FoldScalar) and scalar.magnitude >= 1:
        raise CalculatorHalt("atanh requires magnitude strictly below One")
    ratio = divide(add(forward(1), scalar), subtract(forward(1), scalar))
    result = divide(ln_value(ratio, places + 4), forward(2))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("atanh enclosure construction failed")
    return result


def exact_sum(values: tuple[Value, ...]) -> Value:
    if not values:
        raise CalculatorHalt("sum requires at least one generated value")
    result: Value = EMPTY_ONE
    for value in values:
        result = add(result, value)
    return result


def exact_product(values: tuple[Value, ...]) -> Value:
    if not values:
        raise CalculatorHalt("product requires at least one generated value")
    result: Value = forward(1)
    for value in values:
        result = multiply(result, value)
    return result


def arithmetic_mean(values: tuple[Value, ...]) -> Value:
    return divide(exact_sum(values), forward(len(values)))


def population_variance(values: tuple[Value, ...]) -> Value:
    centre = arithmetic_mean(values)
    squares = tuple(multiply(subtract(item, centre), subtract(item, centre)) for item in values)
    return divide(exact_sum(squares), forward(len(values)))


def population_stddev(values: tuple[Value, ...]) -> Value:
    return root_value(population_variance(values), 2)


def floor_value(value: Value) -> Scalar:
    if isinstance(value, CertifiedInterval):
        lower = floor_value(value.lower)
        upper = floor_value(value.upper)
        if compare_scalar(lower, upper) != 0:
            raise CalculatorHalt("floor is not unique across the certified interval")
        return lower
    scalar = require_scalar(value)
    projected = scalar_to_fraction_for_projection(scalar)
    return scalar_from_projection(projected.numerator // projected.denominator)


def ceil_value(value: Value) -> Scalar:
    if isinstance(value, CertifiedInterval):
        lower = ceil_value(value.lower)
        upper = ceil_value(value.upper)
        if compare_scalar(lower, upper) != 0:
            raise CalculatorHalt("ceiling is not unique across the certified interval")
        return lower
    scalar = require_scalar(value)
    projected = scalar_to_fraction_for_projection(scalar)
    quotient = -((-projected.numerator) // projected.denominator)
    return scalar_from_projection(quotient)


def gcd_value(left: Value, right: Value) -> Scalar:
    a = scalar_to_fraction_for_projection(require_scalar(left))
    b = scalar_to_fraction_for_projection(require_scalar(right))
    if a.denominator != 1 or b.denominator != 1:
        raise CalculatorHalt("gcd requires whole counted inputs")
    return forward(_whole_gcd(a.numerator, b.numerator))


def lcm_value(left: Value, right: Value) -> Scalar:
    a = scalar_to_fraction_for_projection(require_scalar(left))
    b = scalar_to_fraction_for_projection(require_scalar(right))
    if a.denominator != 1 or b.denominator != 1:
        raise CalculatorHalt("lcm requires whole counted inputs")
    if a.numerator == 0 or b.numerator == 0:
        return EMPTY_ONE
    return forward(abs(a.numerator * b.numerator) // _whole_gcd(a.numerator, b.numerator))


def modulo_value(left: Value, right: Value) -> Scalar:
    a = scalar_to_fraction_for_projection(require_scalar(left))
    b = scalar_to_fraction_for_projection(require_scalar(right))
    if a.denominator != 1 or b.denominator != 1 or b.numerator == 0:
        raise CalculatorHalt("mod requires whole counts and a non-empty divisor")
    return scalar_from_projection(Fraction(a.numerator % b.numerator))


def golden_ratio_enclosure() -> CertifiedInterval:
    result = divide(add(forward(1), nth_root(forward(5), 2)), forward(2))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("golden-ratio enclosure construction failed")
    return result
