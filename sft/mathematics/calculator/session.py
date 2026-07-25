"""Stateful memory and history for terminal and graphical calculator use."""

from __future__ import annotations

from dataclasses import dataclass

from .machine import Calculation
from .machine_v3 import Calculator
from .operations import add, subtract
from .values import EMPTY_ONE, Value


@dataclass(frozen=True)
class HistoryEntry:
    index: int
    expression: str
    angle_mode: str
    calculation: Calculation


class CalculatorSession:
    def __init__(self, *, places: int = 18, angle_mode: str = "rad"):
        self.places = places
        self.angle_mode = angle_mode
        self.memory: Value = EMPTY_ONE
        self.answer: Value = EMPTY_ONE
        self.history: list[HistoryEntry] = []

    def set_angle_mode(self, mode: str) -> None:
        if mode not in {"rad", "deg", "grad"}:
            raise ValueError("angle mode must be rad, deg or grad")
        self.angle_mode = mode

    def evaluate(self, expression: str) -> Calculation:
        calculator = Calculator(
            places=self.places,
            angle_mode=self.angle_mode,
            symbols={"ans": self.answer, "mem": self.memory},
        )
        calculation = calculator.calculate(expression)
        self.answer = calculation.value
        self.history.append(HistoryEntry(len(self.history) + 1, expression, self.angle_mode, calculation))
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
