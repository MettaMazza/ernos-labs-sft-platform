"""Force compositional structure, types and functorial transport from Fold paths."""

from __future__ import annotations

from dataclasses import dataclass

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001"


@dataclass(frozen=True)
class Arrow:
    name: str
    source: str
    target: str
    trace: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name or not self.source or not self.target or not self.trace:
            raise ValueError("an arrow retains name, interface and a nonempty proof trace")


def identity(object_name: str) -> Arrow:
    return Arrow(f"id:{object_name}", object_name, object_name, (f"empty-One-return:{object_name}",))


def compose(first: Arrow, second: Arrow) -> Arrow:
    if first.target != second.source:
        raise ValueError("composition requires exact interface identity")
    return Arrow(
        f"{second.name}∘{first.name}",
        first.source,
        second.target,
        first.trace + second.trace,
    )


def canonical_path(arrow: Arrow) -> tuple[str, ...]:
    return tuple(item for item in arrow.trace if not item.startswith("empty-One-return"))


def type_members(carrier: tuple[str, ...], predicate: tuple[tuple[str, bool], ...]) -> tuple[str, ...]:
    verdicts = dict(predicate)
    if set(verdicts) != set(carrier):
        raise ValueError("a type predicate must decide every generated carrier form")
    return tuple(item for item in carrier if verdicts[item])


def product_forms(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return tuple((a, b) for a in left for b in right)


def sum_forms(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[tuple[str, str], ...]:
    return tuple(("left-held", item) for item in left) + tuple(("right-held", item) for item in right)


def functor_preserves(
    arrows: tuple[Arrow, ...],
    object_map: tuple[tuple[str, str], ...],
    arrow_map: tuple[tuple[str, Arrow], ...],
) -> bool:
    objects = dict(object_map)
    images = dict(arrow_map)
    for arrow in arrows:
        if arrow.name not in images or arrow.source not in objects or arrow.target not in objects:
            return False
        image = images[arrow.name]
        if image.source != objects[arrow.source] or image.target != objects[arrow.target]:
            return False
    return True


def naturality_commutes(left_path: tuple[Arrow, ...], right_path: tuple[Arrow, ...]) -> bool:
    def fold_path(path: tuple[Arrow, ...]) -> Arrow:
        held = path[0]
        for arrow in path[1:]:
            held = compose(held, arrow)
        return held
    left = fold_path(left_path)
    right = fold_path(right_path)
    return left.source == right.source and left.target == right.target and canonical_path(left) == canonical_path(right)


_f = Arrow("f", "A", "B", ("f",))
_g = Arrow("g", "B", "C", ("g",))
_h = Arrow("h", "C", "D", ("h",))


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Forced category, type and compositional structure",
    statement=(
        "Canonical Fold forms act as objects and proof-carrying transitions as arrows. Identity is the empty-One "
        "return, composition is forced exactly by equal interfaces, and association follows from canonical complete "
        "path flattening. Types are source-bound predicates over generated carriers; products are complete joint "
        "pair support and sums retain held alternative labels. Functors preserve interfaces, identity and composition, "
        "while naturality is equality of the two complete composite traces."
    ),
    dependencies=(
        "SFT-MATH-GRAPH-NETWORK-001",
        "SFT-MATH-ALGEBRA-001",
        "SFT-MATH-LOGIC-PROOF-001",
    ),
    generation_rule=(
        "Generate the complete product of objects, arrows, identity, composition, association, types, product/sum "
        "structure, functoriality, naturality and extra-composition status."
    ),
    grammar_boundary=(
        "All finite compositional structures generated from canonical objects, proof-carrying arrows, exact interface "
        "matching, empty-One returns, flattened paths, source-bound type predicates and held joint/alternative forms."
    ),
    dimensions=(
        binary_dimension("objects", "What fixes compositional objects?", "presentation-objects", "Presentation names can alias distinct structures.", "canonical-Fold-objects", "Every object is an exact canonical generated form."),
        binary_dimension("arrows", "What fixes a morphism?", "endpoint-only-arrow", "Endpoints alone erase the transformation proof.", "proof-carrying-transition", "An arrow retains source, target and complete transition trace."),
        binary_dimension("identity", "What fixes identity?", "assumed-neutral-map", "A named neutral map has no return witness.", "empty-One-return", "The zero-step structural return preserves the same object without numerical zero."),
        binary_dimension("composition", "When may arrows compose?", "presentation-concatenation", "Textual concatenation can join unequal interfaces.", "exact-interface-match", "The first target and second source must be the same canonical object."),
        binary_dimension("association", "What fixes associativity?", "borrowed-category-axiom", "Importing an axiom would reverse the derivation order.", "canonical-path-flattening", "Both groupings retain the same ordered elementary transition trace."),
        binary_dimension("types", "What fixes a type?", "informal-class-name", "A class name need not decide carrier membership.", "source-bound-form-predicate", "Every generated carrier form receives one exact membership verdict."),
        binary_dimension("constructors", "What fixes product and sum?", "borrowed-set-constructor", "A borrowed constructor imports its ambient universe.", "joint-pairs-and-held-alternatives", "Products are complete pair support; sums retain left/right held provenance."),
        binary_dimension("functor", "What fixes compositional transport?", "arbitrary-renaming", "Renaming can break interfaces and composites.", "identity-and-composition-preservation", "Object and arrow maps retain sources, targets, returns and composites."),
        binary_dimension("naturality", "What fixes a natural correspondence?", "diagram-by-appearance", "A drawn square cannot prove both routes equal.", "equal-complete-paths", "Both interface-compatible composite routes have the same canonical trace."),
        binary_dimension("addition", "Is another compositional axiom added?", "extra-composition-axiom", "An extra universal property is not supplied by the registered traces.", "no-extra-composition-axiom", "Only generated interfaces, paths and preservation witnesses are admitted."),
    ),
    exact_result=(
        "The compositional kernel is canonical Fold objects, proof-carrying arrows, empty-One identity, exact-interface "
        "composition, path-flattening association, source-bound types, joint products, held sums, preserving functors "
        "and equal-path naturality."
    ),
    laws=(
        "identity preserves source and target and contributes no nonidentity transition",
        "composition exists exactly at a canonical interface match",
        "associativity is equality of flattened complete transition traces",
        "products preserve both coordinates and sums preserve the held source alternative",
        "functoriality and naturality are finite replayable preservation witnesses",
    ),
    induction_base="One canonical object supplies its empty-One identity arrow and the first singleton type.",
    induction_step=(
        "Adding one object or arrow generates its identities, every exact interface-compatible composite, product and "
        "sum cells, type verdicts and preservation squares. Closure follows by appending its trace to prior flat paths."
    ),
    boundary_exclusions=(
        "no imported category axioms",
        "no ungenerated universe of all objects",
        "no impredicative type constructor",
        "no universal property without an exhaustive finite witness",
    ),
    witnesses=(
        Witness("interface-composition", "f then g composes from A to C with both traces retained.", compose(_f, _g) == Arrow("g∘f", "A", "C", ("f", "g"))),
        Witness("identity", "Empty-One return preserves the interface and adds no elementary transition.", compose(identity("A"), _f).source == "A" and compose(identity("A"), _f).target == "B" and canonical_path(compose(identity("A"), _f)) == ("f",)),
        Witness("association", "Both groupings of f, g and h flatten to the same complete path.", canonical_path(compose(compose(_f, _g), _h)) == canonical_path(compose(_f, compose(_g, _h)))),
        Witness("type-predicate", "The witness predicate retains exactly its admitted carrier forms.", type_members(("a", "b", "c"), (("a", True), ("b", False), ("c", True))) == ("a", "c")),
        Witness("product-sum", "Joint products and held sums retain both source coordinates.", len(product_forms(("a", "b"), ("x", "y"))) == 4 and sum_forms(("a",), ("b",)) == (("left-held", "a"), ("right-held", "b"))),
        Witness("functor-interface", "The identity transport preserves the witness arrow interface.", functor_preserves((_f,), (("A", "A"), ("B", "B")), (("f", _f),))),
        Witness("naturality-path", "Two independently assembled routes with the same elementary trace commute.", naturality_commutes((_f, _g), (Arrow("fg", "A", "C", ("f", "g")),))),
    ),
    why=(
        "Every later science must compose local derivations without losing interfaces or provenance. The forced path "
        "kernel supplies this language while keeping category and type concepts downstream of Fold structure."
    ),
    derivation=(
        "Graphs supply paths, algebra supplies operation association, and logic supplies proof-carrying transitions. "
        "Ten choices force exact interfaces, identities, flat composition, types and preservation structures."
    ),
    check=(
        "Execute all 1,024 kernels, verify interface composition, identity erasure, three-arrow association, exact "
        "type membership, products/sums, functor interfaces and naturality paths, then regenerate independently."
    ),
    limitations=(
        "This closes the finite compositional kernel. Any stronger universal construction must be separately generated "
        "and exhaustively witness its claimed mapping property inside an explicit grammar."
    ),
    correspondence_terms=("category", "object", "morphism", "identity", "composition", "type", "product", "sum", "functor", "natural transformation"),
)
