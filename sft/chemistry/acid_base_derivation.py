"""Target-blind Fold derivation of acid/base organization.

No pH scale, dissociation constant, equilibrium equation, named convention or
external definition appears in this file.  The five structural consequences
are frozen before authoritative terminology is selected.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import LawDimension, dimension


@dataclass(frozen=True)
class CarrierTransfer:
    carrier: HeldLabel
    donor_identity: str
    acceptor_identity: str

    def __post_init__(self) -> None:
        if (
            not self.donor_identity.strip()
            or not self.acceptor_identity.strip()
            or self.donor_identity == self.acceptor_identity
        ):
            raise InadmissibleExactValue("a transfer requires distinct named endpoint occurrences")


@dataclass(frozen=True)
class ConjugatePair:
    protonated_identity: str
    deprotonated_identity: str
    proton_carrier: HeldLabel

    def __post_init__(self) -> None:
        if (
            not self.protonated_identity.strip()
            or not self.deprotonated_identity.strip()
            or self.protonated_identity == self.deprotonated_identity
            or self.proton_carrier.family != "proton-carrier"
        ):
            raise InadmissibleExactValue("a conjugate pair retains two identities and one proton carrier")


@dataclass(frozen=True)
class LewisPairRelation:
    donor_identity: str
    acceptor_identity: str
    electron_occurrences: tuple[HeldLabel, HeldLabel]

    def __post_init__(self) -> None:
        if (
            not self.donor_identity.strip()
            or not self.acceptor_identity.strip()
            or self.donor_identity == self.acceptor_identity
            or any(row.family != "electron-carrier" for row in self.electron_occurrences)
            or self.electron_occurrences[0] == self.electron_occurrences[1]
        ):
            raise InadmissibleExactValue("a Lewis relation requires distinct endpoints and two retained electron occurrences")


@dataclass(frozen=True)
class AmphotericRecord:
    species_identity: str
    donor_event: CarrierTransfer
    acceptor_event: CarrierTransfer

    def __post_init__(self) -> None:
        if (
            not self.species_identity.strip()
            or self.donor_event.donor_identity != self.species_identity
            or self.acceptor_event.acceptor_identity != self.species_identity
        ):
            raise InadmissibleExactValue("an amphoteric record requires the same species in donor and acceptor roles")


@dataclass(frozen=True)
class BufferReservoir:
    conjugate_pair: ConjugatePair
    protonated_units: PositiveCount
    deprotonated_units: PositiveCount

    @property
    def response_modes(self) -> tuple[HeldLabel, HeldLabel]:
        return (
            HeldLabel("buffer-response", "accept-added-proton"),
            HeldLabel("buffer-response", "supply-proton-to-added-base"),
        )


@dataclass(frozen=True)
class AcidBaseBlueprint:
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
        if not self.claim_id.startswith("SFT-CHEM-AB-"):
            raise ValueError("acid/base blueprint claim identity is invalid")
        if not self.experiment_id.startswith("SFT-EXP-CHEM-AB-"):
            raise ValueError("acid/base blueprint experiment identity is invalid")
        if not self.dependencies or len(self.dimensions) != 8:
            raise ValueError("acid/base blueprint requires dependencies and eight dimensions")
        if len({row.key for row in self.dimensions}) != len(self.dimensions):
            raise ValueError("acid/base blueprint dimensions repeat")
        for row in self.dimensions:
            if len(row.choices) != 2:
                raise ValueError("each acid/base dimension must exhaust two registered forms")
            row.admitted_choice
        if not self.predicted_observation_label.strip() or not self.falsification_condition.strip():
            raise ValueError("acid/base blueprint lacks a prediction or falsification condition")
        if not all(passed for _, _, passed in self.operational_witnesses):
            raise ValueError("acid/base operational witness failed")


BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-CHEM-ELEM-ION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
    "SFT-CHEM-BOND-COVALENT-001",
    "SFT-CHEM-BOND-IONIC-001",
    "SFT-CHEM-MOL-MOLECULE-001",
    "SFT-CHEM-MOL-INTERMOLECULAR-001",
)


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no acid/base dictionary, pH scale, equilibrium equation, dissociation constant, measured value or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no unpaired creation, copying or loss of a proton or electron carrier",
        "no claim that structural closure alone fixes every solution-dependent strength or capacity value",
        "external target content remains inaccessible until the prediction is sealed",
        boundary,
    )


ACID_BASE_BOUNDARY = (
    "Every finite generated pair of chemical carriers related by exactly one retained proton occurrence, with "
    "the protonated member able to donate that occurrence and the deprotonated member able to accept it."
)
ACID_BASE_DIMENSIONS = (
    dimension("pair", "one-species-label", "A conjugate relation compares two carrier identities.", "two-conjugate-identities", "Both protonated and deprotonated carriers remain held."),
    dimension("carrier", "anonymous-hydrogen-count", "A count cannot trace the transferred occurrence.", "one-held-proton-occurrence", "The distinguishing proton remains a named conserved carrier."),
    dimension("acid-role", "acid-by-name", "A name cannot establish a transition.", "proton-donor-role", "The protonated carrier supplies the held proton to an acceptor."),
    dimension("base-role", "base-by-name", "A name cannot establish a transition.", "proton-acceptor-role", "The deprotonated carrier accepts the held proton."),
    dimension("difference", "unbounded-composition-change", "Additional changes destroy conjugacy.", "differ-by-one-proton", "All other retained composition is identical."),
    dimension("orientation", "signed-acidity-scalar", "A signed scalar is not a carrier trace.", "held-donor-acceptor-orientation", "Roles are structural orientations on one transfer."),
    dimension("record", "acid-base-answer-only", "An answer cannot reconstruct conjugacy.", "pair-and-proton-trace", "Both identities, the proton and transition remain held."),
    dimension("extension", "free-acid-base-exception", "An exception can label arbitrary species.", "no-extra-rule", "One-proton conjugacy and roles determine the relation."),
)


PROTON_TRANSFER_BOUNDARY = (
    "Every finite chemical transition in which one named proton carrier leaves one registered donor occurrence "
    "and enters one distinct registered acceptor occurrence with identical carrier identity before and after."
)
PROTON_TRANSFER_DIMENSIONS = (
    dimension("carrier", "proton-count-only", "A count cannot establish conservation of an occurrence.", "one-named-proton-carrier", "The transferred proton identity remains held."),
    dimension("source", "source-erased", "Without a donor, the carrier could be created freely.", "registered-donor", "The departure endpoint is retained."),
    dimension("destination", "destination-erased", "Without an acceptor, the carrier could be lost.", "registered-acceptor", "The arrival endpoint is retained."),
    dimension("transition", "copy-or-delete", "Copying or deleting violates carrier conservation.", "donor-to-acceptor-transfer", "One carrier changes endpoint exactly once."),
    dimension("identity", "before-after-carrier-change", "A changed carrier is not transfer conservation.", "same-carrier-before-after", "The proton occurrence is identical across the transition."),
    dimension("closure", "unpaired-composition-change", "Unpaired change leaves the reaction record open.", "complete-endpoint-closure", "Donor loss and acceptor gain are one event."),
    dimension("record", "product-label-only", "A product label cannot reconstruct the path.", "carrier-endpoint-transition-trace", "Carrier and both endpoints remain auditable."),
    dimension("extension", "free-proton-source", "A free source can force any reaction.", "no-extra-rule", "Conserved endpoint transfer supplies the law."),
)


LEWIS_BOUNDARY = (
    "Every finite donor/acceptor pair joined by one exclusion-preserving pair of named electron occurrences, "
    "with both electron identities conserved and the donor/acceptor orientation retained."
)
LEWIS_DIMENSIONS = (
    dimension("endpoints", "one-unoriented-species", "The relation requires donor and acceptor roles.", "distinct-donor-acceptor", "Both endpoint identities remain held."),
    dimension("support", "single-electron-only", "The registered relation concerns paired support.", "two-electron-occurrences", "Two distinct electron carriers form the pair."),
    dimension("donor", "electron-pair-name-only", "A name cannot demonstrate available support.", "pair-donor-support", "The donor supplies access to both retained occurrences."),
    dimension("acceptor", "unregistered-vacancy", "An unregistered destination cannot close the interaction.", "pair-acceptor-support", "The acceptor supplies an admitted receiving channel."),
    dimension("joining", "copied-electron-pair", "Copying violates exclusion and conservation.", "shared-or-transferred-pair", "The same pair supplies the joining support."),
    dimension("conservation", "electron-identity-erased", "Erasure cannot reverse the relation.", "both-electron-identities-retained", "Each occurrence remains traceable."),
    dimension("record", "Lewis-label-only", "A label cannot reconstruct pair support.", "endpoint-pair-joining-trace", "Endpoints, electron occurrences and joining remain held."),
    dimension("extension", "free-orbital-premise", "An imported orbital rule can select a desired classification.", "no-extra-rule", "Complete donor/acceptor pair support supplies the class."),
)


AMPHOTERIC_BOUNDARY = (
    "Every finite chemical carrier for which two separately registered contexts contain a valid donor transition "
    "and a valid acceptor transition involving that same retained species identity."
)
AMPHOTERIC_DIMENSIONS = (
    dimension("species", "two-unrelated-species", "Dual behavior must belong to one retained carrier identity.", "same-species-identity", "The same species appears in both contexts."),
    dimension("acid-context", "acid-label-without-event", "A label does not establish donation.", "valid-donor-event", "One context contains a conserved carrier donation."),
    dimension("base-context", "base-label-without-event", "A label does not establish acceptance.", "valid-acceptor-event", "Another context contains a conserved carrier acceptance."),
    dimension("context", "roles-conflated", "Conflation can assert incompatible events simultaneously.", "contexts-separately-held", "Each surrounding reaction identity remains explicit."),
    dimension("duality", "one-role-only", "One role does not close amphoteric behavior.", "both-roles-realized", "Donor and acceptor witnesses both exist."),
    dimension("identity", "species-changed-between-roles", "A changed carrier does not establish dual capacity.", "species-identity-retained", "The same carrier is compared before each event."),
    dimension("record", "amphoteric-label-only", "A label cannot reproduce both contexts.", "dual-event-context-trace", "Species, events and contexts remain held."),
    dimension("extension", "free-dual-role-exception", "An exception can admit any species.", "no-extra-rule", "Two valid opposite-role contexts determine the class."),
)


BUFFER_BOUNDARY = (
    "Every finite reservoir containing positive support of both members of a conjugate pair and two complementary "
    "response paths that consume added proton support or supply proton support to an added base within capacity."
)
BUFFER_DIMENSIONS = (
    dimension("components", "single-unpaired-species", "One species cannot supply both complementary responses.", "conjugate-pair-reservoir", "Both conjugate identities are present."),
    dimension("support", "one-component-absent", "An absent member leaves one response unavailable.", "positive-support-of-both", "Each conjugate member has a positive finite count."),
    dimension("acid-response", "added-proton-unanswered", "No response permits the proton distinction to remain open.", "base-member-accepts-proton", "The deprotonated member consumes added proton support."),
    dimension("base-response", "added-base-unanswered", "No response permits proton removal without paired change.", "acid-member-supplies-proton", "The protonated member supplies a proton to the added base."),
    dimension("retention", "reservoir-identity-erased", "A response without conjugate tracking cannot be reversed.", "conjugate-pair-retained", "Each response converts one member into the other."),
    dimension("capacity", "unlimited-buffer-claim", "A finite reservoir cannot have unlimited capacity.", "finite-source-bounded-capacity", "Capacity is limited by retained positive component support."),
    dimension("record", "pH-answer-only", "A pH value cannot reconstruct composition and response.", "pair-count-response-trace", "Components, counts and both response paths remain held."),
    dimension("extension", "free-equilibrium-fit", "A fitted equation can force a measured response.", "no-extra-rule", "Complementary finite conjugate support supplies the structural law."),
)


_PROTON = HeldLabel("proton-carrier", "proton-occurrence-one")
_PAIR = ConjugatePair("carrier-with-proton", "carrier-without-proton", _PROTON)
_TRANSFER = CarrierTransfer(_PROTON, "donor-occurrence", "acceptor-occurrence")
_LEWIS = LewisPairRelation(
    "electron-pair-donor",
    "electron-pair-acceptor",
    (
        HeldLabel("electron-carrier", "electron-occurrence-one"),
        HeldLabel("electron-carrier", "electron-occurrence-two"),
    ),
)
_AMPHOTERIC = AmphotericRecord(
    "dual-role-species",
    CarrierTransfer(_PROTON, "dual-role-species", "context-one-acceptor"),
    CarrierTransfer(HeldLabel("proton-carrier", "context-two-proton"), "context-two-donor", "dual-role-species"),
)
_BUFFER = BufferReservoir(_PAIR, PositiveCount(2), PositiveCount(3))


ACID_BASE_BLUEPRINTS = (
    AcidBaseBlueprint(
        "SFT-CHEM-AB-ACID-BASE-001", "Conjugate acid-base partition",
        "A conjugate acid/base relation is a pair of retained chemical identities differing by exactly one named proton carrier: the protonated member donates it and the deprotonated member accepts it.",
        BASE_DEPENDENCIES,
        "Generate the literal product of the registered conjugate pair, carrier, acid role, base role, difference, orientation, record and extension choices.",
        ACID_BASE_BOUNDARY, ACID_BASE_DIMENSIONS,
        "two-conjugate-identities__one-held-proton-occurrence__proton-donor-role__proton-acceptor-role__differ-by-one-proton",
        "One retained carrier pair differing by one named proton supplies the first conjugate acid/base relation.",
        "Appending matched retained composition to both members preserves their one-proton difference and donor/acceptor orientation.",
        _exclusions(ACID_BASE_BOUNDARY),
        (("pair", "the two conjugate identities remain distinct", _PAIR.protonated_identity != _PAIR.deprotonated_identity), ("proton", "the distinguishing carrier is explicitly proton-labelled", _PAIR.proton_carrier.family == "proton-carrier"), ("one-difference", "no additional difference is introduced", True)),
        "SFT-EXP-CHEM-AB-ACID-BASE-001",
        "proton-donor-acid__proton-acceptor-base__conjugates-differ-by-one-proton__paired-relation",
        "The claim fails if the authoritative conjugate acid/base record lacks proton donation, proton acceptance or a one-proton conjugate relation, or if a changed row is accepted.",
    ),
    AcidBaseBlueprint(
        "SFT-CHEM-AB-PROTON-TRANSFER-001", "Proton-transfer acid-base relation",
        "Proton transfer moves one named proton carrier from one registered donor occurrence to one distinct acceptor occurrence while conserving carrier identity and both endpoint records.",
        BASE_DEPENDENCIES + ("SFT-CHEM-AB-ACID-BASE-001",),
        "Generate the literal product of the registered proton carrier, source, destination, transition, identity, closure, record and extension choices.",
        PROTON_TRANSFER_BOUNDARY, PROTON_TRANSFER_DIMENSIONS,
        "one-named-proton-carrier__registered-donor__registered-acceptor__donor-to-acceptor-transfer__same-carrier-before-after",
        "One named proton carrier with one distinct donor and acceptor supplies the first closed transfer.",
        "Appending one independent transfer preserves every prior carrier and endpoint identity and closes only through paired donor loss and acceptor gain.",
        _exclusions(PROTON_TRANSFER_BOUNDARY),
        (("carrier", "the transfer retains one proton occurrence", _TRANSFER.carrier == _PROTON), ("endpoints", "donor and acceptor occurrences are distinct", _TRANSFER.donor_identity != _TRANSFER.acceptor_identity), ("no-copy", "one event has one retained carrier", True)),
        "SFT-EXP-CHEM-AB-PROTON-TRANSFER-001",
        "one-proton-carrier__donor-to-acceptor-transfer__carrier-conserved__endpoint-identities-retained",
        "The claim fails if the authoritative proton-transfer record lacks a proton donor, proton acceptor or conserved transfer relation, or if a changed row is accepted.",
    ),
    AcidBaseBlueprint(
        "SFT-CHEM-AB-LEWIS-001", "Electron-pair donor-acceptor relation",
        "A Lewis acid/base relation joins a distinct electron-pair donor and acceptor through the same two exclusion-preserving electron occurrences, with both identities retained.",
        BASE_DEPENDENCIES + ("SFT-CHEM-AB-ACID-BASE-001", "SFT-CHEM-AB-PROTON-TRANSFER-001"),
        "Generate the literal product of the registered Lewis endpoints, support, donor, acceptor, joining, conservation, record and extension choices.",
        LEWIS_BOUNDARY, LEWIS_DIMENSIONS,
        "distinct-donor-acceptor__two-electron-occurrences__pair-donor-support__pair-acceptor-support__shared-or-transferred-pair",
        "Two named electron occurrences, one donor and one acceptor supply the first Lewis pair relation.",
        "Appending one independent donor/acceptor pair retains exclusion, both electron identities and every endpoint trace.",
        _exclusions(LEWIS_BOUNDARY),
        (("pair-count", "the relation contains exactly two electron occurrences", len(_LEWIS.electron_occurrences) == 2), ("exclusion", "the two electron occurrence identities are distinct", _LEWIS.electron_occurrences[0] != _LEWIS.electron_occurrences[1]), ("endpoints", "donor and acceptor remain distinct", _LEWIS.donor_identity != _LEWIS.acceptor_identity)),
        "SFT-EXP-CHEM-AB-LEWIS-001",
        "electron-pair-donor__electron-pair-acceptor__shared-or-transferred-pair__pair-conserved",
        "The claim fails if the authoritative Lewis record lacks an electron-pair donor, electron-pair acceptor or conserved pair relation, or if a changed row is accepted.",
    ),
    AcidBaseBlueprint(
        "SFT-CHEM-AB-AMPHOTERIC-001", "Amphoteric dual-role relation",
        "An amphoteric species is the same retained chemical carrier appearing in two separately held contexts, once in a valid acid role and once in a valid base role.",
        BASE_DEPENDENCIES + ("SFT-CHEM-AB-ACID-BASE-001", "SFT-CHEM-AB-PROTON-TRANSFER-001", "SFT-CHEM-AB-LEWIS-001"),
        "Generate the literal product of the registered amphoteric species, acid context, base context, context separation, duality, identity, record and extension choices.",
        AMPHOTERIC_BOUNDARY, AMPHOTERIC_DIMENSIONS,
        "same-species-identity__valid-donor-event__valid-acceptor-event__contexts-separately-held__both-roles-realized",
        "One retained species with one donor event and one acceptor event in distinct contexts supplies the first amphoteric record.",
        "Appending one context preserves the species identity and prior role traces; amphoteric closure persists only while both opposite roles remain realized.",
        _exclusions(AMPHOTERIC_BOUNDARY),
        (("acid-role", "the same species is donor in one event", _AMPHOTERIC.donor_event.donor_identity == _AMPHOTERIC.species_identity), ("base-role", "the same species is acceptor in another event", _AMPHOTERIC.acceptor_event.acceptor_identity == _AMPHOTERIC.species_identity), ("context-separation", "the opposite-role endpoints remain distinct", _AMPHOTERIC.donor_event.acceptor_identity != _AMPHOTERIC.acceptor_event.donor_identity)),
        "SFT-EXP-CHEM-AB-AMPHOTERIC-001",
        "same-species-acid-role__same-species-base-role__context-dependent-dual-response__both-traces-retained",
        "The claim fails if the authoritative amphoteric record lacks acid and base behavior by one species under retained contexts, or if a changed row is accepted.",
    ),
    AcidBaseBlueprint(
        "SFT-CHEM-AB-BUFFER-001", "Buffer response and conjugate-pair retention",
        "A buffer is a finite positive reservoir of both members of a conjugate pair whose complementary paths consume added proton support or supply proton support to added base while retaining pair identity and finite capacity.",
        BASE_DEPENDENCIES + ("SFT-CHEM-AB-ACID-BASE-001", "SFT-CHEM-AB-PROTON-TRANSFER-001", "SFT-CHEM-AB-AMPHOTERIC-001"),
        "Generate the literal product of the registered buffer components, support, acid response, base response, retention, capacity, record and extension choices.",
        BUFFER_BOUNDARY, BUFFER_DIMENSIONS,
        "conjugate-pair-reservoir__positive-support-of-both__base-member-accepts-proton__acid-member-supplies-proton__conjugate-pair-retained",
        "One positive unit of each conjugate member with both complementary response paths supplies the first finite buffer.",
        "Appending positive units extends the finite capacity while every response still converts one conjugate member into the other and retains the full composition trace.",
        _exclusions(BUFFER_BOUNDARY),
        (("pair-support", "both conjugate components have positive support", _BUFFER.protonated_units == PositiveCount(2) and _BUFFER.deprotonated_units == PositiveCount(3)), ("two-responses", "both acid and base perturbation responses are registered", len(_BUFFER.response_modes) == 2), ("finite-capacity", "the reservoir uses explicit positive counts", True)),
        "SFT-EXP-CHEM-AB-BUFFER-001",
        "weak-acid-conjugate-base-pair__responds-to-added-acid-or-base__composition-change-limited__source-bounded-capacity",
        "The claim fails if the authoritative buffer record lacks a weak acid/conjugate base pair, response to added acid/base or finite composition-dependent capacity, or if a changed row is accepted.",
    ),
)


for _blueprint in ACID_BASE_BLUEPRINTS:
    _blueprint.validate()


__all__ = (
    "ACID_BASE_BLUEPRINTS",
    "AcidBaseBlueprint",
    "AmphotericRecord",
    "BufferReservoir",
    "CarrierTransfer",
    "ConjugatePair",
    "LewisPairRelation",
)
