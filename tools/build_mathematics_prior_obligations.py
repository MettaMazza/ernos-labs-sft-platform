#!/usr/bin/env python3
"""Build the complete V1/V2 Mathematics ownership and reconstruction ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2 = ROOT / "audits/v2_407_step_observation_census.json"
OUTPUT = ROOT / "census/mathematics_prior_obligations.json"


def atom(atomic_id: str, statement: str, claims: tuple[str, ...], resolution: str = "reconstructed") -> dict[str, object]:
    return {
        "atomic_obligation_id": atomic_id,
        "prior_observation": statement,
        "categorical_owner": "mathematics",
        "v3_claim_ids": list(claims),
        "resolution_kind": resolution,
        "same_strength_closed": False,
        "disposition": "open_reconstruction_required",
        "reason": "Mapped V3 claims must all carry admitted receipts before this atomic obligation closes.",
    }


E = ("SFT-MATH-EXACT-ARITHMETIC-001",)
R = ("SFT-MATH-EXACT-RELATIONS-002",)
O = ("SFT-MATH-ORBIT-NUMBER-THEORY-002",)
L = ("SFT-MATH-LIMIT-CONTINUUM-002",)
A = ("SFT-MATH-ALGEBRAIC-BALANCE-002",)
N = ("SFT-MATH-BOUNDED-N-BODY-002",)
F = ("SFT-MATH-FLOORED-FLUID-REGULARITY-002",)
P = ("SFT-MATH-PRIME-PAIR-CENSUS-002",)
M = ("SFT-MATH-RIEMANN-MIRROR-002",)
C = ("SFT-MATH-COLLATZ-FINITE-CENSUS-002",)
S = ("SFT-MATH-SELF-SIMILAR-CONVERGENCE-002",)


V1_DECOMPOSITION: dict[str, tuple[dict[str, object], ...]] = {
    "Q3": (atom("V1-Q3-RATIO-SEPARATION", "Exact ratio and shorter-part separation.", R),),
    "Q6": (atom("V1-Q6-COUNT-MEASURE", "Generated count times its equal part reconstructs the One.", R),),
    "Q8": (atom("V1-Q8-SEPARATION-TRANSPORT", "Local uncast separation advances by the Fold factor.", R),),
    "Q9": (atom("V1-Q9-RELATIVE-VIEW", "Exact relative views telescope by ratio composition.", R),),
    "Q10": (atom("V1-Q10-HOLDING-THRESHOLD", "The m-fold holding complement is (m less One)-of-m.", R),),
    "Q12": (atom("V1-Q12-RECIPROCAL", "A positive relation composed with its reciprocal returns the One.", R),),
    "E1": (atom("V1-E1-JOINT-CYCLE", "Finite exact cycles first return jointly at their least common period.", R),),
    "E2": (atom("V1-E2-DYADIC-DESCENT", "Every power-of-two lattice part reaches the One after its counted depth.", L),),
    "E5": (atom("V1-E5-BEAT-PERIOD", "Exact separation modulation repeats at the joint cycle period.", R),),
    "PH1": (atom("V1-PH1-COMMENSURATE-PERIOD", "Commensurate finite periods compose by least common return.", R),),
    "PH1b": (atom("V1-PH1B-RELATIVE-BEAT", "Relative phase advances by the exact held frequency gap.", R),),
    "PH2": (atom("V1-PH2-CHAOTIC-ANTILOG", "Fold expansion and branch counts supply exact Lyapunov and entropy antilogs without logarithms.", S),),
    "PH3": (atom("V1-PH3-SYNCHRONIZATION-THRESHOLD", "The exact coupling balance is the m-fold holding complement.", R),),
    "D9p": (atom("V1-D9P-FINITE-DIFFERENCE", "Exact rational lattice second differences carry a refinement convergence certificate.", L),),
    "D9m": (atom("V1-D9M-FIXED-POINT-CONVERGENCE", "A decreasing exact-rational correction sequence is certified by rational bounds.", S),),
    "D1b": (atom("V1-D1B-ALGEBRAIC-BALANCE", "Algebraic magnitudes are positive polynomial-balance identities with exact rational brackets, never irrational proof values.", A),),
    "D9p2": (atom("V1-D9P2-GENUINE-LIMIT", "The cubic finite-difference error is a positive rational sequence halving at each refinement.", L),),
    "B9": (atom("V1-B9-EXACT-GAP", "The registered coupling gap is one over the product of two generated source counts.", S),),
    "B10": (atom("V1-B10-RATIONAL-SERIES", "Exact rational partial sums and a rational tail bound prove finite accumulated separation without admitting the limit as an irrational value.", S),),
    "XII-1": (atom("V1-XII1-PRIME-ORBIT", "Fold period equals binary multiplicative order; prime period divides one-less-than-prime; asymptotic prime counting remains outside the claim.", O),),
    "XII-2": (atom("V1-XII2-RIEMANN-MIRROR", "Prime orbit structure and the unique half-One symmetry axis are closed; classical complex zero location is explicitly outside the proof language.", M),),
    "XII-3": (atom("V1-XII3-CONTINUUM-BOUNDARY", "No completed continuum is an admitted object, so continuum cardinality is outside the generated language.", L),),
    "XII-6": (atom("V1-XII6-POTENTIAL-INFINITY", "Every finite stage has a successor but no completed actual infinity is admitted.", L),),
    "XIII-3": (atom("V1-XIII3-SHARED-STRUCTURE", "A Fold orbit and its arithmetic period are one object under physical and mathematical readings.", O),),
    "G6": (atom("V1-G6-ODD-DYADIC-DICHOTOMY", "Dyadic denominator factors are transient while reduced odd denominators recur with binary multiplicative-order period.", O),),
    "G7": (atom("V1-G7-COMPOSITE-PERIOD", "Component Fold cycles compose with least-common joint period.", ("SFT-MATH-ORBIT-NUMBER-THEORY-002", "SFT-MATH-EXACT-RELATIONS-002")),),
    "G10": (atom("V1-G10-THREE-BODY-FOLD", "A finite three-component componentwise Fold tuple recurs exactly on bounded denominators.", N),),
    "G14": (atom("V1-G14-N-BODY-FOLD", "Every positive finite componentwise Fold tuple is transient-to-periodic with computable joint return.", N),),
    "G15": (atom("V1-G15-FLOORED-REGULARITY", "A One-bounded velocity gap over a positive finite Fold floor has a finite exact discrete-gradient bound.", F),),
}


V2_DECOMPOSITION: dict[int, tuple[dict[str, object], ...]] = {
    1: (
        atom("V2-001-POSITIVE-WHOLES", "Unlimited generated finite whole traces support exact addition, product, power, comparison, quotient, remainder and greatest common divisor.", E),
        atom("V2-001-SIGN-ZERO-CORRECTION", "Prior signed/zero storage is implementation notation only; admitted direction uses held orientation and the empty case uses structural empty One.", E, "reconciled_boundary_correction"),
    ),
    2: (atom("V2-002-EXACT-FRACTIONS", "Exact positive fractions remain in lowest terms; decimal rendering never re-enters proof.", E),),
    3: (atom("V2-003-RHYTHM", "Return period, phase and beat are exact Fold-derived relations.", R),),
    4: (
        atom("V2-004-PERIOD-SPECTRUM", "Unit-part Fold periods are exact binary multiplicative orders.", O),
        atom("V2-004-COVER-DEPTH", "Cover depth is the first generated support reaching the declared finite volume.", S),
    ),
    27: (atom("V2-027-ORBIT-ORDER", "Fold return periods equal binary multiplicative orders.", O),),
    33: (atom("V2-033-THREE-CYCLE", "The one-, two- and four-of-seven tuple returns after three componentwise Folds.", N),),
    57: (atom("V2-057-BEAT-GAP", "The beat between exact parts is their held positive gap, with unison represented by a complete silent period.", R),),
    86: (atom("V2-086-N-BODY", "Every finite tuple occupying one Fold orbit returns with that orbit period.", N),),
    89: (atom("V2-089-RATIONAL-PROOF-VALUES", "Every scalar proof value generated by the rational kernel remains an exact fraction; algebraic correspondences use balance certificates.", ("SFT-MATH-EXACT-ARITHMETIC-001", "SFT-MATH-ALGEBRAIC-BALANCE-002")),),
    93: (atom("V2-093-QUADRATIC-DIFFERENCE", "The centered second difference of x-squared is exactly two at every positive rational spacing.", L),),
    102: (atom("V2-102-EXACT-EQUAL-SHARE", "The self-complementary binary support has two exact half-One shares.", ("SFT-MATH-PROBABILITY-STATISTICS-001", "SFT-MATH-EXACT-RELATIONS-002")),),
    103: (atom("V2-103-RATIONAL-THRESHOLD", "The mean-field threshold components are exact rational Fold parts; physical exponent correspondence belongs to Physics.", R),),
    118: (atom("V2-118-FINITE-LADDER", "Every dyadic rung is finite and the depth-five ladder plus its boundary rung closes to the One.", L),),
    121: (atom("V2-121-BALANCED-EXTREMUM", "Within the complement grammar, half-One is the unique two-sided balance candidate.", ("SFT-MATH-OPTIMIZATION-001", "SFT-MATH-RIEMANN-MIRROR-002")),),
    124: (atom("V2-124-FLOORED-GRADIENT", "At depth five, One over the positive one-of-thirty-two floor bounds native discrete vorticity by thirty-two.", F),),
    131: (atom("V2-131-PRIME-SPECTRUM", "Odd unit-part Fold periods are binary multiplicative orders and prime periods divide one-less-than-prime.", O),),
    132: (atom("V2-132-FIXED-AXIS", "Half-One is the unique fixed axis of the complement involution; symmetry alone is not admitted as a proof of classical complex zero location.", M, "reconciled_with_adverse_symmetry_control"),),
    158: (atom("V2-158-EFFECTIVENESS", "The physical Fold orbit and the arithmetic order calculation are the same exact transition structure under two readings.", O),),
    163: (atom("V2-163-POTENTIAL-INFINITE", "Every finite dyadic rung has a successor and every rung returns in finite counted depth.", L),),
    179: (atom("V2-179-RATIONAL-FIXED-POINT", "The stated exact rational self-map has a quarter-One fixed point and a shrinking rational gap on its declared initial basin.", S),),
    185: (atom("V2-185-SYNCHRONIZATION", "The binary transverse multiplier reaches the One exactly at half-One coupling.", R),),
    191: (atom("V2-191-UNIQUE-BALANCE", "Half-One is the unique self-complementary point in the exact complement grammar.", M),),
    192: (atom("V2-192-TRANSIENT-RECURRENT", "Dyadic descent, odd recurrence and predecessor merging are distinct exact Fold dynamical classes.", ("SFT-MATH-DYNAMICAL-SYSTEMS-001", "SFT-MATH-ORBIT-NUMBER-THEORY-002")),),
    203: (atom("V2-203-EXACT-CHAOTIC-RATE", "Local separation doubles and one predecessor distinction closes per Fold step.", S),),
    205: (atom("V2-205-PLANAR-LATTICE", "The finite plane extends generated incidence by two axes and two neighbours per axis without importing a continuum.", "SFT-MATH-GEOMETRY-TOPOLOGY-001" if False else ("SFT-MATH-GEOMETRY-TOPOLOGY-001",)),),
    209: (atom("V2-209-VIETA", "Exact root brackets are cross-checked by exact symmetric coefficient identities.", A),),
    219: (atom("V2-219-M-DEPTH", "An m-labelled successor support has m^d generated states at every finite depth.", S),),
    224: (atom("V2-224-RATIO-SCALE", "Exact rational dynamics preserves ratios under common whole rescaling; physical unit interpretation belongs to Physics.", R),),
    254: (atom("V2-254-LEVEL-DEPTH", "The generated binary scale successor supplies two-to-depth support at each finite depth.", S),),
    258: (atom("V2-258-GAP-FORMULA", "The exact rational gap formula is generated and strictly decreasing at every finite depth.", S),),
    259: (atom("V2-259-ACCUMULATED-SEPARATION", "Exact partial sums share two independent constructions and remain inside a proved rational bracket.", S),),
    277: (
        atom("V2-277-PARITY", "Every positive odd start maps to an even whole under three-times-plus-One.", C),
        atom("V2-277-BOUNDED-CENSUS", "Every start one through one hundred thousand reaches the 1-4-2 cycle and start twenty-seven takes 111 steps.", C),
        atom("V2-277-CONTRACTION-CORRECTION", "The constant three-quarter pointwise contraction shortcut is false and is rejected by the exact start-three counterexample.", C, "reconciled_by_mechanical_invalidation"),
    ),
    278: (atom("V2-278-PRIME-PAIR-CENSUS", "All 4,999 evens through ten thousand have a prime complement pair and the exact twin count is 205, with the finite boundary retained.", P),),
    286: (atom("V2-286-FOLD-NUMBER-THEORY", "Reduced odd rational orbits, cyclotomic tiling, antipodes and binary transients are exhaustively reconstructed.", O),),
    288: (atom("V2-288-UNIT-POWER", "The One exponent is uniquely self-similar under rank doubling and count halving in the enumerated positive whole exponent grammar.", S),),
    292: (atom("V2-292-FINITE-LADDER", "Every declared Fold ladder is a finite generated inventory with an explicit positive floor; physical inventories retain downstream owners.", L),),
    306: (atom("V2-306-CFD-BOUND", "The depth-five discrete-gradient bound is derived from the positive floor rather than installed as a tunable cap; application CFD remains a downstream test.", F, "reconciled_method_correction"),),
    391: (atom("V2-391-MATHEMATICS-CONSOLIDATION", "The twelve general mathematical kernels are registered with exact finite generation, controls and depth certificates.", tuple(f"SFT-MATH-{name}-001" for name in ("EXACT-ARITHMETIC", "DISCRETE", "COMBINATORICS", "GRAPH-NETWORK", "ALGEBRA", "ORDER-LATTICE", "GEOMETRY-TOPOLOGY", "PROBABILITY-STATISTICS", "OPTIMIZATION", "DYNAMICAL-SYSTEMS", "LOGIC-PROOF", "CATEGORY-TYPE-COMPOSITION"))),),
}


def main() -> None:
    v1 = json.loads(V1.read_text(encoding="utf-8")); v2 = json.loads(V2.read_text(encoding="utf-8"))
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}; v2_rows = {row["step"]: row for row in v2["steps"]}
    if set(V1_DECOMPOSITION) - set(v1_rows): raise SystemExit("Mathematics V1 decomposition cites an absent row")
    if set(V2_DECOMPOSITION) - set(v2_rows): raise SystemExit("Mathematics V2 decomposition cites an absent step")
    entries: list[dict[str, object]] = []
    for source_id, atoms in V1_DECOMPOSITION.items():
        row = v1_rows[source_id]
        entries.append({"source": "v1", "source_entry": source_id, "source_hash": row["source_row_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})
    for step, atoms in V2_DECOMPOSITION.items():
        row = v2_rows[step]
        entries.append({"source": "v2", "source_entry": step, "source_hash": row["source_block_sha256"], "source_observation": row["prior_result_observation"], "atomic_obligations": list(atoms)})
    admitted = {row["claim_id"] for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"] if row.get("model_admitted")}
    atoms = [item for entry in entries for item in entry["atomic_obligations"]]
    for item in atoms:
        mapped = set(item["v3_claim_ids"])
        if mapped and mapped.issubset(admitted):
            item["same_strength_closed"] = True
            item["disposition"] = "closed" if item["resolution_kind"] == "reconstructed" else item["resolution_kind"]
            item["reason"] = "Every mapped V3 claim carries a model-admitted receipt at the exact registered boundary; corrections and adverse invalidations are retained explicitly rather than erased."
    open_atoms = [item for item in atoms if not item["same_strength_closed"]]
    nonmath_v1 = [key for key in v1_rows if key not in V1_DECOMPOSITION]
    nonmath_v2 = [key for key in v2_rows if key not in V2_DECOMPOSITION]
    exclusion = json.dumps({"v1": nonmath_v1, "v2": nonmath_v2}, separators=(",", ":"), sort_keys=True).encode()
    payload = {
        "schema": "sft-v3-mathematics-prior-obligation-ledger/1",
        "status": "closed" if not open_atoms else "open",
        "source_policy": {"prior_results_are_observational_reconstruction_requirements": True, "prior_executable_answers_are_not_derivational_inputs": True, "composite_rows_are_decomposed": True, "corrections_and_invalidations_are_never_silently_dropped": True},
        "reviewed_source_surface": {
            "v1_total_rows": v1["source_row_count"], "v2_total_steps": v2["source_step_count"], "review_complete_for_branch_ownership": True,
            "reviewed_entry_count": v1["source_row_count"] + v2["source_step_count"],
            "mathematics_relevant_v1_rows": list(V1_DECOMPOSITION), "mathematics_relevant_v2_steps": list(V2_DECOMPOSITION),
            "reviewed_nonmathematics_v1_rows": nonmath_v1, "reviewed_nonmathematics_v2_steps": nonmath_v2,
            "nonmathematics_exclusion_identity": "sha256:" + hashlib.sha256(exclusion).hexdigest(),
        },
        "source_entries": entries,
        "mathematics_summary": {
            "atomic_obligation_count": len(atoms), "same_strength_closed_count": len(atoms) - len(open_atoms), "open_count": len(open_atoms),
            "open_atomic_obligation_ids": [item["atomic_obligation_id"] for item in open_atoms],
            "explicit_correction_or_invalidation_count": sum(item["resolution_kind"] != "reconstructed" for item in atoms),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}: mathematics={len(atoms)} open={len(open_atoms)}")


if __name__ == "__main__": main()

