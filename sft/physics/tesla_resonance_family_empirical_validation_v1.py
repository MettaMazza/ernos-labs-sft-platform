"""Direct source reconstruction plus sealed empirical custody for Claim 082."""

from dataclasses import replace
from html import unescape
import json
from pathlib import Path

from pypdf import PdfReader

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator
from sft.physics.tesla_resonance_family_empirical_v1 import (
    PREREGISTRATION_HASH,
    PREREGISTRATION_PATH,
    SOURCE_FILES,
    SOURCE_HASH,
    SOURCE_PATH,
    SPEC,
)


def pdf_text(path: Path) -> str:
    return " ".join(
        " ".join((page.extract_text() or "").split())
        for page in PdfReader(str(path)).pages
    ).lower()


def normalized_html(path: Path) -> str:
    return " ".join(unescape(path.read_text(encoding="utf-8", errors="replace")).split()).lower()


class TeslaResonanceFamilyMeasurementValidator(BlindExternalMeasurementValidator):
    def __init__(self, root: Path):
        super().__init__(root, SPEC)

    def direct_source_certificate(self) -> dict[str, object]:
        root = self.root
        if hash_file(root / SOURCE_PATH) != SOURCE_HASH:
            raise ValueError("Tesla-family source record differs from its bound identity")
        if hash_file(root / PREREGISTRATION_PATH) != PREREGISTRATION_HASH:
            raise ValueError("Tesla-family source preregistration differs from its frozen identity")
        for path, expected in SOURCE_FILES:
            if hash_file(root / path) != expected:
                raise ValueError(f"Tesla-family source differs: {path}")

        record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
        quarter = pdf_text(root / SOURCE_FILES[0][0])
        diamond = normalized_html(root / SOURCE_FILES[1][0])
        transfer = pdf_text(root / SOURCE_FILES[2][0])
        earth = pdf_text(root / SOURCE_FILES[3][0])
        satellite = normalized_html(root / SOURCE_FILES[4][0])

        checks = {
            "five_source_rows_retained": len(record["rows"]) == len(record["sources"]) == 5,
            "all_registered_classifications_retained": {row["classification"] for row in record["rows"]} == {
                "favorable-with-apparatus-boundary",
                "favorable-with-distinct-speed-control",
                "favorable-with-loss-and-fidelity-boundary",
                "favorable-natural-cavity-with-adverse-generalization-control",
                "favorable-detection-with-delivery-type-adverse-record",
            },
            "quarter_wave_source_measured": all(token in quarter for token in (
                "quarter-wave concentric transmission",
                "third harmonic of this funda",
                "other odd harmonics",
                "as actually obtained by measurement",
            )),
            "orientation_rows_measured": all(token in diamond for token in (
                "round-trip travel time",
                "divided into twice the sample thickness",
                "longitudinal",
                "transverse, 1",
                "transverse, 2",
            )),
            "resonant_transfer_measured": all(token in transfer for token in (
                "resonant cavity formed by an open-ended superconducting transmission line",
                "transferred and stored as a nonclassical photon state",
                "retrieved later by the second qubit",
                "cavity decay rate",
                "fidelity of the state transfer protocol",
            )),
            "earth_cavity_modes_retained": all(token in earth for token in (
                "cavity between the earth and the ionosphere",
                "approximately at 7.8 cycles per second",
                "14, 21, 26, 33, 39, and 45 hz",
                "daily variation of about",
            )),
            "power_claim_remains_proposed_not_measured": all(token in earth for token in (
                "possible applications",
                "wireless transmission of power",
                "free\u201d energy source",
            )),
            "satellite_detection_and_delivery_mismatch_retained": (
                "observation of schumann resonances in the earth's ionosphere" in satellite
                and "first time, schumann resonance signatures detected well beyond" in satellite
                and record["sources"][4]["delivered_media_type"] == "text/html"
            ),
            "formal_and_empirical_boundaries_complete": (
                len(record["source_power"]["establishes"]) == 5
                and len(record["source_power"]["does_not_establish"]) == 6
            ),
        }
        return {
            "checks": checks,
            "all_passed": all(checks.values()),
            "source_ids": tuple(source["source_id"] for source in record["sources"]),
            "source_hashes": tuple((path, expected) for path, expected in SOURCE_FILES),
            "observation_row_count": len(record["rows"]),
            "unsupported_power_inference_rejected": "source-free energy creation" in record["source_power"]["does_not_establish"],
        }

    def validate(self, sealed):
        direct = self.direct_source_certificate()
        if not direct["all_passed"] or not direct["unsupported_power_inference_rejected"]:
            raise ValueError("Tesla-family direct source reconstruction failed")
        base = super().validate(sealed)
        measurements = base.measurements + tuple(
            f"direct source check {name}: {passed}"
            for name, passed in direct["checks"].items()
        ) + (
            "all five source records and every limitation/adverse row retained",
            "source-free or unlimited power inference rejected as unsupported by the captured measurements",
        )
        return replace(
            base,
            all_rows_preserved=base.all_rows_preserved and direct["observation_row_count"] == 5,
            measurements=measurements,
            measurement_receipt_hash=sha256_identity((base.measurement_receipt_hash, direct)),
            passed=base.passed and direct["all_passed"] and direct["unsupported_power_inference_rejected"],
        )


__all__ = ("TeslaResonanceFamilyMeasurementValidator",)
