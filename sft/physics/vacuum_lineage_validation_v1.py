"""Post-seal authoritative validation of the V3 vacuum lineage.

This module opens the registered NIST, PDG and CNES snapshots only after the
six formal receipts exist.  It preserves favorable, indirect, untested and
adverse rows as one complete vector.  An empirical classification is not
allowed to rewrite any formal receipt.
"""

from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from sft.engine.source import hash_file
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.measured_value import exact_decimal
from sft.physics.vacuum_lineage_laws_v1 import (
    VACUUM_CYCLE_ID,
    VACUUM_EXTRACTION_ID,
    VACUUM_FLOOR_ID,
    VACUUM_INERTIA_ID,
    VACUUM_POLARIZATION_ID,
)


FLOOR_VALIDATION_ID = "SFT-PHYS-VALIDATION-VACUUM-FLOOR-003"
POLARIZATION_VALIDATION_ID = "SFT-PHYS-VALIDATION-VACUUM-POLARIZATION-003"
INERTIA_VALIDATION_ID = "SFT-PHYS-VALIDATION-VACUUM-INERTIA-003"
EXTRACTION_VALIDATION_ID = "SFT-PHYS-VALIDATION-VACUUM-EXTRACTION-003"

SOURCE_ID = "VACUUM-LINEAGE-AUTHORITATIVE-2015-2026"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/vacuum-lineage-source-record.json"
SOURCE_HASH = "sha256:327696985650aebaa20436e9da1d7f20f9bbff4205f9e7146ec8bd887535f3a9"

FLOOR_LABEL = "nonempty-ground-confirmed__casimir-boundary-force-confirmed__half-offset-not-directly-isolated"
POLARIZATION_LABEL = "inverse-coupling-decreases-with-scale__effective-coupling-running-direction-confirmed"
INERTIA_LABEL = "equivalence-unity-anchor-confirmed-to-mission-precision__vacuum-control-untested"
EXTRACTION_LABEL = "positive-formal-outward-transfer-sealed__standalone-vacuum-work-not-observed__complete-returned-cycle-consistent"

COMPONENT_HASHES = {
    "nist-zero-point-fluctuations-2015.html": "sha256:e829ac861cca9f84f43f752465b4ee8801fb07fac76e41f0df4de98ff5f54832",
    "nist-casimir-vacuum-forces-2013.html": "sha256:906e3d92d1e664daa5070bcf8cdafa4bf20fc8bb003346946870fa9b64ee7b1f",
    "pdg-2025-electroweak-model.pdf": "sha256:8642888a3408d8c57fc673b379325b07f02948135491f64a2e42320e8929320a",
    "cnes-microscope-final.html": "sha256:65a86753705aaa80f819e833d1ca4e13f0491e56b58a218c4cddb492c9887f12",
}


def authoritative_record(root: Path) -> dict[str, object]:
    path = root / SOURCE_PATH
    if hash_file(path) != SOURCE_HASH:
        raise ValueError("vacuum lineage source record identity changed")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("record_id") != SOURCE_ID:
        raise ValueError("vacuum lineage source record ID changed")
    sources = payload.get("sources")
    if not isinstance(sources, list) or len(sources) != 4:
        raise ValueError("vacuum lineage record must retain all four authoritative sources")
    for source in sources:
        snapshot = source["snapshot"]
        expected = COMPONENT_HASHES.get(snapshot)
        if expected is None or hash_file(path.parent / snapshot) != expected:
            raise ValueError("vacuum lineage component snapshot identity changed")
    return payload


def source_by_id(root: Path) -> dict[str, dict[str, object]]:
    return {row["source_id"]: row for row in authoritative_record(root)["sources"]}


def row_by_quantity(source: dict[str, object], quantity: str) -> dict[str, str]:
    rows = tuple(row for row in source["rows"] if row["quantity"] == quantity)
    if len(rows) != 1:
        raise ValueError(f"authoritative quantity must occur exactly once: {quantity}")
    return rows[0]


def floor_classification(root: Path) -> str:
    sources = source_by_id(root)
    nist = sources["NIST-ZERO-POINT-FLUCTUATIONS-2015"]
    casimir = sources["NIST-CASIMIR-VACUUM-FORCES-2013"]
    nonempty = row_by_quantity(nist, "ground-state residual fluctuation support")["comparison_class"]
    boundary = row_by_quantity(casimir, "Casimir interaction")["comparison_class"]
    if nonempty != "nonempty-ground-support-confirmed" or boundary != "boundary-dependent-vacuum-force-confirmed":
        return "vacuum-floor-authoritative-classification-changed"
    return FLOOR_LABEL


def polarization_classification(root: Path) -> tuple[str, dict[str, Fraction]]:
    pdg = source_by_id(root)["PDG-ELECTROMAGNETIC-RUNNING-2025"]
    low = row_by_quantity(pdg, "inverse electromagnetic coupling at the Thomson limit")
    high = row_by_quantity(pdg, "inverse running electromagnetic coupling at the Z scale in the five-flavour MS scheme")
    direct = row_by_quantity(pdg, "direct running observation")
    low_central = exact_decimal(low["central"])
    low_width = exact_decimal(low["standard_uncertainty"])
    high_central = exact_decimal(high["central"])
    high_width = exact_decimal(high["standard_uncertainty"])
    values = {
        "low_inverse_lower": low_central - low_width,
        "low_inverse_upper": low_central + low_width,
        "high_inverse_lower": high_central - high_width,
        "high_inverse_upper": high_central + high_width,
    }
    direction = values["low_inverse_lower"] > values["high_inverse_upper"]
    observed = direct["comparison_class"] == "closer-probe-effective-coupling-increase-confirmed"
    return (POLARIZATION_LABEL if direction and observed else "vacuum-polarization-direction-changed"), values


def inertia_classification(root: Path) -> str:
    microscope = source_by_id(root)["CNES-MICROSCOPE-FINAL-2022"]
    row = row_by_quantity(microscope, "equivalence of gravitational and inertial response")
    if row["reported_precision"] != "1e-15" or row["comparison_class"] != "unity-response-anchor-confirmed":
        return "vacuum-inertia-anchor-classification-changed"
    return INERTIA_LABEL


def extraction_classification(root: Path) -> str:
    nist = source_by_id(root)["NIST-ZERO-POINT-FLUCTUATIONS-2015"]
    work = row_by_quantity(nist, "removable ground-state energy")["comparison_class"]
    pump = row_by_quantity(nist, "physical amplification boundary")["comparison_class"]
    if work != "free-standing-vacuum-work-not-observed" or pump != "external-pump-energy-retained":
        return "vacuum-extraction-authoritative-classification-changed"
    return EXTRACTION_LABEL


_ROOT = Path(__file__).resolve().parents[2]
_floor = floor_classification(_ROOT)
_polarization, _running = polarization_classification(_ROOT)
_inertia = inertia_classification(_ROOT)
_extraction = extraction_classification(_ROOT)


def common_dependencies(formal_id: str) -> tuple[str, ...]:
    return (
        formal_id,
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    )


def target(label: str, suffix: str) -> tuple[ExternalTargetRow, ...]:
    return (ExternalTargetRow(f"VACUUM-LINEAGE-{suffix}", SOURCE_ID, "complete registered NIST/PDG/CNES source record", label),)


FLOOR_SPEC = EmpiricalPhysicsSpec(
    claim_id=FLOOR_VALIDATION_ID,
    title="Post-seal NIST test of the nonempty vacuum floor",
    statement="After the half-One floor and oscillator support are sealed, the full NIST ground-state and Casimir record confirms nonempty residual quantum support and a boundary-dependent vacuum interaction. The absolute half-spacing energy offset is not isolated as a separately measurable scalar, and that boundary is retained.",
    dependencies=common_dependencies(VACUUM_FLOOR_ID),
    generation_rule="Generate the complete eight-axis post-seal vacuum-floor comparison product.",
    grammar_boundary="Every registered NIST ground-state and Casimir row, including the direct-measurement boundary on the absolute half-spacing offset.",
    dimensions=empirical_dimensions("sealed-vacuum-floor-versus-complete-NIST-record", "Every nonempty-ground, boundary-force and direct-observability row is retained."),
    exact_result="NIST confirms nonempty ground fluctuations and boundary-dependent vacuum force; the sealed half-One coefficient remains a formal structural value rather than a separately isolated measured scalar.",
    induction_base="The first NIST row records calibrated nonempty ground-state fluctuation support.",
    induction_step="The Casimir and observability rows are appended without converting an indirect or model-dependent record into a direct coefficient measurement.",
    exclusions=("no target access before the formal seal", "no claim that Casimir force alone measures the half-One coefficient", "no deletion of the direct-observability boundary"),
    operational_witnesses=(("floor-vector", "The complete authoritative floor classification is retained.", _floor == FLOOR_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-VACUUM-FLOOR-003",
    expected_observation_label=FLOOR_LABEL,
    target_rows=target(FLOOR_LABEL, "FLOOR"),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="NIST ceases to report nonempty ground support or boundary-dependent vacuum interaction, a source hash changes, or the half-offset is falsely promoted from indirect evidence to a direct scalar measurement.",
)


POLARIZATION_SPEC = EmpiricalPhysicsSpec(
    claim_id=POLARIZATION_VALIDATION_ID,
    title="Post-seal PDG test of the vacuum-polarization running direction",
    statement="The sealed structural direction is compared with both complete PDG inverse-coupling intervals. The low-energy inverse interval lies wholly above the Z-scale interval, so the coupling itself increases with closer/higher-energy probing; PDG also retains direct LEP observations of running.",
    dependencies=common_dependencies(VACUUM_POLARIZATION_ID),
    generation_rule="Generate the complete eight-axis post-seal electromagnetic-running comparison product.",
    grammar_boundary="Both full PDG inverse-coupling intervals plus the direct-running observation, with exact interval ordering and no beta-coefficient claim.",
    dimensions=empirical_dimensions("sealed-running-direction-versus-complete-PDG-intervals", "Exact positive inverse-interval ordering fixes the observed direction and retains the direct LEP row."),
    exact_result="The complete PDG intervals confirm the sealed direction: inverse alpha decreases from 137.035999084(21) to 127.930(8), hence effective alpha increases with scale.",
    induction_base="The Thomson-limit row retains its exact central value and uncertainty.",
    induction_step="The Z-scale and direct-observation rows are appended; neither may select or extend the structural law.",
    exclusions=("no measured value accessible before seal", "no fitted running curve", "no omission of either uncertainty", "no claim of an exact beta coefficient from the two endpoints"),
    operational_witnesses=(
        ("nonoverlap", "The complete low-energy inverse interval lies above the Z-scale interval.", _running["low_inverse_lower"] > _running["high_inverse_upper"]),
        ("direct-observation", "The PDG direct-running row is retained.", _polarization == POLARIZATION_LABEL),
    ),
    experiment_id="SFT-EXP-PHYS-VALIDATION-VACUUM-POLARIZATION-003",
    expected_observation_label=POLARIZATION_LABEL,
    target_rows=target(POLARIZATION_LABEL, "POLARIZATION"),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="The authoritative inverse-coupling intervals reverse or overlap contrary to the registered direction, direct running is withdrawn, a row/hash changes, or a fitted beta law is substituted for the sealed structural claim.",
)


INERTIA_SPEC = EmpiricalPhysicsSpec(
    claim_id=INERTIA_VALIDATION_ID,
    title="Post-seal MICROSCOPE anchor test of vacuum-inertia unity",
    statement="The exact vacuum/inertia unity relation is compared with CNES MICROSCOPE's completed equivalence-principle mission. Universal inertial/gravitational response is supported to the reported 10^-15 mission precision. The stronger claim that a vacuum carrier can be engineered to control inertia was not tested and remains a standing prediction.",
    dependencies=common_dependencies(VACUUM_INERTIA_ID),
    generation_rule="Generate the complete eight-axis post-seal vacuum/inertia anchor comparison product.",
    grammar_boundary="The complete CNES mission identity, response class and reported precision together with the explicit untested engineering-control boundary.",
    dimensions=empirical_dimensions("sealed-unity-relation-versus-MICROSCOPE-anchor", "The unity-response anchor and untested controllability statement are retained together."),
    exact_result="MICROSCOPE supports composition-independent inertial/gravitational unity response to 10^-15 mission precision; it does not test vacuum-mediated inertia control.",
    induction_base="The completed mission row retains its exact source identity and precision class.",
    induction_step="Any future direct vacuum-control experiment is appended as a new committed row and cannot rewrite this indirect anchor.",
    exclusions=("no UAP report or propulsion claim used as measurement", "no inference that equivalence alone demonstrates controllable inertia", "no deleted untested boundary"),
    operational_witnesses=(("unity-anchor", "The CNES unity-response record and untested-control boundary are intact.", _inertia == INERTIA_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-VACUUM-INERTIA-003",
    expected_observation_label=INERTIA_LABEL,
    target_rows=target(INERTIA_LABEL, "INERTIA"),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="A verified composition-dependent inertial/gravitational response violates the unity relation, or a claimed direct inertia-control confirmation lacks a separately committed controlled experiment.",
)


EXTRACTION_SPEC = EmpiricalPhysicsSpec(
    claim_id=EXTRACTION_VALIDATION_ID,
    title="Post-seal NIST boundary test of vacuum-work extraction",
    statement="The positive one-sixth formal transfer and complete returned-cycle ledger are tested against the complete NIST ground-state record. NIST reports that no energy can be removed from the ground state and that amplification requires coherent pump energy. Consequently free-standing cyclic vacuum work is not empirically confirmed, while the complete-cycle no-unrecorded-gain ledger is consistent with the measured pump boundary.",
    dependencies=common_dependencies(VACUUM_CYCLE_ID) + (VACUUM_EXTRACTION_ID,),
    generation_rule="Generate the complete eight-axis post-seal vacuum-extraction and returned-cycle comparison product.",
    grammar_boundary="Every registered NIST work-removal and pump row, preserving the positive formal transfer, physical translation boundary and complete returned-cycle ledger.",
    dimensions=empirical_dimensions("sealed-extraction-ledger-versus-complete-NIST-work-boundary", "The formal outward carrier, adverse standalone-work row and pump/restoration ledger remain simultaneously visible."),
    exact_result="The formal outward transfer remains sealed; NIST does not observe standalone extractable vacuum work and requires external pump energy for amplification; this supports the complete returned-cycle accounting rather than a source-free gain claim.",
    induction_base="The exact formal outward transfer and reservoir depletion are immutable admitted records.",
    induction_step="The restoration, external-pump and no-removable-ground-energy rows close the full physical accounting without deleting the outward mathematical event.",
    exclusions=("no erasure of the positive formal extraction claim", "no claim of empirical free-energy confirmation", "no omission of external pump or reservoir restoration", "no target access before seal"),
    operational_witnesses=(("complete-work-vector", "The adverse work row and favorable complete-cycle boundary are both retained.", _extraction == EXTRACTION_LABEL),),
    experiment_id="SFT-EXP-PHYS-VALIDATION-VACUUM-EXTRACTION-003",
    expected_observation_label=EXTRACTION_LABEL,
    target_rows=target(EXTRACTION_LABEL, "EXTRACTION"),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition="A controlled device returns vacuum, apparatus and information records to their initial states while delivering net work without an external source, or any registered NIST source/pump/adverse row is omitted or altered.",
)


VALIDATION_SPECS = (FLOOR_SPEC, POLARIZATION_SPEC, INERTIA_SPEC, EXTRACTION_SPEC)


class CompleteRecordValidator:
    def __init__(self, root: Path, spec: EmpiricalPhysicsSpec, expected: str, classify):
        self.root = root.resolve()
        self.spec = spec
        self.expected = expected
        self.classify = classify

    def validate(self, sealed):
        result = self.classify(self.root)
        label = result[0] if isinstance(result, tuple) else result
        if label != self.expected:
            raise ValueError("authoritative vacuum classification differs from registration")
        return BlindExternalMeasurementValidator(self.root, self.spec).validate(sealed)


VALIDATOR_BY_ID = {
    FLOOR_VALIDATION_ID: lambda root: CompleteRecordValidator(root, FLOOR_SPEC, FLOOR_LABEL, floor_classification),
    POLARIZATION_VALIDATION_ID: lambda root: CompleteRecordValidator(root, POLARIZATION_SPEC, POLARIZATION_LABEL, polarization_classification),
    INERTIA_VALIDATION_ID: lambda root: CompleteRecordValidator(root, INERTIA_SPEC, INERTIA_LABEL, inertia_classification),
    EXTRACTION_VALIDATION_ID: lambda root: CompleteRecordValidator(root, EXTRACTION_SPEC, EXTRACTION_LABEL, extraction_classification),
}

for _spec in VALIDATION_SPECS:
    _spec.validate()


__all__ = ("VALIDATION_SPECS", "VALIDATOR_BY_ID", "authoritative_record")
