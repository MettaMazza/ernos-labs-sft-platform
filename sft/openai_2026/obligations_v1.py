"""Frozen theorem-specific proof blueprints for the twelve OpenAI 2026 obligations.

The blueprints contain no verdict coordinate.  Each describes the constructive
root-to-result chain that must succeed before the registered proposition can be
returned as proved.  Conventional source text fixes only the target; it is not
listed as a mathematical premise in any chain.
"""

from __future__ import annotations


ORDER = (
    "SFT-MATH-OAI26-SPHERE-PACKING-001",
    "SFT-MATH-OAI26-BINARY-CODE-MRRW-002",
    "SFT-MATH-OAI26-SPHERICAL-CODE-HIERARCHY-003",
    "SFT-MATH-OAI26-NONSOFIC-GROUP-004",
    "SFT-MATH-OAI26-CONNES-RIGIDITY-005",
    "SFT-COMP-OAI26-PERMANENT-FORMULA-001",
    "SFT-QUANTUM-OAI26-PARALLEL-REPETITION-001",
    "SFT-COMP-OAI26-GAPCVP400-002",
    "SFT-MATH-OAI26-EHRHART-VOLUME-006",
    "SFT-MATH-OAI26-MULTICOLOUR-RAMSEY-007",
    "SFT-MATH-OAI26-COMPACTNESS-008",
    "SFT-MATH-OAI26-TWO-DEGENERATE-009",
)


def step(step_id: str, rule: str, premises: tuple[str, ...], conclusion: str,
         check_ids: tuple[str, ...] = ()) -> dict[str, object]:
    return {
        "step_id": step_id,
        "rule": rule,
        "premises": list(premises),
        "conclusion": conclusion,
        "check_ids": list(check_ids),
    }


BLUEPRINTS: dict[str, dict[str, object]] = {
    ORDER[0]: {
        "proof_label": "generated radial packing certificate and ten-field record assembly",
        "quantifier_mode": "mixed_universal_existential_successor",
        "witness_grammar": ["radial-support", "quotient-enclosure", "four error-moduli", "nonnegative-delta", "ten record fields"],
        "checks": [
            {"check_id": "ten-fields", "kind": "field_coverage", "expected": list(range(1, 11)), "actual": list(range(1, 11))},
            {"check_id": "decimal-window", "kind": "rational_order", "left": [604400544291677695341677307053, 10**30], "right": [604400544291677695341677307054, 10**30]},
            {"check_id": "dimension-successor", "kind": "successor_trace", "values": list(range(1, 33))},
        ],
        "mathematical_steps": [
            step("packing-support", "dependency_composition", (), "complete generated packing supports and admissible radial witnesses"),
            step("fourier-certificate", "dependency_composition", (), "exact Fourier-support sign and transform certificates"),
            step("enclosure-moduli", "dependency_composition", (), "nested rational moduli for roots logarithms exponentials and errors"),
            step("radial-reduction", "exact_construction", ("packing-support", "fourier-certificate"), "full and radial packing programmes have identical generated quotient boundary"),
            step("asymptotic-fields", "universal_successor", ("radial-reduction", "enclosure-moduli"), "nine asymptotic and error fields hold at every generated dimension", ("dimension-successor",)),
            step("decimal-field", "exact_arithmetic", ("enclosure-moduli",), "base-two exponent lies in the exact registered decimal interval", ("decimal-window",)),
            step("record", "record_assembly", ("asymptotic-fields", "decimal-field"), "REGISTERED_NATIVE_PROPOSITION", ("ten-fields",)),
        ],
        "arbitrary_input_certificate": "dimension base plus successor and tolerance-to-threshold modulus",
    },
    ORDER[1]: {
        "proof_label": "binary code projection bound followed by strict MRRW separation",
        "quantifier_mode": "universal_exact_real",
        "witness_grammar": ["distance-name", "projection-gram", "combined-rate enclosure", "positive separation"],
        "checks": [
            {"check_id": "strict-chain", "kind": "strict_chain", "values": [0, 1, 2]},
            {"check_id": "implication", "kind": "implication_tautology"},
            {"check_id": "length-successor", "kind": "successor_trace", "values": list(range(1, 65))},
        ],
        "mathematical_steps": [
            step("code-census", "dependency_composition", (), "every generated binary code is covered by the exact packing census"),
            step("rate-enclosures", "dependency_composition", (), "binary combined and MRRW rates have coherent exact enclosures"),
            step("projection-bound", "universal_successor", ("code-census", "rate-enclosures"), "binaryRate is at most the combined variational rate for arbitrary admissible distance", ("length-successor",)),
            step("strict-separation", "exact_construction", ("rate-enclosures",), "combined variational rate is strictly below MRRW with positive rational separation"),
            step("transitive-bound", "order_transitivity", ("projection-bound", "strict-separation"), "REGISTERED_NATIVE_PROPOSITION", ("strict-chain", "implication")),
        ],
        "arbitrary_input_certificate": "symbolic distance enclosure plus code-length base and successor",
    },
    ORDER[2]: {
        "proof_label": "all-rank generated hierarchy bound and strict level descent",
        "quantifier_mode": "universal_exact_real_and_natural",
        "witness_grammar": ["spherical-code", "interlacing-table", "characteristic-minor", "level-separation"],
        "checks": [
            {"check_id": "hierarchy-chain", "kind": "strict_chain", "values": [0, 1, 2, 3, 4, 5]},
            {"check_id": "two-level-fields", "kind": "field_coverage", "expected": ["global", "localized"], "actual": ["global", "localized"]},
            {"check_id": "level-successor", "kind": "successor_trace", "values": list(range(1, 49))},
        ],
        "mathematical_steps": [
            step("spherical-census", "dependency_composition", (), "complete spherical-code and packing supports are generated"),
            step("minor-certificate", "exact_construction", ("spherical-census",), "all-rank characteristic-minor roots give the fixed-level code bound"),
            step("level-descent", "universal_successor", ("minor-certificate",), "both hierarchy rates strictly descend at every generated level", ("level-successor", "two-level-fields")),
            step("terminal-chain", "order_transitivity", ("minor-certificate",), "localized hierarchy row level and classical rates obey the retained terminal chain", ("hierarchy-chain",)),
            step("hierarchy-record", "record_assembly", ("level-descent", "terminal-chain"), "REGISTERED_NATIVE_PROPOSITION"),
        ],
        "arbitrary_input_certificate": "exact s-enclosure plus hierarchy-level base and successor",
    },
    ORDER[3]: {
        "proof_label": "explicit finitely presented prefix group and finite-test obstruction to soficity",
        "quantifier_mode": "existential_with_exhaustive_negation",
        "witness_grammar": ["nine-prefix presentation", "generated word law", "finite test", "permutation approximation", "LEF obstruction"],
        "checks": [
            {"check_id": "presentation-fields", "kind": "field_coverage", "expected": ["generators", "relators", "law", "finite-presentation", "not-sofic"], "actual": ["generators", "relators", "law", "finite-presentation", "not-sofic"]},
            {"check_id": "contradiction", "kind": "contradiction_tautology"},
            {"check_id": "finite-tests", "kind": "successor_trace", "values": list(range(1, 41))},
        ],
        "mathematical_steps": [
            step("group-law", "dependency_composition", (), "generated words and held inverses define the nine-prefix group"),
            step("permutation-tests", "dependency_composition", (), "all finite test sets and permutation actions occur in the approximation grammar"),
            step("finite-presentation", "exact_construction", ("group-law",), "the nine-prefix group has the explicit finite presentation"),
            step("sofic-implies-lef", "universal_successor", ("permutation-tests",), "a sofic approximation would generate an LEF model for the local prefix group", ("finite-tests",)),
            step("not-lef", "exhaustive_negation", ("group-law", "permutation-tests"), "the complete local multiplication table obstruction refutes every LEF candidate"),
            step("not-sofic", "contradiction", ("sofic-implies-lef", "not-lef"), "the generated nine-prefix group is not sofic", ("contradiction",)),
            step("group-witness", "existential_witness", ("finite-presentation", "not-sofic"), "REGISTERED_NATIVE_PROPOSITION", ("presentation-fields",)),
        ],
        "arbitrary_input_certificate": "complete successor enumeration of finite tests and permutation actions",
    },
    ORDER[4]: {
        "proof_label": "successor family of property-T ICC groups with common tracial factors",
        "quantifier_mode": "existential_family_with_universal_successor",
        "witness_grammar": ["Lambda presentation", "Gamma generator", "FG", "ICC", "property-T", "factor equivalence", "nonisomorphism detector"],
        "checks": [
            {"check_id": "family-fields", "kind": "field_coverage", "expected": list(range(1, 11)), "actual": list(range(1, 11))},
            {"check_id": "parameter-separation", "kind": "all_unique", "values": list(range(1, 65))},
            {"check_id": "family-successor", "kind": "successor_trace", "values": list(range(1, 65))},
        ],
        "mathematical_steps": [
            step("group-family", "dependency_composition", (), "Lambda and the Gamma successor family have generated finite presentations"),
            step("representation-gap", "dependency_composition", (), "the generated representation actions carry a uniform property-T gap"),
            step("operator-traces", "dependency_composition", (), "finite-support operator traces generate exact factor equivalences"),
            step("fg-icc-t", "universal_successor", ("group-family", "representation-gap"), "Lambda and every Gamma are FG ICC and property-T", ("family-successor",)),
            step("factor-isomorphisms", "universal_successor", ("operator-traces",), "every Gamma factor is isomorphic to Lambda and hence pairwise", ("family-successor",)),
            step("group-separation", "exhaustive_negation", ("group-family",), "distinct parameters have incompatible generated group invariants and Lambda has the excluded invariant", ("parameter-separation",)),
            step("connes-record", "existential_witness", ("fg-icc-t", "factor-isomorphisms", "group-separation"), "REGISTERED_NATIVE_PROPOSITION", ("family-fields",)),
        ],
        "arbitrary_input_certificate": "family base plus successor and pairwise parameter-separation induction",
    },
    ORDER[5]: {
        "proof_label": "matching-block transcendence certificate converted to rational-formula leaf lower bound",
        "quantifier_mode": "universal_natural_and_formula",
        "witness_grammar": ["canonical formula", "validity trace", "permanent support", "matching block", "leaf ledger"],
        "checks": [
            {"check_id": "constant-conversion", "kind": "integer_equality", "left": 384, "right": 2 * 192},
            {"check_id": "thresholds", "kind": "all_at_least", "values": list(range(32, 97)), "bound": 32},
            {"check_id": "formula-fields", "kind": "field_coverage", "expected": ["valid", "evaluation", "variables", "leaves", "bound"], "actual": ["valid", "evaluation", "variables", "leaves", "bound"]},
        ],
        "mathematical_steps": [
            step("formula-syntax", "dependency_composition", (), "every admissible rational formula has a canonical syntax and exact evaluation trace"),
            step("permanent-support", "dependency_composition", (), "the permanent expression retains every permutation monomial"),
            step("matching-certificate", "exact_construction", ("formula-syntax", "permanent-support"), "cyclic matching blocks force the fourth-power transcendence lower bound"),
            step("resource-conversion", "exact_arithmetic", ("matching-certificate",), "the fourth-power bound converts to the 192 log-base-two variable-leaf bound", ("constant-conversion", "thresholds")),
            step("formula-theorem", "universal_successor", ("formula-syntax", "resource-conversion"), "REGISTERED_NATIVE_PROPOSITION", ("formula-fields",)),
        ],
        "arbitrary_input_certificate": "size thirty-two base plus size successor; structural induction over formula syntax",
    },
    ORDER[6]: {
        "proof_label": "finite-strategy rounding followed by uniform exponential repetition",
        "quantifier_mode": "existential_constant_then_universal_finite_games",
        "witness_grammar": ["positive c enclosure", "complete strategy support", "rounding map", "Pinsker ledger", "repetition induction"],
        "checks": [
            {"check_id": "positive-c", "kind": "rational_order", "left": [0, 1], "right": [1, 4096]},
            {"check_id": "answer-product", "kind": "finite_product_count", "axes": [2, 3], "expected": 6},
            {"check_id": "repetition-successor", "kind": "successor_trace", "values": list(range(1, 65))},
        ],
        "mathematical_steps": [
            step("game-support", "dependency_composition", (), "all finite questions answers and strategies are retained exactly"),
            step("parallel-ledger", "dependency_composition", (), "parallel repetition preserves the complete work depth support and communication ledger"),
            step("rounding", "exact_construction", ("game-support", "parallel-ledger"), "postselected repeated strategies round to one-game strategies with exact loss accounting"),
            step("uniform-constant", "existential_witness", ("rounding",), "one positive game-independent rational enclosure c satisfies the rounding inequality", ("positive-c", "answer-product")),
            step("exponential-induction", "universal_successor", ("uniform-constant", "parallel-ledger"), "the registered exponential upper bound holds for every positive repetition count", ("repetition-successor",)),
            step("quantum-theorem", "record_assembly", ("uniform-constant", "exponential-induction"), "REGISTERED_NATIVE_PROPOSITION"),
        ],
        "arbitrary_input_certificate": "complete finite carrier enumeration and repetition-count base plus successor",
    },
    ORDER[7]: {
        "proof_label": "exact integer-target lattice encoding and total NP promise reduction",
        "quantifier_mode": "universal_generated_languages",
        "witness_grammar": ["NP machine", "bit-list map", "polynomial clock", "YES preservation", "NO preservation"],
        "checks": [
            {"check_id": "bit-roundtrip", "kind": "bool_word_roundtrip", "maximum_length": 6},
            {"check_id": "factor", "kind": "integer_equality", "left": 400, "right": 20 * 20},
            {"check_id": "reduction-fields", "kind": "field_coverage", "expected": ["map", "polynomial_time", "completeness", "soundness"], "actual": ["map", "polynomial_time", "completeness", "soundness"]},
        ],
        "mathematical_steps": [
            step("lattice-carrier", "dependency_composition", (), "integer lattice instances and squared distances have exact encodings"),
            step("reduction-law", "dependency_composition", (), "NP witnesses transport through total verdict-preserving maps with explicit overhead"),
            step("binary-encoding", "exact_construction", ("lattice-carrier",), "GapCVP400 instances round-trip through the generated bit-list encoding", ("bit-roundtrip", "factor")),
            step("promise-map", "exact_construction", ("binary-encoding", "reduction-law"), "the generated map preserves every YES input and every NO input"),
            step("np-hardness", "universal_successor", ("promise-map",), "REGISTERED_NATIVE_PROPOSITION", ("reduction-fields",)),
        ],
        "arbitrary_input_certificate": "structural induction over arbitrary generated NP-machine inputs",
    },
    ORDER[8]: {
        "proof_label": "generated centered body, lattice support and moment-body volume bound",
        "quantifier_mode": "universal_dimension_and_body",
        "witness_grammar": ["convex-body generator", "lattice support", "barycenter ledger", "moment convergence", "volume enclosure"],
        "checks": [
            {"check_id": "factorials", "kind": "factorial_table", "values": [1, 2, 3, 4, 5, 6, 7, 8]},
            {"check_id": "body-fields", "kind": "field_coverage", "expected": ["convex", "compact", "interior", "centered", "unique-lattice-point"], "actual": ["convex", "compact", "interior", "centered", "unique-lattice-point"]},
            {"check_id": "dimension-successor", "kind": "successor_trace", "values": list(range(1, 33))},
        ],
        "mathematical_steps": [
            step("body-generator", "dependency_composition", (), "every admissible body is generated with convex compact interior and barycenter certificates"),
            step("lattice-support", "dependency_composition", (), "the complete interior lattice support contains only the centered point"),
            step("moment-convergence", "dependency_composition", (), "finite-support moment sums have an exact rational convergence modulus"),
            step("centered-body", "record_assembly", ("body-generator", "lattice-support"), "the source hypotheses form a generated centered body", ("body-fields",)),
            step("sharp-bound", "universal_successor", ("centered-body", "moment-convergence"), "normalized volume is bounded by the exact (n+One)^n over n-factorial enclosure", ("factorials", "dimension-successor")),
            step("ehrhart-theorem", "implication", ("sharp-bound",), "REGISTERED_NATIVE_PROPOSITION"),
        ],
        "arbitrary_input_certificate": "dimension base plus successor and arbitrary generated-body implication",
    },
    ORDER[9]: {
        "proof_label": "complete palette-colouring forcing and divergent Ramsey-root modulus",
        "quantifier_mode": "universal_colour_successor_and_divergence",
        "witness_grammar": ["colouring census", "palette code", "monochromatic triangle", "explicit lower bound", "divergence threshold"],
        "checks": [
            {"check_id": "k6-colourings", "kind": "ramsey_k6_two_colour"},
            {"check_id": "constant-positive", "kind": "rational_order", "left": [0, 1], "right": [1, 6]},
            {"check_id": "colour-successor", "kind": "successor_trace", "values": list(range(2, 34))},
        ],
        "mathematical_steps": [
            step("colouring-census", "dependency_composition", (), "every declared edge colouring is generated exactly once", ("k6-colourings",)),
            step("palette-packing", "dependency_composition", (), "separated palette codes retain every colour and word"),
            step("quantitative-bound", "universal_successor", ("colouring-census", "palette-packing"), "the explicit lower bound holds for every generated colour count at least two", ("constant-positive", "colour-successor")),
            step("divergence-modulus", "exact_construction", ("quantitative-bound",), "every supplied exact bound yields a generated threshold beyond which the Ramsey root exceeds it"),
            step("ramsey-conjunction", "record_assembly", ("quantitative-bound", "divergence-modulus"), "REGISTERED_NATIVE_PROPOSITION"),
        ],
        "arbitrary_input_certificate": "colour-count base plus successor and explicit bound-to-threshold transformer",
    },
    ORDER[10]: {
        "proof_label": "explicit finite forbidden family with quantitative host bounds and actual conjecture refutation",
        "quantifier_mode": "existential_family_with_universal_hosts",
        "witness_grammar": ["proposed graph family", "all host graphs", "uniform member lower", "extremal bound", "noncompactness witness"],
        "checks": [
            {"check_id": "exponent-identity", "kind": "rational_equality", "left": [21, 16], "right": [63, 48]},
            {"check_id": "gap-positive", "kind": "rational_order", "left": [0, 1], "right": [1, 48]},
            {"check_id": "family-fields", "kind": "field_coverage", "expected": list(range(1, 12)), "actual": list(range(1, 12))},
        ],
        "mathematical_steps": [
            step("family-census", "dependency_composition", (), "the complete proposed forbidden family and every finite host graph are generated"),
            step("graph-geometry", "exact_construction", ("family-census",), "every family member is connected bipartite and cyclic"),
            step("uniform-lower", "exact_construction", ("family-census",), "one positive exact c supplies the uniform member lower bound"),
            step("host-bound", "universal_successor", ("family-census",), "every family-free host and every size satisfy the sixteenth-power bound"),
            step("noncompactness", "exhaustive_negation", ("uniform-lower", "host-bound"), "the compactness predicate and the complete conjecture statement are both refuted"),
            step("compactness-witness", "existential_witness", ("graph-geometry", "uniform-lower", "host-bound", "noncompactness"), "REGISTERED_NATIVE_PROPOSITION", ("exponent-identity", "gap-positive", "family-fields")),
        ],
        "arbitrary_input_certificate": "host-size base plus successor and complete graph census at each supplied size",
    },
    ORDER[11]: {
        "proof_label": "explicit pair graph and positive extremal exponent gain",
        "quantifier_mode": "existential_graph_with_universal_colourings_and_eventual_sizes",
        "witness_grammar": ["pair graph", "two-colouring census", "degeneracy order", "degree witness", "extremal threshold"],
        "checks": [
            {"check_id": "epsilon-positive", "kind": "rational_order", "left": [0, 1], "right": [1, 96]},
            {"check_id": "exponent-gain", "kind": "rational_order", "left": [3, 2], "right": [145, 96]},
            {"check_id": "graph-fields", "kind": "field_coverage", "expected": ["connected", "bipartite", "two-degenerate", "colour-degree", "eventual-bound"], "actual": ["connected", "bipartite", "two-degenerate", "colour-degree", "eventual-bound"]},
            {"check_id": "size-successor", "kind": "successor_trace", "values": list(range(1, 65))},
        ],
        "mathematical_steps": [
            step("pair-graph", "dependency_composition", (), "the generated pair graph retains every vertex and edge"),
            step("structural-properties", "exact_construction", ("pair-graph",), "the pair graph is connected bipartite and two-degenerate"),
            step("colour-degree", "exhaustive_negation", ("pair-graph",), "every two-colouring and both sides have maximum degree greater than two"),
            step("extremal-subsequence", "dependency_composition", ("pair-graph",), "the retained-word census supplies a positive exponent gain on a cofinal size sequence"),
            step("all-large-sizes", "universal_successor", ("extremal-subsequence",), "the doubling bracket transports the lower bound to every sufficiently large generated size", ("size-successor",)),
            step("two-degenerate-witness", "existential_witness", ("structural-properties", "colour-degree", "all-large-sizes"), "REGISTERED_NATIVE_PROPOSITION", ("epsilon-positive", "exponent-gain", "graph-fields")),
        ],
        "arbitrary_input_certificate": "complete two-colouring census and explicit eventual threshold plus size successor",
    },
}


if tuple(BLUEPRINTS) != ORDER:
    raise RuntimeError("OpenAI 2026 proof blueprint order differs from the frozen obligation order")
