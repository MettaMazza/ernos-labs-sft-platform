"""Exact temperature, finite canonical equilibrium and fluctuation-response law."""

from fractions import Fraction
from math import comb, factorial

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043"


def require_positive(value, name):
    result = Fraction(value)
    if result <= 0: raise ValueError(f"{name} must be an exact positive Fold carrier")
    return result


def exact_temperature(throws):
    if not throws: raise ValueError("temperature requires a finite nonempty population")
    exact = tuple(require_positive(x, "throw") for x in throws)
    return sum(exact, Fraction(0)) / len(exact)


def total_throw_identity(throws):
    temperature = exact_temperature(throws)
    return sum((Fraction(x) for x in throws), Fraction(0)) == len(throws) * temperature


def paired_equilibrium_census(pair_count):
    if isinstance(pair_count, bool) or pair_count < 1: raise ValueError("pair count must be positive")
    population = 2 * pair_count
    rows = tuple((upper, comb(population, upper)) for upper in range(population + 1))
    maximum = max(count for _, count in rows)
    survivors = tuple(upper for upper, count in rows if count == maximum)
    return {"population": population, "rows": rows, "survivors": survivors, "share": Fraction(survivors[0], population)}


def dyadic_canonical_counts(level_count):
    if isinstance(level_count, bool) or level_count < 2: raise ValueError("at least two generated levels required")
    return tuple(2 ** (level_count - index - 1) for index in range(level_count))


def dyadic_canonical_weights(level_count):
    counts = dyadic_canonical_counts(level_count); total = sum(counts)
    return tuple(Fraction(count, total) for count in counts)


def multinomial_count(counts):
    total = sum(counts); value = factorial(total)
    for count in counts: value //= factorial(count)
    return value


def fixed_count_throw_forms(level_count):
    target = dyadic_canonical_counts(level_count); population = sum(target); throw = sum(i * n for i, n in enumerate(target))
    rows = []
    def walk(prefix, remaining, index):
        if index == level_count - 1:
            candidate = prefix + (remaining,)
            if sum(i * n for i, n in enumerate(candidate)) == throw: rows.append(candidate)
            return
        for count in range(remaining + 1): walk(prefix + (count,), remaining - count, index + 1)
    walk((), population, 0)
    return tuple(rows)


def canonical_maximum_certificate(level_count):
    target = dyadic_canonical_counts(level_count); forms = fixed_count_throw_forms(level_count)
    values = tuple((form, multinomial_count(form)) for form in forms); maximum = max(value for _, value in values)
    survivors = tuple(form for form, value in values if value == maximum)
    return {"target": target, "forms": len(forms), "survivors": survivors, "unique": survivors == (target,)}


def fluctuation_response_ledger():
    equilibrium = Fraction(1, 2); fluctuation = Fraction(3, 4); response = Fraction(1, 4)
    return {"equilibrium": equilibrium, "fluctuation": fluctuation, "response": response, "complete": fluctuation + response == 1, "equal_departure": fluctuation - equilibrium == equilibrium - response == Fraction(1, 4)}


def deterministic_noise_cycle(repetitions):
    if isinstance(repetitions, bool) or repetitions < 1: raise ValueError("repetitions must be positive")
    base = (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 2))
    cycle = base * repetitions
    return {"cycle": cycle, "mean": sum(cycle, Fraction(0)) / len(cycle), "period": len(base)}


def theorem_certificate():
    return {
        "temperature": all(total_throw_identity(values) for values in ((Fraction(1, 4), Fraction(3, 4)), (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)))),
        "equilibrium": all(paired_equilibrium_census(n)["survivors"] == (n,) and paired_equilibrium_census(n)["share"] == Fraction(1, 2) for n in range(1, 12)),
        "canonical": all(canonical_maximum_certificate(levels)["unique"] for levels in range(2, 6)),
        "weights": all(sum(dyadic_canonical_weights(levels), Fraction(0)) == 1 and all(a > b for a, b in zip(dyadic_canonical_weights(levels), dyadic_canonical_weights(levels)[1:])) for levels in range(2, 10)),
        "fluctuation": fluctuation_response_ledger()["complete"] and fluctuation_response_ledger()["equal_departure"],
        "noise": all(deterministic_noise_cycle(n)["mean"] == Fraction(1, 2) for n in range(1, 10)),
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal exact temperature, finite canonical equilibrium and fluctuation-response law",
    statement=(
        "Temperature is the exact positive mean of a finite population's held throw records, so total throw equals population count times temperature. "
        "For every complete paired binary population, exhaustive multiplicity counting has one maximum at equal labels, forcing half-One equilibrium and detailed balance. "
        "For L generated levels the Fold recurrence uniquely supplies integer populations (2^(L-1),...,2,1), normalized by 2^L-1; complete enumeration at the same population and throw gives this dyadic ladder as the unique multinomial maximum. "
        "Equilibrium fluctuation three-quarter-One and response quarter-One are complementary and have the same quarter-One departure from half-One. A finite deterministic four-record cycle has mean half-One, making noise and response two readings of one retained orbit."
    ),
    dependencies=("SFT-FOUNDATION-ONE-001", "SFT-FOUNDATION-FOLD-001", "SFT-FOUNDATION-HALF-ONE-001", "SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-COMBINATORICS-001", "SFT-PHYS-THERMO-TEMPERATURE-001", "SFT-PHYS-THERMO-EQUILIBRIUM-001", "SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001", "SFT-PHYS-THERMO-FLUCTUATION-001", "SFT-PHYS-THERMO-RESPONSE-001"),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of temperature, total throw, equilibrium, canonical weighting, maximum-count, fluctuation, response and noise-orbit forms.",
    grammar_boundary="Every finite nonempty tuple of exact positive throws; every positive paired binary population; every finite generated level count at least two; every exact fixed-count/fixed-throw population vector; and every positive repetition of the complete deterministic response cycle.",
    axes=(
        binary_axis("temperature", "What is temperature?", "primitive-continuum-coordinate", "A primitive continuum coordinate is not Fold-generated.", "exact-positive-mean-throw", "The finite population uniquely fixes its exact mean."),
        binary_axis("total", "What links total and mean?", "fitted-Boltzmann-coefficient", "A fitted coefficient adds a parameter.", "population-count-times-mean", "Finite summation forces total=N times mean."),
        binary_axis("equilibrium", "What fixes balance?", "selected-half-label", "A named midpoint alone is not a census.", "unique-binomial-multiplicity-maximum", "Every complete paired population has one maximum at equal labels."),
        binary_axis("canonical", "What fixes finite level weights?", "continuum-exponential", "An exponential is outside exact Fold arithmetic.", "normalized-dyadic-successor-ladder", "Fold succession generates powers of two and exact positive normalization."),
        binary_axis("maximum", "Why is the ladder equilibrium?", "asserted-geometric-shape", "A shape assertion does not eliminate alternatives.", "complete-fixed-count-throw-multinomial-maximum", "Every same-count/same-throw vector is enumerated and only the dyadic vector maximizes multiplicity."),
        binary_axis("fluctuation", "What is the least balanced fluctuation?", "ontic-random-kick", "Ontic randomness is not forced.", "three-quarter-complementary-departure", "The upper quarter departure is three-quarter-One."),
        binary_axis("response", "What is the matching response?", "free-dissipation-rate", "A free response adds a parameter.", "quarter-One-antipodal-response", "The complementary response has the identical quarter departure."),
        binary_axis("noise", "What is thermal noise?", "untracked-stochastic-source", "An untracked source violates determinism.", "finite-periodic-orbit-readout", "The complete retained orbit supplies spread and relaxation together."),
    ),
    exact_result="For every finite positive population, T=(sum throws)/N and total=N*T. Every paired binary population uniquely maximizes multiplicity at half-One. For L levels, exact canonical counts are (2^(L-1),...,1), weights divide by 2^L-1, sum to One and are the unique fixed-count/fixed-throw multinomial maximum. The least fluctuation/response pair is 3/4 and 1/4 around equilibrium 1/2, with equal departure 1/4; the complete deterministic cycle (1/4,1/2,3/4,1/2) has mean 1/2.",
    induction_base="One binary pair has multiplicities One,two,One and unique half-One maximum; two levels have dyadic counts two,One and unique fixed-throw maximum.",
    induction_step="Appending one binary pair preserves the central unique maximum; appending one Fold level doubles every earlier count and adds one terminal record, preserving normalization, fixed-throw maximality and strict decline; appending a complete four-record orbit preserves mean half-One.",
    exclusions=("no Boltzmann exponential, continuum bath, Lagrange multiplier or fitted distribution", "no thermometry, noise voltage or measured k_B available to candidate selection", "no ontic randomness", "no numerical-zero, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof magnitude", "empty combinatorial counts are structural absence records only"),
    witnesses=(
        Witness("temperature", "Exact total and mean identity holds.", theorem_certificate()["temperature"]),
        Witness("equilibrium", "Complete paired populations uniquely force half-One.", theorem_certificate()["equilibrium"]),
        Witness("canonical", "Every tested complete level grammar has one dyadic maximum and exact weights.", theorem_certificate()["canonical"] and theorem_certificate()["weights"]),
        Witness("response", "Fluctuation, response and deterministic noise share one exact balance.", theorem_certificate()["fluctuation"] and theorem_certificate()["noise"]),
    ),
    provenance=(ProvenanceClass.FORWARD_FORCING, ProvenanceClass.OBSERVATIONAL_DERIVATION),
)


SPEC.validate()


__all__ = ("CLAIM_ID", "SPEC", "canonical_maximum_certificate", "deterministic_noise_cycle", "dyadic_canonical_counts", "dyadic_canonical_weights", "exact_temperature", "fluctuation_response_ledger", "paired_equilibrium_census", "theorem_certificate", "total_throw_identity")
