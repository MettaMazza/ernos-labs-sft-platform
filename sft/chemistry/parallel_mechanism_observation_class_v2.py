"""Versioned KIN-008 exact observation-class reconstruction.

The source does not select one of the two structures assigned to Supplementary
Figure 31 peak x.  The lawful result is therefore the complete two-member
observation class, not an abandoned failed singleton prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import re

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[2]
SUPPLEMENT = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots/kin-008-parallel-mechanism-v1"
    / "supplementary-information.pdf"
)


@dataclass(frozen=True)
class PeakXObservationClass:
    source_page: int
    members: tuple[str, ...]
    calculated_mass_to_charge: Fraction
    observed_mass_to_charge: Fraction
    maximum_extent_millimolar: Fraction

    @property
    def mass_difference(self) -> Fraction:
        return abs(self.observed_mass_to_charge - self.calculated_mass_to_charge)

    @property
    def preferred_member(self) -> None:
        return None


def _decimal_fraction(inscription: str) -> Fraction:
    whole, fractional = inscription.split(".")
    return Fraction(int(whole + fractional), 10 ** len(fractional))


def reconstruct_peak_x_observation_class(path: Path = SUPPLEMENT) -> PeakXObservationClass:
    reader = PdfReader(path)
    if len(reader.pages) != 54:
        raise ValueError("KIN-008 supplementary page census changed")
    page_number = 49
    text = " ".join((reader.pages[page_number - 1].extract_text() or "").split())
    if "The peak termed as “ x” can have two possible structures, as determined via mass analysis." not in text:
        raise ValueError("KIN-008 exact two-structure source disclosure changed")
    mass = re.search(r"Calculated m/z \[M\+H\]\+:\s*([0-9]+\.[0-9]+), Observed m/z \[M\+H\]\+:\s*([0-9]+\.[0-9]+)", text)
    extent = re.search(r"maximum extent of ~([0-9]+\.[0-9]+) mM", text)
    if mass is None or extent is None:
        raise ValueError("KIN-008 mass or extent inscription changed")
    result = PeakXObservationClass(
        source_page=page_number,
        members=(
            "supplementary-figure-31-depicted-structure-one",
            "supplementary-figure-31-depicted-structure-two",
        ),
        calculated_mass_to_charge=_decimal_fraction(mass.group(1)),
        observed_mass_to_charge=_decimal_fraction(mass.group(2)),
        maximum_extent_millimolar=_decimal_fraction(extent.group(1)),
    )
    if (
        len(result.members) != 2
        or len(set(result.members)) != 2
        or result.calculated_mass_to_charge != Fraction(500807, 625)
        or result.observed_mass_to_charge != Fraction(8012921, 10000)
        or result.mass_difference != Fraction(9, 10000)
        or result.maximum_extent_millimolar != Fraction(2, 5)
    ):
        raise ValueError("KIN-008 exact observation-class reconstruction changed")
    return result


__all__ = ("PeakXObservationClass", "SUPPLEMENT", "reconstruct_peak_x_observation_class")
