"""Complete mainstream scientific-calculator expression machine."""

from __future__ import annotations

from dataclasses import replace

from .machine import Calculation
from .machine_v2 import Calculator as _CalculatorV2
from .operations import absolute, conjugate, divide, nth_root, reciprocal, require_scalar
from .operations_v2 import circle_constant_enclosure
from .operations_v3 import (
    acos_value,
    acosh_value,
    arithmetic_mean,
    asin_value,
    asinh_value,
    atan_value,
    atanh_value,
    ceil_value,
    cos_value,
    cosh_value,
    exact_product,
    exact_sum,
    floor_value,
    from_radians,
    gcd_value,
    golden_ratio_enclosure,
    lcm_value,
    ln_value,
    log_base,
    modulo_value,
    population_stddev,
    population_variance,
    rational_power,
    root_value,
    sin_value,
    sinh_value,
    tan_value,
    tanh_value,
    to_radians,
)
from .values import ComplexFibre, EMPTY_ONE, CalculatorHalt, Value, forward


class Calculator(_CalculatorV2):
    """Exact scientific evaluator with angle modes and named session values."""

    def __init__(
        self,
        *,
        places: int = 18,
        operation_limit: int = 10000,
        angle_mode: str = "rad",
        symbols: dict[str, Value] | None = None,
    ):
        super().__init__(places=places, operation_limit=operation_limit)
        if angle_mode not in {"rad", "deg", "grad"}:
            raise CalculatorHalt("angle mode must be rad, deg or grad")
        self.angle_mode = angle_mode
        self.symbols = {key.lower(): value for key, value in (symbols or {}).items()}

    def calculate(self, expression: str) -> Calculation:
        original = expression
        stripped = expression.strip()
        if stripped.endswith("="):
            stripped = stripped[:-1].rstrip()
        if "=" in stripped:
            raise CalculatorHalt("equals is a terminal execute key, not an internal operator")
        result = super().calculate(stripped)
        return replace(result, expression=original)

    def _power(self) -> Value:
        value = self._postfix()
        if self._peek("^"):
            self._take("^")
            exponent = self._unary()
            value = self._record("exact-or-certified-power", rational_power(value, exponent, self.places))
        return value

    def _primary(self) -> Value:
        if self._position < len(self._tokens):
            token = self._tokens[self._position]
            next_is_call = (
                self._position + 1 < len(self._tokens)
                and self._tokens[self._position + 1].text == "("
            )
            if token.kind == "name" and not next_is_call:
                name = token.text.lower()
                if name in self.symbols:
                    self._take()
                    return self._record(f"session-symbol:{name}", self.symbols[name])
                if name == "tau":
                    self._take()
                    return self._record("certified-full-turn", self._multiply_constant(forward(2), circle_constant_enclosure()))
                if name in {"phi", "golden"}:
                    self._take()
                    return self._record("certified-golden-ratio", golden_ratio_enclosure())
        return super()._primary()

    @staticmethod
    def _multiply_constant(left: Value, right: Value) -> Value:
        from .operations import multiply
        return multiply(left, right)

    def _call(self, name: str, arguments: tuple[Value, ...]) -> Value:
        unary = {
            "asin", "acos", "atan", "sinh", "cosh", "tanh", "asinh", "acosh", "atanh",
            "log2", "log10", "exp", "sqrt", "cbrt", "floor", "ceil",
        }
        if name in unary:
            self._arity(name, arguments, 1)
            value = arguments[0]
            if name == "asin":
                result = from_radians(asin_value(value, self.places), self.angle_mode)
            elif name == "acos":
                result = from_radians(acos_value(value, self.places), self.angle_mode)
            elif name == "atan":
                result = from_radians(atan_value(value, self.places), self.angle_mode)
            elif name == "sinh":
                result = sinh_value(value, self.places)
            elif name == "cosh":
                result = cosh_value(value, self.places)
            elif name == "tanh":
                result = tanh_value(value, self.places)
            elif name == "asinh":
                result = asinh_value(value, self.places)
            elif name == "acosh":
                result = acosh_value(value, self.places)
            elif name == "atanh":
                result = atanh_value(value, self.places)
            elif name == "log2":
                result = log_base(value, forward(2), self.places)
            elif name == "log10":
                result = log_base(value, forward(10), self.places)
            elif name == "exp":
                from .operations_v3 import exp_value
                result = exp_value(value, self.places)
            elif name == "sqrt":
                result = root_value(value, 2)
            elif name == "cbrt":
                result = root_value(value, 3)
            elif name == "floor":
                result = floor_value(value)
            else:
                result = ceil_value(value)
            return self._record(f"generated-function:{name}", result)

        if name in {"sin", "cos", "tan"}:
            self._arity(name, arguments, 1)
            radians = to_radians(arguments[0], self.angle_mode)
            function = {"sin": sin_value, "cos": cos_value, "tan": tan_value}[name]
            return self._record(f"generated-function:{name}:{self.angle_mode}", function(radians, self.places))

        if name in {"sum", "prod", "mean", "variance", "stddev"}:
            if not arguments:
                raise CalculatorHalt(f"{name} requires at least one generated argument")
            function = {
                "sum": exact_sum,
                "prod": exact_product,
                "mean": arithmetic_mean,
                "variance": population_variance,
                "stddev": population_stddev,
            }[name]
            return self._record(f"generated-function:{name}", function(arguments))

        if name in {"gcd", "lcm", "mod", "hypot"}:
            self._arity(name, arguments, 2)
            left, right = arguments
            if name == "gcd":
                result = gcd_value(left, right)
            elif name == "lcm":
                result = lcm_value(left, right)
            elif name == "mod":
                result = modulo_value(left, right)
            else:
                from .operations import add, multiply
                result = root_value(add(multiply(left, left), multiply(right, right)), 2)
            return self._record(f"generated-function:{name}", result)

        if name == "pow":
            self._arity(name, arguments, 2)
            return self._record("generated-function:pow", rational_power(arguments[0], arguments[1], self.places))
        if name == "root":
            self._arity(name, arguments, 2)
            from .operations import require_whole
            return self._record(
                "generated-function:root",
                root_value(arguments[0], require_whole(arguments[1], allow_empty=False)),
            )
        if name == "log":
            if len(arguments) == 1:
                return self._record("generated-function:log10", log_base(arguments[0], forward(10), self.places))
            if len(arguments) == 2:
                return self._record("generated-function:log-base", log_base(arguments[0], arguments[1], self.places))
            raise CalculatorHalt("log requires one value or one value and one base")
        if name == "ln":
            self._arity(name, arguments, 1)
            return self._record("generated-function:ln", ln_value(arguments[0], self.places))
        if name == "abs":
            self._arity(name, arguments, 1)
            return self._record("generated-function:abs", absolute(arguments[0]))
        if name == "recip":
            self._arity(name, arguments, 1)
            return self._record("generated-function:recip", reciprocal(arguments[0]))
        if name == "conj":
            self._arity(name, arguments, 1)
            return self._record("generated-function:conj", conjugate(arguments[0]))
        if name == "complex":
            self._arity(name, arguments, 2)
            return self._record("generated-function:complex", ComplexFibre(require_scalar(arguments[0]), require_scalar(arguments[1])))
        return super()._call(name, arguments)


def calculate(expression: str, *, places: int = 18, angle_mode: str = "rad") -> Calculation:
    return Calculator(places=places, angle_mode=angle_mode).calculate(expression)


__all__ = ("Calculation", "Calculator", "calculate")
