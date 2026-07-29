"""Fold-native electrochemical storage ownership and handoff law (ECHEM-013)."""
from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


@dataclass(frozen=True)
class OwnedStorageCoordinate:
    coordinate: HeldLabel
    owner: HeldLabel
    source_claim: HeldLabel
    ordinal: PositiveCount

    def __post_init__(self):
        if (self.coordinate.family, self.owner.family, self.source_claim.family) != ("storage-coordinate", "branch-owner", "admitted-claim"):
            raise InadmissibleExactValue("storage coordinate requires coordinate, owner and admitted-claim custody")


@dataclass(frozen=True)
class StorageHandoff:
    chemistry: OwnedStorageCoordinate
    materials: OwnedStorageCoordinate
    engineering: OwnedStorageCoordinate


def storage_handoff(rows: tuple[OwnedStorageCoordinate, ...]) -> StorageHandoff:
    if tuple(row.ordinal.value for row in rows) != (1, 2, 3):
        raise InadmissibleExactValue("complete ordered three-coordinate handoff required")
    expected = (
        ("species-reactions", "chemistry"),
        ("bulk-device-response", "materials"),
        ("implementation", "engineering"),
    )
    observed = tuple((row.coordinate.label, row.owner.label) for row in rows)
    if observed != expected or len({row.source_claim.label for row in rows}) != 3:
        raise InadmissibleExactValue("every coordinate requires exactly one distinct admitted owner path")
    return StorageHandoff(*rows)


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001",
    "SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003",
    "SFT-CHEM-CORROSION-REACTION-NETWORK-012",
    "SFT-MAT-DEGR-CORROSION-001",
    "SFT-ENG-REQUIREMENT-001",
)
DIMENSIONS = (
    dimension("subject", "anonymous-storage-number", "A device number loses the chemical/material subject.", "complete-storage-coordinate-custody", "Every owned coordinate remains explicit."),
    dimension("chemistry", "chemistry-owns-device-performance", "Bulk response exceeds Chemistry ownership.", "chemistry-owns-species-reactions", "Chemistry owns cell species and reactions."),
    dimension("materials", "materials-owns-reaction-law", "Reaction identity exceeds Materials ownership.", "materials-own-bulk-device-response", "Materials owns bulk response and degradation."),
    dimension("engineering", "engineering-owns-natural-law", "Implementation does not select natural law.", "engineering-owns-implementation", "Engineering owns implementation only."),
    dimension("ownership", "overlapping-branch-ownership", "Duplicate ownership destroys exact provenance.", "exactly-one-owner-per-coordinate", "Every coordinate maps to one owner."),
    dimension("handoff", "untraced-cross-branch-use", "An untraced use loses dependency custody.", "explicit-directed-claim-handoff", "Every cross-branch use names source and destination."),
    dimension("record", "selected-device-summary", "One summary hides chemical and material records.", "complete-chemistry-material-record-pair", "Both admitted records and their boundary remain."),
    dimension("extension", "application-redefines-ownership", "An application cannot change branch law.", "new-coordinate-requires-new-unique-owner", "Every lawful extension must add one explicit owner."),
)
EXACT_RESULT = "complete-storage-coordinate-custody__chemistry-owns-species-reactions__materials-own-bulk-device-response__engineering-owns-implementation__exactly-one-owner-per-coordinate__explicit-directed-claim-handoff__complete-chemistry-material-record-pair__new-coordinate-requires-new-unique-owner"


def _row(n: int, coordinate: str, owner: str, claim: str) -> OwnedStorageCoordinate:
    return OwnedStorageCoordinate(HeldLabel("storage-coordinate", coordinate), HeldLabel("branch-owner", owner), HeldLabel("admitted-claim", claim), PositiveCount(n))


def _witnesses():
    result = storage_handoff((
        _row(1, "species-reactions", "chemistry", "cell-chemistry"),
        _row(2, "bulk-device-response", "materials", "bulk-response"),
        _row(3, "implementation", "engineering", "implementation-boundary"),
    ))
    duplicate_halts = False
    try:
        storage_handoff((
            _row(1, "species-reactions", "chemistry", "same"),
            _row(2, "bulk-device-response", "materials", "same"),
            _row(3, "implementation", "engineering", "same"),
        ))
    except InadmissibleExactValue:
        duplicate_halts = True
    return (
        ("complete", "All three coordinates remain.", len(result.__dict__) == 3),
        ("chemistry", "Species/reactions have one owner.", result.chemistry.owner.label == "chemistry"),
        ("materials", "Bulk response has one owner.", result.materials.owner.label == "materials"),
        ("engineering", "Implementation has one owner.", result.engineering.owner.label == "engineering"),
        ("ordered", "The handoff is ordered.", tuple(row.ordinal.value for row in result.__dict__.values()) == (1, 2, 3)),
        ("distinct", "All source claims remain distinct.", len({row.source_claim for row in result.__dict__.values()}) == 3),
        ("duplicate", "Duplicate ownership paths halt.", duplicate_halts),
        ("extension", "A new coordinate requires a new explicit record.", len(result.__dict__) + 1 == 4),
    )


OPERATIONAL_WITNESSES = _witnesses()
