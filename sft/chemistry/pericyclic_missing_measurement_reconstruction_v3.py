"""Distinct-route ORG-012 reconstruction without first-failure retirement.

The four blank rows in the originating table are non-experiments.  This module
retains that fact, reconstructs every located condition-distinguished primary
measurement, and keeps every still-unmeasured exact-condition ratio active.
Calculated ratios never substitute for measurements.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader

from sft.chemistry.pericyclic_missing_measurement_status_v2 import (
    reconstruct_missing_measurements,
)


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = (
    ROOT
    / "experiments/external_sources/chemistry/snapshots"
    / "org-012-missing-measurement-repair-v3"
)
MANIFEST = SNAPSHOT / "source-manifest-v3.json"


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _pdf_text(path: Path) -> str:
    return " ".join(
        " ".join((page.extract_text() or "").replace("\u00ad", "").split())
        for page in PdfReader(path).pages
    )


def _exact(value: str) -> Fraction:
    result = Fraction(value)
    if result <= 0:
        raise ValueError("SFT empirical support must be positive")
    return result


@dataclass(frozen=True)
class MeasuredRatio:
    source_identity: str
    condition_identity: str
    first_to_second: Fraction
    uncertainty: Fraction | None
    exact_target_condition: bool = False


@dataclass(frozen=True)
class StructuralMeasurement:
    source_identity: str
    condition_identity: str
    measured_result: str
    exact_target_condition: bool = False


@dataclass(frozen=True)
class MissingIdentityReconstruction:
    ordinal: int
    adduct_pair: str
    originating_status: str
    measured_ratios: tuple[MeasuredRatio, ...]
    structural_measurements: tuple[StructuralMeasurement, ...]
    exact_condition_ratio_status: str
    calculated_ratio_used_as_measurement: bool = False
    scientific_result_retired: bool = False


def _verify_manifest() -> dict[str, object]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (
        manifest.get("all_registered_sources_captured") is not True
        or manifest.get("blind_source_claim") is not False
        or manifest.get("outcome_exposure_disclosed") is not True
    ):
        raise ValueError("ORG-012 distinct-route custody changed")
    for row in manifest["artifacts"]:
        path = SNAPSHOT / row["filename"]
        if not path.is_file() or _digest(path) != row["sha256"]:
            raise ValueError(f"ORG-012 repair source changed: {row['filename']}")
    for row in manifest.get("transport_artifacts", ()):
        path = SNAPSHOT / row["filename"]
        if not path.is_file() or _digest(path) != row["sha256"]:
            raise ValueError(f"ORG-012 transport evidence changed: {row['filename']}")
    return manifest


def reconstruct_missing_identity_measurements() -> tuple[MissingIdentityReconstruction, ...]:
    _verify_manifest()
    blanks = reconstruct_missing_measurements()
    if tuple(row.ordinal for row in blanks) != (6, 19, 27, 30):
        raise ValueError("ORG-012 originating blank vector changed")

    breslow = _pdf_text(SNAPSHOT / "ordinal-006-breslow-guo-1988.pdf")
    required_breslow = (
        "methyl vinyl ketone with 1,3-cyclopentadiene",
        "endo/exo product ratio for reaction 1 was 25.0",
        "ratio of 3.85 in neat cyclopentadiene",
        "or of 8.5 in ethanol",
        "ethylene glycol",
        "formamide",
    )
    if not all(phrase.casefold() in breslow.casefold() for phrase in required_breslow):
        raise ValueError("ORG-012 ordinal-006 primary measurement vector changed")
    ordinal_006_ratios = (
        MeasuredRatio("Breslow-Guo-1988-Table-II", "neat-cyclopentadiene", _exact("3.85"), None),
        MeasuredRatio("Breslow-Guo-1988-Table-II", "ethanol", _exact("8.5"), None),
        MeasuredRatio("Breslow-Guo-1988-Table-II", "water", _exact("25.0"), None),
        MeasuredRatio("Breslow-Guo-1988-Table-II", "formamide", _exact("8.9"), None),
        MeasuredRatio("Breslow-Guo-1988-Table-II", "ethylene-glycol", _exact("10.4"), None),
        MeasuredRatio("Breslow-Guo-1988-text", "water-plus-4.86M-LiCl", _exact("28.0"), _exact("0.4")),
        MeasuredRatio("Breslow-Guo-1988-text", "water-plus-4.86M-guanidinium-chloride", _exact("22.0"), _exact("0.8")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "ethylene-glycol-none", _exact("10.4"), _exact("1.2")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "ethylene-glycol-LiCl-1.02M", _exact("10.3"), _exact("0.7")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "ethylene-glycol-LiClO4-1.00M", _exact("10.5"), _exact("0.6")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "ethylene-glycol-GnCl-1.05M", _exact("10.0"), _exact("0.7")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "ethylene-glycol-Bu4NBr-0.50M", _exact("11.0"), _exact("0.1")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "formamide-none", _exact("8.9"), _exact("0.4")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "formamide-LiCl-2.09M", _exact("10.8"), _exact("0.4")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "formamide-LiClO4-2.00M", _exact("10.5"), _exact("0.3")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "formamide-GnCl-2.08M", _exact("11.0"), _exact("0.5")),
        MeasuredRatio("Breslow-Guo-1988-Table-V", "formamide-Bu4NBr-0.50M", _exact("10.5"), _exact("0.2")),
    )

    lactone_patent = (SNAPSHOT / "ordinal-019-us4588591a.html").read_text(encoding="utf-8")
    required_lactone = (
        "α-Methylene-γ-butyrolactone (142.9 g., 1.46 mole)",
        "aluminum chloride (197 g., 1.48 mole)",
        "butadiene",
        "all of the starting lactone had been consumed",
        "236.1 g. (82.5%)",
        "C<sub>9</sub> H<sub>12</sub> O<sub>2</sub>",
    )
    if not all(phrase in lactone_patent for phrase in required_lactone):
        raise ValueError("ORG-012 ordinal-019 primary structural vector changed")

    thesis_path = SNAPSHOT / "ordinal-027-agagnier-1973-thesis.pdf"
    thesis = _pdf_text(thesis_path)
    required_thesis = (
        "Butadiene-1 ,I,4,4-d",
        "p-benzoquinone Adduct",
        "heated a'L I2OoC for 24 hours",
        "Yield was 2\"0 g\" (1002)",
        "Butad.iene-2, 3-d2-p-benzoquinone Add.uct",
        "slightly yellow crystalline product",
    )
    if not all(phrase.casefold() in thesis.casefold() for phrase in required_thesis):
        raise ValueError("ORG-012 ordinal-027 primary synthesis vector changed")
    if len(PdfReader(thesis_path).pages) != 55:
        raise ValueError("ORG-012 ordinal-027 thesis page boundary changed")

    vnb_patent = (SNAPSHOT / "ordinal-030-us20090054714a1.html").read_text(encoding="utf-8")
    required_vnb = (
        "commercially prepared via a Diels-Alder reaction employing cyclopentadiene",
        "1,3-butadiene (BD) where vinylnorbornene (VNB) is being prepared",
        "Endo-Exo-Vinylnorbornene (80:20)",
        "Endo-Exo-Vinylnorbornene (82:18)",
        "81.45% endo-VNB to 18.22% exo-VNB",
        "25% exo-VNB to 75% endo-VNB",
    )
    if not all(phrase.casefold() in vnb_patent.casefold() for phrase in required_vnb):
        raise ValueError("ORG-012 ordinal-030 primary population vector changed")
    ordinal_030_ratios = (
        MeasuredRatio("US20090054714A1", "commercial-Aldrich-heading", _exact("4"), None),
        MeasuredRatio("US20090054714A1", "commercial-Ineos-heading", _exact("82") / _exact("18"), None),
        MeasuredRatio("US20090054714A1", "Nisseki-GC-with-retained-impurities", _exact("81.45") / _exact("18.22"), None),
        MeasuredRatio("US20090054714A1", "Ineos-batch-record", _exact("3"), None),
    )

    result = (
        MissingIdentityReconstruction(
            ordinal=6,
            adduct_pair="5CPD-n, 5CPD-x",
            originating_status="non-experiment-in-originating-table",
            measured_ratios=ordinal_006_ratios,
            structural_measurements=(),
            exact_condition_ratio_status="active-MeAlCl2-condition-measurement-not-located",
        ),
        MissingIdentityReconstruction(
            ordinal=19,
            adduct_pair="12BD-n, 12BD-x",
            originating_status="calculated-only-in-originating-table",
            measured_ratios=(),
            structural_measurements=(
                StructuralMeasurement(
                    "US4588591A-Example-2A",
                    "unlabeled-butadiene-plus-AlCl3-bound-alpha-methylene-gamma-butyrolactone",
                    "complete starting-lactone consumption; product 236.1 g; isolated yield 82.5 percent",
                ),
            ),
            exact_condition_ratio_status="active-deuterium-resolved-ratio-measurement-not-located",
        ),
        MissingIdentityReconstruction(
            ordinal=27,
            adduct_pair="17BD-n, 17BD-x",
            originating_status="calculated-only-in-originating-table",
            measured_ratios=(),
            structural_measurements=(
                StructuralMeasurement(
                    "Agagnier-1973-thesis",
                    "1,3-butadiene-1,1,4,4-d4-plus-p-benzoquinone-double-addition",
                    "white crystalline adduct; 2.0 g; reported quantitative yield",
                ),
                StructuralMeasurement(
                    "Agagnier-1973-thesis",
                    "1,3-butadiene-2,3-d2-plus-p-benzoquinone-double-addition",
                    "slightly yellow crystalline adduct; 1.17 g; reported 90 percent yield",
                ),
            ),
            exact_condition_ratio_status="active-E,E-1,4-dideutero-single-addition-ratio-measurement-not-located",
        ),
        MissingIdentityReconstruction(
            ordinal=30,
            adduct_pair="18CPD-n, 18CPD-x",
            originating_status="calculated-only-in-originating-table",
            measured_ratios=ordinal_030_ratios,
            structural_measurements=(
                StructuralMeasurement(
                    "US20090054714A1",
                    "cyclopentadiene-plus-1,3-butadiene-commercial-production-identity",
                    "both endo-VNB and exo-VNB product classes explicitly measured by GC or NMR",
                ),
            ),
            exact_condition_ratio_status="condition-distinguished-measured-populations-located-originating-condition-unreported",
        ),
    )
    if any(row.calculated_ratio_used_as_measurement or row.scientific_result_retired for row in result):
        raise ValueError("ORG-012 unlawful retirement or calculation substitution")
    if sum(len(row.measured_ratios) for row in result) != 21:
        raise ValueError("ORG-012 measured ratio census changed")
    if sum(len(row.structural_measurements) for row in result) != 4:
        raise ValueError("ORG-012 structural measurement census changed")
    return result


__all__ = (
    "MANIFEST",
    "MeasuredRatio",
    "MissingIdentityReconstruction",
    "StructuralMeasurement",
    "reconstruct_missing_identity_measurements",
)
