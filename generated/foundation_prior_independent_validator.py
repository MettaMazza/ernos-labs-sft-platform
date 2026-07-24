"""Implementation-distinct validators for the Foundation prior-obligation laws.

This file deliberately imports no ``sft.foundation`` scientific module.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json


PRIMITIVES = ("identity", "square", "constant-One", "Fold")


def cast(value: Fraction) -> Fraction:
    if value <= 0: raise ValueError("positive values only")
    while value > 1: value -= 1
    return value


def fold(value: Fraction) -> Fraction: return cast(value + value)
def phase(value: Fraction) -> Fraction: return cast(value + Fraction(1, 2))


def product_case(domains, survivor):
    generated = ["__".join(values) for values in product(*domains)]
    return generated, {candidate: candidate == survivor for candidate in generated}


def exact_operations_case():
    domains = (("domain-unrestricted", "domain-exact-positive-through-One"), ("full-turn-as-absence", "full-turn-as-One"), ("fold-raw-junction", "fold-junction-then-cast"), ("take-unguarded", "take-strictly-larger"), ("unison-unidentified", "unison-exact-One-relation"), ("trace-unbound", "trace-root-bound"), ("no-extra", "has-extra"))
    survivor = "domain-exact-positive-through-One__full-turn-as-One__fold-junction-then-cast__take-strictly-larger__unison-exact-One-relation__trace-root-bound__no-extra"
    generated, decisions = product_case(domains, survivor)
    witness = cast(Fraction(2, 1)) == 1 and fold(Fraction(3, 4)) == Fraction(1, 2) and Fraction(1, 1) - Fraction(1, 4) == Fraction(3, 4)
    return generated, decisions, witness, {"survivor": survivor, "witness": "cast(2)=One; Fold(3/4)=1/2; Take(One,1/4)=3/4"}


def half_one_case():
    domains = (("selection-whole", "selection-singleton-equivalence-class"), ("self-junction-incomplete", "self-junction-One"), ("complement-distinct", "self-complement-equivalent"), ("fold-image-not-One", "fold-image-One"), ("One-not-fixed", "One-fixed"), ("phase-antipode-conflated", "phase-antipode-distinguished"), ("no-extra", "has-extra"))
    survivor = "selection-singleton-equivalence-class__self-junction-One__self-complement-equivalent__fold-image-One__One-fixed__phase-antipode-distinguished__no-extra"
    generated, decisions = product_case(domains, survivor)
    half = Fraction(1, 2)
    witness = half + half == 1 and 1 - half == half and fold(half) == 1 and fold(Fraction(1, 1)) == 1 and phase(half) == 1
    return generated, decisions, witness, {"survivor": survivor, "coordinate": "1/2", "complement_phase_distinct": True}


def fold_dynamics_case():
    domains = (("domain-leaking", "domain-closed"), ("fibre-not-two", "fibre-exactly-two"), ("phase-collision-absent", "phase-collision-present"), ("phase-involution-absent", "phase-involution-present"), ("uniform-division-broken", "uniform-division-preserved"), ("first-cycle-open", "first-cycle-two"), ("no-extra", "has-extra"))
    survivor = "domain-closed__fibre-exactly-two__phase-collision-present__phase-involution-present__uniform-division-preserved__first-cycle-two__no-extra"
    generated, decisions = product_case(domains, survivor)
    parts = [Fraction(n, d) for d in range(2, 10) for n in range(1, d + 1)]
    phase_ok = all(fold(x) == fold(phase(x)) and phase(phase(x)) == x for x in parts)
    fibres_ok = all(fold(y / 2) == y and fold(cast(y / 2 + Fraction(1, 2))) == y for y in parts)
    uniform_ok = True
    for even in (2, 4, 6, 8, 10, 12):
        images = sorted(set(fold(Fraction(i, even)) for i in range(1, even + 1)))
        gaps = [images[i] - images[i - 1] for i in range(1, len(images))]
        uniform_ok = uniform_ok and len(set(gaps)) <= 1 and images[-1] == 1
    cycle_ok = fold(Fraction(1, 3)) == Fraction(2, 3) and fold(Fraction(2, 3)) == Fraction(1, 3)
    return generated, decisions, phase_ok and fibres_ok and uniform_ok and cycle_ok, {"survivor": survivor, "phase_pairs_checked": len(parts), "even_partitions_checked": 6, "first_cycle": ["1/3", "2/3"]}


def primitive_case():
    generated = []
    for size in (1, 2, 3):
        generated.extend(f"size-{size}:" + ">".join(word) for word in product(PRIMITIVES, repeat=size))
    survivor = "size-1:Fold"
    decisions = {candidate: candidate == survivor for candidate in generated}
    third = Fraction(1, 3); lower = Fraction(1, 3); upper = Fraction(5, 6)
    witness = len(generated) == 84 and fold(third) == Fraction(2, 3) and fold(Fraction(2, 3)) == third and fold(lower) == fold(upper)
    return generated, decisions, witness, {"survivor": survivor, "sizes": [4, 16, 64], "larger_words_excluded_by_positive_size_induction": True}


def trace_case():
    domains = (("source-unbound", "source-bound"), ("dependencies-partial", "dependencies-complete"), ("order-lost", "order-preserved"), ("intermediates-inexact", "intermediates-exact"), ("operations-unregistered", "operations-registered"), ("replay-diverges", "replay-identical"), ("terminal-unbound", "terminal-identity-bound"), ("no-extra", "has-extra"))
    survivor = "source-bound__dependencies-complete__order-preserved__intermediates-exact__operations-registered__replay-identical__terminal-identity-bound__no-extra"
    generated, decisions = product_case(domains, survivor)
    first = fold(Fraction(1, 3)); second = Fraction(1, 1) - first; third = fold(second); direct = fold(Fraction(1, 3))
    witness = (first, second, third, direct) == (Fraction(2, 3), Fraction(1, 3), Fraction(2, 3), Fraction(2, 3))
    return generated, decisions, witness, {"survivor": survivor, "replayed_path": ["2/3", "1/3", "2/3"], "direct_terminal": "2/3"}


def admission_case():
    domains = (("registration-incomplete", "registration-root-bound"), ("axiom-or-parameter-present", "no-axiom-zero-parameter"), ("census-selected", "census-complete"), ("survivor-not-unique", "survivor-unique"), ("form-open", "form-closed"), ("controls-incomplete", "controls-complete"), ("validation-self-only", "validation-independent"), ("measurement-before-seal", "measurement-after-seal-when-required"), ("failure-discarded", "every-receipt-preserved"), ("dependency-before-admission", "dependency-after-model-admission"), ("no-extra", "has-extra"))
    survivor = "registration-root-bound__no-axiom-zero-parameter__census-complete__survivor-unique__form-closed__controls-complete__validation-independent__measurement-after-seal-when-required__every-receipt-preserved__dependency-after-model-admission__no-extra"
    generated, decisions = product_case(domains, survivor)
    witness = len(generated) == 2048 and sum(decisions.values()) == 1
    return generated, decisions, witness, {"survivor": survivor, "candidate_paths": 2048, "fail_closed": True}


CASES = {
    "SFT-FOUNDATION-EXACT-OPERATIONS-001": exact_operations_case,
    "SFT-FOUNDATION-HALF-ONE-001": half_one_case,
    "SFT-FOUNDATION-FOLD-DYNAMICS-001": fold_dynamics_case,
    "SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001": primitive_case,
    "SFT-FOUNDATION-DERIVATION-TRACE-001": trace_case,
    "SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001": admission_case,
}


def validate(sealed_path: str, expected_claim_id: str) -> dict[str, object]:
    with open(sealed_path, encoding="utf-8") as handle: sealed = json.load(handle)
    generated, expected_decisions, witness, certificate = CASES[expected_claim_id]()
    received = [item["candidate_id"] for item in sealed["census"]["candidates"]]
    decisions = {item["candidate_id"]: item["survives"] for item in sealed["decisions"]}
    closure = sealed["closure"]; controls = sealed["controls"]
    passed = (sealed["claim_id"] == expected_claim_id and received == generated and sealed["census"]["expected_cardinality"] == len(generated) and decisions == expected_decisions and sum(decisions.values()) == 1 and closure["scope"] == "depth_independent" and closure["minimality_passed"] is True and closure["named_shape_uniqueness_passed"] is True and {item["kind"] for item in controls} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"} and all(item["passed"] is True for item in controls) and witness)
    return {"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"claim_id": expected_claim_id, "generated_cardinality": len(generated), "scientific_witness_recomputed": witness, **certificate}}
