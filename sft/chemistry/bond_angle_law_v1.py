"""Exact Fold equal-sector molecular-angle law for Chemistry PROP-003.

No measured angle, degree scale, coordinate, continuum trigonometry, fitted
geometry, wavefunction or conventional angle equation appears here.  When a
closed molecular turn contains ``n`` symmetry-indistinguishable positive
sectors, introducing unequal sector size would introduce an ungenerated
distinction.  The One turn is therefore the Junction of ``n`` identical exact
parts, and a retained separation of ``k`` sectors is exactly ``k/n`` turn.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


ALLOWED_EQUAL_SECTOR_GEOMETRIES = (
    "linear-equal-two-sector",
    "trigonal-planar-equal-three-sector",
    "square-planar-equal-four-sector",
)


def equal_sector_turn_fraction(
    geometry: HeldLabel,
    sector_count: PositiveCount,
    sector_separation: PositiveCount,
) -> Fraction:
    """Return the exact undirected separation as a positive part of one turn."""

    if not isinstance(geometry, HeldLabel) or geometry.family != "molecular-geometry":
        raise InadmissibleExactValue("bond-angle geometry must be a retained molecular-geometry label")
    if geometry.label not in ALLOWED_EQUAL_SECTOR_GEOMETRIES:
        raise InadmissibleExactValue("geometry is outside the generated equal-sector boundary")
    if not isinstance(sector_count, PositiveCount) or not isinstance(sector_separation, PositiveCount):
        raise InadmissibleExactValue("sector support must use generated positive counts")
    expected_count = {
        "linear-equal-two-sector": 2,
        "trigonal-planar-equal-three-sector": 3,
        "square-planar-equal-four-sector": 4,
    }[geometry.label]
    if sector_count.value != expected_count:
        raise InadmissibleExactValue("geometry and generated sector count do not agree")
    if sector_separation.value + sector_separation.value > sector_count.value:
        raise InadmissibleExactValue("undirected angle must retain the shorter or opposite generated path")
    return Fraction(sector_separation.value, sector_count.value)


@dataclass(frozen=True)
class MolecularAngleCarrier:
    target_id: str
    species: HeldLabel
    molecular_state: HeldLabel
    geometry: HeldLabel
    coordinate: HeldLabel
    angle_role: HeldLabel
    sector_count: PositiveCount
    sector_separation: PositiveCount

    @property
    def turn_fraction(self) -> Fraction:
        return equal_sector_turn_fraction(self.geometry, self.sector_count, self.sector_separation)


def molecular_angle_vector() -> tuple[MolecularAngleCarrier, ...]:
    """Generate the complete registered structural carrier vector without degrees."""

    state = HeldLabel("molecular-state", "neutral-experimental-geometry-carrier")
    return (
        MolecularAngleCarrier(
            "NIST-CCCBDB-BF3-FBF-ADJACENT",
            HeldLabel("molecular-species", "BF3"), state,
            HeldLabel("molecular-geometry", "trigonal-planar-equal-three-sector"),
            HeldLabel("internal-coordinate", "aFBF"), HeldLabel("angle-role", "adjacent"),
            PositiveCount(3), PositiveCount(1),
        ),
        MolecularAngleCarrier(
            "NIST-CCCBDB-XEF2-FXEF-OPPOSITE",
            HeldLabel("molecular-species", "XeF2"), state,
            HeldLabel("molecular-geometry", "linear-equal-two-sector"),
            HeldLabel("internal-coordinate", "aFXeF"), HeldLabel("angle-role", "opposite"),
            PositiveCount(2), PositiveCount(1),
        ),
        MolecularAngleCarrier(
            "NIST-CCCBDB-XEF4-FXEF-ADJACENT",
            HeldLabel("molecular-species", "XeF4"), state,
            HeldLabel("molecular-geometry", "square-planar-equal-four-sector"),
            HeldLabel("internal-coordinate", "aFXeF"), HeldLabel("angle-role", "adjacent"),
            PositiveCount(4), PositiveCount(1),
        ),
        MolecularAngleCarrier(
            "NIST-CCCBDB-XEF4-FXEF-OPPOSITE",
            HeldLabel("molecular-species", "XeF4"), state,
            HeldLabel("molecular-geometry", "square-planar-equal-four-sector"),
            HeldLabel("internal-coordinate", "aFXeF"), HeldLabel("angle-role", "opposite"),
            PositiveCount(4), PositiveCount(2),
        ),
    )


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-LOCATION-DISPLACEMENT-001",
    "SFT-CHEM-BOND-CHEMICAL-BOND-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-GEOMETRY-001",
    "SFT-CHEM-STATE-SYMMETRY-DEGENERACY-005",
    "SFT-CHEM-CONFIGURATION-ORDER-PATH-011",
    "SFT-CHEM-EQUILIBRIUM-BOND-LENGTH-001",
    "SFT-CHEM-BOND-DISSOCIATION-ENERGY-002",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension(
        "carrier", "answer-only-angle-scalar",
        "An answer-only scalar erases the molecular state, geometry and sector carrier.",
        "named-state-geometry-sector-carrier",
        "Species, state, geometry, internal coordinate and sector identities remain held.",
    ),
    dimension(
        "order", "unordered-ligand-cloud",
        "An unordered cloud cannot distinguish adjacent from opposite ligand paths.",
        "exact-generated-cyclic-order",
        "The admitted configuration-order law retains every ligand position in one closed cycle.",
    ),
    dimension(
        "partition", "unequal-or-fitted-sectors",
        "Unequal sectors introduce an ungenerated distinction or fitted geometric parameter.",
        "symmetry-forced-equal-sectors",
        "Indistinguishable sectors have no structural permission to differ and exactly exhaust the turn.",
    ),
    dimension(
        "relation", "continuum-trigonometric-angle",
        "A continuum or irrational trigonometric construction is outside the exact Fold domain.",
        "positive-sector-separation-over-count",
        "A retained k-sector path in an n-sector turn is the exact positive part k/n.",
    ),
    dimension(
        "prediction", "degree-target-in-prediction",
        "A degree value readable before sealing could select the predicted result.",
        "value-free-exact-turn-fraction",
        "Only structural counts, held identities and exact turn fractions are sealed.",
    ),
    dimension(
        "measurement", "target-open-before-seal",
        "An open target before sealing destroys empirical custody.",
        "all-angle-values-open-post-seal",
        "The complete external degree vector is released only after prediction sealing.",
    ),
    dimension(
        "record", "selected-species-or-angle-role",
        "Selecting one favorable geometry or omitting an opposite row cannot close the registered vector.",
        "complete-three-species-four-angle-vector",
        "BF3, XeF2 and both XeF4 angle roles remain present with source conditions.",
    ),
    dimension(
        "extension", "species-correction-or-angle-exception",
        "A species correction or angle exception is a free rule.",
        "one-law-no-extra-rule",
        "One exact equal-sector law closes every registered carrier without correction.",
    ),
)


EXACT_RESULT = (
    "named-state-geometry-sector-carrier__exact-generated-cyclic-order__"
    "symmetry-forced-equal-sectors__positive-sector-separation-over-count__"
    "value-free-exact-turn-fraction__all-angle-values-open-post-seal__"
    "complete-three-species-four-angle-vector__one-law-no-extra-rule"
)


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    vector = molecular_angle_vector()
    tetrahedral_rejected = False
    try:
        equal_sector_turn_fraction(
            HeldLabel("molecular-geometry", "tetrahedral-continuum-angle"),
            PositiveCount(4), PositiveCount(1),
        )
    except InadmissibleExactValue:
        tetrahedral_rejected = True
    wrong_count_rejected = False
    try:
        equal_sector_turn_fraction(
            HeldLabel("molecular-geometry", "trigonal-planar-equal-three-sector"),
            PositiveCount(4), PositiveCount(1),
        )
    except InadmissibleExactValue:
        wrong_count_rejected = True
    return (
        ("one-turn-partition", "The complete registered carrier vector contains exact positive turn parts.",
         tuple(row.turn_fraction for row in vector) == (Fraction(1, 3), Fraction(1, 2), Fraction(1, 4), Fraction(1, 2))),
        ("geometry-count-identity", "A changed geometry count halts instead of introducing a correction.", wrong_count_rejected),
        ("continuum-boundary", "An ungenerated tetrahedral continuum angle is rejected at this boundary.", tetrahedral_rejected),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "ALLOWED_EQUAL_SECTOR_GEOMETRIES", "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT",
    "MolecularAngleCarrier", "OPERATIONAL_WITNESSES", "equal_sector_turn_fraction",
    "molecular_angle_vector",
)
