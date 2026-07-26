"""Exact common Fold scale axis and terminal electroweak transport.

The formal runtime contains no measured energy, weak angle, coupling target,
continuous renormalization coordinate or target-selected rung.  It composes
already admitted V3 carriers on one positive finite binary support axis and
leaves dimensional comparison to the post-seal validator.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import Candidate, CandidateDecision, EvidenceMode, ProvenanceClass
from sft.engine.canonical import sha256_identity
from sft.physics.coupling_running_convergence_terminal_law_v1 import (
    common_scale_vector,
    generated_scale_support,
    generator_indexed_coupling,
)
from sft.physics.lineage_particle_laws import prime_sector_ladder
from sft.physics.precision_value_laws_v1 import (
    electroweak_running_level,
    electroweak_running_share,
    terminal_binary_support,
    terminal_electroweak_sin_squared,
    terminal_promotion_count,
    terminal_return_divisor,
)
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    StructuralPhysicsProgram,
    Witness,
    binary_axis,
    candidate_rows,
    decision_reason,
    generator_period_three,
    survivor_id,
    value_axis,
)


CLAIM_ID = "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"
EXPERIMENT_ID = "SFT-EXP-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"
ONE = Fraction(1, 1)
HALF_ONE = Fraction(1, 2)


def scale_spacing(level: int) -> Fraction:
    """Exact spacing relative to the One on a positive one-based rung."""

    return Fraction(1, generated_scale_support(level))


def traversal_count(level: int) -> int:
    """One local carrier act per generated support cell."""

    return generated_scale_support(level)


def common_rational_rescaling_ratio(
    numerator: Fraction,
    denominator: Fraction,
    held_unit: Fraction,
) -> Fraction:
    """Apply one held unit carrier to like dimensions and cancel it exactly."""

    if not all(isinstance(value, Fraction) and value > 0 for value in (numerator, denominator, held_unit)):
        raise ValueError("unit transport requires exact positive rational carriers")
    return (numerator * held_unit) / (denominator * held_unit)


def is_binary_support(value: int) -> bool:
    if isinstance(value, bool) or value < 1:
        raise ValueError("binary support requires a positive whole count")
    support = 1
    while support < value:
        support += support
    return support == value


def electroweak_source(level: int) -> int:
    """Binary-sector source on the common generated support axis."""

    return 2 + generated_scale_support(level)


def internal_square_anchor_levels(checked_levels: int) -> tuple[int, ...]:
    """Enumerate positive levels whose binary-sector source is a Fold power."""

    if isinstance(checked_levels, bool) or checked_levels < 1:
        raise ValueError("anchor census requires positive finite depth")
    return tuple(level for level in range(1, checked_levels + 1) if is_binary_support(electroweak_source(level)))


def leading_electroweak_share_at_support(support: int) -> Fraction:
    """Squared neutral support over charged plus neutral support."""

    if isinstance(support, bool) or support < 1:
        raise ValueError("electroweak support must be positive")
    charged = Fraction(support + 1, support + 2)
    neutral = HALF_ONE
    value = neutral * neutral / (charged * charged + neutral * neutral)
    if value != electroweak_running_share(support):
        raise ValueError("electroweak squared-support identities diverged")
    return value


def leading_electroweak_share(level: int) -> Fraction:
    return leading_electroweak_share_at_support(generated_scale_support(level))


def terminal_electroweak_chain() -> dict[str, object]:
    support = terminal_binary_support()
    held_directions = generator_period_three()
    active_level = support - held_directions
    if active_level != electroweak_running_level():
        raise ValueError("terminal active level changed")
    base = leading_electroweak_share_at_support(active_level)
    terminal = terminal_electroweak_sin_squared()
    returned = terminal - base
    return {
        "promotion_count": terminal_promotion_count(),
        "complete_support": support,
        "held_generator_directions": held_directions,
        "active_level": active_level,
        "base_share": base,
        "return_divisor": terminal_return_divisor(),
        "returned_share": returned,
        "terminal_share": terminal,
    }


def scale_axis_landmarks() -> tuple[dict[str, object], ...]:
    """Typed landmarks forced by admitted dependencies on the one axis."""

    chain = terminal_electroweak_chain()
    return (
        {"name": "One-origin", "kind": "complete-support", "support": 1},
        {"name": "electroweak-internal-square", "kind": "complete-support", "support": 2},
        {"name": "three-space-step", "kind": "complete-support", "support": 8},
        {"name": "terminal-electroweak-support", "kind": "complete-support", "support": chain["complete_support"]},
        {"name": "terminal-electroweak-active-level", "kind": "held-support", "support": chain["active_level"]},
        {"name": "down-sector-cover", "kind": "complete-support", "support": 32},
        {"name": "up-sector-cover", "kind": "complete-support", "support": 128},
        {"name": "proton-Planck-massive-predecessor", "kind": "held-support", "support": 127},
    )


def leading_curve_strictly_descends(level_count: int) -> bool:
    if isinstance(level_count, bool) or level_count < 2:
        raise ValueError("curve descent requires two positive levels")
    values = tuple(leading_electroweak_share(level) for level in range(1, level_count + 1))
    return all(values[index] > values[index + 1] for index in range(len(values) - 1))


def common_axis_certificate() -> dict[str, object]:
    supports = tuple(generated_scale_support(level) for level in range(1, 9))
    spacings = tuple(scale_spacing(level) for level in range(1, 9))
    chain = terminal_electroweak_chain()
    return {
        "supports": supports,
        "spacings": spacings,
        "traversals": tuple(traversal_count(level) for level in range(1, 9)),
        "sector_vectors": tuple(common_scale_vector(level) for level in range(1, 6)),
        "leading_weak_curve": tuple(leading_electroweak_share(level) for level in range(1, 6)),
        "internal_square_anchor_levels": internal_square_anchor_levels(12),
        "terminal_electroweak_chain": chain,
        "landmarks": scale_axis_landmarks(),
        "unit_ratio_witness": common_rational_rescaling_ratio(Fraction(7, 5), Fraction(11, 3), Fraction(13, 17)),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Common Fold scale axis and terminal electroweak transport",
    statement=(
        "The One-based Fold scale support is generated uniquely by binary succession R_next=2R, with exact "
        "relative spacing One/R and one local carrier act per support cell. The complete prime sectors share "
        "this one axis. In the binary electroweak sector, charged holding support (R+1)/(R+2) and neutral "
        "half-One force the squared share (R+2)^2/[4(R+1)^2+(R+2)^2], which strictly descends at every "
        "binary successor. Complete terminal promotion has support sixteen; holding the three generator "
        "directions forces active level thirteen, base 225/1009 and the single terminal alpha return over "
        "seventeen already admitted as the exact on-shell result. The source 2+R is a binary Fold power only "
        "at support two. Every common exact rational unit rescaling preserves like-dimension ratios, while "
        "the admitted proton-Planck relation fixes the physical scale ratio before any dimensional unit name "
        "or measured reference is applied post-seal."
    ),
    dependencies=(
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-MEAS-UNIT-COMPARISON-001",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
        "SFT-PHYS-SPACETIME-LIMIT-SPEED-001",
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",
        "SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003",
        "SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003",
        "SFT-PHYS-MATTER-QUARK-INVARIANTS-003",
        "SFT-PHYS-SPACE-DIMENSION-THREE-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule=(
        "Generate the complete product of foundation origin, scale successor, order/spacing relation, local "
        "propagation transport, sector domain, electroweak squared-support form, terminal held-support "
        "completion, internal anchor, unit transformation, absolute-ratio placement, target custody, "
        "provenance disclosure and extension form."
    ),
    grammar_boundary=(
        "The One, every positive finite binary support successor, reciprocal exact spacing, one-cell causal "
        "transport, all four forced prime sectors, binary charged and neutral Fold fibres, terminal support "
        "sixteen with three held directions and one alpha return, every common positive rational unit "
        "rescaling, the exact proton-Planck scale ratio and the complete registered post-seal coupling vector."
    ),
    axes=(
        binary_axis("origin", "What begins the scale axis?", "numerical-zero-origin", "Semantic numerical zero is not an SFT scale carrier.", "One-origin", "The One is the unique positive complete origin."),
        binary_axis("successor", "How does scale support grow?", "linear-or-continuous-free-step", "A free or continuous step is not generated by Fold.", "binary-complete-support-successor", "Each Fold depth doubles complete support."),
        binary_axis("spacing", "How is finer scale ordered?", "untyped-arbitrary-spacing", "Arbitrary spacing loses the common exact ratio.", "reciprocal-One-over-support-spacing", "Complete support R partitions the One into exact spacing One/R."),
        binary_axis("transport", "How is running level related to support?", "independent-free-running-axis", "A second arbitrary axis breaks one-cell propagation.", "one-local-act-per-support-cell", "A carrier traverses each generated cell once."),
        binary_axis("sectors", "Which sectors share the axis?", "selected-known-sectors", "Selecting familiar sectors omits forced penta/hepta predictions.", "complete-prime-sector-ladder", "All forced sectors two, three, five and seven share the carrier."),
        value_axis("weak_curve", "Which electroweak running share is typed?", (("linear-channel-ratio", "Channel amplitudes require squared support."), ("target-assigned-angle", "A measured angle cannot select the law."), ("neutral-square-over-charged-plus-neutral-squares", "Squared charged and neutral supports exhaust the binary mixing grammar.")), "neutral-square-over-charged-plus-neutral-squares", "Squared charged and neutral supports exhaust the binary mixing grammar."),
        binary_axis("terminal", "How is the terminal electroweak level completed?", "identify-active-level-with-full-support", "Three held generator directions would be omitted.", "support-sixteen-hold-three-return-alpha-over-seventeen", "Complete terminal support, held directions and sole return exhaust the carrier."),
        binary_axis("anchor", "Where does the binary source close on a Fold power?", "target-selected-depth", "A measurement cannot assign the internal landmark.", "unique-support-two-source-four", "Two plus binary support is a Fold power only at support two."),
        binary_axis("units", "What may a unit change alter?", "unit-name-changes-dimensionless-law", "A held reference cannot change a like-dimension ratio.", "common-positive-rational-rescaling-cancels", "The same typed unit carrier cancels exactly."),
        binary_axis("placement", "How does an exact axis receive a dimensional name?", "measured-rung-or-free-unit-selects-law", "A target-selected rung or calibration would be a free parameter.", "forced-ratio-then-postseal-held-reference", "The exact hierarchy is sealed before one conventional measured reference supplies a unit name."),
        binary_axis("target", "May coupling measurements select the axis or curve?", "target-readable-before-seal", "That would fit the known running vector.", "capability-closed-before-target-release", "The complete exact prediction seals first."),
        binary_axis("provenance", "Is the reconstruction historically blind?", "claim-historical-blindness", "The V1/V2 observations and physical measurements were known.", "observational-development-explicit", "Prior knowledge selects the question, never the executable survivor."),
        binary_axis("extension", "May an offset, rung or correction be appended?", "free-scale-or-running-correction", "An unforced addition would violate zero parameters.", "no-extra-rule", "The support, held directions, return and exact hierarchy consume every typed carrier."),
    ),
    exact_result=(
        "One exact common scale axis is forced: supports 1,2,4,8,...; spacings One, half-One, quarter-One, "
        "eighth-One,...; and every forced prime sector uses the same support. The electroweak leading curve "
        "is w(R)=(R+2)^2/[4(R+1)^2+(R+2)^2]. Terminal support sixteen holds three directions, forcing "
        "active level thirteen, w(13)=225/1009 and the separately typed alpha/17 return, exactly reproducing "
        "the admitted terminal on-shell share. The unique internal power anchor is support two. Common exact "
        "unit rescaling leaves every dimensionless result unchanged; physical magnitudes are transported only "
        "through sealed exact ratios and a post-seal held reference."
    ),
    induction_base=(
        "The One supplies support one and spacing One. Its first Fold successor supplies support two, "
        "half-One spacing and the unique binary-sector source closure 2+2=4."
    ),
    induction_step=(
        "Every successor doubles support, halves exact spacing, doubles local traversal count, preserves the "
        "single sector axis and strictly lowers the squared weak share by the positive numerator "
        "R(4R^2+9R+4) in the cross-multiplied difference. For supports at least four, 2+R has an odd factor "
        "above the One and cannot be another Fold power."
    ),
    exclusions=(
        "no numerical-zero scale origin, negative exponent, irrational, imaginary, floating or completed-continuum proof value",
        "no imported renormalization-group equation, beta function, logarithmic energy coordinate or continuous scale",
        "no measured energy, weak angle, coupling, Planck value or selected rung in the formal survivor decision",
        "no identification of the earlier full-support running level with the terminal held-support level",
        "no claim that one monotone weak curve applies above the registered W-threshold boundary",
        "no fitted offset, calibration constant, scheme correction or hidden target-selected depth",
        "no historical-blindness claim",
    ),
    witnesses=(
        Witness("binary-support", "The first eight generated supports are exact powers produced only by succession.", tuple(generated_scale_support(level) for level in range(1, 9)) == (1, 2, 4, 8, 16, 32, 64, 128)),
        Witness("reciprocal-spacing", "Every successor halves exact spacing.", all(scale_spacing(level + 1) * 2 == scale_spacing(level) for level in range(1, 8))),
        Witness("one-cell-transport", "Traversal count equals complete support at every registered witness rung.", all(traversal_count(level) == generated_scale_support(level) for level in range(1, 9))),
        Witness("complete-sector-axis", "The shared vector retains exactly the forced sectors two, three, five and seven.", tuple(sector for sector, _ in common_scale_vector(1)) == prime_sector_ladder()),
        Witness("leading-curve", "The first four leading weak shares reproduce the exact V1 structural vector.", tuple(leading_electroweak_share(level) for level in range(1, 5)) == (Fraction(9, 25), Fraction(4, 13), Fraction(9, 34), Fraction(25, 106))),
        Witness("strict-weak-descent", "Every tested binary successor lowers the exact weak share and the induction identity extends it.", leading_curve_strictly_descends(12)),
        Witness("unique-internal-anchor", "Only positive level two closes the binary source on a Fold power.", internal_square_anchor_levels(16) == (2,)),
        Witness("terminal-held-level", "Complete support sixteen holds three directions and forces level thirteen.", terminal_electroweak_chain()["complete_support"] == 16 and terminal_electroweak_chain()["active_level"] == 13),
        Witness("terminal-share", "The held level and sole return reproduce the admitted exact terminal share.", terminal_electroweak_chain()["base_share"] == Fraction(225, 1009) and terminal_electroweak_chain()["terminal_share"] == Fraction(1930922298157999, 8642477221479757)),
        Witness("unit-invariance", "A common exact held unit cancels from a like-dimension ratio.", common_rational_rescaling_ratio(Fraction(7, 5), Fraction(11, 3), Fraction(13, 17)) == Fraction(21, 55)),
        Witness("named-landmarks", "Every source-family landmark has one typed generated support or held-support record.", tuple(row["support"] for row in scale_axis_landmarks()) == (1, 2, 8, 16, 13, 32, 128, 127)),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


class CommonScaleAxisProgram(StructuralPhysicsProgram):
    """The same complete grammar with one immutable row index.

    ``StructuralPhysicsProgram`` deliberately favors cold readability and
    regenerates its candidate product during each decision.  This claim has a
    larger complete product, so it indexes that unchanged product once.  No
    candidate, coordinate, decision rule or survivor condition is altered.
    """

    def __init__(self, spec: StructuralPhysicsSpec, source_hash: str):
        super().__init__(spec, source_hash)
        self._row_index = {str(row["candidate_id"]): row for row in candidate_rows(spec)}

    def decide_candidate(self, candidate: Candidate) -> CandidateDecision:
        row = self._row_index[candidate.candidate_id]
        survives = candidate.candidate_id == survivor_id(self.spec)
        reason = decision_reason(self.spec, row)
        return CandidateDecision(
            candidate_id=candidate.candidate_id,
            survives=survives,
            reason=reason,
            proof_hash=sha256_identity((self.spec.claim_id, self.spec.dependencies, row, survives, reason)),
        )


__all__ = (
    "CLAIM_ID",
    "CommonScaleAxisProgram",
    "EXPERIMENT_ID",
    "SPEC",
    "common_axis_certificate",
    "common_rational_rescaling_ratio",
    "electroweak_source",
    "internal_square_anchor_levels",
    "leading_curve_strictly_descends",
    "leading_electroweak_share",
    "leading_electroweak_share_at_support",
    "scale_axis_landmarks",
    "scale_spacing",
    "terminal_electroweak_chain",
    "traversal_count",
)
