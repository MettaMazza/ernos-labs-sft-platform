"""Force exact arithmetic from positive traces, parts and pair-cell refinement."""

from __future__ import annotations

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-EXACT-ARITHMETIC-001"
Atom = tuple[str, ...]
Trace = tuple[Atom, ...]


def trace(*labels: str) -> Trace:
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("an exact positive trace must contain distinct generated labels")
    return tuple((label,) for label in labels)


def disjoint_junction(left: Trace, right: Trace) -> Trace:
    if not left or not right or set(left).intersection(right):
        raise ValueError("junction requires nonempty disjoint traces")
    return left + right


def pair_cell_product(left: Trace, right: Trace) -> Trace:
    if not left or not right:
        raise ValueError("pair-cell product requires positive traces")
    return tuple(left_atom + right_atom for left_atom in left for right_atom in right)


def exact_pairing(left: Trace, right: Trace) -> tuple[tuple[Atom, Atom], ...] | None:
    if len(left) != len(right):
        return None
    return tuple(zip(left, right))


def oriented_remainder(left: Trace, right: Trace) -> tuple[str, Trace]:
    left_only = tuple(atom for atom in left if atom not in right)
    right_only = tuple(atom for atom in right if atom not in left)
    if left_only and right_only:
        return ("incomparable-held", left_only + right_only)
    if left_only:
        return ("left-held", left_only)
    if right_only:
        return ("right-held", right_only)
    return ("same-form", (("empty-One",),))


_a, _b, _c = trace("a"), trace("b"), trace("c")
_two = disjoint_junction(_a, _b)
_three = disjoint_junction(_two, _c)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact arithmetic and generated number structure",
    statement=(
        "Every admitted arithmetic relation on generated positive finite traces and exact parts has one "
        "parameter-free structural kernel: disjoint junction for addition, complete pair-cell refinement "
        "for product, finite repeated composition for powers, common-refinement pairing for exact quotient "
        "and comparison, and held orientation for unmatched remainder; no semantic zero, negative, irrational, "
        "floating or completed-infinite value enters the law."
    ),
    dependencies=(
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-PART-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    ),
    generation_rule=(
        "Generate the complete product of trace coverage, junction, pair-cell product, exact quotient, "
        "comparison, remainder orientation, finite generality and extra-rule status."
    ),
    grammar_boundary=(
        "All arithmetic kernels constructible from admitted positive finite traces, exact held/whole parts, "
        "common refinement, canonical form identity and no imported scalar field."
    ),
    dimensions=(
        binary_dimension("coverage", "Does the value retain the complete generated trace?", "partial-trace", "A partial trace omits an admitted generated occurrence.", "complete-trace", "The complete trace retains every generated occurrence once."),
        binary_dimension("junction", "How are positive traces combined?", "overlap-merge", "Overlap repeats a shared occurrence and loses disjoint provenance.", "disjoint-junction", "Disjoint junction preserves both complete positive traces."),
        binary_dimension("product", "How is repeated allocation constructed?", "repeated-unlabelled", "Unlabelled repetition erases the two source coordinates.", "pair-cell-refinement", "Each generated left label is paired once with each generated right label."),
        binary_dimension("quotient", "How is an exact division-like relation witnessed?", "rounded-measure", "A rounded or decimal value is measured rather than exact derivational evidence.", "common-refinement-pairing", "A complete common refinement and bijection witnesses the exact part relation."),
        binary_dimension("comparison", "How are magnitudes compared without an imported order?", "borrowed-scalar-order", "A borrowed scalar order imports the answer-producing number model.", "complete-trace-pairing", "Pairing identifies equality and a held unmatched trace identifies orientation."),
        binary_dimension("difference", "How is an unmatched remainder represented?", "signed-magnitude", "A signed magnitude installs forbidden negative quantity.", "held-oriented-remainder", "A distinct held label records which trace retains the unmatched positive remainder."),
        binary_dimension("generality", "What closes all generated finite depths?", "bounded-answer-table", "A finite answer table has no depth-independent arithmetic certificate.", "base-successor-induction", "The One base and generated successor preserve each operation at every finite depth."),
        binary_dimension("addition", "Is any rule added beyond the dependencies?", "has-extra-rule", "An extra scale, constant or field is not supplied by the dependencies.", "no-extra-rule", "The kernel uses only admitted traces, parts, refinement, pairing and held labels."),
    ),
    exact_result=(
        "The exact arithmetic kernel is complete positive-trace coverage with disjoint junction, pair-cell "
        "product, common-refinement quotient, complete pairing comparison, held-oriented remainder, "
        "base/successor generality and no extra rule."
    ),
    laws=(
        "disjoint junction is associative on mutually disjoint generated traces",
        "pair-cell product distributes over disjoint junction by generated cell provenance",
        "pair-cell product composition is associative after canonical path flattening",
        "exact quotient exists only with a complete refinement-pairing witness",
        "comparison returns same-form or a held positive remainder orientation",
    ),
    induction_base="The structural One supplies the first nonempty trace and exact self-whole.",
    induction_step=(
        "Appending one fresh generated occurrence preserves complete trace identity; junction appends it once, "
        "pair-cell refinement appends one labelled cell per opposite trace element, and pairing either extends "
        "with one mate or records the unmatched held remainder."
    ),
    boundary_exclusions=(
        "semantic numerical zero is not a value",
        "negative magnitude is replaced by held orientation",
        "irrational, imaginary and floating proof values are excluded",
        "completed infinity and an ungenerated continuum are excluded",
    ),
    witnesses=(
        Witness("junction-associativity", "(a joined b) joined c and a joined (b joined c) retain the same canonical trace.", disjoint_junction(disjoint_junction(_a, _b), _c) == disjoint_junction(_a, disjoint_junction(_b, _c))),
        Witness("pair-cell-cardinality", "Two generated cells paired with three generated cells produce the complete six labelled pair cells.", len(pair_cell_product(_two, _three)) == 6),
        Witness("product-associativity", "Canonical flattened pair paths are independent of binary grouping.", pair_cell_product(pair_cell_product(_a, _b), _c) == pair_cell_product(_a, pair_cell_product(_b, _c))),
        Witness("exact-pairing", "Equal complete traces admit one-to-one and onto pairing; unequal traces do not.", exact_pairing(_two, trace("x", "y")) is not None and exact_pairing(_two, _three) is None),
        Witness("held-remainder", "A larger trace reports a positive held remainder instead of a negative value.", oriented_remainder(_three, _two)[0] == "left-held"),
    ),
    why=(
        "Arithmetic is required before later branches can count arrangements, compare structures or assign exact "
        "support weights, but importing a conventional number field would violate the clean-room boundary."
    ),
    derivation=(
        "Count supplies complete positive traces; Part supplies held/whole coordinates; Part Equivalence supplies "
        "common refinement and bijection. Exhausting the eight representation choices leaves one kernel that "
        "preserves every source identity without introducing a scale or forbidden value."
    ),
    check=(
        "Execute all 256 assembled kernels, require one survivor, verify the operational associativity, product, "
        "pairing and remainder witnesses, run four adverse controls and recompute the result independently."
    ),
    limitations=(
        "This law closes exact generated finite arithmetic and positive rational part relations. It does not admit "
        "a completed infinite set, continuum, irrational field or negative proof magnitude. Conventional notation "
        "may describe the result only in correspondence."
    ),
    correspondence_terms=("positive integers", "rational numbers", "addition", "multiplication", "division", "order", "signed difference"),
)
