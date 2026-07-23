"""Guarded exact host representations for the SFT derivational boundary."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


class InadmissibleExactValue(ValueError):
    """Raised when a host value cannot represent an SFT derivational object."""


@dataclass(frozen=True, order=True)
class PositiveCount:
    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int) or self.value < 1:
            raise InadmissibleExactValue("an SFT count must be a positive counted value")


@dataclass(frozen=True, order=True)
class ExactPart:
    """An exact positive rational part of the whole, including the One."""

    value: Fraction

    @classmethod
    def from_pair(cls, numerator: int, denominator: int) -> "ExactPart":
        if isinstance(numerator, bool) or isinstance(denominator, bool):
            raise InadmissibleExactValue("boolean host values are not SFT parts")
        if numerator < 1 or denominator < 1:
            raise InadmissibleExactValue("an SFT part cannot contain zero or a negative value")
        if numerator > denominator:
            raise InadmissibleExactValue("an SFT part cannot exceed the One")
        return cls(Fraction(numerator, denominator))

    def __post_init__(self) -> None:
        if not isinstance(self.value, Fraction):
            raise InadmissibleExactValue("an SFT part must use exact Fraction identity")
        if self.value <= 0 or self.value > 1:
            raise InadmissibleExactValue("an SFT part must lie in the exact positive domain through the One")


@dataclass(frozen=True)
class HeldLabel:
    """Structural orientation or complement without installing signed quantity."""

    family: str
    label: str

    def __post_init__(self) -> None:
        if not self.family.strip() or not self.label.strip():
            raise InadmissibleExactValue("held labels require a named family and label")
