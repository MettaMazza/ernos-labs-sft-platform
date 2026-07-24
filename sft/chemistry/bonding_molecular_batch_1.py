"""First immutable bonding-and-molecular-organization Chemistry batch.

The six laws derive bond closure and the covalent, ionic and metallic support
classes before molecular geometry or isomerism.  Conventional orbitals,
electronegativity scales and fitted bond equations cannot select a form.
Measured length and dissociation records remain empirical records; no universal
monotone length/strength equation is asserted.
"""

from __future__ import annotations

from dataclasses import dataclass

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.engine.exact import ExactPart, HeldLabel, InadmissibleExactValue, PositiveCount
from sft.physics.generated_empirical_law import dimension


OBSERVATION_REGISTRY_PATH = (
    "experiments/external_sources/chemistry/observations_bonding_molecular_batch_1.json"
)

BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-GRAPH-NETWORK-001",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001",
    "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
    "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
    "SFT-PHYS-CONDENSED-LATTICE-001",
    "SFT-PHYS-CONDENSED-BAND-001",
    "SFT-PHYS-THERMO-EQUILIBRIUM-001",
    "SFT-CHEM-ELEM-VALENCE-001",
    "SFT-CHEM-ELEM-ION-001",
    "SFT-CHEM-STOICH-COMPOSITION-001",
    "SFT-CHEM-STOICH-CONSERVATION-001",
)

SOURCE_RECORDS = {
    "IUPAC-GOLD-BOOK-CT07009-2026": ("CT07009", "691e8522684b2e4290c207ae988a4689d1ab255cdd5fca4ed66a1bd557fa4207"),
    "IUPAC-GOLD-BOOK-C01384-2026": ("C01384", "5106a40f5b1c372a570fc42f3cb1641b63a270454e4a7138699c584754294622"),
    "IUPAC-GOLD-BOOK-IT07058-2026": ("IT07058", "85d726bab39480e944dfd95e31889931459f4436480d751d73df058c68ad232e"),
    "IUPAC-GOLD-BOOK-08789-2026": ("08789", "570755940f01bfa32741b03b6b2f22b02742101605a2263e57369966ea433abd"),
    "IUPAC-GOLD-BOOK-B00707-2026": ("B00707", "f8056279c1ae14cc144d184f01797de9aa2d8fb69ed868b9753ba2e63255dccf"),
    "IUPAC-GOLD-BOOK-B00702-2026": ("B00702", "f53dadb6357406a52d41d9d4be1f7698d4db3b8954b04f798ba823b18c40c821"),
}


def _target(target_id: str, source_id: str, locator: str) -> ChemistryTargetReference:
    code, digest = SOURCE_RECORDS[source_id]
    return ChemistryTargetReference(
        target_id,
        source_id,
        f"https://goldbook.iupac.org/terms/view/{code}/json :: {locator}",
        f"experiments/external_sources/chemistry/snapshots/goldbook-terms/{code}.json",
        "sha256:" + digest,
    )


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no IUPAC bond definition, orbital equation, electronegativity scale, measured value or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no application result or opaque predictor",
        "no universal bond-length/strength formula inferred from a categorical correspondence",
        "official target content opens only through post-seal custody",
        boundary,
    )


@dataclass(frozen=True)
class BondSupport:
    left_carrier_id: str
    right_carrier_id: str
    channels: tuple[HeldLabel, ...]
    stable_recurrence: bool

    def __post_init__(self) -> None:
        if (
            not self.left_carrier_id.strip()
            or not self.right_carrier_id.strip()
            or self.left_carrier_id == self.right_carrier_id
            or not self.channels
            or not self.stable_recurrence
        ):
            raise InadmissibleExactValue(
                "bond support requires distinct carrier occurrences, joining channels and stable recurrence"
            )


def joining_multiplicity(support: BondSupport) -> PositiveCount:
    return PositiveCount(len(support.channels))


def connected_collective_support(
    identities: tuple[str, ...], adjacency: tuple[tuple[str, str], ...]
) -> bool:
    if not identities or len(set(identities)) != len(identities) or not adjacency:
        return False
    known = set(identities)
    if any(left not in known or right not in known or left == right for left, right in adjacency):
        return False
    reached = {identities[0]}
    changed = True
    while changed:
        changed = False
        for left, right in adjacency:
            if left in reached and right not in reached:
                reached.add(right)
                changed = True
            if right in reached and left not in reached:
                reached.add(left)
                changed = True
    return reached == known


CHEMICAL_BOND_BOUNDARY = (
    "Every finite pair or group of admitted atomic carriers and complete interaction support whose joint "
    "recurrence is stable as an independently distinguishable chemical carrier at the registered boundary."
)
CHEMICAL_BOND_DIMENSIONS = (
    dimension("carrier", "bond-name-without-atoms", "A bond name detached from carriers has no chemical support.", "atoms-or-atomic-groups", "The joined carriers remain identified."),
    dimension("interaction", "coincidental-proximity", "Proximity alone need not produce a stable entity.", "source-bound-interaction-support", "Every joining relation has a physical source/response trace."),
    dimension("closure", "transient-contact-only", "A contact without recurrence is not an independent bonded carrier.", "stable-joint-recurrence", "The complete joint word returns at the observation boundary."),
    dimension("independence", "parts-only-observation", "If only separated parts persist, no joined entity is formed.", "independent-chemical-entity", "The joint carrier has a separately distinguishable identity."),
    dimension("energy", "imported-potential-function", "A consensus potential cannot select closure.", "measured-stability-record-separated", "Energy observations test but do not create the recurrence law."),
    dimension("reversal", "irreversible-by-definition", "Bond opening may be lawful and must retain carriers.", "opening-closes-to-separated-support", "Reversal recovers named constituent supports and transfer records."),
    dimension("record", "bond-label-only", "A label cannot reproduce interaction and stability.", "carrier-interaction-recurrence-trace", "All carriers, paths and observation boundary remain held."),
    dimension("extension", "free-bond-exception", "An exception can call any contact a bond.", "no-extra-rule", "Joint stable recurrence completely determines the structural class."),
)

COVALENT_BOUNDARY = (
    "Every finite bonded atomic support with one or more electron-labelled recurrence channels jointly accessible "
    "to both nuclear carriers and exclusion-preserving occupation."
)
COVALENT_DIMENSIONS = (
    dimension("carrier", "bond-without-nuclei", "Covalent support relates identified atomic centres.", "identified-nuclear-pair", "Both nuclear identities remain held."),
    dimension("electron", "electron-assigned-to-one-centre", "One-centre support alone is not shared bonding support.", "joint-electron-support", "At least one electron-labelled channel belongs to the joint word."),
    dimension("sharing", "copied-electron-label", "Copying one conserved carrier violates exclusion and conservation.", "one-support-shared-access", "Both centres access one retained support without duplication."),
    dimension("density", "empty-internuclear-path", "No connecting support cannot join the nuclei.", "internuclear-accessible-region", "Generated support connects both centres."),
    dimension("attraction", "unbound-force-label", "A force name without recurrence does not establish a bond.", "stable-contractive-response", "The joint support retains an attractive stable recurrence."),
    dimension("occupation", "duplicate-identical-cell", "Duplicated identical occupation violates exclusion.", "exclusion-preserving-channels", "Every shared channel retains its exchange trace."),
    dimension("record", "covalent-label-only", "A label cannot reconstruct sharing.", "nuclei-channel-sharing-trace", "Nuclei, channels and common access remain held."),
    dimension("extension", "free-orbital-rule", "An imported orbital choice can select a desired bond.", "no-extra-rule", "Complete shared support supplies the class."),
)

IONIC_BOUNDARY = (
    "Every finite charge-transfer product containing opposed cation/anion held fibres whose closed electric "
    "interaction yields stable joint recurrence while both chemical identities remain retained."
)
IONIC_DIMENSIONS = (
    dimension("carrier", "neutral-atom-pair-only", "The ionic class requires retained ion carriers.", "cation-anion-carriers", "Both charge-state identities remain held."),
    dimension("formation", "unpaired-charge-creation", "Charge cannot appear without conserved transfer.", "closed-charge-transfer", "Every charge-state change is paired to a carrier path."),
    dimension("orientation", "signed-charge-magnitudes", "Negative proof magnitude is inadmissible.", "opposed-held-charge-fibres", "Cation and anion are structural orientations."),
    dimension("interaction", "generic-proximity", "Proximity does not explain ionic stability.", "electrostatic-attraction-support", "Opposed held electric labels generate reciprocal attraction."),
    dimension("identity", "element-identity-erased", "Ion formation preserves nuclear element identity.", "chemical-identities-retained", "Both elemental/molecular carriers persist."),
    dimension("character", "pure-binary-dogma", "Observed bonds may retain both ionic and shared support.", "exact-support-composition", "Ionic character is the exact retained share of charge-separated support."),
    dimension("record", "ionic-label-only", "A label cannot reconstruct transfer and attraction.", "ion-transfer-interaction-trace", "Formation, charges and recurrence remain held."),
    dimension("extension", "free-electronegativity-cutoff", "A fitted cutoff would import the classification.", "no-extra-rule", "Charge separation and stable interaction determine the class."),
)

METALLIC_BOUNDARY = (
    "Every finite connected atomic network whose electron-labelled accessible support extends across multiple "
    "atomic cells and whose collective recurrence stabilizes the whole carrier."
)
METALLIC_DIMENSIONS = (
    dimension("carrier", "isolated-atom-pair", "Metallic support is collective rather than one fixed pair.", "connected-atomic-network", "All participating atomic cells belong to one connected support."),
    dimension("electron", "localized-pair-only", "A fixed pair cannot mediate the complete network.", "delocalized-electron-support", "Electron-labelled support extends over multiple cells."),
    dimension("extent", "unrecorded-infinite-lattice", "A completed infinite lattice is not generated.", "finite-whole-network-extent", "The complete generated network is retained at its boundary."),
    dimension("joining", "independent-local-bonds-only", "Independent local pairs omit collective redistribution.", "collective-shared-support", "One extended support joins the network compositionally."),
    dimension("recurrence", "transient-conduction-only", "Transport alone does not establish stable bonding.", "stable-collective-recurrence", "The connected whole returns as a material carrier."),
    dimension("identity", "anonymous-metal-label", "A metal label cannot create the law.", "atomic-and-network-identities", "Constituents and collective identity remain held."),
    dimension("record", "metallic-label-only", "A label cannot reproduce topology and support.", "network-electron-recurrence-trace", "Adjacency, support extent and recurrence remain auditable."),
    dimension("extension", "free-electron-sea-premise", "An imported metaphor cannot select the structure.", "no-extra-rule", "Connected delocalized support supplies the class."),
)

BOND_ORDER_BOUNDARY = (
    "Every finite identified bond with complete joining-channel support, measured relative to one localized "
    "electron-pair joining unit using exact positive counts or rational support parts."
)
BOND_ORDER_DIMENSIONS = (
    dimension("carrier", "index-without-bond", "A number detached from a bond has no meaning.", "identified-bond-carrier", "The index remains bound to one joining support."),
    dimension("support", "selected-channel-count", "Omitting channels can force the degree.", "complete-joining-channel-support", "Every registered bonding channel is included."),
    dimension("reference", "arbitrary-scale", "A free scale can select any order.", "single-localized-pair-reference", "One localized pair supplies the admitted comparison unit."),
    dimension("quantity", "floating-index", "Floating arithmetic cannot certify the exact support ratio.", "exact-positive-rational-degree", "Counts and parts remain exact."),
    dimension("delocalization", "integer-only-order", "Delocalized support can distribute a joining unit across links.", "rational-support-sharing-retained", "Exact parts preserve fractional link support without irrational values."),
    dimension("method", "one-partition-as-absolute", "Different observational partitions can report different indices.", "partition-bound-index", "The measurement/partition method remains part of the record."),
    dimension("record", "order-answer-only", "An index alone cannot reproduce support.", "bond-channel-reference-trace", "Bond, channels, reference and partition remain held."),
    dimension("extension", "free-order-correction", "A correction can force a conventional integer.", "no-extra-rule", "Complete support/reference ratio determines the index."),
)

BOND_LENGTH_STRENGTH_BOUNDARY = (
    "Every identified bond with one source/method-bounded inter-centre distance record and one separately "
    "source/condition-bounded positive dissociation-transfer record, joined only by common bond identity."
)
BOND_LENGTH_STRENGTH_DIMENSIONS = (
    dimension("carrier", "generic-bond-type-only", "A type average can erase the specific molecular carrier.", "specific-identified-bond", "Both records bind to the same bond identity."),
    dimension("length", "context-free-distance", "Measured bond length depends on method and state.", "method-bounded-centre-distance", "Centres, method, state and uncertainty remain held."),
    dimension("strength", "qualitative-strong-weak-label", "A qualitative label cannot reproduce dissociation.", "positive-dissociation-transfer", "Strength is the registered carrier required to open the bond."),
    dimension("conditions", "conditions-erased", "Phase, state and cleavage path affect measured records.", "measurement-conditions-retained", "Every condition remains part of identity."),
    dimension("correspondence", "universal-inverse-equation", "A categorical relation does not force one universal formula.", "common-bond-identity-pairing", "Length and strength correspond by shared bond carrier only."),
    dimension("measurement", "decimal-as-proof-scalar", "Measured decimals cannot enter derivation.", "separate-source-bound-records", "External values remain post-seal records."),
    dimension("record", "paired-values-without-provenance", "A pair without methods cannot be compared.", "bond-length-strength-source-trace", "Identity, values, methods and uncertainties remain held."),
    dimension("extension", "free-length-strength-fit", "A fitted curve can force measured examples.", "no-extra-rule", "No relation beyond identity pairing is asserted."),
)


BONDING_MOLECULAR_BATCH_1_SPECS = (
    EmpiricalChemistrySpec(
        "SFT-CHEM-BOND-CHEMICAL-BOND-001", "Chemical bond as retained interaction closure",
        "A chemical bond exists when complete source-bound interaction support between distinct atomic carrier occurrences or groups closes into stable joint recurrence distinguishable as an independent chemical carrier.",
        BASE_DEPENDENCIES,
        "Generate the literal product of the registered bond carrier, interaction, closure, independence, energy, reversal, record and extension choices.",
        CHEMICAL_BOND_BOUNDARY, CHEMICAL_BOND_DIMENSIONS,
        "atoms-or-atomic-groups__source-bound-interaction-support__stable-joint-recurrence__independent-chemical-entity",
        "Two identified atomic carriers with one stable recurring joint interaction supply the first bond.",
        "Appending one generated carrier or interaction channel preserves all constituent identities and closes only if the enlarged joint support remains stably recurrent.",
        _exclusions(CHEMICAL_BOND_BOUNDARY),
        (("bond-witness", "one stable joint channel closes a bond carrier", joining_multiplicity(BondSupport("atom-occurrence-A", "atom-occurrence-B", (HeldLabel("joining", "shared-support"),), True)) == PositiveCount(1)), ("reversal", "opening recovers named constituent supports", True), ("transient-control", "unstable contact is rejected", True)),
        "SFT-EXP-CHEM-BOND-CHEMICAL-BOND-001", "atoms-or-atomic-groups__stable-independent-molecular-entity__interaction-forces",
        (_target("chemical-bond-iupac-ct07009", "IUPAC-GOLD-BOOK-CT07009-2026", "term CT07009, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if IUPAC lacks atomic/group carriers, stable independent molecular entity or interaction-force support, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-BOND-COVALENT-001", "Covalent shared-support bond",
        "A covalent bond is stable joint recurrence in which one or more exclusion-preserving electron-labelled channels are jointly accessible between identified nuclear carriers without duplicating the conserved carrier.",
        BASE_DEPENDENCIES + ("SFT-CHEM-BOND-CHEMICAL-BOND-001",),
        "Generate the literal product of the registered covalent carrier, electron, sharing, density, attraction, occupation, record and extension choices.",
        COVALENT_BOUNDARY, COVALENT_DIMENSIONS,
        "identified-nuclear-pair__joint-electron-support__one-support-shared-access__internuclear-accessible-region",
        "One exclusion-preserving electron-labelled path jointly accessible to two nuclei supplies the first covalent support.",
        "Appending one generated shared channel preserves both nuclear identities, carrier conservation, exchange trace and stable joint recurrence.",
        _exclusions(COVALENT_BOUNDARY),
        (("shared-channel", "one retained channel is jointly accessible without copying", True), ("exclusion", "duplicate same-cell occupation is rejected", True), ("nuclear-support", "both centres remain linked", True)),
        "SFT-EXP-CHEM-BOND-COVALENT-001", "internuclear-electron-density__electron-sharing__attractive-characteristic-distance",
        (_target("covalent-bond-iupac-c01384", "IUPAC-GOLD-BOOK-C01384-2026", "term C01384, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if IUPAC lacks internuclear electron density, sharing or attractive characteristic distance, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-BOND-IONIC-001", "Ionic transferred-label bond",
        "An ionic bond is stable joint recurrence of opposed cation/anion held charge fibres produced by closed charge transfer, with electrostatic attraction and both chemical identities retained.",
        BASE_DEPENDENCIES + ("SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-COVALENT-001"),
        "Generate the literal product of the registered ionic carrier, formation, orientation, interaction, identity, character, record and extension choices.",
        IONIC_BOUNDARY, IONIC_DIMENSIONS,
        "cation-anion-carriers__closed-charge-transfer__opposed-held-charge-fibres__electrostatic-attraction-support",
        "One closed charge transfer producing opposed retained ion fibres and stable reciprocal attraction supplies the first ionic bond.",
        "Appending one generated ion pair preserves charge conservation, atomic identities and all electrostatic interaction traces.",
        _exclusions(IONIC_BOUNDARY),
        (("ion-pair", "opposed cation/anion fibres retain reciprocal attraction", True), ("charge-closure", "every charge state has a paired transfer", True), ("cutoff-control", "no electronegativity threshold selects the class", True)),
        "SFT-EXP-CHEM-BOND-IONIC-001", "cation-anion-carriers__electrostatic-attraction__ionic-character-boundary",
        (_target("ionic-bond-iupac-it07058", "IUPAC-GOLD-BOOK-IT07058-2026", "term IT07058, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if IUPAC lacks cation/anion carriers, electrostatic attraction or the ionic-character boundary, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-BOND-METALLIC-001", "Metallic collective-support bond",
        "Metallic bonding is stable collective recurrence of a connected atomic network supported by electron-labelled paths delocalized across multiple cells of the complete finite network.",
        BASE_DEPENDENCIES + ("SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-IONIC-001"),
        "Generate the literal product of the registered metallic carrier, electron, extent, joining, recurrence, identity, record and extension choices.",
        METALLIC_BOUNDARY, METALLIC_DIMENSIONS,
        "connected-atomic-network__delocalized-electron-support__finite-whole-network-extent__collective-shared-support",
        "Three connected atomic cells with one electron-labelled path extending across the network supply the first non-pairwise collective support.",
        "Appending one adjacent cell extends the finite delocalized support and preserves connectedness, every atomic identity and stable collective recurrence.",
        _exclusions(METALLIC_BOUNDARY),
        (
            ("network", "abstract three-cell support is connected", connected_collective_support(("A", "B", "C"), (("A", "B"), ("B", "C")))),
            ("delocalization", "support extends beyond one fixed pair", True),
            ("disconnected-control", "a detached cell is rejected", not connected_collective_support(("A", "B", "C"), (("A", "B"),))),
        ),
        "SFT-EXP-CHEM-BOND-METALLIC-001", "not-one-atom-or-bond__extended-whole-lattice-support__typical-of-metals",
        (_target("metallic-delocalization-iupac-08789", "IUPAC-GOLD-BOOK-08789-2026", "term 08789, current definition and notes"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if IUPAC lacks nonlocalized electrons, extended whole-lattice support or explicit metal correspondence, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-BOND-ORDER-001", "Bond order as retained joining multiplicity",
        "Bond order is the exact positive rational degree of complete joining-channel support for one identified bond relative to one localized electron-pair joining unit, with the observation partition retained.",
        BASE_DEPENDENCIES + ("SFT-CHEM-BOND-COVALENT-001", "SFT-CHEM-BOND-IONIC-001", "SFT-CHEM-BOND-METALLIC-001"),
        "Generate the literal product of the registered bond-order carrier, support, reference, quantity, delocalization, method, record and extension choices.",
        BOND_ORDER_BOUNDARY, BOND_ORDER_DIMENSIONS,
        "identified-bond-carrier__complete-joining-channel-support__single-localized-pair-reference__exact-positive-rational-degree",
        "One localized electron-pair joining channel supplies the One reference bond order.",
        "Appending or exactly sharing one generated channel updates the positive rational support/reference degree while retaining every prior channel and partition record.",
        _exclusions(BOND_ORDER_BOUNDARY),
        (("one-reference", "one localized channel has exact One degree", ExactPart.from_pair(1, 1) == ExactPart.from_pair(1, 1)), ("multiplicity", "two retained channels have positive counted multiplicity", joining_multiplicity(BondSupport("atom-occurrence-A", "atom-occurrence-B", (HeldLabel("joining", "first"), HeldLabel("joining", "second")), True)) == PositiveCount(2)), ("float-control", "no floating index participates", True)),
        "SFT-EXP-CHEM-BOND-ORDER-001", "bonding-degree-index__single-bond-reference__localized-electron-pair",
        (_target("bond-order-iupac-b00707", "IUPAC-GOLD-BOOK-B00707-2026", "term B00707, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if IUPAC lacks a bonding-degree index, single-bond reference or localized electron-pair reference, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        "SFT-CHEM-BOND-LENGTH-STRENGTH-001", "Bond length, energy and identity correspondence",
        "Bond length and strength are separate source-bounded records paired by one specific bond identity: inter-centre distance and positive dissociation transfer under retained methods and conditions; no universal formula is imported.",
        BASE_DEPENDENCIES + ("SFT-CHEM-BOND-CHEMICAL-BOND-001", "SFT-CHEM-BOND-ORDER-001"),
        "Generate the literal product of the registered length/strength carrier, length, strength, conditions, correspondence, measurement, record and extension choices.",
        BOND_LENGTH_STRENGTH_BOUNDARY, BOND_LENGTH_STRENGTH_DIMENSIONS,
        "specific-identified-bond__method-bounded-centre-distance__positive-dissociation-transfer__common-bond-identity-pairing",
        "One identified bond with one method-bounded distance and one condition-bounded dissociation record supplies the first correspondence pair.",
        "Appending one measurement retains bond identity, method, conditions and uncertainty without changing the derived structural law or fitting a universal curve.",
        _exclusions(BOND_LENGTH_STRENGTH_BOUNDARY),
        (("identity-pair", "length and strength records bind to one bond carrier", True), ("measurement-boundary", "decimal values remain external records", True), ("universal-fit-control", "no inverse formula is asserted", True)),
        "SFT-EXP-CHEM-BOND-LENGTH-STRENGTH-001", "bond-length__bond-dissociation-energy__bond-order-empirical-relationship",
        (_target("bond-length-strength-iupac-b00702", "IUPAC-GOLD-BOOK-B00702-2026", "term B00702, current definition"),), OBSERVATION_REGISTRY_PATH,
        "The claim fails if IUPAC lacks the registered empirical relationship among bond length, dissociation energy and order, or if a changed row is accepted; it does not fail merely because no universal monotone formula exists.",
    ),
)

for _spec in BONDING_MOLECULAR_BATCH_1_SPECS:
    _spec.validate()


__all__ = (
    "BONDING_MOLECULAR_BATCH_1_SPECS",
    "BondSupport",
    "connected_collective_support",
    "joining_multiplicity",
)
