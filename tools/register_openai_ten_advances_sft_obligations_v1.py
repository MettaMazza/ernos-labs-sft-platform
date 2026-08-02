#!/usr/bin/env python3
"""Register the twelve OpenAI 2026 theorem reconstructions without a verdict census.

This tool freezes source statements, quantifiers, categorical ownership, exact
SFT-native translations, correspondence obligations and pre-existing SFT
dependencies.  It deliberately does not execute or admit a theorem.  A later
claim-specific derivation must prove the registered proposition through the
unchanged engine; failure remains a halt and cannot be converted into a
disproof by changing the carrier.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_CAPTURE = (
    ROOT
    / "experiments/external_sources/mathematics/"
    "openai_ten_advances_mathematics_2026-08-01_v1"
)
SOURCE_ROOT = (
    SOURCE_CAPTURE
    / "upstream_tree/ten-proofs-94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
)
OWNER_LEDGER = ROOT / "audits/OPENAI_TEN_ADVANCES_ONE_OWNER_LEDGER_2026-08-02.json"
REGISTRY = ROOT / "census/openai_ten_advances_2026_sft_obligation_registry_v1.json"
SOURCE_COMMIT = "94bc0feb6a9ff12c7d31d6de640a725c9d43d2b6"
SOURCE_CAPTURE_ID = "OPENAI-TEN-ADVANCES-MATHEMATICS-2026-08-01-V1"


TRANSLATION_SEMANTICS = {
    "scope": (
        "Exact preservation on every SFT-admissible encoding of every source binder. "
        "No source conjunct, implication, quantifier dependency or strict inequality may be dropped."
    ),
    "generated_natural": (
        "A potential-successor natural: every supplied value is a positive finite construction; "
        "an unrestricted source forall over naturals requires a base-and-successor certificate."
    ),
    "exact_real_name": (
        "A source real is represented by a coherent generator of nested exact rational enclosures, "
        "held orientation and operation certificates. It is not imported as a completed continuum scalar."
    ),
    "finite_type": (
        "A source Fintype is represented by a complete duplicate-free generated carrier and total index maps."
    ),
    "generated_structure": (
        "Groups, graphs, formulas, games, lattices, sets and operators are finite descriptions with total "
        "generators and replayable law certificates; a description may generate arbitrarily many finite stages."
    ),
    "eventually": (
        "The source atTop/eventually proposition is represented by an exact generated threshold and a "
        "base-and-successor proof that the predicate holds at every generated later stage."
    ),
    "tendsto": (
        "The source limit proposition is represented by a modulus transforming every supplied positive "
        "rational tolerance into a generated threshold plus an exact enclosure proof thereafter."
    ),
    "source_negation": (
        "Negation retains the source predicate and requires a derivation of its logical negation; "
        "an unencoded or inadmissible carrier is not a negation."
    ),
    "correspondence": (
        "For every admitted encoding e with decoder d, decode(encode(x)) = x and the source proposition "
        "at d(e) holds iff the SFT-native proposition at e holds. Surjectivity onto ungenerated source "
        "objects is not asserted and cannot be used to broaden a verdict."
    ),
}


ROWS = (
    {
        "atomic_id": "OAI26-MATH-001",
        "claim_id": "SFT-MATH-OAI26-SPHERE-PACKING-001",
        "owner": "mathematics",
        "title": "SFT reconstruction of sharp Cohn-Elkies sphere-packing asymptotics",
        "declaration": "PackingBounds.sharpFullCohnElkiesManuscriptConclusions",
        "source_file": "SpherePacking.lean",
        "signature_span": (55591, 55592),
        "expanded_spans": ((55430, 55488, "SharpFullCohnElkiesManuscriptConclusions"),),
        "quantifiers": (
            "root_before_infimum: Tendsto over generated dimension d",
            "root_before_infimum_vanishing_error: exists err : Nat -> Real; Tendsto err; forall positive d, exact equality",
            "linear_program_root: Tendsto over generated dimension d",
            "natural_logarithmic_rate: Tendsto over generated dimension d",
            "natural_vanishing_exponential_error: exists err : Nat -> Real; Tendsto err; eventually forall d, exact equality",
            "universal_nonnegative_delta: exists delta : Nat -> Real; Tendsto delta; forall d nonnegative; eventually forall d and every FullAdmissible f, lower bound",
            "base_two_exponent_positive: closed strict inequality",
            "base_two_decimal_certificate: closed interval membership",
            "base_two_logarithmic_rate: Tendsto over generated dimension d",
            "base_two_vanishing_exponential_error: exists err : Nat -> Real; Tendsto err; eventually forall d, exact equality",
        ),
        "native_formula": (
            "The ten-field SharpFullCohnElkiesManuscriptConclusions record holds with every Real replaced by "
            "an exact-real name, every Tendsto by its modulus-and-enclosure definition, every eventually-atTop "
            "by a generated threshold plus successor proof, and every FullAdmissible/fullQuotient/fullLinearProgram "
            "object by its total generated SFT encoding; all ten fields and their original conjunction are retained."
        ),
        "dependencies": (
            "SFT-MATH-GEOM-PACKING-COVERING-TESSELLATION-015",
            "SFT-MATH-ANAL-HARMONIC-FOURIER-SUPPORT-009",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "packing supports x Fourier-support certificates x exact enclosure refinements x generated-dimension successor traces",
    },
    {
        "atomic_id": "OAI26-MATH-002",
        "claim_id": "SFT-MATH-OAI26-BINARY-CODE-MRRW-002",
        "owner": "mathematics",
        "title": "SFT reconstruction of the strict binary-code MRRW improvement",
        "declaration": "MetricCodes.Johnson.binaryRate_lt_mrrw",
        "source_file": "MetricCodes.lean",
        "signature_span": (20797, 20799),
        "expanded_spans": (),
        "quantifiers": (
            "implicit forall d : Real",
            "hypothesis 0 < d",
            "hypothesis d < 1/2",
            "conclusion binaryRate d < mrrwRate d",
        ),
        "native_formula": (
            "For every admissible exact-real name d, if d is strictly positive and strictly below one-of-two, "
            "then the generated-enclosure value of Hamming binaryRate d is strictly below the generated-enclosure "
            "value of mrrwRate d, with a positive rational separation certificate."
        ),
        "dependencies": (
            "SFT-MATH-COMB-CODING-PACKING-010",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "complete finite binary-code censuses x exact distance names x rate enclosures x length-successor certificates",
    },
    {
        "atomic_id": "OAI26-MATH-003",
        "claim_id": "SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-003",
        "owner": "mathematics",
        "title": "SFT reconstruction of the strict spherical-code hierarchy",
        "declaration": "MetricCodes.Spherical.HigherHierarchy.strict_hierarchy",
        "source_file": "MetricCodes.lean",
        "signature_span": (114336, 114344),
        "expanded_spans": (),
        "quantifiers": (
            "implicit forall s : Real",
            "hypothesis 0 < s",
            "hypothesis s < 1",
            "forall r : Nat, two strict successor-level inequalities",
            "four retained hierarchy/row/level comparisons and one terminal equality",
        ),
        "native_formula": (
            "For every admissible exact-real name s strictly between structural absence and the One, every generated "
            "level r satisfies both strict successor-level inequalities, and the source conjunction linking sphericalCodeRate, "
            "localizedHierarchyRate, localizedLevelRate one, localizedRowRate, localizedLevelRate base and "
            "classicalLocalizedRate holds with exact enclosure/separation certificates."
        ),
        "dependencies": (
            "SFT-MATH-COMB-CODING-PACKING-010",
            "SFT-MATH-GEOM-PACKING-COVERING-TESSELLATION-015",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "spherical-code supports x packing certificates x hierarchy-level successor traces x exact rate enclosures",
    },
    {
        "atomic_id": "OAI26-MATH-004",
        "claim_id": "SFT-MATH-OAI26-NONSOFIC-GROUP-004",
        "owner": "mathematics",
        "title": "SFT reconstruction of a finitely presented non-sofic group",
        "declaration": "SoficGroups.SourceTopLevelCompressionFinal.exists_finitelyPresented_nonsofic_group",
        "source_file": "NonSoficGroup.lean",
        "signature_span": (34430, 34432),
        "expanded_spans": (),
        "quantifiers": (
            "exists a carrier type G",
            "exists a Group G instance",
            "Group.IsFinitelyPresented G",
            "not SoficGroups.Sofic G",
        ),
        "native_formula": (
            "There exists an admissible generated group description G with a total group-law certificate and a finite "
            "presentation certificate such that the exact SFT translation of SoficGroups.Sofic G is false; the negation "
            "must exhaust the complete finite-test/permutation-approximation witness grammar rather than infer from carrier rejection."
        ),
        "dependencies": (
            "SFT-MATH-ALG-GROUP-HELD-INVERSE-004",
            "SFT-MATH-ALG-PERMUTATION-GROUP-ACTION-005",
            "SFT-MATH-LOGIC-MODEL-INTERPRETATION-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "finite group presentations x generated word carriers x finite test sets x permutation actions x exact error/separation enclosures",
    },
    {
        "atomic_id": "OAI26-MATH-005",
        "claim_id": "SFT-MATH-OAI26-CONNES-RIGIDITY-005",
        "owner": "mathematics",
        "title": "SFT reconstruction of the Connes-rigidity counterexample family",
        "declaration": "ConnesRigidity.exists_infinite_pairwise_nonisomorphic_propertyT_icc_groups_with_isomorphic_factors",
        "source_file": "ConnesRigidity.lean",
        "signature_span": (37348, 37361),
        "expanded_spans": (),
        "quantifiers": (
            "exists Lambda : CountableDiscreteGroup",
            "exists Gamma : Nat -> CountableDiscreteGroup",
            "FG Lambda and forall n, FG (Gamma n)",
            "IsICC Lambda and forall n, IsICC (Gamma n)",
            "HasKazhdanPropertyT Lambda and forall n, HasKazhdanPropertyT (Gamma n)",
            "forall n, TracialGroupFactorsIsomorphic (Gamma n) Lambda",
            "forall m n, TracialGroupFactorsIsomorphic (Gamma m) (Gamma n)",
            "forall m n, m != n implies not GroupsIsomorphic (Gamma m) (Gamma n)",
            "forall n, not GroupsIsomorphic Lambda (Gamma n)",
        ),
        "native_formula": (
            "There exist a generated countable-discrete-group description Lambda and a successor generator Gamma for group "
            "descriptions satisfying every source FG, ICC, property-(T), tracial-factor-isomorphism and group-nonisomorphism "
            "conjunct, with each universal natural quantifier carried by base-and-successor certificates and every operator/factor "
            "relation carried by exact generated support."
        ),
        "dependencies": (
            "SFT-MATH-ALG-GROUP-HELD-INVERSE-004",
            "SFT-MATH-ALG-REPRESENTATION-ACTION-DECOMPOSITION-013",
            "SFT-MATH-ANAL-BOUNDED-COMPACT-OPERATOR-008",
            "SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "generated group presentations x representation actions x operator supports x finite-support traces x family-successor certificates",
    },
    {
        "atomic_id": "OAI26-COMP-001",
        "claim_id": "SFT-COMP-OAI26-PERMANENT-FORMULA-001",
        "owner": "computation",
        "title": "SFT reconstruction of the permanent rational-formula lower bound",
        "declaration": "PermanentFormulaLowerBound.permanent_rational_formula_logarithmic_lower_bound",
        "source_file": "Permanent.lean",
        "signature_span": (27551, 27560),
        "expanded_spans": (),
        "quantifiers": (
            "implicit forall n : Nat",
            "hypothesis 32 <= n",
            "forall f : RationalFormula (Fin n x Fin n) Complex",
            "hypothesis RationalFormula.Valid f",
            "hypothesis eval f equals the fraction-ring image of permanentPolynomial n",
            "conclusion n^4/(192*log base 2 n) <= variableLeaves f",
        ),
        "native_formula": (
            "For every generated n at least thirty-two and every admissible canonical encoding of a valid rational formula "
            "over structurally paired exact complex coordinates whose evaluation equals the encoded permanent polynomial in "
            "the encoded fraction ring, the source lower bound on variable leaves holds as an exact-real enclosure inequality."
        ),
        "dependencies": (
            "SFT-MATH-SYMB-CANONICAL-EXPRESSION-001",
            "SFT-COMP-CPLXX-FORMULA-BRANCHING-CIRCUIT-014",
            "SFT-COMP-CPLXX-ARBITRARY-FOLD-CIRCUIT-LOWER-024",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
        ),
        "governing_grammar": "canonical rational-formula syntax x validity/evaluation traces x permanent expression support x leaf-resource certificates x size-successor induction",
    },
    {
        "atomic_id": "OAI26-QUANTUM-001",
        "claim_id": "SFT-QUANTUM-OAI26-PARALLEL-REPETITION-001",
        "owner": "quantum_computation",
        "title": "SFT reconstruction of distribution-uniform quantum parallel repetition",
        "declaration": "QuantumParallelRepetition.distributionUniformExponential",
        "source_file": "QuantumParallelRepetition.lean",
        "signature_span": (70953, 70968),
        "expanded_spans": (),
        "quantifiers": (
            "exists c : Real with 0 < c",
            "forall types X Y A B with Fintype instances",
            "forall game G : Game X Y A B",
            "Nonempty A implies Nonempty B implies positive entangled-value gap implies",
            "forall n : Nat, 0 < n implies the stated repeatedEntangledValue exponential upper bound",
        ),
        "native_formula": (
            "There exists one positive exact-real name c such that for every complete finite generated question/answer carrier "
            "and every admitted encoded two-player game with nonempty answer carriers and positive exact entangled-value gap, "
            "every positive generated repetition count satisfies the complete source exponential inequality under the exact "
            "strategy-value and logarithm/exponential enclosure translations."
        ),
        "dependencies": (
            "SFT-QUANTUM-ENTANGLEMENT-001",
            "SFT-QUANTUM-QCPLXX-PARALLEL-016",
            "SFT-QUANTUM-QCPLXX-REDUCTION-018",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
        ),
        "governing_grammar": "finite game carriers x complete strategy supports x exact entangled-value enclosures x repetition successor traces x parallel-resource certificates",
    },
    {
        "atomic_id": "OAI26-COMP-002",
        "claim_id": "SFT-COMP-OAI26-GAPCVP400-002",
        "owner": "computation",
        "title": "SFT reconstruction of GapCVP400 NP-hardness",
        "declaration": "GapCVP.Comparator.gapCVP400IsNPHard",
        "source_file": "GapCVP.lean",
        "signature_span": (130398, 130398),
        "expanded_spans": ((130203, 130214, "PromiseReduction and IsNPHardPromise"),),
        "quantifiers": (
            "forall language : BitLanguage",
            "IsNP language implies Nonempty (PromiseReduction language gapCVP400Promise)",
            "each PromiseReduction existentially carries a total bit-list map and polynomial-time BitTM witness",
            "forall input, language input implies target yes",
            "forall input, not language input implies target no",
        ),
        "native_formula": (
            "For every admissible generated bit language carrying an exact SFT IsNP witness, there exists a total generated "
            "bit-list reduction to the exact encoded gapCVP400 promise, a polynomial-resource machine certificate, and complete "
            "per-input yes-preservation and no-preservation proofs; the four PromiseReduction fields are retained."
        ),
        "dependencies": (
            "SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006",
            "SFT-MATH-GEOM-EUCLIDEAN-DISTANCE-002",
            "SFT-COMP-CPLXX-REDUCTION-COMPLETE-PROBLEM-021",
            "SFT-COMP-CPLXX-APPROXIMATION-RATIO-026",
        ),
        "governing_grammar": "generated bit languages x NP witness machines x total reduction maps x exact lattice instances x promise verdict/resource traces",
    },
    {
        "atomic_id": "OAI26-MATH-006",
        "claim_id": "SFT-MATH-OAI26-EHRHART-VOLUME-006",
        "owner": "mathematics",
        "title": "SFT reconstruction of the sharp Ehrhart volume inequality",
        "declaration": "Ehrhart.Volume.ehrhart_volume_inequality_for_sets",
        "source_file": "EhrhartVolumeInequality.lean",
        "signature_span": (55733, 55738),
        "expanded_spans": (),
        "quantifiers": (
            "implicit forall n : Nat",
            "hypothesis 0 < n",
            "forall S : Set (Space n)",
            "hypotheses Convex Real S, IsCompact S, Nonempty (interior S)",
            "hypothesis barycenter S = zero",
            "hypothesis interiorLatticePoints S = singleton zero",
            "conclusion normalizedVolume S <= (n+1)^n / n!",
        ),
        "native_formula": (
            "For every positive generated dimension and every admissible exact generated encoding of a real-space set with "
            "certificates for the source convexity, compactness, nonempty interior, centered barycenter and unique interior "
            "lattice point hypotheses, the exact normalized-volume enclosure is at most (n plus One)^n divided by n factorial."
        ),
        "dependencies": (
            "SFT-MATH-GEOM-CONVEX-HULL-SEPARATION-005",
            "SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006",
            "SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005",
            "SFT-MATH-MEAS-CONVERGENCE-FINITE-WITNESS-010",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
        ),
        "governing_grammar": "generated convex-body descriptions x lattice-point support x barycenter certificates x exact volume enclosures x dimension-successor traces",
    },
    {
        "atomic_id": "OAI26-MATH-007",
        "claim_id": "SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-007",
        "owner": "mathematics",
        "title": "SFT reconstruction of Erdos problem 183",
        "declaration": "ErdosProblems.MulticolourTriangleRamsey.erdos_problem_183_explicit",
        "source_file": "MulticolorTriangleRamsey.lean",
        "signature_span": (3042, 3050),
        "expanded_spans": (),
        "quantifiers": (
            "first conjunct: forall k : Nat, 2 <= k implies the explicit real lower bound for triangleRamseyNumber k",
            "second conjunct: Tendsto atTop atTop of k-th roots of triangleRamseyNumber k",
        ),
        "native_formula": (
            "The original two-conjunct proposition holds: every generated colour count k at least two satisfies the full "
            "explicit lower bound through exact exp/log/fractional-power enclosures, and a generated threshold/modulus plus "
            "successor proof establishes divergence of the k-th-root sequence beyond every supplied exact bound."
        ),
        "dependencies": (
            "SFT-MATH-COMB-RAMSEY-FORCING-011",
            "SFT-MATH-COMB-CODING-PACKING-010",
            "SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "complete multicolour edge-colouring supports x separated palette codes x Ramsey witnesses x colour-successor induction x divergence modulus",
    },
    {
        "atomic_id": "OAI26-MATH-008",
        "claim_id": "SFT-MATH-OAI26-COMPACTNESS-008",
        "owner": "mathematics",
        "title": "SFT reconstruction of the quantitative compactness counterexample",
        "declaration": "CompactnessConjecture.quantitativeCompactnessCounterexample",
        "source_file": "CompactnessAndDegeneracy.lean",
        "signature_span": (9320, 9337),
        "expanded_spans": ((27, 39, "IsCompactFamily and CompactnessConjectureStatement"),),
        "quantifiers": (
            "exists finite family of FiniteGraph and real constants c C",
            "family nonempty",
            "forall forbidden in family: connected, bipartite and cyclic",
            "positive c and positive C",
            "UniformMemberLower family c",
            "forall n and every host SimpleGraph (Fin n), FamilyFree implies the sixteenth-power host bound",
            "forall n, the sixteenth-power familyExtremal bound",
            "positive 1/48 and exact exponent identity",
            "not IsCompactFamily family and not CompactnessConjectureStatement",
        ),
        "native_formula": (
            "There exist one complete finite generated forbidden-graph family and positive exact-real names c and C satisfying "
            "every source geometry, member-lower, all-host, all-size, exponent, noncompactness and conjecture-negation conjunct; "
            "both negations require actual predicate refutations under their exact translations."
        ),
        "dependencies": (
            "SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007",
            "SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007",
            "SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "finite forbidden-family supports x complete host graphs x free/embedding relations x extremal counts x size-successor certificates",
    },
    {
        "atomic_id": "OAI26-MATH-009",
        "claim_id": "SFT-MATH-OAI26-TWO-DEGENERATE-009",
        "owner": "mathematics",
        "title": "SFT reconstruction of the two-degenerate extremal counterexample",
        "declaration": "TwoDegenerateGraphs.twoDegenerateExtremalCounterexample",
        "source_file": "CompactnessAndDegeneracy.lean",
        "signature_span": (18441, 18453),
        "expanded_spans": (),
        "quantifiers": (
            "exists q : Nat and H : SimpleGraph (Fin q)",
            "H connected, bipartite and two-degenerate",
            "forall two-colourings of H and forall sides, maximum side degree is greater than two",
            "exists real c epsilon with both positive",
            "eventually for all n atTop, c*n^(3/2+epsilon) <= extremalNumber n H",
        ),
        "native_formula": (
            "There exist a generated vertex count q and complete finite graph H satisfying the exact connected, bipartite, "
            "two-degenerate and every-two-colouring degree conjuncts, together with positive exact-real names c and epsilon "
            "and a generated threshold plus successor proof for the complete extremal-number lower bound."
        ),
        "dependencies": (
            "SFT-MATH-COMB-EXTREMAL-SET-SYSTEM-007",
            "SFT-MATH-GRAPH-COLOURING-CONSTRAINT-006",
            "SFT-MATH-GRAPH-MATCHING-COVERING-PACKING-007",
            "SFT-MATH-CALC-RATIONAL-ENCLOSURE-CONVERGENCE-006",
            "SFT-MATH-LIMIT-CONTINUUM-002",
        ),
        "governing_grammar": "finite graph supports x two-colouring census x degree/degeneracy witnesses x extremal host traces x size-successor threshold certificate",
    },
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def object_identity(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_identity(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def source_slice(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise AssertionError(f"invalid source span {path.name}:{start}-{end}")
    return "\n".join(lines[start - 1 : end])


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_protected_seals() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        completed = subprocess.run(
            (sys.executable, str(ROOT / "tools" / tool), "--json"),
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        data = json.loads(completed.stdout)
        if completed.returncode or data.get("status") != expected:
            raise SystemExit(f"registration halted: {tool} did not validate")


def main() -> None:
    verify_protected_seals()
    owner = json.loads(OWNER_LEDGER.read_text(encoding="utf-8"))
    if owner.get("source_commit") != SOURCE_COMMIT or owner.get("counts") != {
        "advertised_advances": 10,
        "formal_declarations": 12,
        "mathematics": 9,
        "computation": 2,
        "quantum_computation": 1,
    }:
        raise SystemExit("registration halted: ownership/source ledger mismatch")
    if len(ROWS) != 12 or len({row["claim_id"] for row in ROWS}) != 12:
        raise SystemExit("registration halted: twelve unique claim identities required")

    owner_rows = {row["atomic_id"]: row for row in owner["rows"]}
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    registry_rows = []
    staged = []

    for row in ROWS:
        package = ROOT / "claims" / row["claim_id"]
        if package.exists():
            raise SystemExit(f"registration halted: package already exists: {row['claim_id']}")
        ledger_row = owner_rows.get(row["atomic_id"])
        if not ledger_row:
            raise SystemExit(f"registration halted: owner row missing: {row['atomic_id']}")
        if ledger_row["owner"] != row["owner"] or ledger_row["declaration"] != row["declaration"]:
            raise SystemExit(f"registration halted: owner/declaration mismatch: {row['atomic_id']}")
        if tuple(ledger_row["typed_dependencies"]) != tuple(row["dependencies"][: len(ledger_row["typed_dependencies"])]):
            # Dependency extension is allowed, but every ledger dependency must remain present.
            if not set(ledger_row["typed_dependencies"]).issubset(row["dependencies"]):
                raise SystemExit(f"registration halted: ledger dependency omitted: {row['atomic_id']}")
        missing = tuple(dependency for dependency in row["dependencies"] if dependency not in admitted)
        if missing:
            raise SystemExit(f"registration halted: unadmitted dependencies for {row['claim_id']}: {missing}")

        source_path = SOURCE_ROOT / row["source_file"]
        signature = source_slice(source_path, *row["signature_span"])
        terminal_name = row["declaration"].rsplit(".", 1)[-1]
        if terminal_name not in signature:
            raise SystemExit(f"registration halted: declaration anchor missing: {row['claim_id']}")
        expanded = []
        for start, end, label in row["expanded_spans"]:
            text = source_slice(source_path, start, end)
            expanded.append(
                {
                    "label": label,
                    "start_line": start,
                    "end_line": end,
                    "text": text,
                    "sha256": "sha256:" + hashlib.sha256(text.encode()).hexdigest(),
                }
            )
        source_record = {
            "schema": "sft-v3-external-theorem-source-statement/1",
            "claim_id": row["claim_id"],
            "atomic_id": row["atomic_id"],
            "source_capture_id": SOURCE_CAPTURE_ID,
            "source_commit": SOURCE_COMMIT,
            "declaration": row["declaration"],
            "source_file": row["source_file"],
            "source_file_sha256": file_identity(source_path),
            "signature_start_line": row["signature_span"][0],
            "signature_end_line": row["signature_span"][1],
            "signature_text": signature,
            "signature_sha256": "sha256:" + hashlib.sha256(signature.encode()).hexdigest(),
            "expanded_source_definitions": expanded,
            "exact_quantifier_and_conjunct_order": list(row["quantifiers"]),
            "upstream_sorry_count": 0,
            "upstream_declared_axioms": ["propext", "Classical.choice", "Quot.sound"],
            "derivational_authority_for_sft": False,
        }
        staged.append((row, package, source_record))
        registry_rows.append(
            {
                "atomic_id": row["atomic_id"],
                "claim_id": row["claim_id"],
                "owner": row["owner"],
                "declaration": row["declaration"],
                "source_file": row["source_file"],
                "source_statement_hash": object_identity(source_record),
                "native_formula": row["native_formula"],
                "governing_preexisting_claims": list(row["dependencies"]),
                "governing_grammar_composition": row["governing_grammar"],
                "registered_outcome": None,
            }
        )

    registry_payload = {
        "schema": "sft-v3-openai-ten-advances-obligation-registry/1",
        "registry_date": "2026-08-02",
        "source_capture_id": SOURCE_CAPTURE_ID,
        "source_commit": SOURCE_COMMIT,
        "owner_ledger_path": OWNER_LEDGER.relative_to(ROOT).as_posix(),
        "owner_ledger_sha256": file_identity(OWNER_LEDGER),
        "counts": {"formal_declarations": 12, "mathematics": 9, "computation": 2, "quantum_computation": 1},
        "translation_semantics": TRANSLATION_SEMANTICS,
        "verdict_selection_rule": (
            "No verdict coordinate is generated or registered. Each proposition is submitted only after a proof of the "
            "registered native formula or an actual negation/counterexample forces a scientifically distinct successor."
        ),
        "rows": registry_rows,
    }
    registry_payload["registry_identity"] = object_identity(registry_payload)
    write_json(REGISTRY, registry_payload)

    for row, package, source_record in staged:
        registration = {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": row["claim_id"],
            "title": row["title"],
            "branch": row["owner"],
            "status": "registered",
            "statement": row["native_formula"],
            "dependencies": list(row["dependencies"]),
            "provenance_classes": ["forward_forcing"],
            "candidate_grammar": {
                "generator": (
                    "Compose, without an outcome axis, the admitted candidate generators of: "
                    + row["governing_grammar"]
                    + ". Generate theorem-specific witnesses, arbitrary-input proof steps, eliminations and certificates."
                ),
                "boundary": (
                    "Every SFT-admissible encoding of every source binder and every original hypothesis/conjunct. "
                    "Universal natural scope requires base-and-successor closure; existential scope requires the complete "
                    "registered witness grammar; a rejected carrier is not a mathematical negation."
                ),
                "completeness_certificate": None,
            },
            "excluded_inputs": [
                "malformed or non-total source-object encodings",
                "an imported OpenAI proof term, theorem result or conventional axiom used to select the SFT derivation",
                "a fitted, rounded or target-selected scalar used as proof authority",
                "carrier inadmissibility presented as the logical negation of the source proposition",
            ],
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": (
                "Exact source and native propositions, proved encode/decode and truth correspondence, complete root-to-result "
                "dependency trace, exhaustive theorem-specific proof or witness grammar, frozen-engine receipt, executable "
                "checks, implementation-distinct verification and Lean 4 proof with an explicit axiom audit."
            ),
            "empirical_protocol": None,
            "registered_by": "Maria Smith",
            "registration_date": "2026-08-02",
        }
        translation = {
            "schema": "sft-v3-external-theorem-native-translation/1",
            "claim_id": row["claim_id"],
            "atomic_id": row["atomic_id"],
            "source_declaration": row["declaration"],
            "registry_path": REGISTRY.relative_to(ROOT).as_posix(),
            "registry_identity": registry_payload["registry_identity"],
            "native_formula": row["native_formula"],
            "source_quantifier_and_conjunct_order": list(row["quantifiers"]),
            "governing_preexisting_claims": list(row["dependencies"]),
            "governing_grammar_composition": row["governing_grammar"],
            "outcome_axis_present": False,
            "proof_body_imported": False,
        }
        correspondence = {
            "schema": "sft-v3-external-theorem-correspondence-obligation/1",
            "claim_id": row["claim_id"],
            "atomic_id": row["atomic_id"],
            "status": "registered_pending_derivation",
            "scope": TRANSLATION_SEMANTICS["scope"],
            "required_theorem": (
                "For every admitted source encoding e, decode(encode(decode(e))) = decode(e), and the exact source "
                "proposition at decode(e) holds if and only if the registered native formula at e holds."
            ),
            "required_preservation": [
                "binder order and dependency",
                "forall/exists polarity",
                "implication direction",
                "strict versus non-strict comparison",
                "every conjunction field",
                "source negation as actual predicate negation",
            ],
            "forbidden_shortcuts": [
                "carrier rejection called contradiction",
                "a finite example called an unrestricted theorem",
                "the upstream proof used as SFT derivation authority",
                "a verdict-first candidate product",
            ],
        }
        write_json(package / "registration.json", registration)
        write_json(package / "source_statement.json", source_record)
        write_json(package / "translation.json", translation)
        write_json(package / "correspondence_obligation.json", correspondence)
        package.joinpath("STATUS.md").write_text(
            f"# {row['claim_id']}\n\n"
            "Status: `registered`\n\n"
            f"Owner: `{row['owner']}`  \n"
            f"Source declaration: `{row['declaration']}`  \n"
            "Outcome: not selected at registration.\n\n"
            "Admission requires the complete proposition, correspondence theorem, theorem-specific derivation, "
            "two executable implementations and Lean 4 validation. No compatibility or paper verdict follows from registration.\n",
            encoding="utf-8",
        )
        package.joinpath("WHY_DERIVATION_CHECK.md").write_text(
            f"# Why {row['claim_id']} requires a derivation check\n\n"
            f"The frozen target is `{row['declaration']}`. Its exact source text and quantifier order are in "
            "`source_statement.json`; its exact SFT-native proposition is in `translation.json`.\n\n"
            "The OpenAI proof body and its declared axioms have no SFT derivational authority. The result may enter "
            "the model only after the registered proposition is independently forced from the named admitted dependencies, "
            "with arbitrary-input or complete-witness closure as appropriate. Inadmissibility alone is not a negation.\n",
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "status": "REGISTERED",
                "registry": REGISTRY.relative_to(ROOT).as_posix(),
                "registry_identity": registry_payload["registry_identity"],
                "claims": [row["claim_id"] for row in ROWS],
                "counts": registry_payload["counts"],
                "engine_or_verification_authority_edited": False,
                "model_admissions_created": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
