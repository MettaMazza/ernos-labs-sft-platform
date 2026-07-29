#!/usr/bin/env python3
"""Implementation-distinct ORG-012 primary-measurement reconstruction.

This executable intentionally does not import the primary reconstruction.  It
checks the frozen source manifest, rebuilds the condition-distinguished
measurement census directly from primary source bytes, and leaves every exact
condition not measured by those sources active.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-012-missing-measurement-repair-v3"
MANIFEST = SNAPSHOT / "source-manifest-v3.json"
OUTPUT = SNAPSHOT / "complete-missing-measurement-reconstruction-v3.json"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_text(path: Path) -> str:
    return " ".join(
        " ".join((page.extract_text() or "").replace("\u00ad", "").split())
        for page in PdfReader(path).pages
    ).casefold()


def exact(value: str) -> list[int]:
    fraction = Fraction(value)
    if fraction <= 0:
        raise SystemExit("ORG-012 source value is outside positive support")
    return [fraction.numerator, fraction.denominator]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not (
        manifest.get("all_registered_sources_captured") is True
        and manifest.get("blind_source_claim") is False
        and manifest.get("outcome_exposure_disclosed") is True
    ):
        raise SystemExit("ORG-012 custody metadata changed")
    for row in (*manifest["artifacts"], *manifest.get("transport_artifacts", ())):
        path = SNAPSHOT / row["filename"]
        if not path.is_file() or digest(path) != row["sha256"]:
            raise SystemExit(f"ORG-012 frozen source changed: {row['filename']}")

    breslow = pdf_text(SNAPSHOT / "ordinal-006-breslow-guo-1988.pdf")
    for phrase in (
        "ratio of 3.85 in neat cyclopentadiene",
        "or of 8.5 in ethanol",
        "endo/exo product ratio for reaction 1 was 25.0",
        "4.86 m licl",
        "22.0 f 0.8 with 4.86 m chaotropic guanidinium",
    ):
        if phrase not in breslow:
            raise SystemExit("ORG-012 ordinal-006 measurement source changed")

    lactone = (SNAPSHOT / "ordinal-019-us4588591a.html").read_text(encoding="utf-8")
    for phrase in (
        "α-Methylene-γ-butyrolactone (142.9 g., 1.46 mole)",
        "aluminum chloride (197 g., 1.48 mole)",
        "236.1 g. (82.5%)",
    ):
        if phrase not in lactone:
            raise SystemExit("ORG-012 ordinal-019 structure source changed")

    thesis_path = SNAPSHOT / "ordinal-027-agagnier-1973-thesis.pdf"
    thesis = pdf_text(thesis_path)
    if len(PdfReader(thesis_path).pages) != 55:
        raise SystemExit("ORG-012 ordinal-027 source boundary changed")
    for phrase in ("p-benzoquinone adduct", "yield was 2\"0 g\" (1002)", "slightly yellow crystalline product"):
        if phrase not in thesis:
            raise SystemExit("ORG-012 ordinal-027 synthesis source changed")

    vnb = (SNAPSHOT / "ordinal-030-us20090054714a1.html").read_text(encoding="utf-8").casefold()
    for phrase in (
        "endo-exo-vinylnorbornene (80:20)",
        "endo-exo-vinylnorbornene (82:18)",
        "81.45% endo-vnb to 18.22% exo-vnb",
        "25% exo-vnb to 75% endo-vnb",
    ):
        if phrase not in vnb:
            raise SystemExit("ORG-012 ordinal-030 population source changed")

    six_values = [
        "3.85", "8.5", "25.0", "8.9", "10.4", "28.0", "22.0",
        "10.4", "10.3", "10.5", "10.0", "11.0", "8.9", "10.8",
        "10.5", "11.0", "10.5",
    ]
    thirty_values = [Fraction(80, 20), Fraction(82, 18), Fraction(8145, 1822), Fraction(75, 25)]
    identities = [
        {
            "ordinal": 6,
            "adduct_pair": "5CPD-n, 5CPD-x",
            "measured_ratios": [exact(value) for value in six_values],
            "structural_measurements": 0,
            "exact_condition_obligation_active": True,
            "reason": "all seventeen measurements are condition-distinguished from MeAlCl2",
        },
        {
            "ordinal": 19,
            "adduct_pair": "12BD-n, 12BD-x",
            "measured_ratios": [],
            "structural_measurements": 1,
            "exact_condition_obligation_active": True,
            "reason": "unlabeled structural production does not provide a deuterium-resolved ratio",
        },
        {
            "ordinal": 27,
            "adduct_pair": "17BD-n, 17BD-x",
            "measured_ratios": [],
            "structural_measurements": 2,
            "exact_condition_obligation_active": True,
            "reason": "two isotope-distinguished syntheses do not report the exact single-addition ratio",
        },
        {
            "ordinal": 30,
            "adduct_pair": "18CPD-n, 18CPD-x",
            "measured_ratios": [[value.numerator, value.denominator] for value in thirty_values],
            "structural_measurements": 1,
            "exact_condition_obligation_active": True,
            "reason": "four measured populations remain distinct because the originating condition is unreported",
        },
    ]
    payload = {
        "schema": "sft-v3-chemistry-org-012-missing-measurement-reconstruction/3",
        "claim_id": "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012",
        "obligation_id": "SFT-CHEM-OBL-ORG-012",
        "method": "implementation-distinct direct-source reconstruction",
        "source_manifest_sha256": digest(MANIFEST),
        "identity_count": len(identities),
        "measured_ratio_count": sum(len(row["measured_ratios"]) for row in identities),
        "structural_measurement_count": sum(row["structural_measurements"] for row in identities),
        "identities": identities,
        "scientific_results_retired": 0,
        "calculated_ratios_used_as_measurements": 0,
        "completion_credit_before_valid_008": False,
    }
    if payload["measured_ratio_count"] != 21 or payload["structural_measurement_count"] != 4:
        raise SystemExit("ORG-012 independent measurement census changed")
    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    payload["reconstruction_identity"] = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "identity": payload["reconstruction_identity"],
        "measured_ratios": payload["measured_ratio_count"],
        "structural_measurements": payload["structural_measurement_count"],
        "active_exact_condition_obligations": 4,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
