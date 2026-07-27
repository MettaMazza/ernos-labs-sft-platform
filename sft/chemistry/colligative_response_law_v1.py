"""Fold-native colligative composition-response law for THERMO-014."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sft.claim_evidence import EmptyOne, PositiveRatio
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


RESPONSE_ORIENTATIONS = {
    "boiling": "temperature-support-expanded-until-liquid-gas-balance",
    "freezing": "temperature-support-reduced-until-liquid-crystal-balance",
    "osmotic": "pressure-support-directed-toward-solute-holding-solution",
}


@dataclass(frozen=True)
class ColligativeParticleAccount:
    solvent_identity: HeldLabel
    solute_identity: HeldLabel
    response_class: HeldLabel
    composition_coordinate: PositiveRatio | EmptyOne
    solvent_transmission_support: PositiveCount
    solute_retention_support: PositiveCount

    def __post_init__(self) -> None:
        if not isinstance(self.solvent_identity, HeldLabel) or self.solvent_identity.family != "chemical-component":
            raise InadmissibleExactValue("colligative account lost solvent identity")
        if not isinstance(self.solute_identity, HeldLabel) or self.solute_identity.family != "chemical-component":
            raise InadmissibleExactValue("colligative account lost solute identity")
        if self.solvent_identity == self.solute_identity:
            raise InadmissibleExactValue("colligative account requires distinct solvent and solute identities")
        if not isinstance(self.response_class, HeldLabel) or self.response_class.family != "colligative-response" or self.response_class.label not in RESPONSE_ORIENTATIONS:
            raise InadmissibleExactValue("colligative response class is not generated")
        if not isinstance(self.composition_coordinate, (PositiveRatio, EmptyOne)):
            raise InadmissibleExactValue("colligative composition requires an exact positive ratio or structural EmptyOne")
        if not isinstance(self.solvent_transmission_support, PositiveCount) or not isinstance(self.solute_retention_support, PositiveCount):
            raise InadmissibleExactValue("colligative boundary requires exact positive particle support")


@dataclass(frozen=True)
class ColligativeOrientation:
    relation: HeldLabel
    composition_boundary: PositiveRatio | EmptyOne


def forced_colligative_orientation(account: ColligativeParticleAccount) -> ColligativeOrientation:
    if not isinstance(account, ColligativeParticleAccount):
        raise InadmissibleExactValue("colligative orientation requires a complete particle account")
    if isinstance(account.composition_coordinate, EmptyOne):
        return ColligativeOrientation(HeldLabel("colligative-orientation", "pure-solvent-reference"), EmptyOne())
    return ColligativeOrientation(
        HeldLabel("colligative-orientation", RESPONSE_ORIENTATIONS[account.response_class.label]),
        account.composition_coordinate,
    )


@dataclass(frozen=True)
class ExactResponseSeparation:
    orientation: HeldLabel
    separation: PositiveRatio | EmptyOne


def exact_response_separation(reference: PositiveRatio, response: PositiveRatio) -> ExactResponseSeparation:
    if not isinstance(reference, PositiveRatio) or not isinstance(response, PositiveRatio):
        raise InadmissibleExactValue("response separation requires two exact positive supports")
    first, second = reference.fraction, response.fraction
    if first == second:
        return ExactResponseSeparation(HeldLabel("response-order", "coincident"), EmptyOne())
    if first < second:
        orientation = "response-expanded-from-reference"
        difference = second - first
    else:
        orientation = "response-reduced-from-reference"
        difference = first - second
    return ExactResponseSeparation(
        HeldLabel("response-order", orientation),
        PositiveRatio.from_pair(difference.numerator, difference.denominator),
    )


def common_particle_replication_preserves_orientation(
    account: ColligativeParticleAccount, replication: PositiveCount
) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("particle replication requires exact positive support")
    prior = forced_colligative_orientation(account).relation
    replicated = ColligativeParticleAccount(
        account.solvent_identity, account.solute_identity, account.response_class,
        account.composition_coordinate,
        PositiveCount(account.solvent_transmission_support.value * replication.value),
        PositiveCount(account.solute_retention_support.value * replication.value),
    )
    return forced_colligative_orientation(replicated).relation == prior


def exact_response_replication_preserves_order(
    reference: PositiveRatio, response: PositiveRatio, replication: PositiveCount
) -> bool:
    if not isinstance(replication, PositiveCount):
        raise InadmissibleExactValue("response replication requires exact positive support")
    prior = exact_response_separation(reference, response).orientation
    factor = replication.value
    replicated_reference = PositiveRatio.from_pair(reference.numerator.value * factor, reference.denominator.value)
    replicated_response = PositiveRatio.from_pair(response.numerator.value * factor, response.denominator.value)
    return exact_response_separation(replicated_reference, replicated_response).orientation == prior


DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-MIXTURE-001",
    "SFT-CHEM-STOICH-SOLUTION-001",
    "SFT-CHEM-SOLUTION-EQUILIBRIUM-001",
    "SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002",
    "SFT-CHEM-ENTROPY-MULTIPLICITY-CORRESPONDENCE-005",
    "SFT-CHEM-FREE-ENERGY-EQUIVALENT-DIRECTION-007",
    "SFT-CHEM-CHEMICAL-POTENTIAL-EQUIVALENT-COMPONENT-008",
    "SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009",
    "SFT-CHEM-FUGACITY-EQUIVALENT-GAS-MIXTURE-010",
    "SFT-CHEM-PHASE-RULE-STRUCTURAL-011",
    "SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012",
    "SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013",
)


DIMENSIONS: tuple[LawDimension, ...] = (
    dimension("carrier", "unbound-response-number", "A detached number erases the solvent, solute, condition and response boundary.", "complete-solvent-solute-particle-account", "Every response retains both component identities, exact composition and particle supports."),
    dimension("identity", "anonymous-particle-count-or-erased-solvent", "Anonymous particles cannot distinguish the transmitted solvent from the held solute.", "distinct-held-solvent-and-solute-identities", "Solvent and solute identities remain distinct and held."),
    dimension("boundary", "imported-colligative-equation-or-dissociation-factor", "An imported equation or factor selects a response instead of forcing it.", "exact-solvent-transmission-and-solute-retention-boundary", "The phase or membrane transmits solvent while retaining the solute distinction."),
    dimension("direction", "signed-temperature-or-pressure-displacement", "A signed displacement imports negative arithmetic.", "held-boiling-freezing-osmotic-orientation-label", "Boiling, freezing and osmotic directions are held relations with positive support only."),
    dimension("magnitude", "linear-constant-fit-or-target-correction", "A fitted constant or target correction adds an unforced parameter.", "exact-positive-reference-response-separation", "Measured response separation is an exact positive fraction after the relation seals."),
    dimension("absence", "numerical-zero-solute-coordinate", "Numerical zero is not an SFT value.", "structural-EmptyOne-pure-solvent-boundary", "An absent solute coordinate is structural EmptyOne and marks the pure-solvent reference."),
    dimension("prediction", "response-values-readable-before-seal", "Readable values could select the response law.", "complete-value-free-276-record-identity-seal", "All 144 boiling, 37 freezing and 95 osmotic identities seal before values open."),
    dimension("extension", "refit-after-particle-or-response-replication", "Refitting destroys exact support provenance.", "depth-independent-common-replication-and-record-append", "Common exact particle/response replication and finite record append preserve orientation."),
)


EXACT_RESULT = (
    "complete-solvent-solute-particle-account__distinct-held-solvent-and-solute-identities__"
    "exact-solvent-transmission-and-solute-retention-boundary__held-boiling-freezing-osmotic-orientation-label__"
    "exact-positive-reference-response-separation__structural-EmptyOne-pure-solvent-boundary__"
    "complete-value-free-276-record-identity-seal__depth-independent-common-replication-and-record-append"
)


def _account(response_class: str, present: bool = True) -> ColligativeParticleAccount:
    return ColligativeParticleAccount(
        HeldLabel("chemical-component", "solvent"), HeldLabel("chemical-component", "solute"),
        HeldLabel("colligative-response", response_class),
        PositiveRatio.from_pair(1, 5) if present else EmptyOne(), PositiveCount(7), PositiveCount(3),
    )


def _witnesses() -> tuple[tuple[str, str, bool], ...]:
    orientations = tuple(forced_colligative_orientation(_account(name)).relation.label for name in RESPONSE_ORIENTATIONS)
    absent = forced_colligative_orientation(_account("boiling", False))
    separation = exact_response_separation(PositiveRatio.from_pair(7, 3), PositiveRatio.from_pair(8, 3))
    return (
        ("three-response-orientations", "Boiling, freezing and osmotic boundaries retain three distinct forced orientations.", orientations == tuple(RESPONSE_ORIENTATIONS.values())),
        ("pure-solvent-EmptyOne", "Absent solute is the structural pure-solvent boundary.", absent.relation.label == "pure-solvent-reference" and isinstance(absent.composition_boundary, EmptyOne)),
        ("exact-positive-separation", "Reference and response are compared by exact positive separation without signed magnitude.", separation.orientation.label == "response-expanded-from-reference" and separation.separation.fraction == Fraction(1, 3)),
        ("replication-successor", "Common exact particle and response replication preserve orientation.", common_particle_replication_preserves_orientation(_account("osmotic"), PositiveCount(6)) and exact_response_replication_preserves_order(PositiveRatio.from_pair(7, 3), PositiveRatio.from_pair(8, 3), PositiveCount(6))),
    )


OPERATIONAL_WITNESSES = _witnesses()


__all__ = (
    "DEPENDENCIES", "DIMENSIONS", "EXACT_RESULT", "ColligativeOrientation", "ColligativeParticleAccount",
    "ExactResponseSeparation", "OPERATIONAL_WITNESSES", "RESPONSE_ORIENTATIONS",
    "common_particle_replication_preserves_orientation", "exact_response_replication_preserves_order",
    "exact_response_separation", "forced_colligative_orientation",
)
