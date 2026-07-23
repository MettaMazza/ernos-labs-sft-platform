"""Force finite collections, relations, maps, sequences and induction."""

from __future__ import annotations

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-DISCRETE-001"
Form = tuple[str, ...]
Relation = tuple[tuple[Form, Form], ...]
EMPTY_ONE: Form = ("empty-One",)


def generated_collection(*forms: Form) -> tuple[Form, ...]:
    if not forms or len(set(forms)) != len(forms):
        raise ValueError("a generated collection requires distinct nonempty forms")
    return forms


def held_selection(collection: tuple[Form, ...], held: tuple[Form, ...]) -> tuple[Form, ...] | Form:
    if any(form not in collection for form in held) or len(set(held)) != len(held):
        raise ValueError("a selection must retain distinct members of its source collection")
    return held if held else EMPTY_ONE


def generated_relation(left: tuple[Form, ...], right: tuple[Form, ...], held_pairs: Relation) -> Relation:
    complete_pairs = tuple((a, b) for a in left for b in right)
    if any(pair not in complete_pairs for pair in held_pairs) or len(set(held_pairs)) != len(held_pairs):
        raise ValueError("a relation is a held selection of the complete pair-cell support")
    return held_pairs


def is_total_single_valued(source: tuple[Form, ...], relation: Relation) -> bool:
    return all(len(tuple(target for origin, target in relation if origin == item)) == 1 for item in source)


def successor_trace(collection: tuple[Form, ...], fresh: Form) -> tuple[Form, ...]:
    if fresh in collection:
        raise ValueError("successor must be freshly generated")
    return collection + (fresh,)


_a, _b, _c = ("a",), ("b",), ("c",)
_collection = generated_collection(_a, _b, _c)
_map = ((_a, _b), (_b, _c), (_c, _a))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Generated discrete objects, relations and induction",
    statement=(
        "Every admitted discrete object is a complete canonical generated finite collection or held selection; "
        "membership is retained occurrence, relations are held selections of complete pair-cell support, maps are "
        "total single-valued relations, sequences retain generated order, and general laws close by structural "
        "One/base-successor induction."
    ),
    dependencies=(
        "SFT-FOUNDATION-COUNT-001",
        "SFT-FOUNDATION-FORM-GRAMMAR-001",
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    generation_rule=(
        "Generate the complete product of collection coverage, canonical identity, membership, relation support, "
        "map law, sequence order, induction closure and extra-constructor status."
    ),
    grammar_boundary=(
        "All discrete structures generated from finite canonical One/Fold forms, exact positive traces, held "
        "selections, pair-cell relations and successor construction."
    ),
    dimensions=(
        binary_dimension("collection", "What identifies a finite collection?", "partial-or-duplicated", "Omission or duplication changes the generated collection trace.", "complete-unique-trace", "Every generated member occurs once in the canonical collection trace."),
        binary_dimension("identity", "How are members identified?", "presentation-alias", "Presentation names can merge distinct forms or split one form.", "canonical-form-identity", "Canonical construction traces supply exact member identity."),
        binary_dimension("membership", "What establishes membership?", "unrecorded-assertion", "An unrecorded assertion has no source-bound occurrence witness.", "retained-occurrence", "Membership retains the canonical member occurrence within the source trace."),
        binary_dimension("relation", "What generates a relation?", "free-pair-list", "A free pair list has no complete source-product boundary.", "held-pair-cell-selection", "A relation holds a generated selection from complete source pair-cell support."),
        binary_dimension("map", "What distinguishes a map?", "partial-or-multivalued", "A missing or repeated image does not define one image for every source member.", "total-single-valued", "Every source member has exactly one retained target mate."),
        binary_dimension("sequence", "How is order preserved?", "unordered-carrier", "An unordered carrier erases the generated predecessor relation.", "held-generation-order", "The canonical trace retains each predecessor-successor position."),
        binary_dimension("induction", "What closes laws at arbitrary generated finite size?", "sampled-depths", "Sampled depths do not establish the successor step.", "One-base-successor", "The One base and freshness-preserving successor cover every generated finite trace."),
        binary_dimension("addition", "Are ungenerated constructors admitted?", "extra-constructor", "An extra constructor is not supplied by the Foundation grammar.", "no-extra-constructor", "All objects decompose into admitted forms, selections, pair cells and successors."),
    ),
    exact_result=(
        "The discrete kernel is complete unique canonical collections with retained membership, pair-cell-selected "
        "relations, total single-valued maps, held sequence order, One/base-successor induction and no extra constructor."
    ),
    laws=(
        "canonical membership is decidable for every generated finite collection",
        "held selection never introduces an element outside its source collection",
        "relation complement is a held complementary selection of the same complete pair support",
        "map composition preserves total single-valuedness when interfaces agree",
        "structural induction covers every generated finite collection trace",
    ),
    induction_base="The structural One is the first canonical generated member and the empty One marks a held-empty selection without numerical zero.",
    induction_step=(
        "Given a complete unique canonical collection, append one fresh canonical form once; membership, relation "
        "pair support, map-image obligation and predecessor order extend by their local generated clauses."
    ),
    boundary_exclusions=(
        "no completed infinite set",
        "no ungenerated universal collection",
        "no semantic numerical zero for the empty selection",
        "no presentation alias may replace canonical form identity",
    ),
    witnesses=(
        Witness("unique-collection", "A generated collection retains each canonical member once.", _collection == (_a, _b, _c) and len(set(_collection)) == len(_collection)),
        Witness("held-membership", "A held selection contains only members of its registered source.", held_selection(_collection, (_a, _c)) == (_a, _c)),
        Witness("empty-One-selection", "A held-empty selection returns the empty One form, not numerical zero.", held_selection(_collection, ()) == EMPTY_ONE),
        Witness("relation-boundary", "Every retained relation pair belongs to the complete generated pair-cell support.", generated_relation(_collection, _collection, _map) == _map),
        Witness("total-map", "The example relation gives every source form exactly one image.", is_total_single_valued(_collection, _map)),
        Witness("fresh-successor", "A successor appends exactly one fresh canonical form.", successor_trace((_a, _b), _c) == _collection),
    ),
    why=(
        "Combinatorics, graphs, algebra, logic and computation require exact collections and relations, but an "
        "imported set-theoretic universe would add axioms and completed infinities outside the SFT domain."
    ),
    derivation=(
        "Canonical form enforcement supplies identity; count supplies complete finite traces; exact arithmetic "
        "supplies lawful trace composition. Product enumeration of the eight representational questions forces "
        "the collection-selection-relation-map-induction kernel."
    ),
    check=(
        "Execute all 256 kernels, test unique membership, source-contained selections, pair-cell relation support, "
        "total map images and freshness-preserving succession, then run adverse controls and independent regeneration."
    ),
    limitations=(
        "The theorem concerns generated finite objects. It does not install an ungenerated universe, completed "
        "infinite set or unrestricted comprehension principle."
    ),
    correspondence_terms=("finite set", "subset", "membership", "relation", "function", "sequence", "structural induction"),
)
