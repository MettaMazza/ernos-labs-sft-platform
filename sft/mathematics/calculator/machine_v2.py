"""Active calculator machine with the corrected circle certificate."""

from __future__ import annotations

from .machine import Calculation, Calculator as _CalculatorV1
from .operations_v2 import circle_constant_enclosure
from .values import CalculatorHalt


class Calculator(_CalculatorV1):
    """Version-two evaluator retaining all exact v1 operations except corrected pi."""

    def _primary(self):
        if self._position < len(self._tokens):
            token = self._tokens[self._position]
            next_is_call = (
                self._position + 1 < len(self._tokens)
                and self._tokens[self._position + 1].text == "("
            )
            if token.kind == "name" and token.text.lower() == "pi" and not next_is_call:
                self._take()
                return self._record("certified-circle-constant-v2", circle_constant_enclosure())
        return super()._primary()


def calculate(expression: str, *, places: int = 18) -> Calculation:
    return Calculator(places=places).calculate(expression)


__all__ = ("Calculation", "Calculator", "CalculatorHalt", "calculate")
