"""Terminal nucleon composition and binding-dominance successor.

The executable law contains no nucleon measurement. Opposed charge and energy
orientations are held labels with positive magnitudes; neutral closure is the
empty form. Algebraic quark roots remain rationally enclosed and are never
formed as irrational proof values.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import binary_count, fine_structure_blocks, inverse_fine_structure, positive_power
from sft.physics.matter_flavour_laws_v1 import bisect_bracket, isolate_cubic_roots, quark_cubic_invariants
from sft.physics.matter_flavour_terminal_proton_laws_v1 import terminal_proton_dressing
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    first_return_trace,
    generator_period_three,
    generator_unit_part,
    positive_predecessor,
)


NUCLEON_BINDING_TERMINAL_ID = "SFT-PHYS-NUCLEON-BINDING-TERMINAL-005"


def colour_cycle() -> tuple[Fraction, ...]:
    unit = generator_unit_part(generator_period_three())
    trace = first_return_trace(unit)
    cycle = (unit, *trace[:-1])
    if cycle != (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7)):
        raise ValueError("complete colour cycle changed")
    if cycle[0] + cycle[1] + cycle[2] != Fraction(1, 1):
        raise ValueError("colour cycle does not close to the One")
    return cycle


def baryon_charge_class(up_count: int, down_count: int) -> tuple[str, Fraction] | tuple[()]:
    colour = generator_period_three()
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in (up_count, down_count)):
        raise ValueError("baryon flavour counts must be positive wholes")
    if up_count + down_count != colour:
        raise ValueError("a minimal baryon requires the complete colour count")
    positive = Fraction(binary_count() * up_count, colour)
    counter = Fraction(down_count, colour)
    if positive == counter:
        return ()
    if positive > counter:
        return ("positive-charge-hand", positive_take(positive, counter))
    return ("counter-charge-hand", positive_take(counter, positive))


def nucleon_flavour_words() -> dict[str, tuple[str, ...]]:
    proton = ("up", "up", "down")
    neutron = ("up", "down", "down")
    if baryon_charge_class(2, 1) != ("positive-charge-hand", Fraction(1, 1)):
        raise ValueError("unique unit-charge baryon did not close")
    if baryon_charge_class(1, 2) != ():
        raise ValueError("unique neutral baryon did not close")
    return {"proton": proton, "neutron": neutron}


def nucleon_mass_ledger() -> dict[str, Fraction | int]:
    depth = fine_structure_blocks()["up"]
    support = positive_power(binary_count(), depth)
    bare = Fraction(1, support)
    held = positive_take(Fraction(1, 1), bare)
    if not isinstance(held, Fraction) or held != Fraction(positive_predecessor(support), support):
        raise ValueError("nucleon held-cycle ledger did not close")
    return {"depth": depth, "support": support, "bare": bare, "held_cycle": held}


def refined_light_quark_roots() -> dict[str, tuple[Fraction, Fraction]]:
    result: dict[str, tuple[Fraction, Fraction]] = {}
    for name, values in quark_cubic_invariants().items():
        roots = isolate_cubic_roots(values[1], values[2])
        while roots[0][1] - roots[0][0] > Fraction(1, 10 ** 12):
            roots = tuple(bisect_bracket(row, values[1], values[2]) for row in roots)
        result[name] = roots[0]
    return result


def light_down_up_surplus_interval() -> tuple[Fraction, Fraction]:
    roots = refined_light_quark_roots()
    down, up = roots["down"], roots["up"]
    lower = positive_take(down[0], up[1])
    upper = positive_take(down[1], up[0])
    if not isinstance(lower, Fraction) or not isinstance(upper, Fraction) or lower >= upper:
        raise ValueError("light down/up exact ordering failed")
    return lower, upper


def neutron_proton_order_certificate() -> dict[str, Fraction]:
    lower, upper = light_down_up_surplus_interval()
    electromagnetic = terminal_proton_dressing()
    net_lower = positive_take(lower, electromagnetic)
    net_upper = positive_take(upper, electromagnetic)
    if not isinstance(net_lower, Fraction) or not isinstance(net_upper, Fraction):
        raise ValueError("light-flavour surplus did not exceed the admitted proton dressing")
    return {
        "flavour_surplus_lower": lower,
        "flavour_surplus_upper": upper,
        "proton_electromagnetic_dressing": electromagnetic,
        "net_neutron_surplus_lower": net_lower,
        "net_neutron_surplus_upper": net_upper,
    }


def axes() -> tuple:
    return (
        binary_axis("predecessor", "How are admitted colour, confinement and quark laws used?", "rewrite-predecessor-laws", "A successor cannot alter admitted receipts.", "compose-immutable-predecessors", "The new law composes the exact admitted colour, depth, quark-root and proton-dressing carriers."),
        binary_axis("colour", "What closes internal colour?", "listed-three-colour-names", "Names do not prove a closed orbit.", "complete-period-three-One-cycle", "The generated 1/7, 2/7, 4/7 cycle uses every colour position and sums exactly to the One."),
        binary_axis("composition", "Which minimal words produce charged and neutral nucleons?", "import-proton-neutron-labels", "Imported particle labels would select the result.", "enumerate-complete-three-flavour-charge-words", "Among complete positive u/d count splits, two-up/one-down uniquely has unit positive charge and one-up/two-down uniquely closes to the empty neutral form."),
        binary_axis("depth", "Which support bounds the nucleon ledger?", "selected-binding-depth", "A chosen depth can tune a mass share.", "admitted-upper-quark-depth-seven", "The already forced upper-quark cover supplies depth seven without nucleon data."),
        binary_axis("ledger", "How are bare and held mass support partitioned?", "free-binding-percentage", "A percentage read from observation is a parameter.", "one-cell-and-complete-positive-predecessor", "Complete depth-seven binary support has one explicit cell and its unique 127-cell held predecessor."),
        binary_axis("binding", "What mass-dominance statement follows?", "qualitative-most-without-bound", "An unbounded slogan is not falsifiable.", "bare-below-one-percent-held-above-ninety-nine", "Exact 1/128 is below 1/100 and exact 127/128 is above 99/100."),
        binary_axis("flavour", "How is down/up ordering obtained?", "borrowed-quark-mass-order", "Borrowing a measured ordering reverses the derivation.", "exact-light-root-enclosure-order", "The admitted down/up cubic invariants give disjoint rational enclosures with a positive down-minus-up surplus."),
        binary_axis("electromagnetic", "Can proton self-energy reverse that ordering?", "ignore-or-fit-electromagnetic-effect", "Ignoring or fitting the competing carrier cannot close the sign.", "compare-admitted-terminal-proton-dressing", "The exact lower flavour surplus exceeds the complete admitted proton electromagnetic dressing."),
        binary_axis("ordering", "What follows for the nucleons?", "assert-measured-mass-order", "An asserted ordering has no Fold certificate.", "one-down-replacement-forces-neutron-heavier", "Common held support cancels; replacing one up by one down leaves a strictly positive net neutron surplus."),
        binary_axis("target", "May PDG or NIST values enter execution?", "external-target-readable", "Target access cannot seal a prediction.", "target-inaccessible-until-seal", "No nucleon or measured quark mass is accessible to the executable law."),
        binary_axis("provenance", "How is prior observation used?", "conceal-observational-development", "Concealment misstates the derivation history.", "registered-observational-prediction-protocol", "Observation informs the explicit law, then capability-closed execution seals before target release."),
        binary_axis("extension", "May another mass term or percentage be added?", "free-mass-term-or-percentage", "An ungenerated term is a parameter.", "no-extra-rule", "Colour closure, depth support, exact roots and admitted electromagnetic dressing exhaust the declared grammar."),
    )


NUCLEON_BINDING_SPEC = StructuralPhysicsSpec(
    claim_id=NUCLEON_BINDING_TERMINAL_ID,
    title="Terminal nucleon composition, binding dominance and mass ordering",
    statement=(
        "The generated period-three colour cycle closes as 1/7+2/7+4/7=One. Complete positive u/d count "
        "enumeration then uniquely gives the unit-charged word uud and empty-neutral word udd. At the admitted "
        "upper-quark depth seven, one of 128 cells is the explicit valence share and the positive predecessor "
        "127/128 is the held-cycle share. Exact light-quark root enclosures place down above up by more than "
        "the admitted terminal proton electromagnetic dressing, so replacing one up by one down forces the "
        "neutron above the proton."
    ),
    dependencies=(
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
        "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
        "SFT-PHYS-MATTER-QUARK-CUBICS-003",
        "SFT-PHYS-MATTER-CONFINEMENT-LIFT-003",
        "SFT-PHYS-MATTER-PROTON-ELECTRON-TERMINAL-004",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete twelve-axis predecessor, colour, composition, depth, ledger, dominance, flavour, electromagnetic, ordering, custody, provenance and extension product.",
    grammar_boundary="All minimal positive u/d count splits over the complete generated colour-three cycle, complete depth-seven binary support, the admitted light-quark algebraic enclosures and the admitted terminal proton electromagnetic dressing.",
    axes=axes(),
    exact_result="The proton word is uud and the neutron word is udd; the exact structural mass ledger is bare 1/128 and held-cycle 127/128, hence bare below 1/100 and held above 99/100; the exact down-minus-up enclosure exceeds the proton electromagnetic dressing and forces neutron mass above proton mass.",
    induction_base="The generator-three first-return orbit supplies one complete three-member colour singlet and depth One supplies one explicit cell with one held predecessor cell.",
    induction_step="Every binary depth successor doubles complete support while retaining one explicit cell, so at forced depth seven the held predecessor is 127; replacing one up label by the already ordered down root preserves common binding and appends one strictly positive surplus.",
    exclusions=(
        "no V1/V2 executable, certificate, answer value or measured mass as a premise",
        "no semantic numerical zero, negative, irrational, imaginary or floating proof value",
        "no fitted binding percentage, constituent mass, electromagnetic correction or nucleon scale",
        "no claim that a scheme-dependent PDG current-quark mass ratio is identical to the structural 1/128 cell",
        "no target access before the derivation and prediction seals",
    ),
    witnesses=(
        Witness("colour-One", "The complete generated colour cycle sums to the One.", colour_cycle() == (Fraction(1, 7), Fraction(2, 7), Fraction(4, 7))),
        Witness("nucleon-words", "Complete positive count splits force uud charged and udd neutral.", nucleon_flavour_words() == {"proton": ("up", "up", "down"), "neutron": ("up", "down", "down")}),
        Witness("mass-ledger", "One depth-seven cell and its positive predecessor close the whole mass ledger.", nucleon_mass_ledger()["bare"] == Fraction(1, 128) and nucleon_mass_ledger()["held_cycle"] == Fraction(127, 128)),
        Witness("dominance", "The exact bare share is below one percent and held share above ninety-nine percent.", nucleon_mass_ledger()["bare"] < Fraction(1, 100) and nucleon_mass_ledger()["held_cycle"] > Fraction(99, 100)),
        Witness("ordering", "The exact light-flavour surplus remains positive after the admitted proton dressing.", neutron_proton_order_certificate()["net_neutron_surplus_lower"] > Fraction(1, 1000)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


NUCLEON_BINDING_SPEC.validate()


__all__ = (
    "NUCLEON_BINDING_SPEC",
    "NUCLEON_BINDING_TERMINAL_ID",
    "baryon_charge_class",
    "colour_cycle",
    "light_down_up_surplus_interval",
    "neutron_proton_order_certificate",
    "nucleon_flavour_words",
    "nucleon_mass_ledger",
    "refined_light_quark_roots",
)
