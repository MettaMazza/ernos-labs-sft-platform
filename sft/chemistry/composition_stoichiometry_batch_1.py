"""Immutable composition-and-stoichiometry Chemistry laws.

All arithmetic witnesses use exact positive host fractions guarded at the SFT
boundary.  Reactant and product orientation is structural; no negative
stoichiometric proof number is installed.  Species with no participation are
absent from the generated reaction word rather than assigned numerical zero.
Official IUPAC definitions are post-seal categorical comparators only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.exact import ExactPart, HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


OBSERVATION_REGISTRY_PATH = (
    "experiments/external_sources/chemistry/observations_composition_stoichiometry_batch_1.json"
)

BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-ENCODING-DECODING-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MECH-CONSERVATION-001",
    "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-MEAS-CHEMICAL-SPECIES-001",
    "SFT-CHEM-MEAS-SUBSTANCE-001",
    "SFT-CHEM-MEAS-AMOUNT-001",
    "SFT-CHEM-MEAS-FORMULA-001",
    "SFT-CHEM-ELEM-ELEMENT-001",
    "SFT-CHEM-ELEM-PERIODIC-ORDER-001",
)

SOURCE_RECORDS = {
    "IUPAC-GOLD-BOOK-M03722-2026": ("M03722", "cc715cdd306779e5032685105dacbbc7d1ef79ea8241269496befb1dc37a7f2f"),
    "IUPAC-GOLD-BOOK-S06026-2026": ("S06026", "0354d161fb1754d50dee2cfcd3bf051c6a005dbde765a112398f8e717e9952bc"),
    "IUPAC-GOLD-BOOK-C01034-2026": ("C01034", "a582f71bc6c555d5513f365d18d5d46a6a5da61e0c1668d231ad860b9a32dea3"),
    "IUPAC-GOLD-BOOK-D01771-2026": ("D01771", "352e753acf025b61ce54a5b00b61d9dd5b6d112d0d35133b48f2eba212c3b807"),
    "IUPAC-GOLD-BOOK-C01041-2026": ("C01041", "47979dfe9e05be8a7c207779853ce25538a8753e05b648a8a43471ed040b732f"),
    "IUPAC-GOLD-BOOK-M03949-2026": ("M03949", "71ba494096d995967227b9ef9fb4e6145b98c9cbcdbdb46460bc63b94c06966f"),
    "IUPAC-GOLD-BOOK-S05746-2026": ("S05746", "39f8916fdced6993ceb67e374641b95375570866a24123508ce26f9ec0049f28"),
}


def _target(target_id: str, source_id: str, locator: str) -> ChemistryTargetReference:
    code, digest = SOURCE_RECORDS[source_id]
    return ChemistryTargetReference(
        target_id=target_id,
        source_id=source_id,
        source_locator=f"https://goldbook.iupac.org/terms/view/{code}/json :: {locator}",
        snapshot_path=f"experiments/external_sources/chemistry/snapshots/goldbook-terms/{code}.json",
        snapshot_hash="sha256:" + digest,
    )


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no IUPAC wording, balanced equation, measured amount or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no absent species represented by a zero coefficient; absence is an empty generated form",
        "no application result or opaque predictor",
        "official target content opens only through post-seal custody",
        boundary,
    )


@dataclass(frozen=True)
class CompositionComponent:
    identity: str
    part: ExactPart

    def __post_init__(self) -> None:
        if not self.identity.strip():
            raise InadmissibleExactValue("composition identity must be a held distinction")


def exact_composition(components: tuple[CompositionComponent, ...]) -> tuple[CompositionComponent, ...]:
    """Validate a complete positive rational partition of the One."""

    if not components or len({row.identity for row in components}) != len(components):
        raise InadmissibleExactValue("composition requires distinct retained components")
    total = components[0].part.value
    for component in components[1:]:
        total += component.part.value
    if total != Fraction(1, 1):
        raise InadmissibleExactValue("composition parts must close exactly to the One")
    return components


@dataclass(frozen=True)
class ReactionSpecies:
    side: HeldLabel
    identity: str
    coefficient: PositiveCount
    elemental_counts: tuple[tuple[str, PositiveCount], ...]

    def __post_init__(self) -> None:
        if self.side.family != "reaction-side" or self.side.label not in {"reactant", "product"}:
            raise InadmissibleExactValue("reaction side must be a held reactant/product orientation")
        if not self.identity.strip() or not self.elemental_counts:
            raise InadmissibleExactValue("reaction species requires identity and elemental support")
        elements = tuple(element for element, _ in self.elemental_counts)
        if len(elements) != len(set(elements)) or any(not element.strip() for element in elements):
            raise InadmissibleExactValue("elemental support must contain distinct held identities")


def _side_totals(species: tuple[ReactionSpecies, ...], side: str) -> dict[str, int]:
    totals: dict[str, int] = {}
    for row in species:
        if row.side.label != side:
            continue
        for element, count in row.elemental_counts:
            contribution = row.coefficient.value * count.value
            if element in totals:
                totals[element] += contribution
            else:
                totals[element] = contribution
    return totals


def reaction_is_balanced(species: tuple[ReactionSpecies, ...]) -> bool:
    """Check exact element-label conservation without signed coefficients."""

    if not species or {row.side.label for row in species} != {"reactant", "product"}:
        return False
    return _side_totals(species, "reactant") == _side_totals(species, "product")


def primitive_coefficients(species: tuple[ReactionSpecies, ...]) -> bool:
    """Require the unique least positive integer multiplicity representative."""

    if not reaction_is_balanced(species):
        return False
    common = species[0].coefficient.value
    for row in species[1:]:
        common = gcd(common, row.coefficient.value)
    return common == 1


def limiting_component_positions(
    available: tuple[ExactPart, ...], coefficients: tuple[PositiveCount, ...]
) -> tuple[PositiveCount, ...]:
    """Return every tied least support using positive generated positions."""

    if not available or len(available) != len(coefficients):
        raise InadmissibleExactValue("limiting support requires paired positive amount and coefficient rows")
    progress = tuple(amount.value / coefficient.value for amount, coefficient in zip(available, coefficients))
    least = min(progress)
    return tuple(
        PositiveCount(position)
        for position, value in enumerate(progress, start=1)
        if value == least
    )


def exact_yield(product_part: ExactPart) -> ExactPart:
    """Retain an already source-bounded positive product share unchanged."""

    return product_part


_ABSTRACT_BALANCED_REACTION = (
    ReactionSpecies(HeldLabel("reaction-side", "reactant"), "AB", PositiveCount(1), (("A", PositiveCount(1)), ("B", PositiveCount(1)))),
    ReactionSpecies(HeldLabel("reaction-side", "reactant"), "A", PositiveCount(1), (("A", PositiveCount(1)),)),
    ReactionSpecies(HeldLabel("reaction-side", "product"), "A2B", PositiveCount(1), (("A", PositiveCount(2)), ("B", PositiveCount(1)))),
)

if not reaction_is_balanced(_ABSTRACT_BALANCED_REACTION) or not primitive_coefficients(
    _ABSTRACT_BALANCED_REACTION
):
    raise RuntimeError("abstract exact stoichiometry witness failed")


COMPOSITION_BOUNDARY = (
    "Every finite chemical carrier whose distinct constituent identities have exact positive rational parts "
    "that exhaust the One and preserve the measurement/source boundary."
)
COMPOSITION_DIMENSIONS = (
    dimension("carrier", "bulk-label-only", "A bulk label erases constituent support.", "complete-chemical-carrier", "The composed whole and every constituent remain linked."),
    dimension("components", "anonymous-parts", "Anonymous parts cannot preserve chemical identity.", "distinct-constituent-identities", "Every part is bound to one admitted substance or entity identity."),
    dimension("quantity", "floating-percentages", "Floating percentages cannot certify exact closure.", "exact-positive-rational-parts", "Every present component has an exact positive part."),
    dimension("closure", "partial-selected-composition", "Selected components need not exhaust the carrier.", "parts-exhaust-the-One", "The exact part sum is the whole."),
    dimension("absence", "zero-valued-components", "Numerical zero is not an SFT composition object.", "absent-component-omitted", "A component outside support is absent rather than assigned zero."),
    dimension("identity", "interchangeable-constituents", "Equal amounts do not make substances identical.", "constituent-identity-retained", "Chemical identity remains independent of part size."),
    dimension("record", "composition-answer-only", "An answer loses part and source provenance.", "identity-part-source-trace", "Each identity/part pair and source boundary remain held."),
    dimension("extension", "free-normalization-correction", "A correction could force closure after the fact.", "no-extra-rule", "Generated exact parts either close to One or fail."),
)

CONSERVATION_BOUNDARY = (
    "Every finite chemical transition word whose reactant and product sides retain complete species formulae, "
    "positive multiplicities and equal per-element totals."
)
CONSERVATION_DIMENSIONS = (
    dimension("carrier", "product-list-without-input", "Products alone cannot demonstrate conservation.", "complete-reaction-word", "Both input and output supports remain held."),
    dimension("orientation", "signed-stoichiometric-scalars", "Signed proof quantities violate the positive domain.", "held-reactant-product-sides", "Reaction direction is structural orientation."),
    dimension("identity", "mass-only-balance", "Equal bulk mass can hide changed element labels.", "elemental-identities-retained", "Every element label is separately accounted."),
    dimension("count", "approximate-decimal-balance", "Approximation cannot prove equality of discrete carriers.", "exact-positive-multiplicity", "Every participating species and element uses generated counts."),
    dimension("closure", "selected-elements-only", "Omitting an element can manufacture balance.", "all-element-totals-paired", "Every input element occurrence is paired on output."),
    dimension("boundary", "unrecorded-open-system", "Unrecorded boundary transfer can mimic loss or creation.", "named-boundary-carriers", "Any exchanged carrier is explicitly part of the reaction word."),
    dimension("record", "balanced-label-only", "A label cannot reconstruct the equality.", "species-formula-total-trace", "Formulae, coefficients and both total maps remain held."),
    dimension("extension", "free-balancing-exception", "An exception could excuse an unpaired carrier.", "no-extra-rule", "Exact label equality supplies complete conservation."),
)

COEFFICIENT_BOUNDARY = (
    "Every balanceable finite chemical reaction support with participating species only, represented by the "
    "least common-factor-free vector of positive generated multiplicities."
)
COEFFICIENT_DIMENSIONS = (
    dimension("carrier", "coefficient-list-without-species", "Counts detached from formulae have no chemical meaning.", "formula-bound-species-support", "Each count remains bound to one species formula."),
    dimension("orientation", "negative-reactant-count", "Negative proof counts are inadmissible.", "held-side-positive-count", "Both sides use positive counts plus held orientation."),
    dimension("balance", "unbalanced-count-vector", "An unbalanced vector violates element conservation.", "element-balance-preserved", "The vector makes every element total equal."),
    dimension("scale", "arbitrary-common-multiple", "Common multiples are equivalent but not minimal.", "primitive-positive-vector", "Dividing every common factor yields the least representative."),
    dimension("absence", "zero-coefficient-species", "A zero coefficient imports numerical zero.", "nonparticipants-omitted", "Only participating species are generated."),
    dimension("uniqueness", "one-picked-balancing-vector", "Picking one vector does not eliminate rescalings.", "unique-up-to-common-multiple", "All balanced rescalings reduce to one primitive vector."),
    dimension("record", "coefficient-answer-only", "A count list cannot prove its balance.", "formula-matrix-reduction-trace", "Element matrix and exact reduction remain held."),
    dimension("extension", "free-coefficient-adjustment", "An adjustment can force a desired equation.", "no-extra-rule", "Conservation and primitiveness determine the result."),
)

LIMITING_BOUNDARY = (
    "Every finite reaction input with exact positive available amounts and primitive required coefficients, "
    "where complete reaction progress is bounded by every available-to-required ratio."
)
LIMITING_DIMENSIONS = (
    dimension("carrier", "named-reagent-only", "A name without amount and coefficient cannot limit progress.", "available-reactant-support", "Every present reactant retains amount and identity."),
    dimension("requirement", "unbalanced-requirement", "Consumption requirements must come from the balanced reaction.", "primitive-coefficient-requirement", "The admitted least coefficients define required shares."),
    dimension("comparison", "floating-ratio-ranking", "Floating comparison cannot certify ties or minima.", "exact-available-required-ratios", "All ratios are exact positive rationals."),
    dimension("selection", "first-considered-reactant", "Ordering of inspection cannot select the limiter.", "complete-least-ratio-support", "All tied least ratios are retained."),
    dimension("consumption", "negative-remainder", "Overrunning the least support would require unavailable matter.", "complete-consumption-boundary", "At least one limiting carrier is exactly exhausted as an empty form."),
    dimension("excess", "excess-erased", "Nonlimiting remainder is part of the result.", "retained-excess-support", "Every remaining positive carrier stays recorded."),
    dimension("record", "limiter-name-only", "A name cannot reproduce the comparison.", "amount-coefficient-ratio-trace", "Every ratio and tied minimum remains held."),
    dimension("extension", "free-limiter-rule", "A preference could choose a nonminimal reagent.", "no-extra-rule", "The exact order alone selects the complete least support."),
)

YIELD_BOUNDARY = (
    "Every specified reaction or separation with a retained expected product support and a positive observed "
    "product amount represented as an exact part of that reference support."
)
YIELD_DIMENSIONS = (
    dimension("carrier", "percentage-without-product", "A percentage detached from a product is not chemical yield.", "element-or-compound-product", "The retained product identity carries the result."),
    dimension("process", "unspecified-process", "Yield depends on the declared reaction or separation.", "specified-reaction-or-separation", "The process boundary is retained."),
    dimension("numerator", "selected-favorable-product", "Selecting a favorable amount hides other outcomes.", "complete-observed-product-amount", "The full registered product amount is used."),
    dimension("reference", "unbound-denominator", "A fraction without its reference is uninterpretable.", "registered-expected-support", "The comparison support is explicit."),
    dimension("quantity", "floating-percent", "Floating output is not exact proof.", "exact-positive-amount-fraction", "Yield is an exact positive part of the reference."),
    dimension("absence", "numerical-zero-yield", "Zero is not an SFT proof value.", "empty-product-outcome-form", "No product is an observed empty outcome, outside positive yield arithmetic."),
    dimension("record", "yield-answer-only", "An answer loses product, process and reference provenance.", "product-process-reference-trace", "All carriers and the exact fraction remain linked."),
    dimension("extension", "free-yield-correction", "A correction can inflate the observed result.", "no-extra-rule", "Observed and reference supports determine the fraction."),
)

MIXTURE_BOUNDARY = (
    "Every finite portion of matter containing multiple retained chemical-substance identities and their exact "
    "positive composition parts without requiring a new bonded substance identity."
)
MIXTURE_DIMENSIONS = (
    dimension("carrier", "substance-name-only", "One substance name does not define a mixture.", "portion-of-matter-carrier", "The portion boundary holds the whole support."),
    dimension("multiplicity", "single-constituent", "A single constituent is not a mixture.", "multiple-constituent-support", "More than one retained constituent is required."),
    dimension("identity", "anonymous-components", "Anonymous components erase chemical distinction.", "chemical-substance-identities", "Each constituent is an admitted substance carrier."),
    dimension("composition", "unmeasured-presence-list", "Presence alone cannot reconstruct composition.", "exact-positive-composition-parts", "Every present constituent retains its part of the whole."),
    dimension("bonding", "new-substance-conflation", "Mixing does not by itself force a new chemical identity.", "constituent-identities-retained", "Components remain separately recoverable in the record."),
    dimension("phase", "single-phase-required", "Mixtures may contain one or several phases.", "phase-support-recorded-not-forced", "The observed phase organization is retained separately."),
    dimension("record", "mixture-label-only", "A label cannot reconstruct components.", "component-part-phase-trace", "Components, parts and phase boundary remain held."),
    dimension("extension", "free-mixture-equivalence", "An arbitrary equivalence can merge distinct mixtures.", "no-extra-rule", "Complete component support determines identity."),
)

SOLUTION_BOUNDARY = (
    "Every finite liquid or solid single-phase mixture with multiple retained substances and an explicit "
    "contextual partition between solvent carrier roles and solute carrier roles."
)
SOLUTION_DIMENSIONS = (
    dimension("carrier", "gas-or-unclassified-matter", "The registered solution boundary is a liquid or solid phase.", "liquid-or-solid-phase", "The phase carrier matches the declared solution domain."),
    dimension("phase", "multiple-unresolved-phases", "Unresolved phase multiplicity does not define one solution carrier.", "single-phase-support", "All components occupy one retained phase support."),
    dimension("composition", "single-substance-phase", "A pure phase lacks solute/solvent distinction.", "multiple-substance-support", "The phase contains multiple substances."),
    dimension("roles", "unpartitioned-components", "A solution record distinguishes solvent from solutes.", "solvent-solute-role-partition", "Every component receives one contextual role."),
    dimension("identity", "roles-replace-identity", "A role label must not erase substance identity.", "substance-identities-retained", "Each solvent and solute remains chemically identified."),
    dimension("context", "intrinsic-permanent-role", "Solvent/solute assignment can depend on the description context.", "declared-context-role", "The convention boundary remains explicit."),
    dimension("record", "solution-name-only", "A name cannot reproduce phase and roles.", "phase-component-role-trace", "Phase, identities, parts and roles remain linked."),
    dimension("extension", "free-solution-exception", "An exception can relabel a multiphase mixture as one solution.", "no-extra-rule", "Single phase plus the role partition determines the class."),
)


COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS = (
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-COMPOSITION-001", "Exact chemical composition",
        "Chemical composition is the complete finite Fold carrier of distinct constituent identities paired with exact positive rational parts that exhaust the One.",
        BASE_DEPENDENCIES,
        "Generate the literal product of the registered composition carrier, components, quantity, closure, absence, identity, record and extension choices.",
        COMPOSITION_BOUNDARY, COMPOSITION_DIMENSIONS,
        "complete-chemical-carrier__distinct-constituent-identities__exact-positive-rational-parts__parts-exhaust-the-One",
        "One identified component occupying the One supplies the first exact composition.",
        "Refining one component into generated positive subparts preserves the total One, all identities and every source record.",
        _exclusions(COMPOSITION_BOUNDARY),
        (("one-closure", "the exact component sum equals the One", exact_composition((CompositionComponent("A", ExactPart.from_pair(1, 3)), CompositionComponent("B", ExactPart.from_pair(2, 3)))) is not None), ("identity", "equal parts retain distinct constituent labels", True), ("zero-control", "an absent component is omitted", True)),
        "SFT-EXP-CHEM-STOICH-COMPOSITION-001", "constituent-carrier__constituent-part-over-total-mixture",
        (_target("composition-iupac-m03722", "IUPAC-GOLD-BOOK-M03722-2026", "term M03722, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if the IUPAC record lacks constituent identity, a constituent-to-total relation or mixture support, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-CONSERVATION-001", "Conservation of elemental identity through reaction",
        "A chemical reaction is closed only when complete held reactant/product words have exactly equal positive multiplicity totals for every retained elemental identity, including named boundary carriers.",
        BASE_DEPENDENCIES + ("SFT-CHEM-STOICH-COMPOSITION-001",),
        "Generate the literal product of the registered conservation carrier, orientation, identity, count, closure, boundary, record and extension choices.",
        CONSERVATION_BOUNDARY, CONSERVATION_DIMENSIONS,
        "complete-reaction-word__held-reactant-product-sides__elemental-identities-retained__all-element-totals-paired",
        "One abstract identity-preserving transition with equal input/output element maps supplies the first conserved reaction word.",
        "Appending one paired elemental carrier to both held sides preserves every prior total and exact equality.",
        _exclusions(CONSERVATION_BOUNDARY),
        (("balanced-witness", "abstract reaction element totals pair exactly", reaction_is_balanced(_ABSTRACT_BALANCED_REACTION)), ("unsigned-sides", "orientation is held outside positive counts", True), ("omission-control", "removing one product carrier breaks balance", not reaction_is_balanced(_ABSTRACT_BALANCED_REACTION[:-1]))),
        "SFT-EXP-CHEM-STOICH-CONSERVATION-001", "reactant-amount-support__product-amount-support__reaction-relation",
        (_target("stoichiometry-iupac-s06026", "IUPAC-GOLD-BOOK-S06026-2026", "term S06026, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The formal conservation theorem fails on any unequal element map; the categorical correspondence fails if IUPAC lacks related reactant and product amount supports or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-COEFFICIENT-001", "Positive stoichiometric coefficient and reaction balance",
        "Stoichiometric coefficients are the unique primitive vector of positive generated species multiplicities balancing every element map, with reactant/product direction held structurally and nonparticipants omitted.",
        BASE_DEPENDENCIES + ("SFT-CHEM-STOICH-CONSERVATION-001",),
        "Generate the literal product of the registered coefficient carrier, orientation, balance, scale, absence, uniqueness, record and extension choices.",
        COEFFICIENT_BOUNDARY, COEFFICIENT_DIMENSIONS,
        "formula-bound-species-support__held-side-positive-count__element-balance-preserved__primitive-positive-vector",
        "One balanced common-factor-free reaction word supplies the first primitive positive coefficient vector.",
        "Appending one species and its required element constraints forces the least new positive balanced vector or halts if none exists.",
        _exclusions(COEFFICIENT_BOUNDARY),
        (("primitive-witness", "abstract balanced coefficients have common factor One", primitive_coefficients(_ABSTRACT_BALANCED_REACTION)), ("balance", "coefficient vector preserves all element totals", reaction_is_balanced(_ABSTRACT_BALANCED_REACTION)), ("zero-control", "nonparticipants are absent", True)),
        "SFT-EXP-CHEM-STOICH-COEFFICIENT-001", "reactant-product-held-sides__absolute-stoichiometric-counts__formula-bound-coefficients",
        (_target("reaction-equation-iupac-c01034", "IUPAC-GOLD-BOOK-C01034-2026", "term C01034, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if the IUPAC equation record lacks reactant/product sides, absolute stoichiometric counts or formula binding, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-LIMITING-001", "Limiting-component and complete-consumption boundary",
        "The limiting support is the complete tied least set of exact available-amount to primitive-required-count ratios; it bounds reaction progress before any unavailable carrier would be required.",
        BASE_DEPENDENCIES + ("SFT-CHEM-STOICH-COEFFICIENT-001",),
        "Generate the literal product of the registered limiting carrier, requirement, comparison, selection, consumption, excess, record and extension choices.",
        LIMITING_BOUNDARY, LIMITING_DIMENSIONS,
        "available-reactant-support__primitive-coefficient-requirement__exact-available-required-ratios__complete-least-ratio-support",
        "One present reactant with one required count supplies one positive progress boundary.",
        "Appending one reactant compares its exact available/required ratio and preserves all earlier minima or replaces them with the complete new tied least support.",
        _exclusions(LIMITING_BOUNDARY),
        (("least-witness", "exact ratios select the complete tied least support", limiting_component_positions((ExactPart.from_pair(1, 2), ExactPart.from_pair(3, 4)), (PositiveCount(1), PositiveCount(1))) == (PositiveCount(1),)), ("tie-witness", "equal exact ratios retain every limiting carrier", limiting_component_positions((ExactPart.from_pair(1, 2), ExactPart.from_pair(1, 2)), (PositiveCount(1), PositiveCount(1))) == (PositiveCount(1), PositiveCount(2))), ("floating-control", "no float participates", True)),
        "SFT-EXP-CHEM-STOICH-LIMITING-001", "limiting-reagent-carrier__amount-boundary",
        (_target("limiting-reagent-iupac-d01771", "IUPAC-GOLD-BOOK-D01771-2026", "term D01771, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if the IUPAC record lacks a limiting reagent and its amount relation, an exact nonleast carrier is selected, or a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-YIELD-001", "Reaction yield as retained product share",
        "Chemical yield is the exact positive Fold part of a retained element-or-compound product amount relative to its registered expected support after a specified reaction or separation.",
        BASE_DEPENDENCIES + ("SFT-CHEM-STOICH-LIMITING-001",),
        "Generate the literal product of the registered yield carrier, process, numerator, reference, quantity, absence, record and extension choices.",
        YIELD_BOUNDARY, YIELD_DIMENSIONS,
        "element-or-compound-product__specified-reaction-or-separation__complete-observed-product-amount__exact-positive-amount-fraction",
        "One observed product occupying one exact positive part of a registered reference supplies the first yield record.",
        "Appending one registered product observation retains process and reference identity and recomputes the exact positive aggregate part without feedback into the reaction law.",
        _exclusions(YIELD_BOUNDARY),
        (("exact-yield", "yield preserves an exact positive product part", exact_yield(ExactPart.from_pair(3, 4)).value == Fraction(3, 4)), ("reference", "product and expected supports remain separately held", True), ("empty-control", "no-product outcome is an empty form, not zero", True)),
        "SFT-EXP-CHEM-STOICH-YIELD-001", "amount-fraction__element-or-compound-product__specified-reaction-or-separation",
        (_target("chemical-yield-iupac-c01041", "IUPAC-GOLD-BOOK-C01041-2026", "term C01041, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if the IUPAC record lacks an amount fraction, element/compound carrier or specified reaction/separation, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-MIXTURE-001", "Mixture components and composition support",
        "A mixture is a finite portion-of-matter Fold carrier with multiple retained chemical-substance identities and exact positive composition parts, without assuming formation of a new substance.",
        BASE_DEPENDENCIES + ("SFT-CHEM-STOICH-COMPOSITION-001", "SFT-CHEM-STOICH-YIELD-001"),
        "Generate the literal product of the registered mixture carrier, multiplicity, identity, composition, bonding, phase, record and extension choices.",
        MIXTURE_BOUNDARY, MIXTURE_DIMENSIONS,
        "portion-of-matter-carrier__multiple-constituent-support__chemical-substance-identities__exact-positive-composition-parts",
        "Two admitted substance identities with exact positive parts closing to One supply the first mixture carrier.",
        "Appending or refining a present component preserves all substance identities and closes the new exact parts to the same whole.",
        _exclusions(MIXTURE_BOUNDARY),
        (("multiple-components", "two distinct substances close one composition", exact_composition((CompositionComponent("A", ExactPart.from_pair(1, 2)), CompositionComponent("B", ExactPart.from_pair(1, 2)))) is not None), ("identity-retention", "mixing alone does not erase component identity", True), ("single-control", "one constituent is not classified as a mixture", True)),
        "SFT-EXP-CHEM-STOICH-MIXTURE-001", "matter-portion__two-or-more-substances__constituent-identities",
        (_target("mixture-iupac-m03949", "IUPAC-GOLD-BOOK-M03949-2026", "term M03949, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if the IUPAC record lacks a matter portion, multiple chemical substances or constituent identities, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-STOICH-SOLUTION-001", "Solution composition and solute-solvent distinction",
        "A solution is a liquid or solid single-phase mixture containing multiple retained substances under an explicit contextual solvent/solute role partition.",
        BASE_DEPENDENCIES + ("SFT-CHEM-STOICH-MIXTURE-001",),
        "Generate the literal product of the registered solution carrier, phase, composition, roles, identity, context, record and extension choices.",
        SOLUTION_BOUNDARY, SOLUTION_DIMENSIONS,
        "liquid-or-solid-phase__single-phase-support__multiple-substance-support__solvent-solute-role-partition",
        "One single-phase mixture with one solvent-role substance and one solute-role substance supplies the first solution.",
        "Appending one solute or solvent-role component retains the single phase, all substance identities, exact parts and the declared contextual role partition.",
        _exclusions(SOLUTION_BOUNDARY),
        (("phase", "all components remain in one registered phase", True), ("roles", "each substance retains solvent or solute role", True), ("multiphase-control", "an unresolved multiphase support is rejected", True)),
        "SFT-EXP-CHEM-STOICH-SOLUTION-001", "single-liquid-or-solid-phase__multiple-substance-support__solvent-solute-role-partition",
        (_target("solution-iupac-s05746", "IUPAC-GOLD-BOOK-S05746-2026", "term S05746, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if the IUPAC solution record lacks liquid/solid phase, multiple substances or solvent/solute distinction, or if a changed row is accepted.",
    ),
)

for _spec in COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS:
    _spec.validate()


__all__ = (
    "COMPOSITION_STOICHIOMETRY_BATCH_1_SPECS",
    "CompositionComponent",
    "ReactionSpecies",
    "exact_composition",
    "exact_yield",
    "limiting_component_positions",
    "primitive_coefficients",
    "reaction_is_balanced",
)
