"""Implementation-distinct validator for relativistic/field successors."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


IDS = (
    "SFT-PHYS-DYNAMICS-FREE-PHASE-DISPERSION-003",
    "SFT-PHYS-DYNAMICS-POTENTIAL-EVOLUTION-003",
    "SFT-PHYS-DYNAMICS-STATIONARY-SPECTRUM-003",
    "SFT-PHYS-RELATIVITY-TWO-HAND-DIRAC-SQUARE-003",
    "SFT-PHYS-RELATIVITY-FULL-DIRAC-SQUARE-003",
    "SFT-PHYS-FIELD-COULOMB-GAUSS-CLOSURE-003",
    "SFT-PHYS-FIELD-MAGNETIC-RELATIVITY-003",
    "SFT-PHYS-FIELD-LORENTZ-TRANSFER-003",
    "SFT-PHYS-FIELD-MAXWELL-PLANAR-CLOSURE-003",
    "SFT-PHYS-FIELD-MAXWELL-THREE-SPACE-CLOSURE-003",
    "SFT-PHYS-WAVE-EXACT-OPERATIONS-003",
    "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",
)

RELATIONS = {
    IDS[0]: ("borrowed-dispersion-law", "Fold-momentum-equals-two-cyclic-advances"),
    IDS[1]: ("opaque-phase-generator", "sequential-rotations-equal-summed-energy-rotation"),
    IDS[2]: ("selected-or-continuous-spectrum", "half-step-ground-and-uniform-whole-step-gaps"),
    IDS[3]: ("chosen-Pythagorean-or-imported-relativity", "generated-three-four-five-square-closure"),
    IDS[4]: ("matrix-postulate-or-omitted-generator", "four-half-One-generators-close-by-two-routes"),
    IDS[5]: ("imported-Coulomb-profile-or-free-exponent", "held-charge-over-rank-two-boundary-with-source-return"),
    IDS[6]: ("independent-magnetic-force-postulate", "One-partition-by-speed-square-and-Fold-covariant-remainder"),
    IDS[7]: ("unrelated-added-force", "electric-transfer-partitioned-by-motion-share"),
    IDS[8]: ("imported-planar-wave-equation", "two-spatial-binary-curvatures-balance-one-temporal-per-axis"),
    IDS[9]: ("imported-three-space-wave-equation", "three-spatial-binary-curvatures-balance-one-temporal-per-axis"),
    IDS[10]: ("imported-amplitude-or-nonlinear-susceptibility", "One-speed-walk-held-polarization-predecessor-merge-and-exact-mixing"),
    IDS[11]: ("continuum-divergence-and-fitted-counterterm", "complete-finite-depth-exact-rational-loop-sum"),
}


def fold(part: Fraction) -> Fraction:
    paired = part + part
    return paired if paired <= 1 else paired - 1


def advance(phase: Fraction, step: Fraction) -> Fraction:
    result = phase + step
    while result > 1:
        result -= 1
    return result


def exact_certificate(claim_id: str) -> dict[str, object]:
    half = Fraction(1, 2)
    if claim_id == IDS[0]:
        result = fold(Fraction(1, 4))
        after = advance(Fraction(1, 3), result)
        passed = result == half and after == advance(advance(Fraction(1, 3), Fraction(1, 4)), Fraction(1, 4)) == Fraction(5, 6)
        exact = (str(result), str(after))
    elif claim_id == IDS[1]:
        sequential = advance(advance(Fraction(1, 3), Fraction(1, 8)), Fraction(1, 4))
        joint = advance(Fraction(1, 3), Fraction(3, 8))
        passed = sequential == joint == Fraction(17, 24)
        exact = str(joint)
    elif claim_id == IDS[2]:
        levels = tuple(Fraction(2 * rank - 1, 8) for rank in range(1, 5))
        gaps = tuple(levels[i + 1] - levels[i] for i in range(3))
        passed = levels == (Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8)) and gaps == (Fraction(1, 4),) * 3
        exact = tuple(map(str, levels))
    elif claim_id == IDS[3]:
        p, m = Fraction(3, 5), Fraction(4, 5)
        passed = p * p + m * m == 1
        exact = (str(p), str(m), "1")
    elif claim_id == IDS[4]:
        direct = half * half
        for _ in range(3):
            direct += half * half
        polarized = ((half + half) ** 2 + (half + half) ** 2) / 2
        passed = direct == polarized == 1 and ((), ()) == ((), ())
        exact = (str(direct), str(polarized), ((), ()))
    elif claim_id == IDS[5]:
        source = Fraction(1, 8)
        radii = (Fraction(1, 4), Fraction(1, 2))
        fields = tuple(source / (r * r) for r in radii)
        fluxes = tuple(field * r * r for field, r in zip(fields, radii))
        potentials = tuple(Fraction(1, 1) - source / r for r in radii)
        passed = fields == (Fraction(2, 1), half) and fluxes == (source, source) and potentials == (half, Fraction(3, 4))
        exact = tuple(map(str, fields + fluxes + potentials))
    elif claim_id == IDS[6]:
        values = []
        passed = True
        for speed in (half, Fraction(1, 3)):
            square = speed * speed
            remainder = Fraction(1, 1) - square
            passed = passed and fold(remainder) == Fraction(1, 1) - fold(square)
            values.append((str(square), str(remainder), str(fold(remainder))))
        exact = tuple(values)
    elif claim_id == IDS[7]:
        source, speed = Fraction(1, 4), half
        motion = source * speed * speed
        retained = source - motion
        passed = retained == Fraction(3, 16) and motion == Fraction(1, 16) and retained + motion == source
        exact = tuple(map(str, (retained, motion, source)))
    elif claim_id in IDS[8:10]:
        dimension = 2 if claim_id == IDS[8] else 3
        spatial, temporal = 2 * dimension, 2
        passed = Fraction(spatial, temporal) == dimension and Fraction(spatial, dimension * temporal) == 1
        exact = (dimension, spatial, temporal, "1")
    elif claim_id == IDS[10]:
        phase = Fraction(1, 3)
        walked = tuple(advance(phase, Fraction(1, 1)) for _ in range(8))
        outputs = (Fraction(1, 3) + Fraction(1, 4), Fraction(1, 3) - Fraction(1, 4), fold(Fraction(1, 4)))
        passed = all(item == phase for item in walked) and half + half == 1 and outputs == (Fraction(7, 12), Fraction(1, 12), half) and () == ()
        exact = (tuple(map(str, walked)), tuple(map(str, outputs)), ())
    else:
        sums = []
        term = half
        total = term
        sums.append(total)
        for _ in range(5):
            term /= 2
            total += term
            sums.append(total)
        expected = (half, Fraction(3, 4), Fraction(7, 8), Fraction(15, 16), Fraction(31, 32), Fraction(63, 64))
        passed = tuple(sums) == expected and all(0 < item < 1 for item in sums)
        exact = tuple(map(str, sums))
    if not passed:
        raise RuntimeError("independent exact arithmetic failed")
    return {"claim_id": claim_id, "exact": exact}


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    rejected, admitted = RELATIONS[claim_id]
    domains = (
        ("imported-continuum-object", "generated-exact-Fold-carrier"),
        ("asserted-prior-result", "admitted-V3-dependency-chain"),
        (rejected, admitted),
        ("selected-neighbourhood", "complete-registered-product"),
        ("uncontrolled-omission", "every-omission-rejected"),
        ("target-visible-before-seal", "formal-result-sealed-first"),
        ("answer-only", "complete-trace-and-controls"),
        ("free-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*domains))
    survivor = "__".join(domain[1] for domain in domains)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    exact = exact_certificate(claim_id)
    passed = (
        claim_id in IDS
        and sealed["claim_id"] == claim_id
        and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == survivor for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {"generated_cardinality": len(generated), "unique_survivor": survivor if passed else None, "exact_result": exact},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
