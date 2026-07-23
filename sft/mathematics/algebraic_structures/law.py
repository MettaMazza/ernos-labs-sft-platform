"""Force finite algebraic structure from generated carriers and operation traces."""

from __future__ import annotations

from dataclasses import dataclass

from sft.mathematics.generated_law import LawSpec, Witness, binary_dimension


CLAIM_ID = "SFT-MATH-ALGEBRA-001"


@dataclass(frozen=True)
class OperationTable:
    carrier: tuple[str, ...]
    rows: tuple[tuple[str, str, str], ...]

    def __post_init__(self) -> None:
        if not self.carrier or len(set(self.carrier)) != len(self.carrier):
            raise ValueError("an operation requires a nonempty canonical carrier")
        expected = tuple((left, right) for left in self.carrier for right in self.carrier)
        inputs = tuple((left, right) for left, right, _ in self.rows)
        if len(self.rows) != len(expected) or set(inputs) != set(expected):
            raise ValueError("the table must assign every generated input pair exactly once")
        if any(result not in self.carrier for _, _, result in self.rows):
            raise ValueError("operation closure forbids results outside the carrier")

    def apply(self, left: str, right: str) -> str:
        matches = tuple(result for a, b, result in self.rows if a == left and b == right)
        if len(matches) != 1:
            raise ValueError("operation input is outside the complete table")
        return matches[0]


def has_identity(table: OperationTable, identity: str) -> bool:
    return identity in table.carrier and all(
        table.apply(identity, item) == item and table.apply(item, identity) == item
        for item in table.carrier
    )


def is_associative(table: OperationTable) -> bool:
    return all(
        table.apply(table.apply(a, b), c) == table.apply(a, table.apply(b, c))
        for a in table.carrier for b in table.carrier for c in table.carrier
    )


def return_mates(table: OperationTable, identity: str) -> tuple[tuple[str, str], ...] | None:
    if not has_identity(table, identity):
        return None
    mates: list[tuple[str, str]] = []
    for item in table.carrier:
        matches = tuple(
            candidate for candidate in table.carrier
            if table.apply(item, candidate) == identity and table.apply(candidate, item) == identity
        )
        if len(matches) != 1:
            return None
        mates.append((item, matches[0]))
    return tuple(mates)


def is_commutative(table: OperationTable) -> bool:
    return all(table.apply(a, b) == table.apply(b, a) for a in table.carrier for b in table.carrier)


def preserves_operation(
    source: OperationTable,
    target: OperationTable,
    mapping: tuple[tuple[str, str], ...],
) -> bool:
    images = {origin: image for origin, image in mapping}
    return (
        len(images) == len(source.carrier)
        and all(origin in images and images[origin] in target.carrier for origin in source.carrier)
        and all(
            images[source.apply(a, b)] == target.apply(images[a], images[b])
            for a in source.carrier for b in source.carrier
        )
    )


_xor = OperationTable(
    ("One", "held"),
    (
        ("One", "One", "One"),
        ("One", "held", "held"),
        ("held", "One", "held"),
        ("held", "held", "One"),
    ),
)
_left_projection = OperationTable(
    ("a", "b"),
    (("a", "a", "a"), ("a", "b", "a"), ("b", "a", "b"), ("b", "b", "b")),
)


SPEC = LawSpec(
    claim_id=CLAIM_ID,
    title="Generated finite algebraic structures",
    statement=(
        "An admitted finite algebraic structure is a complete canonical carrier with a complete, single-valued, "
        "closed pair-cell operation relation. Identity, associative composition, reversible return mates, "
        "commutation, substructure and structure-preserving maps are admitted exactly when their exhaustive "
        "carrier witnesses pass; none is installed as an ungenerated axiom."
    ),
    dependencies=(
        "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-DISCRETE-001",
    ),
    generation_rule=(
        "Generate the complete product of carrier, operation coverage, closure, identity, association, return, "
        "property-admission, structure-map and extra-law status."
    ),
    grammar_boundary=(
        "All finite operation structures generated from canonical carriers, complete pair-cell relations, "
        "canonical path composition, held reversal and exhaustive property witnesses."
    ),
    dimensions=(
        binary_dimension("carrier", "What fixes the algebraic carrier?", "partial-or-aliased-carrier", "Omission or aliasing changes which operation inputs exist.", "complete-canonical-carrier", "Every generated carrier form occurs once with canonical identity."),
        binary_dimension("operation", "What fixes an operation?", "partial-operation-sample", "A partial sample does not assign every generated input pair.", "complete-single-valued-table", "Every ordered carrier pair has exactly one retained result."),
        binary_dimension("closure", "Where may an operation result lie?", "external-result", "An external result silently enlarges the registered carrier.", "carrier-closed-result", "Every result is a canonical member of the same carrier."),
        binary_dimension("identity", "How is identity established?", "named-identity", "A name alone does not prove left and right preservation.", "exhaustive-identity-witness", "One carrier form preserves every member on both sides."),
        binary_dimension("association", "How is association established?", "assumed-parenthesis-law", "An assumed equation imports an algebraic axiom.", "complete-triple-witness", "Every carrier triple has equal canonical flattened composites."),
        binary_dimension("return", "How are inverse-like returns represented?", "signed-inverse-value", "A signed magnitude imports negative quantity.", "unique-held-return-mate", "A retained complementary carrier mate returns on both sides to identity."),
        binary_dimension("properties", "When are special properties admitted?", "property-by-name", "A familiar structure name cannot supply commutation or return.", "property-by-exhaustive-witness", "Each property is registered only after every required carrier tuple passes."),
        binary_dimension("maps", "What makes a structure map lawful?", "arbitrary-carrier-map", "An arbitrary map can erase the operation relation.", "operation-preserving-map", "The complete image relation commutes with every source operation cell."),
        binary_dimension("addition", "Is another algebraic law added?", "extra-algebraic-axiom", "An extra axiom is not forced by the registered operation traces.", "no-extra-algebraic-axiom", "All admitted properties have explicit generated witnesses."),
    ),
    exact_result=(
        "The algebraic kernel is a complete canonical carrier and complete closed single-valued operation table, "
        "with identity, association, returns, special properties and maps admitted only by exhaustive witnesses."
    ),
    laws=(
        "closure is exact membership of every operation result in the registered carrier",
        "identity is a two-sided exhaustive preservation witness",
        "association is equality of both complete composite traces for every carrier triple",
        "return is a unique held mate relation and never a negative proof value",
        "homomorphism is complete operation preservation, not resemblance of presentations",
    ),
    induction_base="The One carrier has one pair cell, its result remains One, and identity and association coincide.",
    induction_step=(
        "Adding one fresh carrier form generates exactly its left, right and self pair cells. A proposed extension "
        "is admitted only after results remain in the extended carrier and every newly formed identity, triple, "
        "return and map obligation is checked."
    ),
    boundary_exclusions=(
        "no imported group, ring or field axioms",
        "no negative or irrational carrier requirement",
        "no property inferred from a conventional name",
        "no completed infinite carrier",
    ),
    witnesses=(
        Witness("closed-table", "Every complete input pair in the witness table has one carrier result.", len(_xor.rows) == 4),
        Witness("identity", "The structural One form preserves both witness carrier forms.", has_identity(_xor, "One")),
        Witness("association", "Both parenthesizations agree for every witness triple.", is_associative(_xor)),
        Witness("return-mates", "Every witness form has one held two-sided return mate.", return_mates(_xor, "One") == (("One", "One"), ("held", "held"))),
        Witness("commutation-is-conditional", "Commutation passes for the symmetric witness and fails for a lawful noncommuting table.", is_commutative(_xor) and not is_commutative(_left_projection)),
        Witness("structure-map", "The canonical self-map preserves every operation cell.", preserves_operation(_xor, _xor, (("One", "One"), ("held", "held")))),
    ),
    why=(
        "Algebra is forced when generated operations are composed and compared. The exhaustive table boundary "
        "prevents familiar algebraic classifications from supplying unproved laws."
    ),
    derivation=(
        "Discrete pair support supplies all operation inputs; exact canonical equality tests results; form "
        "enforcement supplies carrier identity. The nine-way census leaves the witness-governed operation kernel."
    ),
    check=(
        "Execute all 512 kernels, verify table totality and closure, exhaustive identity and association, unique "
        "return mates, a deliberately noncommuting control and operation-preserving maps, then regenerate independently."
    ),
    limitations=(
        "This closes the finite algebraic kernel and its property tests. Particular richer algebraic species require "
        "their own generated carriers and independently witnessed additional operations."
    ),
    correspondence_terms=("magma", "monoid", "group", "commutativity", "subalgebra", "homomorphism"),
)
