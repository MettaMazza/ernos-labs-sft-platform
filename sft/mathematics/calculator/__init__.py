"""SFT-native exact scientific calculator.

The public interface deliberately exposes typed Fold values rather than host
floating-point numbers.  See :mod:`sft.mathematics.calculator.machine` for the
executable evaluator.
"""

from .machine_v3 import Calculation, Calculator, calculate
from .session import CalculatorSession
from .values import CertifiedInterval, ComplexFibre, EMPTY_ONE, FoldScalar

__all__ = (
    "Calculation",
    "Calculator",
    "CalculatorSession",
    "CertifiedInterval",
    "ComplexFibre",
    "EMPTY_ONE",
    "FoldScalar",
    "calculate",
)
