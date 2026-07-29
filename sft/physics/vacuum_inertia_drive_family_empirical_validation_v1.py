"""Direct source reconstruction plus sealed custody for empirical Claim 087."""

from dataclasses import replace
from html import unescape
import json
from pathlib import Path

from pypdf import PdfReader

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import BlindExternalMeasurementValidator
from sft.physics.vacuum_inertia_drive_family_empirical_v1 import (
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


def ocr_text(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return " ".join(
        line["text"]
        for page in payload["pages"]
        for line in page["lines"]
    ).lower()


class VacuumInertiaDriveFamilyMeasurementValidator(BlindExternalMeasurementValidator):
    def __init__(self, root: Path):
        super().__init__(root, SPEC)

    def direct_source_certificate(self) -> dict[str, object]:
        root = self.root
        if hash_file(root / SOURCE_PATH) != SOURCE_HASH:
            raise ValueError("vacuum/inertia source record differs from its bound identity")
        if hash_file(root / PREREGISTRATION_PATH) != PREREGISTRATION_HASH:
            raise ValueError("vacuum/inertia preregistration differs from its frozen identity")
        for path, expected in SOURCE_FILES:
            if hash_file(root / path) != expected:
                raise ValueError(f"vacuum/inertia source differs: {path}")

        record = json.loads((root / SOURCE_PATH).read_text(encoding="utf-8"))
        pax = pdf_text(root / SOURCE_FILES[0][0])
        prosecution = ocr_text(root / SOURCE_FILES[2][0])
        zero_point = normalized_html(root / SOURCE_FILES[3][0])
        casimir = normalized_html(root / SOURCE_FILES[4][0])
        microscope = normalized_html(root / SOURCE_FILES[5][0])

        checks = {
            "five_source_identities_retained": len(record["sources"]) == 5,
            "all_classifications_retained": {source["classification"] for source in record["sources"]} == {
                "mechanism-described-with-explicit-no-prototype-boundary",
                "official-concept-and-prosecution-record-with-proposed-experiment-boundary",
                "measured-nonempty-ground-response-with-work-and-pump-boundaries",
                "measured-boundary-dependent-vacuum-interaction",
                "measured-inertial-gravitational-unity-with-engineering-scope-control",
            },
            "navy_mechanism_description_retained": all(token in pax for token in (
                "high energy, electromagnetic fields interact strongly with the vacuum",
                "mechanism of transfer of vibrational energy between the fields",
                "coupling of hyper-frequency axial spin with hyper-frequency vibrations",
            )),
            "navy_no_prototype_status_retained": all(token in pax for token in (
                "this is a theoretical concept",
                "no prototype in existence, as yet",
                "funding for experimental investigation",
            )),
            "prosecution_mechanism_retained": all(token in prosecution for token in (
                "local vacuum polarization",
                "accelerated high frequency vibration",
                "accelerated high frequency axial rotation",
                "inertial mass reduction can be achieved via manipulation",
            )),
            "prosecution_proposed_experiment_status_retained": all(token in prosecution for token in (
                "only a theoretical concept",
                "a simple laboratory experiment is proposed",
            )),
            "nist_ground_and_pump_boundary_retained": all(token in zero_point for token in (
                "exactly one quantum of zero-point fluctuations",
                "cannot do any real work",
                "coherent pumping of microwave radiation",
                "you can never transfer real energy out of the 'vacuum fluctuations'",
            )),
            "nist_casimir_boundary_response_retained": all(token in casimir for token in (
                "casimir force",
                "accurately measured and calculated for simple flat conductors",
                "control the casimir force",
            )),
            "cnes_unity_and_scope_record_retained": all(token in microscope for token in (
                "equality of gravitational and inertial mass",
                "precision on the order of 10",
                "two concentric cylindrical test masses made of different materials",
            )),
            "complete_power_and_scope_boundary_retained": (
                len(record["complete_comparison_vector"]) == 8
                and len(record["source_power"]["establishes"]) == 5
                and len(record["source_power"]["does_not_establish"]) == 6
                and "source-free energy creation" in record["source_power"]["does_not_establish"]
                and "a completed public measurement of controllable inertial-mass reduction" in record["source_power"]["does_not_establish"]
            ),
        }
        return {
            "checks": checks,
            "all_passed": all(checks.values()),
            "source_ids": tuple(source["source_id"] for source in record["sources"]),
            "source_hashes": tuple((path, expected) for path, expected in SOURCE_FILES),
            "source_count": len(record["sources"]),
            "apparatus_measurement_not_invented": "a completed public measurement of controllable inertial-mass reduction" in record["source_power"]["does_not_establish"],
            "formal_channel_not_falsified_by_absent_apparatus_row": "that absence of a public prototype measurement falsifies the sealed exact structural channel" in record["source_power"]["does_not_establish"],
        }

    def validate(self, sealed):
        direct = self.direct_source_certificate()
        if not all((direct["all_passed"], direct["apparatus_measurement_not_invented"], direct["formal_channel_not_falsified_by_absent_apparatus_row"])):
            raise ValueError("vacuum/inertia direct source reconstruction failed")
        base = super().validate(sealed)
        measurements = base.measurements + tuple(
            f"direct source check {name}: {passed}"
            for name, passed in direct["checks"].items()
        ) + (
            "all official source identities and every favorable, adverse, absent, untested and scope-limiting row retained",
            "no public apparatus measurement invented and no formal channel falsification inferred from its absence",
        )
        return replace(
            base,
            all_rows_preserved=base.all_rows_preserved and direct["source_count"] == 5,
            measurements=measurements,
            measurement_receipt_hash=sha256_identity((base.measurement_receipt_hash, direct)),
            passed=base.passed and direct["all_passed"] and direct["apparatus_measurement_not_invented"] and direct["formal_channel_not_falsified_by_absent_apparatus_row"],
        )


__all__ = ("VacuumInertiaDriveFamilyMeasurementValidator",)
