"""Complete calculator session using the claim-006 machine."""

from __future__ import annotations

from dataclasses import dataclass

from sft.mathematics.calculator.machine import Calculation
from sft.mathematics.calculator.operations import add, subtract
from sft.mathematics.calculator.values import EMPTY_ONE, CalculatorHalt, Value

from .machine import Calculator


@dataclass(frozen=True)
class HistoryEntry:
    index: int
    expression: str
    angle_mode: str
    calculation: Calculation


class CalculatorSession:
    def __init__(
        self,
        *,
        places: int = 18,
        angle_mode: str = "rad",
        operation_limit: int = 10000,
    ):
        if angle_mode not in {"rad", "deg", "grad"}:
            raise CalculatorHalt("angle mode must be rad, deg or grad")
        self.places = places
        self.angle_mode = angle_mode
        self.operation_limit = operation_limit
        self.memory: Value = EMPTY_ONE
        self.answer: Value = EMPTY_ONE
        self.history: list[HistoryEntry] = []

    def set_angle_mode(self, mode: str) -> None:
        if mode not in {"rad", "deg", "grad"}:
            raise CalculatorHalt("angle mode must be rad, deg or grad")
        self.angle_mode = mode

    def evaluate(self, expression: str) -> Calculation:
        calculator = Calculator(
            places=self.places,
            operation_limit=self.operation_limit,
            angle_mode=self.angle_mode,
            symbols={"ans": self.answer, "mem": self.memory},
        )
        calculation = calculator.calculate(expression)
        self.answer = calculation.value
        self.history.append(
            HistoryEntry(len(self.history) + 1, expression, self.angle_mode, calculation)
        )
        return calculation

    def memory_store(self, value: Value | None = None) -> Value:
        self.memory = self.answer if value is None else value
        return self.memory

    def memory_clear(self) -> Value:
        self.memory = EMPTY_ONE
        return self.memory

    def memory_add(self, value: Value | None = None) -> Value:
        self.memory = add(self.memory, self.answer if value is None else value)
        return self.memory

    def memory_subtract(self, value: Value | None = None) -> Value:
        self.memory = subtract(self.memory, self.answer if value is None else value)
        return self.memory

    def clear_history(self) -> None:
        self.history.clear()

    def all_clear(self) -> None:
        self.answer = EMPTY_ONE


__all__ = ("CalculatorSession", "HistoryEntry")
