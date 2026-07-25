"""Exact value forms for the SFT scientific calculator.

No object in this module stores numerical zero, a negative magnitude, an
irrational scalar, an imaginary scalar or a floating-point proof value.
Conventional signs and decimals are boundary notation only.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Union


class CalculatorHalt(ValueError):
    """A mandatory halt at an SFT type, domain or resource boundary."""


@dataclass(frozen=True)
class EmptyOne:
    """The structural empty-One form used where correspondence writes 0."""

    def __str__(self) -> str:
        return "empty-One"


EMPTY_ONE = EmptyOne()


@dataclass(frozen=True)
class FoldScalar:
    """A positive rational magnitude with one of the two held orientations."""

    orientation: str
    magnitude: Fraction

    def __post_init__(self) -> None:
        if self.orientation not in {"forward-held", "counter-held"}:
            raise CalculatorHalt("a scalar requires one of the two generated held orientations")
        if not isinstance(self.magnitude, Fraction) or self.magnitude <= 0:
            raise CalculatorHalt("a Fold magnitude must be an exact positive rational part")

    @property
    def is_forward(self) -> bool:
        return self.orientation == "forward-held"


Scalar = Union[EmptyOne, FoldScalar]


@dataclass(frozen=True)
class CertifiedInterval:
    """An exact rational enclosure, never a substituted irrational scalar."""

    lower: Scalar
    upper: Scalar
    certificate: tuple[str, ...]

    def __post_init__(self) -> None:
        if compare_scalar(self.lower, self.upper) > 0:
            raise CalculatorHalt("an enclosure's lower boundary must precede its upper boundary")
        if not self.certificate:
            raise CalculatorHalt("an enclosure requires a replayable exact certificate")


@dataclass(frozen=True)
class ComplexFibre:
    """Two exact orthogonal Fold fibres; no imaginary scalar is introduced."""

    real: Scalar
    orthogonal: Scalar


Value = Union[Scalar, CertifiedInterval, ComplexFibre]


def forward(magnitude: Fraction | int) -> Scalar:
    part = magnitude if isinstance(magnitude, Fraction) else Fraction(magnitude)
    if part == 0:
        return EMPTY_ONE
    if part < 0:
        raise CalculatorHalt("negative host magnitudes are not admitted")
    return FoldScalar("forward-held", part)


def counter(magnitude: Fraction | int) -> Scalar:
    part = magnitude if isinstance(magnitude, Fraction) else Fraction(magnitude)
    if part == 0:
        return EMPTY_ONE
    if part < 0:
        raise CalculatorHalt("negative host magnitudes are not admitted")
    return FoldScalar("counter-held", part)


def parse_exact_number(token: str) -> Scalar:
    """Parse decimal/scientific boundary notation directly into a rational part."""

    text = token.strip().lower()
    if not text:
        raise CalculatorHalt("empty numeric token")
    if text.startswith(("+", "-")):
        raise CalculatorHalt("orientation is parsed separately from magnitude")
    if "e" in text:
        mantissa, exponent_text = text.split("e", 1)
        if not exponent_text or exponent_text in {"+", "-"}:
            raise CalculatorHalt("invalid counted exponent")
        exponent = int(exponent_text)
    else:
        mantissa, exponent = text, 0
    if mantissa.count(".") > 1:
        raise CalculatorHalt("invalid decimal projection")
    if "." in mantissa:
        whole, parts = mantissa.split(".", 1)
    else:
        whole, parts = mantissa, ""
    if not whole:
        whole = "0"
    if not whole.isdigit() or (parts and not parts.isdigit()):
        raise CalculatorHalt("numeric input must be generated from decimal digits")
    digits = int(whole + parts)
    denominator = 10 ** len(parts)
    magnitude = Fraction(digits, denominator)
    if exponent >= 0:
        magnitude *= 10 ** exponent
    else:
        magnitude /= 10 ** (-exponent)
    return forward(magnitude)


def reverse(value: Scalar) -> Scalar:
    if isinstance(value, EmptyOne):
        return value
    return FoldScalar(
        "counter-held" if value.is_forward else "forward-held",
        value.magnitude,
    )


def compare_scalar(left: Scalar, right: Scalar) -> int:
    if isinstance(left, EmptyOne):
        if isinstance(right, EmptyOne):
            return 0
        return -1 if right.is_forward else 1
    if isinstance(right, EmptyOne):
        return 1 if left.is_forward else -1
    if left.is_forward and not right.is_forward:
        return 1
    if right.is_forward and not left.is_forward:
        return -1
    if left.magnitude == right.magnitude:
        return 0
    if left.is_forward:
        return 1 if left.magnitude > right.magnitude else -1
    return -1 if left.magnitude > right.magnitude else 1


def add_scalar(left: Scalar, right: Scalar) -> Scalar:
    if isinstance(left, EmptyOne):
        return right
    if isinstance(right, EmptyOne):
        return left
    if left.orientation == right.orientation:
        return FoldScalar(left.orientation, left.magnitude + right.magnitude)
    if left.magnitude == right.magnitude:
        return EMPTY_ONE
    if left.magnitude > right.magnitude:
        return FoldScalar(left.orientation, left.magnitude - right.magnitude)
    return FoldScalar(right.orientation, right.magnitude - left.magnitude)


def subtract_scalar(left: Scalar, right: Scalar) -> Scalar:
    return add_scalar(left, reverse(right))


def multiply_scalar(left: Scalar, right: Scalar) -> Scalar:
    if isinstance(left, EmptyOne) or isinstance(right, EmptyOne):
        return EMPTY_ONE
    orientation = "forward-held" if left.orientation == right.orientation else "counter-held"
    return FoldScalar(orientation, left.magnitude * right.magnitude)


def reciprocal_scalar(value: Scalar) -> Scalar:
    if isinstance(value, EmptyOne):
        raise CalculatorHalt("division by structural empty-One is undefined")
    return FoldScalar(value.orientation, Fraction(value.magnitude.denominator, value.magnitude.numerator))


def divide_scalar(left: Scalar, right: Scalar) -> Scalar:
    return multiply_scalar(left, reciprocal_scalar(right))


def scalar_to_fraction_for_projection(value: Scalar) -> Fraction:
    """Correspondence-only signed projection; never used as an admitted value."""

    if isinstance(value, EmptyOne):
        return Fraction(0)
    return value.magnitude if value.is_forward else -value.magnitude


def scalar_from_projection(value: Fraction) -> Scalar:
    """Immediately translate a host comparison result back to an SFT form."""

    if value == 0:
        return EMPTY_ONE
    return forward(value) if value > 0 else counter(-value)


def decimal_projection(value: Scalar, places: int = 18) -> str:
    if isinstance(value, EmptyOne):
        return "0"
    with localcontext() as context:
        context.prec = places + 8
        result = Decimal(value.magnitude.numerator) / Decimal(value.magnitude.denominator)
        text = format(result, f".{places}g")
    return text if value.is_forward else "-" + text


def exact_text(value: Scalar) -> str:
    if isinstance(value, EmptyOne):
        return "empty-One"
    prefix = "" if value.is_forward else "counter:"
    if value.magnitude.denominator == 1:
        return prefix + str(value.magnitude.numerator)
    return prefix + f"{value.magnitude.numerator}/{value.magnitude.denominator}"


def value_text(value: Value, places: int = 18) -> str:
    if isinstance(value, CertifiedInterval):
        if compare_scalar(value.lower, value.upper) == 0:
            return exact_text(value.lower)
        return (
            f"[{exact_text(value.lower)}, {exact_text(value.upper)}] "
            f"≈ [{decimal_projection(value.lower, places)}, {decimal_projection(value.upper, places)}]"
        )
    if isinstance(value, ComplexFibre):
        return f"fibre(real={exact_text(value.real)}, orthogonal={exact_text(value.orthogonal)})"
    exact = exact_text(value)
    projected = decimal_projection(value, places)
    return exact if exact == projected else f"{exact} ≈ {projected}"
