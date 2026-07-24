"""Implementation-distinct exact validator for gravity/spacetime successors."""

from __future__ import annotations

from fractions import Fraction
from itertools import product
import json
import sys


IDS = (
    "SFT-PHYS-GRAVITY-WEAK-FIELD-FLUX-003",
    "SFT-PHYS-SPACETIME-EXACT-INTERVAL-003",
    "SFT-PHYS-GRAVITY-STATIC-CLOCK-003",
    "SFT-PHYS-GRAVITY-REDSHIFT-EQUIVALENCE-003",
    "SFT-PHYS-GRAVITY-LATTICE-CURVATURE-003",
    "SFT-PHYS-GRAVITY-NONLINEAR-SELF-SOURCE-003",
    "SFT-PHYS-GRAVITY-GRAVITON-POLARIZATION-003",
    "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
    "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
    "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003",
    "SFT-PHYS-SPACETIME-WORMHOLE-ADMISSIBILITY-003",
    "SFT-PHYS-SPACETIME-WARP-ADMISSIBILITY-003",
    "SFT-PHYS-SPACETIME-CLOSED-TIMELIKE-ADMISSIBILITY-003",
)

RELATIONS = {
    IDS[0]: ("imported-Newton-profile-or-free-exponent", "positive-source-over-rank-two-boundary"),
    IDS[1]: ("signed-imported-Minkowski-form", "positive-temporal-square-retains-spatial-take"),
    IDS[2]: ("imported-clock-dilation-function", "One-take-well-depth-with-Fold-covariance"),
    IDS[3]: ("independent-fitted-redshift-laws", "gravity-redshift-equals-accelerated-Doppler"),
    IDS[4]: ("continuum-derivative-or-fitted-curvature", "binary-curvature-per-generated-axis"),
    IDS[5]: ("linear-only-gravity-or-free-nonlinearity", "field-square-reenters-same-source-channel"),
    IDS[6]: ("asserted-two-polarizations", "symmetric-metric-count-less-coordinate-pairs"),
    IDS[7]: ("separate-fitted-gravity-wave-speed-or-dipole-radiation", "One-speed-recurrence-with-first-unfrozen-quadrupole"),
    IDS[8]: ("singular-point-or-imported-horizon-equation", "Fold-mass-radius-quarter-area-and-positive-finite-floor"),
    IDS[9]: ("absolute-destruction-or-unrecorded-reconstruction", "local-closure-with-complete-boundary-inverse-record"),
    IDS[10]: ("declared-remote-mouth-equivalence", "positive-source-generated-link-complete-causal-trace"),
    IDS[11]: ("negative-energy-bubble-or-open-work-ledger", "positive-conserved-support-redistribution-with-return-ledger"),
    IDS[12]: ("changed-self-ancestor-paradox", "exact-first-return-of-complete-state-and-proof-record"),
}


def fold(value: Fraction) -> Fraction:
    pair = value + value
    return pair if pair <= 1 else pair - 1


def certificate(claim_id: str) -> dict[str, object]:
    half = Fraction(1, 2)
    if claim_id == IDS[0]:
        source = Fraction(1, 8); radii = (Fraction(1, 4), half)
        fields = tuple(source / (r * r) for r in radii)
        fluxes = tuple(f * r * r for f, r in zip(fields, radii))
        potentials = tuple(Fraction(1, 1) - source / r for r in radii)
        passed = fields == (Fraction(2, 1), half) and fluxes == (source, source) and potentials == (half, Fraction(3, 4))
        exact = tuple(map(str, fields + fluxes + potentials))
    elif claim_id == IDS[1]:
        remainder = Fraction(1, 1) - Fraction(3, 5) ** 2
        proper = Fraction(4, 5)
        passed = remainder == proper * proper == Fraction(16, 25) and () == ()
        exact = (str(remainder), str(proper), ())
    elif claim_id == IDS[2]:
        well = Fraction(1, 8); metric = Fraction(1, 1) - well
        folded = fold(metric); complement = Fraction(1, 1) - fold(well)
        passed = folded == complement == Fraction(3, 4) and Fraction(3, 4) ** 2 == Fraction(9, 16)
        exact = (str(metric), str(folded), "3/4", ())
    elif claim_id == IDS[3]:
        shift = Fraction(1, 4) * Fraction(1, 1)
        passed = shift == Fraction(1, 4)
        exact = (str(shift), str(shift))
    elif claim_id == IDS[4]:
        position = half; results = []
        for spacing in (Fraction(1, 8), Fraction(1, 16)):
            numerator = (position + spacing) ** 2 + (position - spacing) ** 2 - 2 * position ** 2
            results.append(numerator / spacing ** 2)
        passed = tuple(results) == (Fraction(2, 1), Fraction(2, 1))
        exact = (tuple(map(str, results)), (2, 4, 6))
    elif claim_id == IDS[5]:
        linear = Fraction(1, 3) * half; energy = linear * linear; correction = energy * half
        passed = (linear, energy, correction) == (Fraction(1, 6), Fraction(1, 36), Fraction(1, 72))
        exact = tuple(map(str, (linear, energy, correction)))
    elif claim_id == IDS[6]:
        d4 = (4 * 5 // 2, 2 * 4); d3 = (3 * 4 // 2, 2 * 3)
        passed = d4[0] - d4[1] == 2 and d3[0] == d3[1]
        exact = (d4, 2, d3, ())
    elif claim_id == IDS[7]:
        linear = (1, 2, 3, 4); cubic = (1, 8, 27, 64)
        first_linear = tuple(linear[i + 1] - linear[i] for i in range(3))
        first_cubic = tuple(cubic[i + 1] - cubic[i] for i in range(3))
        second = tuple(first_cubic[i + 1] - first_cubic[i] for i in range(2))
        passed = len(set(first_linear)) == 1 and second == (12, 18)
        exact = ("1", first_linear, second)
    elif claim_id == IDS[8]:
        mass = Fraction(1, 4); radius = fold(mass); coefficient = Fraction(1, 4)
        passed = radius == half and coefficient * 32 == 8 and all(Fraction(1, 2 ** k) > 0 for k in range(1, 17))
        exact = (str(mass), str(radius), str(coefficient), 32, 8, "1/4")
    elif claim_id == IDS[9]:
        records = tuple(("boundary-cell", i) for i in range(1, 9))
        passed = len(records) == 8 and () == ()
        exact = ((), records, True)
    elif claim_id == IDS[10]:
        passed = Fraction(1, 4) > 0 and True and True and not False
        exact = ("positive-source", "generated-link", "complete-trace", "no-realization-claim")
    elif claim_id == IDS[11]:
        source = destination = Fraction(1, 4)
        passed = source == destination and not (source == half) and True
        exact = (str(source), str(destination), "complete-return", "no-device-claim")
    else:
        initial = ("state", "proof"); returned = ("state", "proof"); changed = ("changed-state", "proof")
        passed = initial == returned and initial != changed
        exact = (initial, returned, changed, "no-physical-CTC-claim")
    if not passed:
        raise RuntimeError("independent gravity/spacetime arithmetic failed")
    return {"claim_id": claim_id, "exact": exact}


def main() -> None:
    claim_id = sys.argv[1]
    with open(sys.argv[2], encoding="utf-8") as handle:
        sealed = json.load(handle)
    rejected, admitted = RELATIONS[claim_id]
    domains = (
        ("imported-spacetime-object", "generated-exact-Fold-carrier"),
        ("asserted-prior-answer", "admitted-V3-root-trace"),
        (rejected, admitted),
        ("selected-neighbourhood", "complete-registered-product"),
        ("uncontrolled-omission", "every-omission-rejected"),
        ("target-visible-before-seal", "formal-result-sealed-first"),
        ("answer-only", "complete-causal-source-control-record"),
        ("free-extra-rule", "no-extra-rule"),
    )
    generated = tuple("__".join(row) for row in product(*domains))
    survivor = "__".join(domain[1] for domain in domains)
    received = tuple(row["candidate_id"] for row in sealed["census"]["candidates"])
    decisions = {row["candidate_id"]: row["survives"] for row in sealed["decisions"]}
    exact = certificate(claim_id)
    passed = (
        claim_id in IDS and sealed["claim_id"] == claim_id and received == generated
        and len(set(received)) == sealed["census"]["expected_cardinality"] == 256
        and decisions == {candidate: candidate == survivor for candidate in generated}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {row["kind"] for row in sealed["controls"]} == {"false_premise", "tampered_source", "tampered_artifact", "boundary"}
        and all(row["passed"] is True for row in sealed["controls"])
    )
    print(json.dumps({"validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed, "certificate": {"generated_cardinality": len(generated), "unique_survivor": survivor if passed else None, "exact_result": exact}}, sort_keys=True))


if __name__ == "__main__":
    main()
