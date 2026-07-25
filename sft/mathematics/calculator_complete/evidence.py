"""Engine-comparable calculator evidence without issuing an admission receipt."""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.mathematics.calculator.machine import Calculation
from sft.mathematics.calculator.values import (
    CertifiedInterval,
    ComplexFibre,
    EmptyOne,
    FoldScalar,
    Value,
    value_text,
)


CALCULATOR_CLAIM_ID = "SFT-MATH-SCIENTIFIC-CALCULATOR-006"
CALCULATOR_DEPENDENCY = "SFT-MATH-SCIENTIFIC-CALCULATOR-005"


def value_form(value: Value) -> str:
    if isinstance(value, EmptyOne):
        return "structural_empty_One"
    if isinstance(value, FoldScalar):
        return "forward_held_positive_rational" if value.is_forward else "counter_held_positive_rational"
    if isinstance(value, CertifiedInterval):
        return "certified_exact_rational_enclosure"
    if isinstance(value, ComplexFibre):
        return "typed_real_and_orthogonal_Fold_fibres"
    raise TypeError("unknown calculator value form")


def _certificate(value: Value) -> tuple[str, ...]:
    return value.certificate if isinstance(value, CertifiedInterval) else ()


def _scalar_is_valid(value: object) -> bool:
    if isinstance(value, EmptyOne):
        return True
    return (
        isinstance(value, FoldScalar)
        and value.orientation in {"forward-held", "counter-held"}
        and isinstance(value.magnitude, Fraction)
        and value.magnitude > 0
    )


def validate_value(value: Value) -> dict[str, bool]:
    """Inspect the returned object rather than premarking constraint outcomes."""

    if isinstance(value, (EmptyOne, FoldScalar)):
        valid = _scalar_is_valid(value)
        enclosure = True
        typed_fibres = True
    elif isinstance(value, CertifiedInterval):
        valid = _scalar_is_valid(value.lower) and _scalar_is_valid(value.upper)
        enclosure = bool(value.certificate)
        typed_fibres = True
    elif isinstance(value, ComplexFibre):
        valid = _scalar_is_valid(value.real) and _scalar_is_valid(value.orthogonal)
        enclosure = True
        typed_fibres = True
    else:
        valid = enclosure = typed_fibres = False
    checks = {
        "recognized_exact_value_form": valid,
        "all_scalar_parts_are_empty_One_or_positive_Fractions": valid,
        "held_orientation_encodes_conventional_sign": valid,
        "nonrational_output_has_rational_enclosure_certificate": enclosure,
        "complex_correspondence_uses_typed_Fold_fibres": typed_fibres,
        "no_float_object_in_proof_value": not isinstance(value, float),
    }
    if not all(checks.values()):
        raise TypeError("calculator returned a value that violates its exact SFT runtime type boundary")
    return checks


def _receipt(root: Path, claim_id: str) -> str | None:
    path = root / "census" / "claims.json"
    if not path.exists():
        return None
    rows = json.loads(path.read_text(encoding="utf-8"))["claims"]
    row = next((item for item in rows if item["claim_id"] == claim_id), None)
    return None if row is None else row.get("receipt_hash")


def calculation_evidence(calculation: Calculation, root: Path | None = None) -> dict[str, object]:
    repository = root or Path(__file__).resolve().parents[3]
    value = calculation.value
    return {
        "kind": "SFT_calculator_evaluation_not_engine_admission",
        "calculator_claim_id": CALCULATOR_CLAIM_ID,
        "admitted_dependency": CALCULATOR_DEPENDENCY,
        "official_calculator_receipt_hash": _receipt(repository, CALCULATOR_CLAIM_ID),
        "expression": calculation.expression,
        "status": "complete_generated_expression_consumed",
        "value_form": value_form(value),
        "exact_value": value_text(value, 24),
        "certificate": _certificate(value),
        "trace": calculation.trace,
        "resources": {
            "tokens_read": calculation.tokens_read,
            "operations_executed": calculation.operations_executed,
        },
        "constraint_checks": validate_value(value),
        "halt_policy": "invalid, unclosed or resource-exhausted expressions raise CalculatorHalt and return no value",
        "engine_admission_issued": False,
    }


def calculation_evidence_json(calculation: Calculation, root: Path | None = None) -> str:
    return json.dumps(calculation_evidence(calculation, root), indent=2, sort_keys=True) + "\n"


__all__ = (
    "CALCULATOR_CLAIM_ID",
    "CALCULATOR_DEPENDENCY",
    "calculation_evidence",
    "calculation_evidence_json",
    "validate_value",
    "value_form",
)
