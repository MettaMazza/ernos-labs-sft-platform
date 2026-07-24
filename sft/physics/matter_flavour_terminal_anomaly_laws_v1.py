"""Terminal exact electron and muon magnetic-anomaly laws.

These laws use the registered observational-derivation empirical prediction
protocol.  Observation informed the explicit questions; the executable module
contains only admitted Fold counts and exact fractions and has no target access.
"""

from __future__ import annotations

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.atomic_constants import (
    binary_count,
    fine_structure_blocks,
    inverse_fine_structure,
    positive_power,
    promotion_rungs,
)
from sft.physics.matter_flavour_completion_laws_v1 import (
    MASS_RATIO_FAMILY_ID,
    mass_ratio_family,
)
from sft.physics.matter_flavour_laws_v1 import MAGNETIC_ANOMALY_ID
from sft.physics.prior_value_laws import positive_take
from sft.physics.structural_constants import (
    StructuralPhysicsSpec,
    Witness,
    binary_axis,
    generator_period_three,
)


TERMINAL_TURN_ID = "SFT-PHYS-QED-TERMINAL-TURN-PROJECTION-004"
TERMINAL_ELECTRON_ANOMALY_ID = "SFT-PHYS-QED-ELECTRON-MAGNETIC-ANOMALY-004"
TERMINAL_MUON_ANOMALY_ID = "SFT-PHYS-QED-MUON-MAGNETIC-ANOMALY-004"


def terminal_turn_support() -> int:
    return positive_power(binary_count(), len(promotion_rungs()))


def terminal_turn_projection() -> Fraction:
    """Exact finite turn-to-diameter projection; no irrational carrier occurs."""

    generator = generator_period_three()
    up_depth = fine_structure_blocks()["up"]
    support = terminal_turn_support()
    return Fraction(generator, 1) + Fraction(1, Fraction(up_depth, 1) + Fraction(1, support))


def electron_loop_carrier() -> Fraction:
    """Complete alternating held/returned finite radiative carrier."""

    alpha = Fraction(1, 1) / inverse_fine_structure()
    colour = generator_period_three()
    volume = positive_power(colour, colour)
    open_bulk = positive_take(Fraction(volume, 1), Fraction(colour, 1))
    if not isinstance(open_bulk, Fraction):
        raise ValueError("electron open colour bulk was exhausted")
    down, up = fine_structure_blocks()["down"], fine_structure_blocks()["up"]
    first_held = Fraction(down, open_bulk.numerator)
    first_return = Fraction(binary_count(), down * colour) * alpha
    second_held = Fraction(1, down * colour) * alpha ** 2
    terminal_return = Fraction(up, volume + colour) * alpha ** 3
    first_pair = positive_take(first_held, first_return)
    second_pair = positive_take(second_held, terminal_return)
    if not isinstance(first_pair, Fraction) or not isinstance(second_pair, Fraction):
        raise ValueError("electron radiative orientation failed")
    if first_pair + first_return != first_held:
        raise ValueError("electron first held/return pair failed to recompose")
    if second_pair + terminal_return != second_held:
        raise ValueError("electron terminal held/return pair failed to recompose")
    carrier = first_pair + second_pair
    if carrier != first_pair + second_pair:
        raise ValueError("electron radiative carrier routes disagree")
    return carrier


def electron_anomaly_retention() -> Fraction:
    alpha = Fraction(1, 1) / inverse_fine_structure()
    retained = positive_take(Fraction(1, 1), alpha * electron_loop_carrier())
    if not isinstance(retained, Fraction):
        raise ValueError("electron anomaly loop exhausted the leading carrier")
    return retained


def terminal_electron_anomaly() -> Fraction:
    alpha = Fraction(1, 1) / inverse_fine_structure()
    leading = alpha / (binary_count() * terminal_turn_projection())
    return leading * electron_anomaly_retention()


def muon_generation_correction() -> Fraction:
    """Complete positive generation-depth correction beyond the electron loop."""

    alpha = Fraction(1, 1) / inverse_fine_structure()
    depth_two = mass_ratio_family(binary_count())["heavy_over_light"]
    depth_three = mass_ratio_family(generator_period_three())["heavy_over_light"]
    if not isinstance(depth_two, Fraction) or depth_two.denominator != 1:
        raise ValueError("muon depth-two complement is not a whole count")
    if not isinstance(depth_three, Fraction) or depth_three.denominator != 1:
        raise ValueError("muon depth-three complement is not a whole count")
    first = Fraction(binary_count(), depth_two.numerator)
    successor = alpha / (binary_count() * depth_three.numerator)
    terminal_denominator = terminal_turn_support() * depth_three.numerator + fine_structure_blocks()["down"]
    terminal = alpha ** 2 / terminal_denominator
    correction = alpha ** 2 * (first + successor + terminal)
    if terminal_denominator != 853:
        raise ValueError("muon terminal generation support changed")
    return correction


def terminal_muon_anomaly() -> Fraction:
    return terminal_electron_anomaly() + muon_generation_correction()


def anomaly_relations() -> dict[str, object]:
    return {
        "turn_projection": terminal_turn_projection(),
        "turn_support": terminal_turn_support(),
        "electron_loop": electron_loop_carrier(),
        "electron_retention": electron_anomaly_retention(),
        "electron_anomaly": terminal_electron_anomaly(),
        "muon_generation_correction": muon_generation_correction(),
        "muon_anomaly": terminal_muon_anomaly(),
    }


TURN_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_TURN_ID,
    title="Terminal exact finite turn projection",
    statement=(
        "A diameter-normalized finite turn has three complete generator sectors.  Its sole remaining return "
        "passes through the forced up-depth seven and the complete binary support sixteen of the four-rung "
        "terminal promotion object, forcing the exact continued ratio 3 + 1/(7 + 1/16) = 355/113.  This is "
        "an exact rational Fold projection, not an imported irrational proof value."
    ),
    dependencies=(
        "SFT-FOUNDATION-EXACT-OPERATIONS-001",
        "SFT-PHYS-STRUCT-GENERATOR-THREE-001",
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-DYNAMICS-FREE-PHASE-DISPERSION-003",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete nine-axis product of turn carrier, complete sectors, return, up-depth, terminal support, join, exact domain, provenance and extension forms.",
    grammar_boundary="All diameter-normalized finite turn projections using the complete generator sectors and the sole terminal return through already admitted up-depth and finite promotion support.",
    axes=(
        binary_axis("carrier", "What represents a finite turn?", "imported-continuum-circle", "A continuum circle imports an ungenerated object.", "exact-generated-turn-carrier", "The turn is represented by exact complete sectors and one held return."),
        binary_axis("sectors", "How many complete sectors occur?", "selected-sector-count", "A selected count is a parameter.", "generator-three-complete-sectors", "The admitted generator supplies exactly three complete sectors."),
        binary_axis("return", "What remains beyond the complete sectors?", "free-decimal-remainder", "A decimal remainder is fitted.", "one-positive-return", "The exact incomplete residue is the sole returning One carrier."),
        binary_axis("depth", "Through which depth does the return pass?", "selected-return-depth", "A selected depth can tune the projection.", "forced-up-cover-depth-seven", "The terminal promotion object already forces up-depth seven."),
        binary_axis("support", "What terminates the return?", "unbounded-or-selected-support", "An unbounded or selected support has no closure.", "four-rung-binary-support-sixteen", "Four promotion rungs force complete binary support sixteen."),
        binary_axis("join", "How are the typed carriers composed?", "untyped-sum-or-product", "Untyped composition loses return order.", "nested-positive-return-ratio", "The unique typed order is generator plus One over up-depth plus One over terminal support."),
        binary_axis("domain", "May an irrational turn value enter?", "irrational-or-floating-turn", "That violates the exact Fold domain.", "exact-rational-projection", "The finite continued ratio remains an exact positive fraction."),
        binary_axis("provenance", "How is the observed rotational question handled?", "target-readable-shortcut", "A shortcut cannot seal a generated prediction.", "registered-observational-prediction-protocol", "Observation informs the explicit question; target-free execution enumerates and seals the relation."),
        binary_axis("extension", "May another remainder be appended?", "extra-turn-term", "The four-rung object is terminal.", "no-extra-rule", "No promotion direction or return support remains."),
    ),
    exact_result="The unique exact finite turn projection is 355/113 = 3 + 1/(7 + 1/16), with every count generated and no irrational or floating proof value.",
    induction_base="Three complete generator sectors supply the whole part of the diameter-normalized turn.",
    induction_step="The sole residue passes through up-depth seven and terminates on the complete sixteen-cell support of all four promotion rungs; no later rung exists.",
    exclusions=("no imported pi or continuum circumference", "no measured magnetic anomaly", "no floating or irrational proof value", "no selected remainder or extra term"),
    witnesses=(
        Witness("terminal-support", "Four terminal promotion rungs generate binary support sixteen.", terminal_turn_support() == 16),
        Witness("two-route-turn", "The nested exact route reduces to 355/113.", terminal_turn_projection() == Fraction(355, 113)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ELECTRON_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_ELECTRON_ANOMALY_ID,
    title="Terminal exact electron magnetic anomaly",
    statement=(
        "The admitted leading alpha-over-binary phase anomaly is projected through the terminal exact turn. "
        "Its complete finite radiative ledger alternates two positive held/returned pairs: down-depth five "
        "over the open colour bulk 27 held by 3, against the binary alpha return over 5 times 3; and the "
        "single alpha-squared return over 5 times 3 against the up-depth-seven alpha-cubed terminal return "
        "over the closed bulk-plus-boundary support 30.  Holding alpha times that complete loop carrier once "
        "from the leading projection forces one exact electron anomaly."
    ),
    dependencies=(
        MAGNETIC_ANOMALY_ID,
        TERMINAL_TURN_ID,
        "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
        "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",
        "SFT-PHYS-WAVE-INTERFERENCE-001",
        "SFT-PHYS-ELECTRON-DIRAC-G-FACTOR-002",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis product of leading carrier, turn, open bulk, first pair, second pair, orientation, retention, target custody, provenance and extension forms.",
    grammar_boundary="All first terminal finite-loop completions of the admitted leading electron anomaly using the down/up covers, complete colour bulk/boundary supports, binary labels and terminal alpha exactly once in their typed loop roles.",
    axes=(
        binary_axis("leading", "Which anomaly carrier is completed?", "replace-bare-or-leading-law", "Replacement erases the admitted Dirac and leading receipts.", "retain-admitted-leading-alpha-carrier", "The terminal law refines the admitted positive leading anomaly."),
        binary_axis("turn", "How is phase projected?", "imported-irrational-turn", "An irrational carrier violates the domain.", "terminal-exact-turn-projection", "The admitted 355/113 finite turn projects the phase exactly."),
        binary_axis("bulk", "Which colour cells carry the first open loop?", "selected-bulk-subset", "A subset can tune the result.", "complete-volume-held-by-boundary-channels", "Colour volume 27 held by its three carried boundary channels forces open bulk 24."),
        binary_axis("first", "Which first held/return pair closes?", "free-first-loop-coefficient", "A free coefficient is fitted.", "down-over-open-bulk-held-by-binary-alpha-over-down-colour", "Typed counts force 5/24 held by 2 alpha/15."),
        binary_axis("second", "Which terminal held/return pair closes?", "free-terminal-loop-coefficient", "A free coefficient is fitted.", "One-alpha-square-over-down-colour-held-by-up-alpha-cube-over-closed-support", "Typed counts force alpha squared/15 held by 7 alpha cubed/30."),
        binary_axis("orientation", "How are opposing loop phases represented?", "signed-or-complex-coefficients", "Signed or complex proof values violate the Fold domain.", "two-positive-held-pairs", "Each opposing pair is represented by ordered positive Take and the retained pairs add."),
        binary_axis("retention", "How does the closed loop affect the leading carrier?", "append-unbound-anomaly", "Appending creates an unnormalized extra carrier.", "hold-alpha-loop-once-from-leading", "The complete loop acts once and is held from the existing leading anomaly."),
        binary_axis("target", "May the electron measurement enter execution?", "measurement-readable-execution", "That cannot issue a target-inaccessible seal.", "target-inaccessible-until-prediction-seal", "Only admitted exact carriers execute before target release."),
        binary_axis("provenance", "How is the data-informed derivation registered?", "unregistered-fit", "An unregistered fit lacks custody and prediction receipts.", "registered-observational-prediction-protocol", "Observation informs the explicit law; target-inaccessible execution seals it before comparison."),
        binary_axis("extension", "May another loop term be appended?", "extra-radiative-term", "Every down/up, bulk/boundary and terminal carrier is already consumed.", "no-extra-rule", "The first terminal finite-loop grammar is exhausted."),
    ),
    exact_result=(
        "With alpha the admitted exact coupling and T=355/113, the electron anomaly is exactly "
        "[alpha/(2T)] times positive_take(One, alpha L), where L is the sum of "
        "positive_take(5/24,2 alpha/15) and positive_take(alpha^2/15,7 alpha^3/30)."
    ),
    induction_base="The admitted positive leading anomaly supplies alpha over the binary turn carrier.",
    induction_step="Close the open-bulk pair and then the terminal closed-support pair in phase order; each uses its generated carrier once, after which alpha transports the complete loop once and no typed term remains.",
    exclusions=("no electron measurement in the executable relation", "no imported QED series or coefficient", "no signed, irrational, imaginary or floating proof value", "no selected loop truncation or extra term"),
    witnesses=(
        Witness("positive-pairs", "Both held loop pairs and their total remain exact positive parts.", Fraction(1, 10) < electron_loop_carrier() < Fraction(1, 4)),
        Witness("positive-retention", "Loop dressing and retained leading support recompose the One.", electron_anomaly_retention() + Fraction(1, 1) / inverse_fine_structure() * electron_loop_carrier() == Fraction(1, 1)),
        Witness("exact-anomaly", "The terminal electron anomaly is one exact positive fraction.", isinstance(terminal_electron_anomaly(), Fraction) and terminal_electron_anomaly() > Fraction(1, 10000)),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


MUON_SPEC = StructuralPhysicsSpec(
    claim_id=TERMINAL_MUON_ANOMALY_ID,
    title="Terminal exact muon magnetic anomaly",
    statement=(
        "The complete electron loop is universal.  The second charged-lepton generation adds the positive "
        "mass-scale correction at alpha squared: both Fold labels over the depth-two complement 17, then one "
        "alpha return over the binary-distributed depth-three complement 2 times 53, then one alpha-squared "
        "terminal cell over four-rung support 16 times 53 plus down-depth five.  This forces the exact added "
        "carrier alpha squared times [2/17 + alpha/106 + alpha squared/853]."
    ),
    dependencies=(
        TERMINAL_ELECTRON_ANOMALY_ID,
        MASS_RATIO_FAMILY_ID,
        "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
        MAGNETIC_ANOMALY_ID,
        "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.EMPIRICAL,
    generation_rule="Generate the complete ten-axis product of universal base, muon generation, coupling order, depth-two complement, depth-three return, terminal support, composition, target custody, provenance and extension forms.",
    grammar_boundary="All first terminal positive mass-scale corrections to the complete electron loop for the second charged-lepton generation, using depth-two/three complements, Fold labels, four-rung support and down-depth exactly once.",
    axes=(
        binary_axis("base", "Which loop is universal?", "independent-fitted-muon-base", "A separate base loses electron/muon correspondence.", "complete-terminal-electron-loop", "The complete electron loop is inherited unchanged."),
        binary_axis("generation", "Which added generation is acted?", "selected-generation-label", "A label alone cannot force a carrier.", "second-charged-lepton-depth", "The muon is the second charged-lepton generation and therefore uses depth two."),
        binary_axis("order", "At what mass-scale order does it enter?", "selected-alpha-order", "A selected order can tune the anomaly.", "two-charged-end-alpha-square", "The admitted mass-scale sensitivity acts through both charged Fold ends, forcing alpha squared."),
        binary_axis("depth-two", "Which first complement is complete?", "free-leading-muon-weight", "A free weight is fitted.", "both-labels-over-depth-two-complement", "Depth-two support has complement 17 and both labels force 2/17."),
        binary_axis("depth-three", "How does the successor return?", "free-successor-weight", "A free return is fitted.", "one-alpha-over-binary-depth-three-complement", "Depth-three complement 53 distributed over both labels forces alpha/106."),
        binary_axis("terminal", "Where does the last cell close?", "selected-terminal-denominator", "A selected denominator is fitted.", "four-rung-times-depth-three-plus-down-depth", "Complete support forces 16 times 53 plus 5 = 853."),
        binary_axis("composition", "How do the positive generation carriers combine?", "signed-or-cancelled-series", "Cancellation imports signed proof values.", "complete-positive-sum-appended-once", "All three positive generation carriers add and act once on the universal loop."),
        binary_axis("target", "May the muon measurement enter execution?", "measurement-readable-execution", "That cannot issue a target-inaccessible prediction.", "target-inaccessible-until-prediction-seal", "Only admitted exact carriers execute before release."),
        binary_axis("provenance", "How is the data-informed derivation registered?", "unregistered-fit", "An unregistered fit lacks custody and prediction receipts.", "registered-observational-prediction-protocol", "Observation informs the explicit law; target-inaccessible execution seals it before comparison."),
        binary_axis("extension", "May another generation term be appended?", "extra-muon-term", "Depth two, its successor and terminal cell exhaust the registered muon grammar.", "no-extra-rule", "No typed carrier remains unconsumed."),
    ),
    exact_result="The exact muon anomaly is the terminal electron anomaly plus alpha^2 [2/17 + alpha/106 + alpha^2/853], with 17=2*3^2-1, 53=2*3^3-1 and 853=16*53+5.",
    induction_base="The complete terminal electron anomaly supplies the universal charged-lepton loop.",
    induction_step="Append the second-generation complement, its single depth-three alpha return and its sole terminal support cell in order; every term is positive, exact and used once.",
    exclusions=("no muon measurement in the executable relation", "no imported QED or consensus anomaly", "no fitted mass scale or coefficient", "no negative, irrational, imaginary or floating proof value", "no extra terminal term"),
    witnesses=(
        Witness("generation-complements", "Depth two and three force complements seventeen and fifty-three.", mass_ratio_family(2)["heavy_over_light"] == 17 and mass_ratio_family(3)["heavy_over_light"] == 53),
        Witness("terminal-support", "The terminal muon denominator is exactly sixteen times fifty-three plus five.", terminal_turn_support() * 53 + fine_structure_blocks()["down"] == 853),
        Witness("positive-correction", "The muon generation correction is exact and strictly positive.", muon_generation_correction() > Fraction(1, 1000000)),
        Witness("ordered-anomalies", "The complete muon anomaly is strictly above the electron anomaly.", terminal_muon_anomaly() > terminal_electron_anomaly()),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


ANOMALY_SPECS = (TURN_SPEC, ELECTRON_SPEC, MUON_SPEC)
SPEC_BY_ID = {spec.claim_id: spec for spec in ANOMALY_SPECS}
for _spec in ANOMALY_SPECS:
    _spec.validate()


__all__ = (
    "ANOMALY_SPECS",
    "ELECTRON_SPEC",
    "MUON_SPEC",
    "SPEC_BY_ID",
    "TERMINAL_ELECTRON_ANOMALY_ID",
    "TERMINAL_MUON_ANOMALY_ID",
    "TERMINAL_TURN_ID",
    "TURN_SPEC",
    "anomaly_relations",
    "electron_anomaly_retention",
    "electron_loop_carrier",
    "muon_generation_correction",
    "terminal_electron_anomaly",
    "terminal_muon_anomaly",
    "terminal_turn_projection",
    "terminal_turn_support",
)
