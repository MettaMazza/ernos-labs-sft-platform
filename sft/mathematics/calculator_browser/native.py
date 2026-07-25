"""SFT-native result text with no conventional prohibited scalar projection."""

from __future__ import annotations

from dataclasses import asdict

from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EmptyOne,
    FoldScalar,
    Scalar,
    Value,
    compare_scalar,
)
from sft.mathematics.calculator_complete.controller import CalculatorController


def native_scalar(value: Scalar) -> str:
    if isinstance(value, EmptyOne):
        return "0"
    magnitude = (
        str(value.magnitude.numerator)
        if value.magnitude.denominator == 1
        else f"{value.magnitude.numerator}/{value.magnitude.denominator}"
    )
    return magnitude if value.is_forward else f"counter-held {magnitude}"


def native_value(value: Value) -> str:
    if isinstance(value, CertifiedInterval):
        if compare_scalar(value.lower, value.upper) == 0:
            return native_scalar(value.lower)
        return f"certified rational interval [{native_scalar(value.lower)}, {native_scalar(value.upper)}]"
    if isinstance(value, ComplexFibre):
        return f"Fold fibres (real: {native_scalar(value.real)}; orthogonal: {native_scalar(value.orthogonal)})"
    return native_scalar(value)


def contains_counter(value: Value) -> bool:
    if isinstance(value, EmptyOne):
        return False
    if isinstance(value, FoldScalar):
        return not value.is_forward
    if isinstance(value, CertifiedInterval):
        return contains_counter(value.lower) or contains_counter(value.upper)
    return contains_counter(value.real) or contains_counter(value.orthogonal)


def native_view(controller: CalculatorController) -> dict[str, object]:
    view = asdict(controller.view())
    view["history"] = tuple(
        f"{item.expression.rstrip('=')}  =  {native_value(item.calculation.value)}"
        for item in controller.session.history
    )
    if view["error"]:
        return view
    view["result"] = native_value(controller.session.answer)
    if controller.session.history:
        calculation = controller.session.history[-1].calculation
        view["exact_details"] = (
            "Exact SFT result\n"
            + native_value(calculation.value)
            + "\n\nProof trace\n"
            + "\n".join(line.split(" ≈ ", 1)[0] for line in calculation.trace)
            + f"\n\nResources\ntokens: {calculation.tokens_read}\noperations: {calculation.operations_executed}"
        )
    return view


__all__ = ("contains_counter", "native_scalar", "native_value", "native_view")
