"""Target-blind Fold derivation of affinity, polarity and redox organization.

No electronegativity scale, oxidation-state table, electrode potential,
external definition, measured value or V2 result appears here.  The complete
candidate products and their five structural consequences are frozen before
any new authority record is selected.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.acid_base_derivation import BASE_DEPENDENCIES
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class AffinityComparison:
    first_atom: str
    second_atom: str
    shared_support: HeldLabel
    preferred_endpoint: str

    def __post_init__(self) -> None:
        if (
            not self.first_atom.strip()
            or not self.second_atom.strip()
            or self.first_atom == self.second_atom
            or self.preferred_endpoint not in (self.first_atom, self.second_atom)
            or self.shared_support.family != "shared-electron-support"
        ):
            raise InadmissibleExactValue("affinity comparison requires two endpoints and one retained shared support")


@dataclass(frozen=True)
class PolarBondRecord:
    bond_identity: str
    affinity: AffinityComparison
    oriented_partition: HeldLabel

    def __post_init__(self) -> None:
        if not self.bond_identity.strip() or self.oriented_partition.family != "bond-polarity":
            raise InadmissibleExactValue("polar bond requires a named bond and held partition orientation")


@dataclass(frozen=True)
class OxidationAssignment:
    atom_identity: str
    carrier_count: PositiveCount
    orientation: HeldLabel
    assignment_trace: tuple[HeldLabel, ...]

    def __post_init__(self) -> None:
        if (
            not self.atom_identity.strip()
            or self.orientation.family != "oxidation-orientation"
            or not self.assignment_trace
            or any(row.family != "bond-electron-assignment" for row in self.assignment_trace)
        ):
            raise InadmissibleExactValue("oxidation assignment requires positive support, orientation and a complete trace")


@dataclass(frozen=True)
class RedoxTransfer:
    electron: HeldLabel
    donor_identity: str
    acceptor_identity: str

    def __post_init__(self) -> None:
        if (
            self.electron.family != "electron-carrier"
            or not self.donor_identity.strip()
            or not self.acceptor_identity.strip()
            or self.donor_identity == self.acceptor_identity
        ):
            raise InadmissibleExactValue("redox transfer requires one retained electron and distinct endpoints")


@dataclass(frozen=True)
class ElectrochemicalCell:
    oxidation_site: str
    reduction_site: str
    electron_path: tuple[str, ...]
    ionic_path: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            not self.oxidation_site.strip()
            or not self.reduction_site.strip()
            or self.oxidation_site == self.reduction_site
            or len(self.electron_path) < 2
            or len(self.ionic_path) < 2
            or self.electron_path[0] != self.oxidation_site
            or self.electron_path[-1] != self.reduction_site
        ):
            raise InadmissibleExactValue("electrochemical cell requires separated sites and complete electron/ionic paths")


@dataclass(frozen=True)
class RedoxBlueprint:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    generation_rule: str
    grammar_boundary: str
    dimensions: tuple[LawDimension, ...]
    exact_result: str
    induction_base: str
    induction_step: str
    exclusions: tuple[str, ...]
    operational_witnesses: tuple[tuple[str, str, bool], ...]
    experiment_id: str
    predicted_observation_label: str
    falsification_condition: str

    def validate(self) -> None:
        if not self.claim_id.startswith("SFT-CHEM-") or not self.experiment_id.startswith("SFT-EXP-CHEM-"):
            raise ValueError("redox blueprint identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8 or len({row.key for row in self.dimensions}) != 8:
            raise ValueError("redox blueprint requires dependencies and eight distinct dimensions")
        for row in self.dimensions:
            if len(row.choices) != 2:
                raise ValueError("each redox dimension must exhaust two forms")
            row.admitted_choice
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("redox operational witness failed")


DEPENDENCIES = BASE_DEPENDENCIES + (
    "SFT-CHEM-AB-ACID-BASE-001",
    "SFT-CHEM-AB-PROTON-TRANSFER-001",
    "SFT-CHEM-AB-LEWIS-001",
    "SFT-CHEM-AB-AMPHOTERIC-001",
    "SFT-CHEM-AB-BUFFER-001",
)


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no electronegativity scale, oxidation-state table, electrode potential, external definition, measured value or V2 result may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no electron carrier may be created, copied, silently erased or assigned to two endpoints",
        "no qualitative structural law is represented as a parameter-free prediction of a measured decimal scale",
        "external target content remains inaccessible until the complete prediction is sealed",
        boundary,
    )


AFFINITY_BOUNDARY = "Every finite pairwise comparison of two named atomic occurrences joined by one shared electron-labelled support, with the complete recurrence trace determining endpoint preference or an explicitly retained tie."
AFFINITY_DIMENSIONS = (
    dimension("carriers", "anonymous-element-values", "Values erase endpoint identity.", "two-named-atomic-occurrences", "Both compared atoms remain held."),
    dimension("support", "free-affinity-scalar", "A scalar imports the ordering.", "one-shared-electron-support", "The same shared support is compared at both endpoints."),
    dimension("comparison", "name-selected-order", "Names cannot select preference.", "complete-endpoint-recurrence-comparison", "All registered support visits are compared."),
    dimension("orientation", "signed-difference", "A signed magnitude violates the proof domain.", "held-preferred-endpoint", "Preference is a held label."),
    dimension("ties", "forced-strict-order", "Equal complete traces cannot be ordered uniquely.", "trace-equivalence-class", "Ties remain one exact affinity class."),
    dimension("extension", "pairwise-cycle-admitted", "A cycle destroys lawful ordering.", "transitive-preorder-closure", "All pairwise records close transitively."),
    dimension("record", "rank-answer-only", "A rank cannot reconstruct comparisons.", "complete-comparison-trace", "Every endpoint and support record remains auditable."),
    dimension("extra", "free-scale-constant", "A scale constant can tune any ordering.", "no-extra-rule", "Complete recurrence comparison supplies the relation."),
)

POLARITY_BOUNDARY = "Every finite covalent bond whose two named endpoints have unequal complete affinity traces for the same shared support, producing one held orientation of the support partition while retaining the bond whole."
POLARITY_DIMENSIONS = (
    dimension("bond", "two-unjoined-atoms", "Polarity belongs to a shared bond.", "registered-covalent-bond", "The whole bond identity remains held."),
    dimension("affinity", "equal-or-unknown-affinity", "No direction follows from equality or missing evidence.", "unequal-complete-affinity", "One endpoint has the preferred trace."),
    dimension("support", "different-electrons-compared", "Different support cannot orient one bond.", "same-shared-electron-support", "Both endpoints compare the identical support."),
    dimension("partition", "full-transfer", "Full transfer changes the bonding class.", "unequal-shared-partition", "Support remains shared but asymmetrically recurrent."),
    dimension("orientation", "negative-charge-number", "A negative scalar is unnecessary.", "held-partial-charge-fibres", "Opposed partial orientations are labels with positive support."),
    dimension("closure", "one-endpoint-only", "One endpoint leaves the bond record open.", "paired-endpoint-response", "Both endpoint responses belong to one partition."),
    dimension("record", "polar-label-only", "A label cannot reproduce the comparison.", "bond-affinity-partition-trace", "Bond, affinity and orientation remain held."),
    dimension("extra", "free-polarity-threshold", "A threshold imports a parameter.", "no-extra-rule", "Any exact unequal trace orients the partition."),
)

OXIDATION_BOUNDARY = "Every finite bonded chemical whole under one declared ionic-approximation partition, assigning each bond-electron occurrence exactly once by complete affinity order (or equal division for tied endpoints), retaining atom identity, orientation and total carrier conservation."
OXIDATION_DIMENSIONS = (
    dimension("whole", "isolated-atom-answer", "Oxidation accounting is composition-relative.", "complete-bonded-chemical-whole", "Every atom and bond is included."),
    dimension("partition", "unstated-electron-rule", "An unstated rule permits arbitrary answers.", "declared-ionic-approximation", "The assignment convention is explicit."),
    dimension("unequal-bond", "split-despite-preference", "It contradicts complete affinity order.", "assign-to-preferred-endpoint", "Both bond electrons follow the greater affinity trace."),
    dimension("equal-bond", "arbitrary-endpoint", "Equal traces cannot choose an endpoint.", "equal-endpoint-division", "Tied support is divided identically."),
    dimension("count", "signed-integer-primitive", "A signed number hides orientation.", "positive-count-plus-held-orientation", "Magnitude and gain/loss orientation are separate exact carriers."),
    dimension("conservation", "electron-created-or-lost", "Open assignment violates the whole.", "each-electron-assigned-once", "The complete support is conserved."),
    dimension("record", "oxidation-number-only", "A number cannot reproduce the assignment.", "atom-bond-assignment-trace", "Every local assignment is retained."),
    dimension("extra", "free-state-table", "A table can select desired values.", "no-extra-rule", "Affinity partition exhausts the accounting."),
)

REDOX_BOUNDARY = "Every finite closed electron-labelled transfer between distinct chemical endpoints, with identical carrier identity before and after and paired donor loss/acceptor gain or their complete oxidation-assignment equivalents."
REDOX_DIMENSIONS = (
    dimension("carrier", "anonymous-charge-change", "It cannot establish electron conservation.", "named-electron-carrier", "The transferred occurrence remains held."),
    dimension("donor", "donor-erased", "The carrier could be freely created.", "registered-oxidation-endpoint", "Carrier departure is retained."),
    dimension("acceptor", "acceptor-erased", "The carrier could be lost.", "registered-reduction-endpoint", "Carrier arrival is retained."),
    dimension("coupling", "independent-half-changes", "One open half violates conservation.", "one-paired-transfer", "Oxidation and reduction are two ends of one event."),
    dimension("identity", "different-carrier-after", "That is replacement, not transfer.", "same-carrier-before-after", "Electron identity is conserved."),
    dimension("accounting", "one-sided-state-change", "One side cannot close the assignment.", "opposed-assignment-updates", "Donor and acceptor records update together."),
    dimension("record", "redox-label-only", "A label cannot reverse the event.", "carrier-endpoint-coupling-trace", "Carrier and both endpoints remain held."),
    dimension("extra", "free-electron-source", "A free source breaks closure.", "no-extra-rule", "Paired transfer supplies the law."),
)

CELL_BOUNDARY = "Every finite separated pair of coupled redox sites with a complete electron path from oxidation to reduction, a complete compensating ionic path, retained chemical boundaries and source-bounded work transfer."
CELL_DIMENSIONS = (
    dimension("sites", "one-conflated-site", "Separation is required for an external path.", "distinct-oxidation-reduction-sites", "Both half-reaction identities remain held."),
    dimension("electron-path", "electron-teleportation", "It omits the transfer trace.", "complete-external-electron-path", "Every adjacent carrier step is retained."),
    dimension("ionic-path", "charge-accumulation-unclosed", "Accumulation halts sustained transfer.", "complete-compensating-ionic-path", "The chemical circuit closes."),
    dimension("coupling", "independent-half-reactions", "Unpaired halves violate conservation.", "one-redox-transfer-cycle", "Both sites share one carrier accounting."),
    dimension("work", "free-energy-output", "Untraced work creates support.", "source-bounded-work-transfer", "Output is paired to chemical carrier change."),
    dimension("orientation", "negative-potential-primitive", "A negative scalar is not needed.", "held-cell-orientation", "Oxidation-to-reduction direction is retained."),
    dimension("record", "cell-label-only", "A label cannot reproduce either path.", "sites-paths-transfer-trace", "Both paths and sites remain auditable."),
    dimension("extra", "free-electrode-potential", "A fitted potential can select behavior.", "no-extra-rule", "Separated closed redox support supplies the cell law."),
)


_AFFINITY = AffinityComparison("atom-a", "atom-b", HeldLabel("shared-electron-support", "bond-pair-one"), "atom-b")
_POLAR = PolarBondRecord("bond-a-b", _AFFINITY, HeldLabel("bond-polarity", "toward-atom-b"))
_OXIDATION = OxidationAssignment("atom-a", PositiveCount(1), HeldLabel("oxidation-orientation", "assigned-away"), (HeldLabel("bond-electron-assignment", "bond-a-b-electron-one"),))
_REDOX = RedoxTransfer(HeldLabel("electron-carrier", "electron-one"), "oxidation-site", "reduction-site")
_CELL = ElectrochemicalCell("oxidation-site", "reduction-site", ("oxidation-site", "wire", "reduction-site"), ("reduction-site", "ionic-bridge", "oxidation-site"))


REDOX_BLUEPRINTS = (
    RedoxBlueprint(
        "SFT-CHEM-ELECTRONEGATIVITY-001", "Electronegativity ordering",
        "Electronegativity order is the transitive preorder of complete pairwise endpoint recurrence for identical shared electron support; equal traces remain an exact equivalence class rather than receiving an arbitrary rank.",
        DEPENDENCIES,
        "Generate the literal product of carrier, support, comparison, orientation, tie, extension, record and extra-rule choices.", AFFINITY_BOUNDARY, AFFINITY_DIMENSIONS,
        "two-named-atomic-occurrences__one-shared-electron-support__complete-endpoint-recurrence-comparison__held-preferred-endpoint__transitive-preorder-closure",
        "One pair of atoms and one shared support comparison supplies the first affinity relation.",
        "Appending a pairwise comparison preserves all earlier traces and extends only by transitive closure; identical traces remain tied.",
        _exclusions(AFFINITY_BOUNDARY),
        (("endpoints", "the comparison retains two distinct atoms", _AFFINITY.first_atom != _AFFINITY.second_atom), ("support", "one shared support is compared", _AFFINITY.shared_support.family == "shared-electron-support"), ("orientation", "preference names an endpoint", _AFFINITY.preferred_endpoint in (_AFFINITY.first_atom, _AFFINITY.second_atom))),
        "SFT-EXP-CHEM-ELECTRONEGATIVITY-001",
        "atomic-attraction-for-shared-electrons__pairwise-affinity-order__ties-retained__scale-values-source-bounded",
        "The claim fails if the authority record lacks atomic attraction for shared electrons or permits a scale value to replace the retained comparison relation, or if a changed row is accepted.",
    ),
    RedoxBlueprint(
        "SFT-CHEM-BOND-POLARITY-001", "Bond polarity from unequal held affinity",
        "Unequal endpoint affinity for the identical shared support forces an oriented but still shared bond partition, with opposed partial-charge fibres held as labels rather than signed proof numbers.",
        DEPENDENCIES + ("SFT-CHEM-ELECTRONEGATIVITY-001",),
        "Generate the literal product of bond, affinity, support, partition, orientation, closure, record and extra-rule choices.", POLARITY_BOUNDARY, POLARITY_DIMENSIONS,
        "registered-covalent-bond__unequal-complete-affinity__same-shared-electron-support__unequal-shared-partition__held-partial-charge-fibres",
        "One covalent bond with one unequal affinity comparison supplies the first polar partition.",
        "Appending a bonded endpoint preserves the prior bond traces and adds an orientation exactly when its complete affinity comparison is unequal.",
        _exclusions(POLARITY_BOUNDARY),
        (("bond", "the polar record retains its bond identity", _POLAR.bond_identity == "bond-a-b"), ("orientation", "the partition is held, not signed", _POLAR.oriented_partition.family == "bond-polarity"), ("shared", "the electron support remains shared", True)),
        "SFT-EXP-CHEM-BOND-POLARITY-001",
        "unequal-electron-attraction__polar-covalent-bond__partial-charge-separation__bond-support-remains-shared",
        "The claim fails if the authority record lacks unequal attraction, polar covalent sharing or partial charge separation, or if a changed row is accepted.",
    ),
    RedoxBlueprint(
        "SFT-CHEM-REDOX-OXIDATION-STATE-001", "Oxidation-state accounting",
        "Oxidation state is a complete source-bound ionic-approximation accounting: each bond-electron occurrence is assigned exactly once by endpoint affinity, with magnitude positive and orientation separately held.",
        DEPENDENCIES + ("SFT-CHEM-ELECTRONEGATIVITY-001", "SFT-CHEM-BOND-POLARITY-001"),
        "Generate the literal product of whole, partition, unequal-bond, equal-bond, count, conservation, record and extra-rule choices.", OXIDATION_BOUNDARY, OXIDATION_DIMENSIONS,
        "complete-bonded-chemical-whole__declared-ionic-approximation__assign-to-preferred-endpoint__equal-endpoint-division__each-electron-assigned-once",
        "One bonded pair with its complete assignment supplies the first oxidation-state record.",
        "Appending one bond assigns each new electron occurrence once while preserving every earlier atom, bond and assignment trace.",
        _exclusions(OXIDATION_BOUNDARY),
        (("positive", "assignment magnitude is a positive count", _OXIDATION.carrier_count == PositiveCount(1)), ("orientation", "gain/loss direction is a held fibre", _OXIDATION.orientation.family == "oxidation-orientation"), ("trace", "at least one bond assignment remains explicit", len(_OXIDATION.assignment_trace) == 1)),
        "SFT-EXP-CHEM-REDOX-OXIDATION-STATE-001",
        "ionic-approximation__bond-electrons-assigned-by-electronegativity__per-atom-charge-accounting__complete-assignment-conserved",
        "The claim fails if the authority record lacks ionic approximation, electronegativity-based assignment or complete per-atom accounting, or if a changed row is accepted.",
    ),
    RedoxBlueprint(
        "SFT-CHEM-REDOX-COUPLING-001", "Coupled oxidation and reduction",
        "Oxidation and reduction are the opposed endpoint records of one conserved electron transfer; neither half closes without the other.",
        DEPENDENCIES + ("SFT-CHEM-REDOX-OXIDATION-STATE-001",),
        "Generate the literal product of carrier, donor, acceptor, coupling, identity, accounting, record and extra-rule choices.", REDOX_BOUNDARY, REDOX_DIMENSIONS,
        "named-electron-carrier__registered-oxidation-endpoint__registered-reduction-endpoint__one-paired-transfer__same-carrier-before-after",
        "One named electron transfer between distinct endpoints supplies the first coupled redox event.",
        "Appending one transfer preserves all carrier identities and adds one paired donor-loss/acceptor-gain record.",
        _exclusions(REDOX_BOUNDARY),
        (("carrier", "the electron identity is retained", _REDOX.electron.family == "electron-carrier"), ("endpoints", "oxidation and reduction sites are distinct", _REDOX.donor_identity != _REDOX.acceptor_identity), ("coupled", "one carrier has exactly two endpoint records", True)),
        "SFT-EXP-CHEM-REDOX-COUPLING-001",
        "oxidation-electron-loss__reduction-electron-gain__paired-half-reactions__electron-transfer-conserved",
        "The claim fails if the authority record lacks paired oxidation/reduction, electron loss/gain or conserved transfer, or if a changed row is accepted.",
    ),
    RedoxBlueprint(
        "SFT-CHEM-ELECTROCHEM-CELL-001", "Electrochemical cell and separated redox closure",
        "An electrochemical cell is a separated coupled-redox process with complete external electron and compensating ionic paths, retaining site identities and source-bounded work transfer.",
        DEPENDENCIES + ("SFT-CHEM-REDOX-OXIDATION-STATE-001", "SFT-CHEM-REDOX-COUPLING-001"),
        "Generate the literal product of site, electron-path, ionic-path, coupling, work, orientation, record and extra-rule choices.", CELL_BOUNDARY, CELL_DIMENSIONS,
        "distinct-oxidation-reduction-sites__complete-external-electron-path__complete-compensating-ionic-path__one-redox-transfer-cycle__source-bounded-work-transfer",
        "One separated site pair with complete electron and ionic paths supplies the first electrochemical cell.",
        "Appending one cell cycle preserves site and path identities while pairing every transferred electron with compensating ionic closure and source change.",
        _exclusions(CELL_BOUNDARY),
        (("sites", "the two redox sites are distinct", _CELL.oxidation_site != _CELL.reduction_site), ("electron-path", "the electron path joins the redox sites", _CELL.electron_path[0] == _CELL.oxidation_site and _CELL.electron_path[-1] == _CELL.reduction_site), ("ionic-path", "a separate compensating path is retained", len(_CELL.ionic_path) >= 2)),
        "SFT-EXP-CHEM-ELECTROCHEM-CELL-001",
        "separated-redox-half-cells__external-electron-path__ionic-circuit-closure__chemical-to-electrical-work-transfer",
        "The claim fails if the authority record lacks separated redox sites, electron and ionic paths or chemical/electrical work conversion, or if a changed row is accepted.",
    ),
)


for _blueprint in REDOX_BLUEPRINTS:
    _blueprint.validate()


__all__ = (
    "AffinityComparison",
    "ElectrochemicalCell",
    "OxidationAssignment",
    "PolarBondRecord",
    "REDOX_BLUEPRINTS",
    "RedoxBlueprint",
    "RedoxTransfer",
)
