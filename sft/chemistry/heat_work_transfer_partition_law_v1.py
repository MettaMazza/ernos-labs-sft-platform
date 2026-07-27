"""Fold-native chemical heat/work transfer partition for THERMO-004."""

from __future__ import annotations

from dataclasses import dataclass

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue
from sft.physics.generated_empirical_law import LawDimension, dimension


def _ratio(value) -> PositiveRatio:
    return PositiveRatio.from_pair(value.numerator, value.denominator)


@dataclass(frozen=True)
class ChemicalTransferRecord:
    boundary: HeldLabel
    chemical_path: HeldLabel
    orientation: HeldLabel
    carrier_observation: HeldLabel
    transfer_class: HeldLabel
    exact_positive_magnitude: PositiveRatio

    def __post_init__(self) -> None:
        required = (
            (self.boundary, "chemical-boundary"),
            (self.chemical_path, "chemical-path"),
            (self.orientation, "energy-transfer-orientation"),
            (self.carrier_observation, "transfer-carrier-observation"),
            (self.transfer_class, "chemical-transfer-class"),
        )
        if any(not isinstance(value, HeldLabel) or value.family != family for value, family in required):
            raise InadmissibleExactValue("chemical transfer record lost a held identity")
        if self.orientation.label not in {"into-held-support", "out-of-held-support"}:
            raise InadmissibleExactValue("transfer direction must remain a held orientation")
        forced = transfer_class_from_observation(self.carrier_observation)
        if self.transfer_class != forced:
            raise InadmissibleExactValue("heat/work class was not forced by carrier observation")
        if not isinstance(self.exact_positive_magnitude, PositiveRatio):
            raise InadmissibleExactValue("transfer content must be exact and positive")


@dataclass(frozen=True)
class ChemicalHeatWorkPartition:
    boundary: HeldLabel
    chemical_path: HeldLabel
    records: tuple[ChemicalTransferRecord, ...]
    heat_total: PositiveRatio | EmptyOne
    work_total: PositiveRatio | EmptyOne
    complete_transfer_total: PositiveRatio


def transfer_class_from_observation(carrier_observation: HeldLabel) -> HeldLabel:
    """Derive the transfer class from what observation retains or closes."""

    if not isinstance(carrier_observation, HeldLabel) or carrier_observation.family != "transfer-carrier-observation":
        raise InadmissibleExactValue("transfer carrier requires a held observation class")
    if carrier_observation.label == "carrier-label-closed-by-receiving-macro-observation":
        return HeldLabel("chemical-transfer-class", "heat-transfer")
    if carrier_observation.label == "organized-source-response-label-retained":
        return HeldLabel("chemical-transfer-class", "work-transfer")
    raise InadmissibleExactValue("unforced transfer carrier observation")


def chemical_transfer_record(
    boundary: HeldLabel,
    chemical_path: HeldLabel,
    orientation: HeldLabel,
    carrier_observation: HeldLabel,
    magnitude: PositiveRatio,
) -> ChemicalTransferRecord:
    return ChemicalTransferRecord(
        boundary,
        chemical_path,
        orientation,
        carrier_observation,
        transfer_class_from_observation(carrier_observation),
        magnitude,
    )


def _class_total(records: tuple[ChemicalTransferRecord, ...]) -> PositiveRatio | EmptyOne:
    if not records:
        return EmptyOne()
    total = records[0].exact_positive_magnitude.fraction
    for record in records[1:]:
        total += record.exact_positive_magnitude.fraction
    return _ratio(total)


def partition_chemical_transfers(
    records: tuple[ChemicalTransferRecord, ...],
) -> ChemicalHeatWorkPartition:
    """Retain every transfer and compose exact positive totals by forced class."""

    if not isinstance(records, tuple) or not records or any(not isinstance(record, ChemicalTransferRecord) for record in records):
        raise InadmissibleExactValue("chemical transfer partition requires a nonempty exact path")
    boundary = records[0].boundary
    path = records[0].chemical_path
    if any(record.boundary != boundary or record.chemical_path != path for record in records):
        raise InadmissibleExactValue("one partition cannot merge different boundaries or chemical paths")
    heat = tuple(record for record in records if record.transfer_class.label == "heat-transfer")
    work = tuple(record for record in records if record.transfer_class.label == "work-transfer")
    if len(heat) + len(work) != len(records):
        raise InadmissibleExactValue("heat/work partition omitted a transfer record")
    total = records[0].exact_positive_magnitude.fraction
    for record in records[1:]:
        total += record.exact_positive_magnitude.fraction
    return ChemicalHeatWorkPartition(boundary, path, records, _class_total(heat), _class_total(work), _ratio(total))


def append_transfer_preserves_partition(
    records: tuple[ChemicalTransferRecord, ...],
    extension: ChemicalTransferRecord,
) -> bool:
    prior = partition_chemical_transfers(records)
    if extension.boundary != prior.boundary or extension.chemical_path != prior.chemical_path:
        raise InadmissibleExactValue("transfer successor changed the held boundary or chemical path")
    extended = partition_chemical_transfers(records + (extension,))
    expected = _ratio(prior.complete_transfer_total.fraction + extension.exact_positive_magnitude.fraction)
    return extended.records[:-1] == prior.records and extended.complete_transfer_total == expected


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001", "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001", "SFT-COMP-FORM-COMPOSITION-001",
    "SFT-PHYS-MECH-WORK-ENERGY-001", "SFT-PHYS-THERMO-HEAT-WORK-001",
    "SFT-PHYS-THERMO-FIRST-LAW-001", "SFT-PHYS-THERMO-STATE-RELATION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-MOLECULAR-FORMATION-ENERGY-013",
    "SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001", "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    "SFT-CHEM-INTERNAL-ENERGY-COMPOSITION-003",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "answer-only-signed-net-energy", "A signed answer erases the boundary, path and transfer provenance.", "complete-held-chemical-transfer-path", "Every transfer remains attached to one held chemical boundary and path."),
    dimension("class", "imported-or-arbitrary-heat-work-label", "An arbitrary label does not explain the heat/work distinction.", "observation-forced-closed-or-held-carrier-class", "Closed carrier identity forces heat; retained organized source-response identity forces work."),
    dimension("orientation", "negative-or-signed-transfer-content", "A signed proof value conflates direction with content.", "held-direction-plus-exact-positive-content", "Direction is held separately from exact positive transfer content."),
    dimension("partition", "merged-or-overlapping-transfer-classes", "A merged or overlapping record cannot retain which distinction observation closed.", "disjoint-exhaustive-heat-work-path-partition", "Every path transfer occurs exactly once in one forced class."),
    dimension("composition", "signed-net-cancellation-or-numerical-zero", "Signed cancellation deletes transfer history and numerical zero is not an SFT number.", "per-class-positive-composition-plus-EmptyOne-absence", "Each present class composes exactly; an absent class is structural EmptyOne."),
    dimension("prediction", "calorimetric-or-work-target-readable-before-seal", "Target values could select the partition.", "complete-value-free-transfer-identity-seal", "All state and column identities seal before calorimetric or work values open."),
    dimension("record", "selected-calorimetric-or-expansion-row", "A selected row can hide phase and unfavorable records.", "complete-13-row-joint-calorimetric-expansion-vector", "All returned liquid, boundary and vapour rows remain in one joint record."),
    dimension("extension", "repartition-prior-path-after-successor", "Repartitioning earlier transfers destroys path invariance.", "depth-independent-append-only-transfer-successor", "One new transfer appends without changing any prior record."),
)


EXACT_RESULT = (
    "complete-held-chemical-transfer-path__observation-forced-closed-or-held-carrier-class__"
    "held-direction-plus-exact-positive-content__disjoint-exhaustive-heat-work-path-partition__"
    "per-class-positive-composition-plus-EmptyOne-absence__complete-value-free-transfer-identity-seal__"
    "complete-13-row-joint-calorimetric-expansion-vector__depth-independent-append-only-transfer-successor"
)


def _record(carrier: str, numerator: int, denominator: int) -> ChemicalTransferRecord:
    return chemical_transfer_record(
        HeldLabel("chemical-boundary", "held-boundary"),
        HeldLabel("chemical-path", "held-path"),
        HeldLabel("energy-transfer-orientation", "into-held-support"),
        HeldLabel("transfer-carrier-observation", carrier),
        PositiveRatio.from_pair(numerator, denominator),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    first = _record("carrier-label-closed-by-receiving-macro-observation", 2, 3)
    second = _record("carrier-label-closed-by-receiving-macro-observation", 5, 4)
    third = _record("organized-source-response-label-retained", 7, 5)
    heat_only = partition_chemical_transfers((first, second))
    complete = partition_chemical_transfers((first, second, third))
    return (
        ("forced-classes", "Carrier observability alone forces distinct heat and work classes.", first.transfer_class.label == "heat-transfer" and third.transfer_class.label == "work-transfer"),
        ("disjoint-complete", "Every transfer occurs exactly once in the partition.", len(complete.records) == 3),
        ("exact-class-totals", "Heat and work contents compose exactly without signs.", complete.heat_total == PositiveRatio.from_pair(23, 12) and complete.work_total == PositiveRatio.from_pair(7, 5)),
        ("structural-absence", "An absent transfer class is EmptyOne, not numerical zero.", isinstance(heat_only.work_total, EmptyOne)),
        ("complete-total", "The complete retained transfer content is exact.", complete.complete_transfer_total == PositiveRatio.from_pair(199, 60)),
        ("append-only", "Appending one transfer preserves every prior path record.", append_transfer_preserves_partition((first, second), third)),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "OPERATIONAL_WITNESSES",
    "ChemicalHeatWorkPartition", "ChemicalTransferRecord", "append_transfer_preserves_partition",
    "chemical_transfer_record", "partition_chemical_transfers", "transfer_class_from_observation",
)
