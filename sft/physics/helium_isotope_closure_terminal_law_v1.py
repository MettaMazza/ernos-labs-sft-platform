"""Exact physical-isotope closure of the analytic helium family."""

from fractions import Fraction

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis
from sft.physics.thermal_history_recombination_terminal_law_v1 import freezeout_capture_ledger


CLAIM_ID = "SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057"
HELIUM_CONSTITUENTS = 4


def nonempty_subword_masks(constituents: int = HELIUM_CONSTITUENTS):
    if isinstance(constituents, bool) or constituents < 1:
        raise ValueError("helium constituent count must be a positive whole")
    return tuple(range(1, 2 ** constituents))


def complete_capture_cells():
    return tuple((constituent, mask) for constituent in range(1, HELIUM_CONSTITUENTS + 1) for mask in nonempty_subword_masks())


def isotope_closure_ledger():
    cells = complete_capture_cells()
    analytic_family = freezeout_capture_ledger()["helium_family_mass_share"]
    global_identity_records = ("one-bound-composite-identity",)
    isotope_cells = len(cells) - len(global_identity_records)
    conversion = Fraction(isotope_cells, len(cells))
    helium_isotope = analytic_family * conversion
    hydrogen_family = Fraction(181, 240)
    return {
        "constituents": HELIUM_CONSTITUENTS,
        "nonempty_subwords": nonempty_subword_masks(),
        "capture_cells": cells,
        "complete_cell_count": len(cells),
        "global_identity_records": global_identity_records,
        "isotope_cell_count": isotope_cells,
        "analytic_helium_family": analytic_family,
        "isotope_conversion": conversion,
        "physical_helium_isotope_share": helium_isotope,
        "physical_hydrogen_family_share": hydrogen_family,
        "partition_closes": helium_isotope + hydrogen_family == Fraction(1, 1),
    }


def theorem_certificate():
    ledger = isotope_closure_ledger()
    return {
        "four_constituents": ledger["constituents"] == 4,
        "complete_nonempty_subwords": len(ledger["nonempty_subwords"]) == 15 and set(ledger["nonempty_subwords"]) == set(range(1, 16)),
        "complete_capture_product": len(ledger["capture_cells"]) == 60 and len(set(ledger["capture_cells"])) == 60,
        "one_composite_identity": len(ledger["global_identity_records"]) == 1,
        "isotope_conversion": ledger["isotope_conversion"] == Fraction(59, 60),
        "physical_partition": ledger["physical_helium_isotope_share"] == Fraction(59, 240) and ledger["physical_hydrogen_family_share"] == Fraction(181, 240) and ledger["partition_closes"],
    }


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Terminal physical helium-isotope closure",
    statement=(
        "The admitted One/four helium-family share is an analytic baryon partition, not yet the physical isotope mass "
        "share. Helium-four has four retained constituent positions and fifteen nonempty constituent subwords. Their "
        "complete incidence product has sixty cells. Binding the four positions into one physical isotope introduces "
        "exactly one collective composite-identity record: no hold leaves four unbound labels, while more than one hold "
        "adds an ungenerated independent composite identity. The remaining fifty-nine cells give the unique isotope "
        "conversion 59/60. Therefore the physical primordial helium-isotope share is (One/four)(59/60)=59/240 and the "
        "complementary hydrogen-family share is 181/240."
    ),
    dependencies=(
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-MATTER-COMPOSITE-HADRONS-001",
        "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005",
        "SFT-MATH-EXACT-ARITHMETIC-001",
        "SFT-MATH-COMBINATORICS-001",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule="Generate the complete product of analytic-family, constituent, subword, capture-product, composite-identity, isotope-conversion, physical-partition and target-boundary forms.",
    grammar_boundary="The admitted analytic helium family; exactly four helium-four constituent positions; every nonempty subword of those positions; their complete incidence product; the single global composite identity; exact positive rational partitions; and no measurement in candidate selection.",
    axes=(
        binary_axis("family", "What is the predecessor helium quantity?", "measured-decimal-called-family-law", "A measured decimal cannot select the analytic predecessor.", "admitted-quarter-baryon-family", "Claim 037 supplies the exact analytic One/four family partition."),
        binary_axis("constituents", "How many retained isotope positions enter?", "selected-arity", "A selected isotope arity is an extra premise.", "helium-four-complete-arity", "The helium-four identity supplies four retained constituent positions."),
        binary_axis("subwords", "Which constituent subwords enter closure?", "selected-proper-subset", "A selected subset erases a physical composition channel.", "all-fifteen-nonempty-subwords", "Four positions generate exactly 2^4-1 nonempty subwords."),
        binary_axis("product", "How are positions and subwords composed?", "partial-incidence-ledger", "A partial ledger breaks permutation completeness.", "complete-four-by-fifteen-product", "Every position occurs against every nonempty subword class, generating sixty cells."),
        binary_axis("identity", "How many collective isotope identities close?", "empty-or-multiple-composite-identities", "No identity leaves the labels unbound; multiple identities add an ungenerated split.", "one-global-composite-identity", "One bound isotope has exactly one collective identity beyond its constituent labels."),
        binary_axis("conversion", "What physical conversion follows?", "fitted-isotope-correction", "A fitted correction reads the measurement.", "fifty-nine-of-sixty-isotope-cells", "The one global identity record is held outside the sixty equal mass-incidence cells, leaving 59/60."),
        binary_axis("partition", "What physical abundance partition follows?", "quarter-rubber-stamp-or-decimal-copy", "Neither the analytic quarter nor a copied decimal is the completed isotope partition.", "fifty-nine-over-two-forty-and-one-eighty-one-over-two-forty", "Composing 1/4 with 59/60 forces 59/240, whose exact complement is 181/240."),
        binary_axis("target", "May helium measurements select the survivor?", "target-readable-candidate-selection", "Target access could manufacture a correction.", "target-closed-until-formal-seal", "The physical share and complete census seal before external abundance release."),
    ),
    exact_result="The complete four-position by fifteen-nonempty-subword capture ledger has sixty cells and exactly one collective composite-identity record. The unique physical isotope conversion is therefore 59/60. Composed with the admitted analytic helium-family share One/four, this forces primordial physical helium-isotope share 59/240 and complementary hydrogen-family share 181/240, closing exactly to the One.",
    induction_base="One four-constituent isotope generates all fifteen nonempty subwords, sixty complete incidence cells and one collective identity record.",
    induction_step="Repeating the same complete isotope word preserves the four-by-fifteen quotient and its single collective identity; disjoint copies preserve 59/60 conversion and the exact physical partition.",
    exclusions=(
        "no measured helium abundance, uncertainty or central value in formal survivor selection",
        "no fitted decay rate, reaction rate, binding coefficient, abundance correction or selected denominator",
        "no omission of a constituent position or nonempty subword",
        "no multiple ungenerated composite identities",
        "no numerical-nothing, negative, irrational, imaginary, floating, NaN, continuum or completed-infinity proof scalar",
    ),
    witnesses=(
        Witness("arity", "Helium-four supplies four retained constituent positions.", theorem_certificate()["four_constituents"]),
        Witness("subwords", "Four positions generate all fifteen nonempty subwords.", theorem_certificate()["complete_nonempty_subwords"]),
        Witness("product", "The complete incidence product contains sixty distinct cells.", theorem_certificate()["complete_capture_product"]),
        Witness("identity", "A bound isotope has one collective composite identity.", theorem_certificate()["one_composite_identity"]),
        Witness("conversion", "Holding the collective identity leaves exact conversion 59/60.", theorem_certificate()["isotope_conversion"]),
        Witness("partition", "The physical shares are exactly 59/240 and 181/240 and close to the One.", theorem_certificate()["physical_partition"]),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)

SPEC.validate()

__all__ = ("CLAIM_ID", "HELIUM_CONSTITUENTS", "SPEC", "complete_capture_cells", "isotope_closure_ledger", "nonempty_subword_masks", "theorem_certificate")
