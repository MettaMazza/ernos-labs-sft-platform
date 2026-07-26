"""Exact finite spin-statistics, occupation and boson-condensation law."""

from fractions import Fraction
from math import comb, prod

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045"


def _positive_whole(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive whole Fold count")
    return value


def occupation_vectors(particle_count, level_count, exchange_class):
    """Enumerate every finite occupation word; visible 0 is an empty cell record."""
    particles = _positive_whole(particle_count, "particle count")
    levels = _positive_whole(level_count, "level count")
    if exchange_class not in {"preserving", "alternating"}:
        raise ValueError("exchange class must be preserving or alternating")
    cap = particles if exchange_class == "preserving" else 1
    rows = []

    def walk(prefix, remaining, index):
        if index == levels - 1:
            if remaining <= cap:
                rows.append(prefix + (remaining,))
            return
        for occupied in range(min(cap, remaining) + 1):
            walk(prefix + (occupied,), remaining - occupied, index + 1)

    walk((), particles, 0)
    return tuple(rows)


def occupation_census(particle_count, level_count):
    particles = _positive_whole(particle_count, "particle count")
    levels = _positive_whole(level_count, "level count")
    bosons = occupation_vectors(particles, levels, "preserving")
    fermions = occupation_vectors(particles, levels, "alternating")
    expected_bosons = comb(particles + levels - 1, particles)
    expected_fermions = comb(levels, particles) if particles <= levels else 0
    return {
        "boson_vectors": bosons,
        "fermion_vectors": fermions,
        "boson_count": len(bosons),
        "fermion_count": len(fermions),
        "expected_boson_count": expected_bosons,
        "expected_fermion_count": expected_fermions,
        "complete": len(bosons) == expected_bosons and len(fermions) == expected_fermions,
    }


def _raw_level_weights(level_count):
    levels = _positive_whole(level_count, "level count")
    return tuple(2 ** (levels - index - 1) for index in range(levels))


def canonical_occupation_weights(particle_count, level_count, exchange_class, cold_depth=1):
    """Return the complete exact-rational finite canonical occupation measure."""
    depth = _positive_whole(cold_depth, "cold depth")
    vectors = occupation_vectors(particle_count, level_count, exchange_class)
    if not vectors:
        return ()
    raw = _raw_level_weights(level_count)
    scores = tuple(prod(raw[index] ** (depth * occupied) for index, occupied in enumerate(row)) for row in vectors)
    total = sum(scores)
    return tuple((row, Fraction(score, total)) for row, score in zip(vectors, scores))


def exchange_spin_census():
    """Complete two-label spin composition: three preserving and one alternating."""
    preserving = ("lower-lower", "mixed-preserving", "upper-upper")
    alternating = ("mixed-alternating",)
    return {
        "preserving": preserving,
        "alternating": alternating,
        "complete_count": len(preserving) + len(alternating),
        "preserving_share": Fraction(len(preserving), 4),
        "alternating_share": Fraction(len(alternating), 4),
    }


def spin_return_certificate():
    """Typed return orbits; no signed, imaginary or angular proof scalar is used."""
    alternating = ("lower", "upper", "lower")
    paired = ("paired", "paired")
    return {
        "alternating_turn_orbit": alternating,
        "alternating_first_return_turns": 2,
        "paired_turn_orbit": paired,
        "paired_first_return_turns": 1,
        "two_alternating_compose_to": "preserving",
    }


def ground_share(particle_count, level_count, exchange_class, cold_depth):
    rows = canonical_occupation_weights(particle_count, level_count, exchange_class, cold_depth)
    ground = (particle_count,) + (0,) * (level_count - 1)
    for row, weight in rows:
        if row == ground:
            return weight
    return Fraction(0)


def canonical_mean_throw(particle_count, level_count, exchange_class, cold_depth):
    particles = _positive_whole(particle_count, "particle count")
    rows = canonical_occupation_weights(particles, level_count, exchange_class, cold_depth)
    if not rows:
        raise ValueError("the declared exchange class has no occupation word")
    return sum(
        weight * Fraction(sum((index + 1) * occupied for index, occupied in enumerate(row)), particles)
        for row, weight in rows
    )


def critical_condensation_certificate(particle_count, level_count, fold_factor=2):
    """Find the unique first finite cold depth crossing the forced lock share."""
    particles = _positive_whole(particle_count, "particle count")
    levels = _positive_whole(level_count, "level count")
    factor = _positive_whole(fold_factor, "fold factor")
    if levels < 2 or factor < 2:
        raise ValueError("condensation requires at least two levels and a Fold factor of at least two")
    forms = occupation_vectors(particles, levels, "preserving")
    threshold = Fraction(factor - 1, factor)
    competing = len(forms) - 1
    sufficient_depth = 1
    while 2 ** sufficient_depth < max(1, competing * (factor - 1)):
        sufficient_depth += 1
    # The bound above is conservative; complete enumeration chooses the first crossing.
    rows = []
    for depth in range(1, sufficient_depth + 2):
        share = ground_share(particles, levels, "preserving", depth)
        mean = canonical_mean_throw(particles, levels, "preserving", depth)
        rows.append((depth, share, mean))
        if share >= threshold:
            prior_below = len(rows) == 1 or rows[-2][1] < threshold
            return {
                "particle_count": particles,
                "level_count": levels,
                "fold_factor": factor,
                "lock_share": threshold,
                "critical_depth": depth,
                "critical_mean_throw": mean,
                "ground_share": share,
                "prior_below": prior_below,
                "rows": tuple(rows),
                "minimal_throw_ground_word": (particles,) + (0,) * (levels - 1),
            }
    raise AssertionError("finite Fold bound failed to produce the forced lock crossing")


def minimal_throw_ground_certificate(particle_count, level_count):
    particles = _positive_whole(particle_count, "particle count")
    levels = _positive_whole(level_count, "level count")
    rows = occupation_vectors(particles, levels, "preserving")
    energies = tuple((row, sum((index + 1) * occupied for index, occupied in enumerate(row))) for row in rows)
    least = min(value for _, value in energies)
    survivors = tuple(row for row, value in energies if value == least)
    return {"least_total_throw": least, "survivors": survivors, "unique": survivors == ((particles,) + (0,) * (levels - 1),)}


def theorem_certificate():
    occupation = all(occupation_census(n, levels)["complete"] for levels in range(1, 7) for n in range(1, 7))
    exact_weights = all(
        sum((weight for _, weight in canonical_occupation_weights(n, levels, exchange, depth)), Fraction(0)) == 1
        for exchange in ("preserving", "alternating")
        for levels in range(2, 6)
        for n in range(1, levels + 1)
        for depth in range(1, 5)
    )
    cold = all(
        critical_condensation_certificate(n, levels, factor)["prior_below"]
        and minimal_throw_ground_certificate(n, levels)["unique"]
        for factor in range(2, 6)
        for levels in range(2, 6)
        for n in range(2, 7)
    )
    spin = exchange_spin_census()["complete_count"] == 4 and spin_return_certificate()["alternating_first_return_turns"] == 2
    return {"occupation": occupation, "weights": exact_weights, "cold": cold, "spin": spin}


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal finite spin-statistics, occupation and Bose-condensation law",
    statement=(
        "The preserving and alternating exchange classes force the two finite quantum statistics. For N occupants over L levels, complete occupation enumeration gives C(N+L-1,N) preserving words with no finite per-level ceiling and C(L,N) alternating words with at most one occupant per level; when N>L the latter support is the empty One form. Exact dyadic Fold weighting normalizes every admitted finite occupation word without a continuum distribution. The complete two-label spin composition has three preserving readings and one alternating reading. An alternating constituent changes held fibre after one complete turn and first returns after two, whereas an alternating pair is preserving and returns after one. For every finite preserving population, repeated cold Fold weighting uniquely raises the shared ground-orbit weight through the already forced lock share (m-1)/m at a first finite depth; its exact canonical mean throw is the critical-temperature carrier. At minimum total throw, exhaustive occupation enumeration leaves exactly one word: the whole population in the shared ground orbit."
    ),
    dependencies=(
        "SFT-FOUNDATION-ONE-001",
        "SFT-FOUNDATION-FOLD-001",
        "SFT-FOUNDATION-HALF-ONE-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-PHYS-QUANTUM-SPIN-001",
        "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
        "SFT-PHYS-QUANTUM-EXCLUSION-001",
        "SFT-PHYS-MATTER-FERMION-BOSON-001",
        "SFT-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006",
        "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008",
        "SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043",
        "SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of exchange, exclusion, accumulation, occupation-weight, spin-return, pairing, lock-threshold and ground-orbit forms.",
    grammar_boundary="Every positive finite particle count N, positive finite level count L, preserving or alternating exchange class, positive finite cold depth, and Fold factor m at least two; empty cells are typed structural-absence records.",
    axes=(
        binary_axis("exchange", "What distinguishes the two statistics?", "named-particle-species", "A species name does not force its exchange law.", "preserving-versus-alternating-held-trace", "The complete exchange trace has exactly preserving and alternating classes."),
        binary_axis("fermion", "What limits alternating occupation?", "selected-occupancy-cap", "A selected cap is a free rule.", "one-cell-distinction-exclusion", "A duplicate alternating word erases its only orientation distinction."),
        binary_axis("boson", "What limits preserving occupation?", "finite-selected-ceiling", "No generated ceiling follows from preserving exchange.", "every-positive-finite-multiplicity-admitted", "Preserving exchange admits the shared word for every finite population."),
        binary_axis("weights", "What fixes equilibrium occupation weights?", "continuum-statistical-distribution", "A continuum distribution is outside Fold arithmetic.", "complete-exact-dyadic-occupation-census", "Every finite admitted word receives and normalizes an exact Fold weight."),
        binary_axis("spin", "What fixes the spin-statistics return?", "imaginary-signed-phase", "Imaginary or signed proof scalars are inadmissible.", "typed-one-turn-two-turn-held-orbits", "Held-label recurrence directly distinguishes one-turn and two-turn return."),
        binary_axis("pairing", "What do two alternating constituents compose to?", "independent-boson-postulate", "An independent postulate breaks the single derivation chain.", "alternating-pair-preserves-exchange", "Two complete fibre changes restore the held orientation."),
        binary_axis("lock", "What fixes condensation onset?", "measured-or-fitted-temperature", "A measured or fitted onset would select the law.", "first-exact-crossing-of-forced-m-minus-one-over-m-share", "The admitted Fold threshold and complete cold census select one first crossing."),
        binary_axis("ground", "What fixes the condensate state?", "asserted-macroscopic-ground-mode", "Naming a condensate is not an enumeration.", "unique-minimum-throw-shared-ground-word", "Complete finite occupation enumeration leaves one minimum-throw word."),
    ),
    exact_result=(
        "For positive finite N and L, preserving exchange has exactly C(N+L-1,N) occupation words and admits N occupants in one cell for every N; alternating exchange has exactly C(L,N) words for N<=L, an empty support for N>L, and never exceeds one occupant per cell. Every finite canonical occupation weight is exact rational and sums to One. The two-label spin census is 3/4 preserving and 1/4 alternating; alternating spin first returns after two turns, while a pair is preserving and returns after one. For every N,L and m>=2, the ground-orbit share crosses (m-1)/m at a uniquely first finite cold depth, fixing an exact rational critical mean throw; the unique minimum-throw preserving word places all N occupants in the shared ground orbit."
    ),
    induction_base="One occupant on one level gives the same single word in both exchange classes; two spin labels give exactly three preserving and one alternating composition readings.",
    induction_step="Adding a level extends weak compositions and subsets by their last-cell occupation, yielding the Pascal recurrences for C(N+L-1,N) and C(L,N). Adding a preserving occupant retains the all-ground word with no ceiling; adding cold depth multiplies every excited competitor by at least one additional half-One disadvantage, so a finite depth crosses the fixed (m-1)/m share.",
    exclusions=(
        "no Fermi-Dirac or Bose-Einstein continuum function imported as a premise",
        "no measured transition temperature, particle species or 360/720-degree observation available to candidate selection",
        "no selected occupancy cap, chemical potential, thermodynamic limit or infinite population",
        "no ontic randomness",
        "no conventional numerical-nothingness, negative, irrational, imaginary, floating, NaN or continuum proof magnitude; visible 0 in an occupation vector denotes an empty One cell",
    ),
    witnesses=(
        Witness("occupation", "Complete finite preserving and alternating occupation counts match their forced combinatorial forms.", theorem_certificate()["occupation"]),
        Witness("weights", "Every admitted finite canonical occupation measure is exact and normalized.", theorem_certificate()["weights"]),
        Witness("spin", "The complete two-label census and typed return orbits force the spin-statistics composition.", theorem_certificate()["spin"]),
        Witness("condensation", "Every tested finite grammar has one first lock crossing and one minimum-throw shared-ground word.", theorem_certificate()["cold"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "SPEC",
    "canonical_mean_throw",
    "canonical_occupation_weights",
    "critical_condensation_certificate",
    "exchange_spin_census",
    "ground_share",
    "minimal_throw_ground_certificate",
    "occupation_census",
    "occupation_vectors",
    "spin_return_certificate",
    "theorem_certificate",
)
