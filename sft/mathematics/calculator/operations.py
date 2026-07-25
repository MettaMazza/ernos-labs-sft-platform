"""Generated exact operations and certified-enclosure operations."""

from __future__ import annotations

from fractions import Fraction

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
    divide_scalar,
    forward,
    multiply_scalar,
    reciprocal_scalar,
    reverse,
    scalar_from_projection,
    scalar_to_fraction_for_projection,
    subtract_scalar,
)


def as_interval(value: Scalar, reason: str = "exact-degenerate-enclosure") -> CertifiedInterval:
    return CertifiedInterval(value, value, (reason,))


def add(left: Value, right: Value) -> Value:
    if isinstance(left, ComplexFibre) or isinstance(right, ComplexFibre):
        a = left if isinstance(left, ComplexFibre) else ComplexFibre(require_scalar(left), EMPTY_ONE)
        b = right if isinstance(right, ComplexFibre) else ComplexFibre(require_scalar(right), EMPTY_ONE)
        return ComplexFibre(add_scalar(a.real, b.real), add_scalar(a.orthogonal, b.orthogonal))
    if isinstance(left, CertifiedInterval) or isinstance(right, CertifiedInterval):
        a = left if isinstance(left, CertifiedInterval) else as_interval(left)
        b = right if isinstance(right, CertifiedInterval) else as_interval(right)
        return CertifiedInterval(
            add_scalar(a.lower, b.lower),
            add_scalar(a.upper, b.upper),
            a.certificate + b.certificate + ("endpoint-addition",),
        )
    return add_scalar(left, right)


def subtract(left: Value, right: Value) -> Value:
    return add(left, negate(right))


def negate(value: Value) -> Value:
    if isinstance(value, ComplexFibre):
        return ComplexFibre(reverse(value.real), reverse(value.orthogonal))
    if isinstance(value, CertifiedInterval):
        return CertifiedInterval(reverse(value.upper), reverse(value.lower), value.certificate + ("held-orientation-reversal",))
    return reverse(value)


def multiply(left: Value, right: Value) -> Value:
    if isinstance(left, ComplexFibre) or isinstance(right, ComplexFibre):
        a = left if isinstance(left, ComplexFibre) else ComplexFibre(require_scalar(left), EMPTY_ONE)
        b = right if isinstance(right, ComplexFibre) else ComplexFibre(require_scalar(right), EMPTY_ONE)
        real = subtract_scalar(multiply_scalar(a.real, b.real), multiply_scalar(a.orthogonal, b.orthogonal))
        orthogonal = add_scalar(multiply_scalar(a.real, b.orthogonal), multiply_scalar(a.orthogonal, b.real))
        return ComplexFibre(real, orthogonal)
    if isinstance(left, CertifiedInterval) or isinstance(right, CertifiedInterval):
        a = left if isinstance(left, CertifiedInterval) else as_interval(left)
        b = right if isinstance(right, CertifiedInterval) else as_interval(right)
        products = tuple(
            multiply_scalar(x, y)
            for x in (a.lower, a.upper)
            for y in (b.lower, b.upper)
        )
        lower = min(products, key=scalar_to_fraction_for_projection)
        upper = max(products, key=scalar_to_fraction_for_projection)
        return CertifiedInterval(lower, upper, a.certificate + b.certificate + ("four-endpoint-product",))
    return multiply_scalar(left, right)


def reciprocal(value: Value) -> Value:
    if isinstance(value, ComplexFibre):
        denominator = add_scalar(multiply_scalar(value.real, value.real), multiply_scalar(value.orthogonal, value.orthogonal))
        return ComplexFibre(divide_scalar(value.real, denominator), divide_scalar(reverse(value.orthogonal), denominator))
    if isinstance(value, CertifiedInterval):
        if compare_scalar(value.lower, EMPTY_ONE) <= 0 <= compare_scalar(value.upper, EMPTY_ONE):
            raise CalculatorHalt("an interval crossing empty-One has no single reciprocal enclosure")
        return CertifiedInterval(
            reciprocal_scalar(value.upper),
            reciprocal_scalar(value.lower),
            value.certificate + ("reciprocal-endpoint-reversal",),
        )
    return reciprocal_scalar(value)


def divide(left: Value, right: Value) -> Value:
    return multiply(left, reciprocal(right))


def absolute(value: Value) -> Value:
    if isinstance(value, ComplexFibre):
        squared = add_scalar(multiply_scalar(value.real, value.real), multiply_scalar(value.orthogonal, value.orthogonal))
        return nth_root(squared, 2)
    if isinstance(value, CertifiedInterval):
        if compare_scalar(value.lower, EMPTY_ONE) <= 0 <= compare_scalar(value.upper, EMPTY_ONE):
            far = max((reverse(value.lower), value.upper), key=scalar_to_fraction_for_projection)
            return CertifiedInterval(EMPTY_ONE, far, value.certificate + ("absolute-enclosure",))
        if compare_scalar(value.upper, EMPTY_ONE) < 0:
            return negate(value)
        return value
    return reverse(value) if isinstance(value, FoldScalar) and not value.is_forward else value


def require_scalar(value: Value) -> Scalar:
    if isinstance(value, (CertifiedInterval, ComplexFibre)):
        raise CalculatorHalt("operation requires one exact Fold scalar")
    return value


def require_whole(value: Value, *, allow_empty: bool = True) -> int:
    scalar = require_scalar(value)
    if isinstance(scalar, EmptyOne):
        if allow_empty:
            return 0
        raise CalculatorHalt("operation requires a positive whole count")
    if not scalar.is_forward or scalar.magnitude.denominator != 1:
        raise CalculatorHalt("operation requires a forward-held whole count")
    return scalar.magnitude.numerator


def whole_power(base: Value, exponent: Value) -> Value:
    scalar = require_scalar(exponent)
    if isinstance(scalar, EmptyOne):
        return forward(1)
    if scalar.magnitude.denominator != 1:
        raise CalculatorHalt("power requires a whole counted exponent")
    result: Value = forward(1)
    factor = base
    count = scalar.magnitude.numerator
    while count:
        if count % 2:
            result = multiply(result, factor)
        count //= 2
        if count:
            factor = multiply(factor, factor)
    return result if scalar.is_forward else reciprocal(result)


def factorial(value: Value) -> Scalar:
    count = require_whole(value)
    result = Fraction(1)
    for held in range(2, count + 1):
        result *= held
    return forward(result)


def permutation(total: Value, held: Value) -> Scalar:
    n = require_whole(total)
    r = require_whole(held)
    if r > n:
        raise CalculatorHalt("held selection cannot exceed generated support")
    result = Fraction(1)
    for item in range(n - r + 1, n + 1):
        result *= item
    return forward(result)


def combination(total: Value, held: Value) -> Scalar:
    n = require_whole(total)
    r = require_whole(held)
    if r > n:
        raise CalculatorHalt("held selection cannot exceed generated support")
    r = min(r, n - r)
    result = Fraction(1)
    for step in range(1, r + 1):
        result = result * (n - r + step) / step
    return forward(result)


def _perfect_root(number: int, degree: int) -> int | None:
    if number in {0, 1}:
        return number
    low, high = 1, number
    while low <= high:
        middle = (low + high) // 2
        powered = middle ** degree
        if powered == number:
            return middle
        if powered < number:
            low = middle + 1
        else:
            high = middle - 1
    return None


def nth_root(value: Value, degree: int, depth: int = 80) -> Value:
    scalar = require_scalar(value)
    if degree < 1:
        raise CalculatorHalt("root degree must be a positive count")
    if isinstance(scalar, EmptyOne):
        return EMPTY_ONE
    if not scalar.is_forward and degree % 2 == 0:
        rooted = nth_root(FoldScalar("forward-held", scalar.magnitude), degree, depth)
        if isinstance(rooted, CertifiedInterval):
            raise CalculatorHalt("a non-exact orthogonal root requires a paired enclosure not admitted by this operation")
        return ComplexFibre(EMPTY_ONE, rooted)
    numerator = _perfect_root(scalar.magnitude.numerator, degree)
    denominator = _perfect_root(scalar.magnitude.denominator, degree)
    if numerator is not None and denominator is not None:
        rooted = FoldScalar("forward-held", Fraction(numerator, denominator))
        return rooted if scalar.is_forward else reverse(rooted)
    target = scalar.magnitude
    lower = Fraction(0)
    upper = target if target >= 1 else Fraction(1)
    for _ in range(depth):
        midpoint = (lower + upper) / 2
        if midpoint ** degree < target:
            lower = midpoint
        else:
            upper = midpoint
    low_value, high_value = forward(lower), forward(upper)
    certificate = (
        f"positive-polynomial-balance:x^{degree}=target",
        f"generated-bisection-depth:{depth}",
        f"lower-power:{lower ** degree}",
        f"upper-power:{upper ** degree}",
    )
    if scalar.is_forward:
        return CertifiedInterval(low_value, high_value, certificate)
    return CertifiedInterval(reverse(high_value), reverse(low_value), certificate + ("odd-held-orientation",))


def _tolerance(places: int) -> Fraction:
    if places < 1 or places > 60:
        raise CalculatorHalt("requested projection precision is outside the counted bound 1..60")
    return Fraction(1, 10 ** places)


def exp_enclosure(value: Value, places: int = 18, max_terms: int = 4096) -> CertifiedInterval:
    scalar = require_scalar(value)
    if isinstance(scalar, EmptyOne):
        return as_interval(forward(1), "exp-empty-One-identity")
    if not scalar.is_forward:
        positive = exp_enclosure(FoldScalar("forward-held", scalar.magnitude), places, max_terms)
        return reciprocal(positive)  # type: ignore[return-value]
    x = scalar.magnitude
    total = Fraction(1)
    term = Fraction(1)
    tolerance = _tolerance(places)
    for count in range(1, max_terms + 1):
        term = term * x / count
        total += term
        next_term = term * x / (count + 1)
        if Fraction(count + 1) > x:
            ratio = x / (count + 2)
            tail = next_term / (1 - ratio)
            if tail <= tolerance:
                return CertifiedInterval(
                    forward(total),
                    forward(total + tail),
                    (f"exp-positive-series-terms:{count + 1}", f"geometric-tail:{tail}"),
                )
    raise CalculatorHalt("exp certificate did not close inside the declared term bound")


def ln_enclosure(value: Value, places: int = 18, max_terms: int = 4096) -> CertifiedInterval:
    scalar = require_scalar(value)
    if isinstance(scalar, EmptyOne) or not scalar.is_forward:
        raise CalculatorHalt("ln requires a forward-held positive magnitude")
    x = scalar.magnitude
    if x == 1:
        return as_interval(EMPTY_ONE, "ln-One-is-empty-One")
    if x > 1:
        z = (x - 1) / (x + 1)
        orientation = "forward"
    else:
        z = (1 - x) / (1 + x)
        orientation = "counter"
    z_squared = z * z
    total = Fraction(0)
    power = z
    tolerance = _tolerance(places)
    for count in range(max_terms):
        total += power / (2 * count + 1)
        next_power = power * z_squared
        tail = 2 * next_power / ((2 * count + 3) * (1 - z_squared))
        if tail <= tolerance:
            centre = 2 * total
            centre_value = forward(centre) if orientation == "forward" else counter(centre)
            lower = subtract_scalar(centre_value, forward(tail))
            upper = add_scalar(centre_value, forward(tail))
            return CertifiedInterval(
                lower,
                upper,
                (f"ln-atanh-series-terms:{count + 1}", f"positive-tail:{tail}"),
            )
        power = next_power
    raise CalculatorHalt("ln certificate did not close inside the declared term bound")


def log10_enclosure(value: Value, places: int = 18) -> CertifiedInterval:
    return divide(ln_enclosure(value, places + 4), ln_enclosure(forward(10), places + 4))  # type: ignore[return-value]


def _alternating_trig(value: Scalar, cosine: bool, places: int, max_terms: int) -> CertifiedInterval:
    if isinstance(value, EmptyOne):
        return as_interval(forward(1) if cosine else EMPTY_ONE, "trigonometric-empty-One-base")
    x = value.magnitude
    x_squared = x * x
    total: Scalar = forward(1) if cosine else forward(x)
    term = Fraction(1) if cosine else x
    tolerance = _tolerance(places)
    for index in range(1, max_terms + 1):
        if cosine:
            denominator = (2 * index - 1) * (2 * index)
        else:
            denominator = (2 * index) * (2 * index + 1)
        term = term * x_squared / denominator
        signed_term = forward(term) if index % 2 == 0 else counter(term)
        total = add_scalar(total, signed_term)
        if cosine:
            next_denominator = (2 * index + 1) * (2 * index + 2)
        else:
            next_denominator = (2 * index + 2) * (2 * index + 3)
        next_term = term * x_squared / next_denominator
        if next_term <= term and next_term <= tolerance:
            lower = subtract_scalar(total, forward(next_term))
            upper = add_scalar(total, forward(next_term))
            if not cosine and not value.is_forward:
                lower, upper = reverse(upper), reverse(lower)
            return CertifiedInterval(
                lower,
                upper,
                (f"{'cos' if cosine else 'sin'}-alternating-terms:{index + 1}", f"next-term-bound:{next_term}"),
            )
    raise CalculatorHalt("trigonometric certificate did not close inside the declared term bound")


def sin_enclosure(value: Value, places: int = 18) -> CertifiedInterval:
    return _alternating_trig(require_scalar(value), False, places, 4096)


def cos_enclosure(value: Value, places: int = 18) -> CertifiedInterval:
    return _alternating_trig(require_scalar(value), True, places, 4096)


def tan_enclosure(value: Value, places: int = 18) -> CertifiedInterval:
    return divide(sin_enclosure(value, places + 4), cos_enclosure(value, places + 4))  # type: ignore[return-value]


def _atan_unit_enclosure(x: Fraction, terms: int) -> CertifiedInterval:
    positive_total = Fraction(0)
    counter_total = Fraction(0)
    for index in range(terms):
        term = x ** (2 * index + 1) / (2 * index + 1)
        if index % 2:
            counter_total += term
        else:
            positive_total += term
    partial = positive_total - counter_total
    next_term = x ** (2 * terms + 1) / (2 * terms + 1)
    if terms % 2:
        lower, upper = partial, partial + next_term
    else:
        lower, upper = partial - next_term, partial
    return CertifiedInterval(
        forward(lower),
        forward(upper),
        (f"atan-alternating-terms:{terms}", f"next-term-bound:{next_term}"),
    )


def circle_constant_enclosure(terms: int = 32) -> CertifiedInterval:
    """Certified circle constant from an exactly replayed angle composition."""

    fifth = _atan_unit_enclosure(Fraction(1, 5), terms)
    two_thirty_ninth = _atan_unit_enclosure(Fraction(1, 239), terms)
    result = subtract(multiply(forward(16), fifth), multiply(forward(4), two_thirty_ninth))
    if not isinstance(result, CertifiedInterval):
        raise CalculatorHalt("circle enclosure construction failed")
    return CertifiedInterval(
        result.lower,
        result.upper,
        result.certificate + ("exact-tangent-composition:16*atan(1/5)-4*atan(1/239)",),
    )


def conjugate(value: Value) -> Value:
    if not isinstance(value, ComplexFibre):
        return value
    return ComplexFibre(value.real, reverse(value.orthogonal))
