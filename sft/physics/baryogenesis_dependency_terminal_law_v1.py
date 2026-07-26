"""Exact Fold dependency law for a retained baryon residue."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

from sft.engine import EvidenceMode, ProvenanceClass
from sft.physics.structural_constants import StructuralPhysicsSpec, Witness, binary_axis


CLAIM_ID = "SFT-PHYS-BARYOGENESIS-DEPENDENCY-TERMINAL-021"
ONE = Fraction(1, 1)
EMPTY_ONE = ("empty-One",)


@dataclass(frozen=True)
class ResidueRecord:
    orientation: str
    support: Fraction


def retained_baryon_residue(
    *,
    baryon_tally_changes: bool,
    conjugate_paths_distinguished: bool,
    reverse_completion_held: bool,
) -> ResidueRecord | tuple[str]:
    """Execute the complete minimal three-condition Fold process.

    The initial carrier contains one matter and one antimatter record.  A
    tally-changing act appends a positive carrier.  If conjugate paths remain
    paired, the same carrier is appended to both orientations.  If reverse
    completion is not held, every append is closed by its reverse act.  The
    result is structural emptiness unless all three distinctions are retained.
    """

    matter = [ONE]
    antimatter = [ONE]
    if baryon_tally_changes:
        matter.append(ONE)
        if not conjugate_paths_distinguished:
            antimatter.append(ONE)
    if not reverse_completion_held:
        matter = matter[:1]
        antimatter = antimatter[:1]
    matter_support = sum(matter, ONE) - ONE
    antimatter_support = sum(antimatter, ONE) - ONE
    if matter_support == antimatter_support:
        return EMPTY_ONE
    if matter_support > antimatter_support:
        return ResidueRecord("matter", matter_support - antimatter_support)
    return ResidueRecord("antimatter", antimatter_support - matter_support)


def complete_condition_census() -> tuple[dict[str, object], ...]:
    rows = []
    for tally, conjugacy, hold in product((False, True), repeat=3):
        residue = retained_baryon_residue(
            baryon_tally_changes=tally,
            conjugate_paths_distinguished=conjugacy,
            reverse_completion_held=hold,
        )
        rows.append(
            {
                "baryon_tally_changes": tally,
                "conjugate_paths_distinguished": conjugacy,
                "reverse_completion_held": hold,
                "residue": residue,
                "positive_residue": isinstance(residue, ResidueRecord),
            }
        )
    return tuple(rows)


def unique_positive_process() -> bool:
    rows = complete_condition_census()
    survivors = tuple(row for row in rows if row["positive_residue"])
    return len(survivors) == 1 and all(
        (
            survivors[0]["baryon_tally_changes"],
            survivors[0]["conjugate_paths_distinguished"],
            survivors[0]["reverse_completion_held"],
            survivors[0]["residue"] == ResidueRecord("matter", ONE),
        )
    )


SPEC = StructuralPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Fold baryogenesis dependency and retained-residue law",
    statement=(
        "Beginning from one exactly paired particle/antiparticle carrier, a "
        "positive retained baryon residue occurs in the complete minimal Fold "
        "process grammar if and only if three independently held distinctions "
        "co-occur: a transition changes the baryon tally, conjugate transition "
        "paths are distinguished by the admitted CP carrier, and reverse "
        "completion is held by a nonequilibrium process record.  Complete "
        "enumeration of all eight presence/absence combinations leaves exactly "
        "one residue-bearing process.  The already sealed terminal CKM and "
        "baryon-to-photon claims supply the post-derivation physical carrier and "
        "abundance comparison; they do not select this dependency law."
    ),
    dependencies=(
        "SFT-FOUNDATION-FOLD-DYNAMICS-001",
        "SFT-FOUNDATION-PART-EQUIVALENCE-001",
        "SFT-PHYS-MATTER-PARTICLE-ANTIPARTICLE-001",
        "SFT-PHYS-THERMO-IRREVERSIBILITY-001",
        "SFT-PHYS-MATTER-CKM-TERMINAL-004",
        "SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",
        "SFT-MATH-EXACT-ARITHMETIC-001",
    ),
    evidence_mode=EvidenceMode.FORMAL,
    generation_rule=(
        "Generate the complete product of initial carrier, baryon-tally action, "
        "conjugate-path relation, reverse-completion relation, residue ledger, "
        "dependency composition, enumeration, physical correspondence, "
        "provenance disclosure and extension forms."
    ),
    grammar_boundary=(
        "Every finite minimal process beginning from one positive paired "
        "particle/antiparticle carrier, with each of baryon-tally change, "
        "conjugate-path distinction and reverse-completion hold either present "
        "or absent, plus the already admitted terminal CP and baryon-abundance "
        "comparison records."
    ),
    axes=(
        binary_axis("carrier", "What is the initial matter carrier?", "preloaded-unpaired-residue", "A preloaded residue assumes the result.", "exact-paired-particle-antiparticle-carrier", "One positive carrier in each held orientation supplies no initial residue."),
        binary_axis("tally", "May the baryon tally change?", "every-transition-preserves-baryon-tally", "A preserving transition cannot create a tally difference from paired support.", "one-explicit-tally-changing-transition", "A positive appended carrier makes a residue logically possible without importing its measured size."),
        binary_axis("conjugacy", "How are conjugate paths related?", "exactly-paired-conjugate-paths", "Equal conjugate appends preserve the paired tally.", "CP-carrier-distinguishes-conjugate-paths", "The admitted CP carrier retains one transition orientation from its conjugate."),
        binary_axis("reverse", "Does the reverse process complete?", "complete-reverse-recurrence", "Complete reversal closes every newly appended carrier.", "nonequilibrium-reverse-completion-held", "A retained process orientation prevents exact reverse cancellation of the new distinction."),
        binary_axis("ledger", "How is the result recorded?", "signed-or-unrecorded-net-number", "A signed or missing ledger violates positive exact accounting.", "positive-oriented-residue-or-empty-One", "Equal sides return structural emptiness; an ordered difference is retained as one positive oriented carrier."),
        binary_axis("composition", "How are the three requirements related?", "named-independent-conditions", "Names alone do not prove their joint necessity.", "single-three-condition-process-composition", "The complete process trace tests every condition jointly from the same paired source."),
        binary_axis("enumeration", "How is necessity established?", "selected-successful-combination", "Selecting the familiar triple is not uniqueness.", "all-eight-presence-absence-combinations", "The complete Boolean product proves that exactly one combination retains a residue."),
        binary_axis("comparison", "How does physical abundance enter?", "abundance-selects-dependency-law", "A measured abundance cannot choose the formal conditions.", "inherit-sealed-CKM-and-baryon-photon-records", "The physical CP carrier and abundance test were admitted separately and enter only as downstream correspondence."),
        binary_axis("provenance", "How is the known historical target disclosed?", "mislabel-as-blind-discovery", "The dependency triple was known before this V3 reconstruction.", "observational-reconstruction-explicit", "The law is an independently executed reconstruction, not a claim of blind historical discovery."),
        binary_axis("extension", "May an efficiency or extra mechanism be inserted?", "free-efficiency-or-extra-condition", "An inserted efficiency or condition is a free parameter.", "no-extra-rule", "The minimal complete process grammar is exhausted by the three distinctions and retained ledger."),
    ),
    exact_result=(
        "From exact paired particle/antiparticle support, a positive retained "
        "baryon residue exists exactly when baryon tally change, CP-distinguished "
        "conjugate paths and a nonequilibrium reverse-completion hold are all "
        "present; the other seven complete combinations return the empty-One "
        "residue record."
    ),
    induction_base=(
        "One matter and one antimatter carrier form an exact paired source with "
        "an empty-One residue record."
    ),
    induction_step=(
        "A tally-changing append creates one possible difference; conjugate "
        "pairing duplicates it on the opposite orientation and closes it, while "
        "reverse completion removes every unmatched append.  Therefore an append "
        "survives exactly when conjugacy and reversal are both held."
    ),
    exclusions=(
        "no imported Sakharov theorem or conventional kinetic equation as a premise",
        "no V1/V2 executable, result table, measurement or stored survivor",
        "no numerical-zero, negative, irrational, imaginary or floating proof magnitude",
        "no measured baryon abundance, fitted efficiency or selected mechanism in the derivation",
        "no claim that the V3 reconstruction was a blind historical discovery",
        "no cosmic-history claim beyond the universal physical dependency law",
    ),
    witnesses=(
        Witness("complete-eight-case-census", "Every presence/absence combination is generated once.", len(complete_condition_census()) == 8 and len({(row["baryon_tally_changes"], row["conjugate_paths_distinguished"], row["reverse_completion_held"]) for row in complete_condition_census()}) == 8),
        Witness("unique-positive-residue", "Exactly the three-condition process retains a positive matter-oriented One residue.", unique_positive_process()),
        Witness("all-omissions-close", "Removing any one required distinction returns the empty-One residue.", all(retained_baryon_residue(baryon_tally_changes=tally, conjugate_paths_distinguished=cp, reverse_completion_held=hold) == EMPTY_ONE for tally, cp, hold in ((False, True, True), (True, False, True), (True, True, False)))),
    ),
    provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EMPTY_ONE",
    "ResidueRecord",
    "SPEC",
    "complete_condition_census",
    "retained_baryon_residue",
    "unique_positive_process",
)
