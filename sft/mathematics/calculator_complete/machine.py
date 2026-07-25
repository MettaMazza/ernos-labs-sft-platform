"""Resource-closed complete scientific expression machine."""

from __future__ import annotations

from fractions import Fraction

from sft.mathematics.calculator.machine import Calculation
from sft.mathematics.calculator.machine_v3 import Calculator as _CalculatorV3
from sft.mathematics.calculator.operations import (
    divide,
    factorial,
    require_scalar,
    require_whole,
)
from sft.mathematics.calculator.operations_v3 import rational_power, to_radians
from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EMPTY_ONE,
    CalculatorHalt,
    EmptyOne,
    FoldScalar,
    Scalar,
    Value,
    forward,
)

from .operations import cos_value, sin_value, tan_value


class Calculator(_CalculatorV3):
    """Claim-006 evaluator with early counted limits and reduced circular input."""

    def _lex(self, expression: str):
        tokens = super()._lex(expression)
        for token in tokens:
            if token.kind != "number":
                continue
            normalized = token.text.lower()
            mantissa, _, exponent = normalized.partition("e")
            digit_count = sum(character.isdigit() for character in mantissa)
            if digit_count > self.operation_limit:
                raise CalculatorHalt("numeric token exceeds the declared counted digit bound")
            if exponent and abs(int(exponent)) > self.operation_limit:
                raise CalculatorHalt("scientific exponent exceeds the declared counted bound")
        return tokens

    def _bounded_whole(self, value: Value, purpose: str, *, allow_empty: bool = True) -> int:
        count = require_whole(value, allow_empty=allow_empty)
        if count > self.operation_limit:
            raise CalculatorHalt(f"{purpose} exceeds the declared counted operation bound")
        return count

    def _power(self) -> Value:
        value = self._postfix()
        if self._peek("^"):
            self._take("^")
            exponent = self._unary()
            if isinstance(exponent, FoldScalar):
                if (
                    exponent.magnitude.numerator > self.operation_limit
                    or exponent.magnitude.denominator > self.operation_limit
                ):
                    raise CalculatorHalt("power exponent exceeds the declared counted bound")
            value = self._record(
                "exact-or-certified-power",
                rational_power(value, exponent, self.places),
            )
        return value

    def _postfix(self) -> Value:
        value = self._primary()
        while self._peek("!") or self._peek("%"):
            operator = self._take().text
            if operator == "!":
                self._bounded_whole(value, "factorial count")
                value = self._record("generated-factorial-recurrence", factorial(value))
            else:
                value = self._record("exact-hundredth-part", divide(value, forward(100)))
        return value

    def _call(self, name: str, arguments: tuple[Value, ...]) -> Value:
        if name in {"sin", "cos", "tan"}:
            self._arity(name, arguments, 1)
            radians = to_radians(arguments[0], self.angle_mode)
            function = {"sin": sin_value, "cos": cos_value, "tan": tan_value}[name]
            return self._record(
                f"generated-function:{name}:{self.angle_mode}:periodic-reduction",
                function(radians, self.places),
            )
        if name == "root":
            self._arity(name, arguments, 2)
            self._bounded_whole(arguments[1], "root degree", allow_empty=False)
        elif name in {"ncr", "npr"}:
            self._arity(name, arguments, 2)
            self._bounded_whole(arguments[0], f"{name} support")
            self._bounded_whole(arguments[1], f"{name} selection")
        elif name in {"sum", "prod", "mean", "variance", "stddev"}:
            if len(arguments) > self.operation_limit:
                raise CalculatorHalt(f"{name} argument count exceeds the declared operation bound")
        return super()._call(name, arguments)


def calculate(
    expression: str,
    *,
    places: int = 18,
    angle_mode: str = "rad",
    operation_limit: int = 10000,
) -> Calculation:
    return Calculator(
        places=places,
        angle_mode=angle_mode,
        operation_limit=operation_limit,
    ).calculate(expression)


__all__ = ("Calculation", "Calculator", "calculate")
