"""Force finite orders and conditional lattice operations from exact relations."""

from __future__ import annotations

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-ORDER-LATTICE-001"
Relation = tuple[tuple[str, str], ...]


def is_partial_order(carrier: tuple[str, ...], relation: Relation) -> bool:
    if not carrier or len(set(carrier)) != len(carrier) or len(set(relation)) != len(relation):
        return False
    if any(a not in carrier or b not in carrier for a, b in relation):
        return False
    reflexive = all((item, item) in relation for item in carrier)
    antisymmetric = all(a == b or (b, a) not in relation for a, b in relation)
    transitive = all((a, c) in relation for a, b in relation for x, c in relation if b == x)
    return reflexive and antisymmetric and transitive


def comparable(relation: Relation, left: str, right: str) -> bool:
    return (left, right) in relation or (right, left) in relation


def is_total(carrier: tuple[str, ...], relation: Relation) -> bool:
    return is_partial_order(carrier, relation) and all(
        comparable(relation, left, right) for left in carrier for right in carrier
    )


def lower_bounds(carrier: tuple[str, ...], relation: Relation, held: tuple[str, ...]) -> tuple[str, ...]:
    if not held or any(item not in carrier for item in held):
        raise ValueError("bounds require a nonempty held carrier selection")
    return tuple(candidate for candidate in carrier if all((candidate, item) in relation for item in held))


def upper_bounds(carrier: tuple[str, ...], relation: Relation, held: tuple[str, ...]) -> tuple[str, ...]:
    if not held or any(item not in carrier for item in held):
        raise ValueError("bounds require a nonempty held carrier selection")
    return tuple(candidate for candidate in carrier if all((item, candidate) in relation for item in held))


def unique_greatest(bounds: tuple[str, ...], relation: Relation) -> str | None:
    matches = tuple(candidate for candidate in bounds if all((other, candidate) in relation for other in bounds))
    return matches[0] if len(matches) == 1 else None


def unique_least(bounds: tuple[str, ...], relation: Relation) -> str | None:
    matches = tuple(candidate for candidate in bounds if all((candidate, other) in relation for other in bounds))
    return matches[0] if len(matches) == 1 else None


def meet(carrier: tuple[str, ...], relation: Relation, held: tuple[str, ...]) -> str | None:
    return unique_greatest(lower_bounds(carrier, relation, held), relation)


def join(carrier: tuple[str, ...], relation: Relation, held: tuple[str, ...]) -> str | None:
    return unique_least(upper_bounds(carrier, relation, held), relation)


def is_monotone(source: Relation, target: Relation, mapping: tuple[tuple[str, str], ...]) -> bool:
    images = dict(mapping)
    return all(a in images and b in images and (images[a], images[b]) in target for a, b in source)


_diamond_carrier = ("One", "left", "right", "whole")
_diamond_relation = (
    ("One", "One"), ("left", "left"), ("right", "right"), ("whole", "whole"),
    ("One", "left"), ("One", "right"), ("One", "whole"),
    ("left", "whole"), ("right", "whole"),
)
_chain_relation = (
    ("a", "a"), ("b", "b"), ("c", "c"),
    ("a", "b"), ("b", "c"), ("a", "c"),
)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Exact finite order and conditional lattice structure",
    statement=(
        "An admitted finite order is a held carrier relation whose reflexive, antisymmetric and transitive cells "
        "are exhaustively witnessed. Totality is admitted only when every generated pair is comparable. Lower and "
        "upper bounds are complete relation selections; meet and join exist only as unique greatest-lower and "
        "least-upper witnesses, and monotone maps preserve every retained comparison."
    ),
    dependencies=(
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DISCRETE-001",
        "SFT-MATH-ALGEBRA-001",
    ),
    generation_rule=(
        "Generate the complete product of carrier identity, relation provenance, partial-order laws, comparability, "
        "bound generation, meet uniqueness, join uniqueness, monotonicity and extra-order status."
    ),
    grammar_boundary=(
        "All finite order structures generated from canonical carriers, held pair-cell relations, exhaustive "
        "relation closure, complete bound selections and unique extremal witnesses."
    ),
    dimensions=(
        binary_dimension("carrier", "What fixes ordered objects?", "presentation-carrier", "Presentation aliases do not fix exact ordered identity.", "canonical-carrier", "Every ordered form has canonical generated identity."),
        binary_dimension("relation", "What fixes comparison?", "borrowed-scalar-comparison", "A scalar comparison imports an answer-producing order.", "held-pair-relation", "Each comparison is a retained generated carrier pair."),
        binary_dimension("order", "What makes the relation an order?", "named-order", "A name does not establish reflexivity, antisymmetry and transitivity.", "exhaustive-partial-order-witness", "Every required relation cell and composite is checked."),
        binary_dimension("comparability", "When is the order total?", "assumed-totality", "Partial orders can contain incomparable forms.", "pairwise-totality-witness", "Totality is recorded only when every generated pair is comparable."),
        binary_dimension("bounds", "How are bounds found?", "selected-bound", "Selecting a familiar candidate can omit another held condition.", "complete-bound-selection", "Every carrier form is tested against every held target."),
        binary_dimension("meet", "When does a meet exist?", "assumed-meet", "A lower bound need not be greatest or unique.", "unique-greatest-lower-witness", "Exactly one lower bound is above every other lower bound."),
        binary_dimension("join", "When does a join exist?", "assumed-join", "An upper bound need not be least or unique.", "unique-least-upper-witness", "Exactly one upper bound is below every other upper bound."),
        binary_dimension("maps", "What makes an order map lawful?", "arbitrary-map", "An arbitrary map can reverse a retained comparison.", "comparison-preserving-map", "Every source relation cell maps to a target relation cell."),
        binary_dimension("addition", "Is another order axiom added?", "extra-order-axiom", "An extra totality or completeness axiom is not structurally forced.", "no-extra-order-axiom", "Only exhaustively witnessed order properties are admitted."),
    ),
    exact_result=(
        "The order/lattice kernel is a canonical carrier with an exhaustively witnessed partial-order relation, "
        "conditional totality, complete bound selections, uniquely witnessed meet/join and monotone maps."
    ),
    laws=(
        "partial order requires reflexive, antisymmetric and transitive relation closure",
        "incomparability is retained and never forced into a borrowed total scale",
        "meet and join are partial operations unless unique extremal witnesses exist",
        "a finite lattice is exactly an admitted partial order with meet and join for every generated pair",
        "monotonicity is preservation of every registered relation cell",
    ),
    induction_base="The One carrier has its identity relation and One is both unique lower and upper bound of itself.",
    induction_step=(
        "Adding one fresh canonical form generates all comparisons to prior forms. Order closure, comparability, "
        "bounds and extremal uniqueness are rechecked only for pairs and composites touching the fresh form."
    ),
    boundary_exclusions=(
        "no imported real-number line",
        "no assumed total order",
        "no lattice completeness without generated meets and joins",
        "no completed infinite chain",
    ),
    witnesses=(
        Witness("partial-order", "The diamond relation passes all three partial-order obligations.", is_partial_order(_diamond_carrier, _diamond_relation)),
        Witness("incomparability-retained", "The diamond retains left and right as incomparable.", not comparable(_diamond_relation, "left", "right")),
        Witness("conditional-totality", "The explicit chain is total while the diamond is not.", is_total(("a", "b", "c"), _chain_relation) and not is_total(_diamond_carrier, _diamond_relation)),
        Witness("meet", "The two incomparable diamond arms have structural One as their unique meet.", meet(_diamond_carrier, _diamond_relation, ("left", "right")) == "One"),
        Witness("join", "The two incomparable diamond arms have whole as their unique join.", join(_diamond_carrier, _diamond_relation, ("left", "right")) == "whole"),
        Witness("monotone-identity", "The canonical identity map preserves every diamond comparison.", is_monotone(_diamond_relation, _diamond_relation, tuple((item, item) for item in _diamond_carrier))),
    ),
    why=(
        "Order is needed for comparison, optimization, proof strength and topology. Retaining incomparability "
        "prevents a conventional scalar line from being imported where the Fold structure does not force one."
    ),
    derivation=(
        "Discrete relations supply the comparison cells; algebra supplies lawful composition; exact identity "
        "supplies antisymmetry. Exhausting nine choices forces witnessed partial order and conditional lattice operations."
    ),
    check=(
        "Execute all 512 kernels, verify the diamond and chain, retain an incomparability control, compute complete "
        "bounds and unique meet/join, test monotonicity and independently regenerate the census."
    ),
    limitations=(
        "This theorem closes finite generated orders. It does not assert totality, lattice status or completeness "
        "for a carrier unless the corresponding finite witness is present."
    ),
    correspondence_terms=("partial order", "total order", "poset", "meet", "join", "lattice", "monotone map"),
)
