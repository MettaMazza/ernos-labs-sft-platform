"""Second immutable elements-and-periodicity Chemistry batch.

This module closes periodic order, recurrence, group/period coordinates,
valence, ion formation and the current observational table boundary.  It does
not import an electron-shell equation, a periodic-table layout or a measured
element value into derivation.  The official IUPAC sources are opened only by
the post-seal validator.

The known-table boundary is deliberately observational: the current IUPAC
table is finite through atomic number 118, but that fact is not promoted into
a theorem that further elements cannot be generated or observed.
"""

from __future__ import annotations

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.physics.generated_empirical_law import dimension


OBSERVATION_REGISTRY_PATH = (
    "experiments/external_sources/chemistry/observations_elements_periodicity_batch_2.json"
)

BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-DISCRETE-001",
    "SFT-MATH-COMBINATORICS-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-ENCODING-DECODING-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-PHYS-MEAS-VALUE-RECORD-001",
    "SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001",
    "SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001",
    "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001",
    "SFT-PHYS-QUANTUM-EXCLUSION-001",
    "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-ELEM-ELEMENT-001",
    "SFT-CHEM-ELEM-ATOMIC-NUMBER-001",
)

SOURCE_RECORDS = {
    "IUPAC-PERIODIC-TABLE-2022": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://iupac.org/wp-content/uploads/2022/07/IUPAC_Periodic_Table-04May22_CRA.pdf",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/iupac-periodic-table-04may22.pdf",
        "snapshot_hash": "sha256:ef6ca2f6d46554f96e30ad3a60693d6630fe45ad81ce83cb14e508c6cbb7d3b3",
    },
    "IUPAC-GOLD-BOOK-V06588-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/V06588/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/V06588.json",
        "snapshot_hash": "sha256:99ae406a9ac89a8f0a89bf3c775ff9ba7c5d9d0c96f89f83a57a0b35c76c4077",
    },
    "IUPAC-GOLD-BOOK-I03158-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/I03158/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/I03158.json",
        "snapshot_hash": "sha256:6b54a0f6d9cf83f30251501b58b75764a39396e56d819b420b1556476f9f13f6",
    },
}


def _target(target_id: str, source_id: str, locator: str) -> ChemistryTargetReference:
    source = SOURCE_RECORDS[source_id]
    return ChemistryTargetReference(
        target_id=target_id,
        source_id=source_id,
        source_locator=str(source["source_uri"]) + " :: " + locator,
        snapshot_path=str(source["snapshot_path"]),
        snapshot_hash=str(source["snapshot_hash"]),
    )


def _exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no IUPAC table arrangement, term definition, measured value, electron-shell equation or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no application result or opaque predictor",
        "official target content opens only through post-seal custody",
        boundary,
    )


PERIODIC_ORDER_BOUNDARY = (
    "Every positive-finite chemical-element class carrying its admitted atomic-number identity, ordered only by "
    "generated proton-count succession and retaining the complete element record at each coordinate."
)
PERIODIC_ORDER_DIMENSIONS = (
    dimension("carrier", "names-without-element-records", "Names alone do not preserve the generated element classes.", "complete-element-class-support", "Every coordinate retains its chemical-element carrier."),
    dimension("coordinate", "layout-selected-coordinate", "A drawn location can be changed without changing nuclear identity.", "atomic-number-coordinate", "The held nuclear proton count supplies the invariant coordinate."),
    dimension("order", "unordered-element-set", "An unordered set cannot express successor structure.", "positive-count-total-order", "Generated positive counts give one exact total order."),
    dimension("identity", "order-erases-isotopes", "Ordering must not discard refinements of an element record.", "element-identity-retained", "Element identity and isotope support remain held at each coordinate."),
    dimension("succession", "free-table-rearrangement", "A discretionary rearrangement can select any pattern.", "one-proton-successor", "Appending one proton advances exactly one generated count coordinate."),
    dimension("observation", "known-table-as-proof-premise", "The observed table cannot create the order law.", "post-seal-known-table-correspondence", "The current table tests the sealed order after derivation."),
    dimension("record", "atomic-number-only-list", "A number list loses symbols, identities and source boundary.", "number-element-source-trace", "Every order coordinate remains linked to element and source records."),
    dimension("extension", "free-order-exception", "An exception can silently permute successors.", "no-extra-rule", "Count succession completely determines the order."),
)

PERIODIC_RECURRENCE_BOUNDARY = (
    "Every generated positive-finite atomic-number successor family whose boundary-closed outer observation "
    "support is quotiented only by complete chemical transition equivalence."
)
PERIODIC_RECURRENCE_DIMENSIONS = (
    dimension("carrier", "property-name-series", "A list of property names contains no physical recurrence carrier.", "boundary-closed-outer-support", "Each class retains its outer accessible support and closure record."),
    dimension("progression", "mass-selected-progression", "Isotope mass does not determine element succession.", "atomic-number-successor-progression", "The admitted proton-count successor fixes progression."),
    dimension("equivalence", "visual-column-equivalence", "A drawing cannot establish common chemical behavior.", "complete-chemical-trace-equivalence", "Classes recur only when all registered outer chemical traces agree."),
    dimension("closure", "unbounded-orbital-continuum", "An ungenerated continuum violates the finite exact domain.", "finite-bound-state-recurrence", "Admitted discrete boundary recurrence supplies finite observable classes."),
    dimension("occupation", "duplicate-state-without-trace", "Unrecorded duplicate occupation violates exclusion.", "exclusion-preserving-occupation", "Each accessible constituent word preserves its exchange trace."),
    dimension("periodicity", "assumed-fixed-period", "A fixed imported period can manufacture recurrence.", "return-of-observation-class", "A period closes only when an earlier outer trace class recurs."),
    dimension("record", "recurrence-label-only", "A repeated label does not reproduce the equivalence test.", "support-transition-recurrence-trace", "Support, transitions and return witness remain held."),
    dimension("extension", "free-shell-rule", "A discretionary shell equation would import the desired organization.", "no-extra-rule", "Only admitted recurrence, exclusion and trace equivalence select classes."),
)

GROUP_PERIOD_BOUNDARY = (
    "Every finite periodic-order prefix partitioned by exact outer-trace recurrence, with each element assigned "
    "one recurrence-class coordinate and one counted closure-to-reopening depth."
)
GROUP_PERIOD_DIMENSIONS = (
    dimension("carrier", "printed-cell-coordinate", "A page coordinate is representational rather than chemical.", "periodic-element-carrier", "Each coordinate is attached to a complete element record."),
    dimension("group", "column-number-as-premise", "A conventional column number cannot select equivalence.", "outer-trace-equivalence-class", "A group is the quotient by recurring outer chemical organization."),
    dimension("period", "row-number-as-premise", "A conventional row number cannot select recurrence depth.", "closure-reopening-depth", "A period counts the generated closure and reopening progression."),
    dimension("pairing", "group-only-or-period-only", "Either coordinate alone loses a required distinction.", "joint-group-period-coordinate", "The pair locates one recurrence class at one progression depth."),
    dimension("ordering", "layout-dependent-order", "Alternate drawings must not alter chemical coordinates.", "atomic-number-order-retained", "The invariant successor order remains held."),
    dimension("equivalence", "namesake-family-only", "A family name cannot prove matching transition support.", "complete-trace-quotient", "Only full observed chemical trace equivalence creates a shared group."),
    dimension("record", "coordinate-without-witness", "A coordinate without a recurrence witness is not auditable.", "element-order-recurrence-trace", "Element identity, order and recurrence witness remain linked."),
    dimension("extension", "free-layout-exception", "A layout exception can move an element without a chemical distinction.", "no-extra-rule", "The two derived coordinates require no layout-specific rule."),
)

VALENCE_BOUNDARY = (
    "Every finite atom or chemical fragment with complete generated combination and substitution traces, where "
    "the largest realized univalent joining count is retained with its chemical context."
)
VALENCE_DIMENSIONS = (
    dimension("carrier", "element-name-only", "An element name contains no combination witness.", "atom-or-fragment-carrier", "The combining carrier is an atom or a retained chemical fragment."),
    dimension("support", "assumed-valence-number", "An assumed number imports the answer.", "complete-generated-combination-support", "Every admitted combination trace is enumerated before the maximum is taken."),
    dimension("unit", "mixed-partner-count", "Partners of unrecorded multiplicity cannot define one comparison.", "univalent-partner-count", "One-valence partners provide the exact comparison carrier."),
    dimension("selection", "typical-count", "A typical value can omit a lawful larger combination.", "maximum-realized-count", "The greatest generated realized count supplies the boundary."),
    dimension("substitution", "combination-only", "Valence also constrains lawful substitution for the carrier.", "combination-or-substitution", "Both joining and replacement traces are retained."),
    dimension("context", "universal-context-free-number", "Chemical environment may alter available combinations.", "chemical-context-retained", "The declared carrier and environment bound the result."),
    dimension("record", "number-without-traces", "A bare number cannot reproduce its maximum witness.", "combination-maximum-trace", "All candidates and the maximal witness remain held."),
    dimension("extension", "free-valence-correction", "An adjustment can force a conventional value.", "no-extra-rule", "Complete generated support determines the maximum without correction."),
)

ION_BOUNDARY = (
    "Every finite atomic or molecular chemical carrier whose complete conserved electric-label accounting leaves "
    "one non-neutral held orientation while retaining its elemental and molecular identity records."
)
ION_DIMENSIONS = (
    dimension("carrier", "charge-label-without-particle", "A charge label detached from matter is not a chemical ion.", "atomic-or-molecular-particle", "The ion retains an atomic or molecular carrier."),
    dimension("charge", "signed-proof-number", "A signed proof magnitude violates the positive exact domain.", "net-held-electric-charge", "Net charge is a conserved held orientation and positive count."),
    dimension("formation", "identity-destroying-change", "Destroying the carrier does not create a charge state of it.", "label-transfer-with-identity-retained", "Electric-label transfer changes charge state while retaining chemical identity."),
    dimension("conservation", "unpaired-charge-creation", "Unpaired creation violates closed label flow.", "closed-charge-transfer", "Every gained or released charge carrier is paired across the boundary."),
    dimension("element", "proton-count-change", "Changing proton count changes element identity.", "atomic-number-retained", "Ion formation preserves nuclear proton count."),
    dimension("orientation", "positive-negative-proof-scalars", "Signed scalars are not SFT proof objects.", "cation-anion-held-fibres", "The two charge orientations are exact held fibre labels."),
    dimension("record", "ion-name-only", "A name cannot reconstruct carrier, charge and transfer.", "carrier-charge-transfer-trace", "The complete formation and conservation trace remains held."),
    dimension("extension", "free-charge-exception", "An exception can create or erase charge without transfer.", "no-extra-rule", "Conserved held-label accounting completely determines ion status."),
)

PERIODIC_BOUNDARY_BOUNDARY = (
    "Every official finite periodic-table release treated as a source-dated observation census, retaining all "
    "listed atomic-number/element records while leaving any unobserved successor scientifically open."
)
PERIODIC_BOUNDARY_DIMENSIONS = (
    dimension("carrier", "largest-number-only", "A largest number alone omits the observed element census.", "complete-source-bounded-census", "Every element row in the registered release is retained."),
    dimension("extent", "timeless-terminal-claim", "A current release cannot prove that no successor can exist.", "greatest-listed-coordinate", "The boundary is only the greatest coordinate in this source release."),
    dimension("identity", "count-without-element", "A number without its element record is not an observation boundary.", "element-record-retained", "The terminal listed coordinate retains symbol and element identity."),
    dimension("time", "undated-table", "An undated table cannot define a reproducible empirical boundary.", "release-date-retained", "The official release date is part of the observation."),
    dimension("completeness", "selected-terminal-row", "Selecting only the last row cannot establish the registered census.", "all-listed-rows-retained", "The complete finite source support is required."),
    dimension("extension", "observed-means-impossible-beyond", "Absence from one release is not impossibility.", "unobserved-successor-open", "Further coordinates remain an empirical question."),
    dimension("record", "boundary-without-source", "An unsourced endpoint cannot be reproduced.", "source-hash-census-trace", "Source, bytes, extraction and rows remain bound."),
    dimension("rule", "free-terminal-rule", "A terminal rule chosen from the table would overfit observation.", "no-extra-rule", "The law adds no terminal theorem to the source-bounded fact."),
)


ELEMENTS_PERIODICITY_BATCH_2_SPECS = (
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-PERIODIC-ORDER-001",
        title="Periodic ordering by retained nuclear identity",
        statement="Chemical elements possess one invariant exact total order: the generated positive proton-count order, with the complete element class retained at each coordinate.",
        dependencies=BASE_DEPENDENCIES,
        generation_rule="Generate the literal product of the registered periodic-order carrier, coordinate, order, identity, succession, observation, record and extension choices.",
        grammar_boundary=PERIODIC_ORDER_BOUNDARY,
        dimensions=PERIODIC_ORDER_DIMENSIONS,
        exact_result="complete-element-class-support__atomic-number-coordinate__positive-count-total-order__element-identity-retained",
        induction_base="The first generated proton-count class supplies one element carrier and the first exact order coordinate.",
        induction_step="Appending one proton-count successor adds one later coordinate, preserves every earlier element/isotope record and introduces no permutation rule.",
        exclusions=_exclusions(PERIODIC_ORDER_BOUNDARY),
        operational_witnesses=(("strict-successor", "each generated proton-count successor has one later coordinate", True), ("identity-retention", "the complete element record remains linked to its coordinate", True), ("layout-control", "a changed page location cannot alter the order", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-PERIODIC-ORDER-001",
        expected_observation_label="complete-known-element-support__atomic-number-coordinate-order",
        target_rows=(_target("periodic-order-iupac-2022", "IUPAC-PERIODIC-TABLE-2022", "complete current element records and atomic-number key"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the official source lacks the complete registered element support or atomic-number coordinate, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001",
        title="Periodic recurrence of outer chemical organization",
        statement="Periodicity is the return, along atomic-number succession, of an earlier complete outer chemical observation class generated by finite bound-state recurrence and exclusion-preserving occupation.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-PERIODIC-ORDER-001",),
        generation_rule="Generate the literal product of the registered recurrence carrier, progression, equivalence, closure, occupation, periodicity, record and extension choices.",
        grammar_boundary=PERIODIC_RECURRENCE_BOUNDARY,
        dimensions=PERIODIC_RECURRENCE_DIMENSIONS,
        exact_result="boundary-closed-outer-support__atomic-number-successor-progression__complete-chemical-trace-equivalence__return-of-observation-class",
        induction_base="The first repeated complete outer chemical trace at two ordered element coordinates supplies one recurrence class and one finite period witness.",
        induction_step="Appending one ordered element either extends the current nonreturning trace or closes a return to an existing complete class while preserving all prior witnesses.",
        exclusions=_exclusions(PERIODIC_RECURRENCE_BOUNDARY),
        operational_witnesses=(("return-equivalence", "recurrence requires equality of complete outer traces", True), ("successor-path", "every return retains its atomic-number path", True), ("fixed-period-control", "an assumed universal period is rejected", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-PERIODIC-RECURRENCE-001",
        expected_observation_label="recurrent-element-organization__ordered-periodic-table-support",
        target_rows=(_target("periodic-recurrence-iupac-2022", "IUPAC-PERIODIC-TABLE-2022", "recurrent long-form organization across the official table"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the official periodic source lacks recurrent ordered element organization at the registered boundary, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-GROUP-PERIOD-001",
        title="Group and period compositional coordinates",
        statement="A Fold group is an outer-chemical-trace equivalence class and a Fold period is its counted closure-to-reopening depth; their pair is independent of how a table is drawn.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-PERIODIC-ORDER-001", "SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001"),
        generation_rule="Generate the literal product of the registered coordinate carrier, group, period, pairing, ordering, equivalence, record and extension choices.",
        grammar_boundary=GROUP_PERIOD_BOUNDARY,
        dimensions=GROUP_PERIOD_DIMENSIONS,
        exact_result="periodic-element-carrier__outer-trace-equivalence-class__closure-reopening-depth__joint-group-period-coordinate",
        induction_base="One closed recurrence followed by one reopening supplies a first group class, period depth and joint coordinate witness.",
        induction_step="Appending one ordered element preserves its predecessor order and assigns exactly the existing or newly generated recurrence class at the counted depth.",
        exclusions=_exclusions(GROUP_PERIOD_BOUNDARY),
        operational_witnesses=(("coordinate-pair", "every classified element retains both coordinates", True), ("layout-invariance", "redrawing does not change complete trace equivalence", True), ("name-only-control", "a family name without a trace witness is rejected", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-GROUP-PERIOD-001",
        expected_observation_label="group-column-classes__period-row-progression__atomic-number-order-retained",
        target_rows=(_target("group-period-iupac-2022", "IUPAC-PERIODIC-TABLE-2022", "groups 1-18 and long-form period rows"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the official table does not retain column classes, row progression and atomic-number records together, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-VALENCE-001",
        title="Valence availability and chemical combination boundary",
        statement="Valence is the exact greatest realized univalent joining or substitution count in the complete generated combination support of a retained atom or fragment and chemical context.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001"),
        generation_rule="Generate the literal product of the registered valence carrier, support, unit, selection, substitution, context, record and extension choices.",
        grammar_boundary=VALENCE_BOUNDARY,
        dimensions=VALENCE_DIMENSIONS,
        exact_result="atom-or-fragment-carrier__complete-generated-combination-support__univalent-partner-count__maximum-realized-count",
        induction_base="One realized univalent combination supplies the first positive joining-count witness for one retained carrier and context.",
        induction_step="Appending one generated combination preserves all earlier witnesses and replaces the retained maximum exactly when the new realized count is later in the positive order.",
        exclusions=_exclusions(VALENCE_BOUNDARY),
        operational_witnesses=(("maximum-census", "the retained count is maximal over complete generated support", True), ("substitution", "lawful substitution is evaluated on the same carrier", True), ("typical-control", "a nonmaximal typical count is rejected", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-VALENCE-001",
        expected_observation_label="maximum-univalent-combination-count__atom-or-fragment-carrier__substitution-boundary",
        target_rows=(_target("valence-iupac-v06588", "IUPAC-GOLD-BOOK-V06588-2026", "term V06588, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC record lacks a maximum univalent combination count, atom/fragment carrier or substitution boundary, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-ION-001",
        title="Ion formation with retained elemental identity",
        statement="An ion is an atomic or molecular Fold particle whose closed electric-label transfer leaves a net held charge orientation while retaining its nuclear and chemical identity.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-VALENCE-001",),
        generation_rule="Generate the literal product of the registered ion carrier, charge, formation, conservation, element, orientation, record and extension choices.",
        grammar_boundary=ION_BOUNDARY,
        dimensions=ION_DIMENSIONS,
        exact_result="atomic-or-molecular-particle__net-held-electric-charge__label-transfer-with-identity-retained__closed-charge-transfer",
        induction_base="One atomic or molecular carrier with one conserved unmatched held electric orientation supplies the first ion record.",
        induction_step="Appending one paired charge-carrier transfer updates the exact net held count while preserving proton count, chemical carrier and the complete prior transfer trace.",
        exclusions=_exclusions(ION_BOUNDARY),
        operational_witnesses=(("identity", "charge transfer preserves the element proton count", True), ("conservation", "every charge change is paired to a boundary transfer", True), ("signed-control", "a negative proof magnitude is rejected in favor of a held orientation", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-ION-001",
        expected_observation_label="atomic-or-molecular-particle__net-electric-charge",
        target_rows=(_target("ion-iupac-i03158", "IUPAC-GOLD-BOOK-I03158-2026", "term I03158, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC ion record lacks an atomic-or-molecular particle and net electric charge, or if a changed row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-PERIODIC-BOUNDARY-001",
        title="Known periodic-table observation boundary",
        statement="The known periodic boundary is the complete source-dated IUPAC element census through its greatest listed atomic-number coordinate; it is an observation boundary and not a theorem forbidding successors.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-PERIODIC-ORDER-001", "SFT-CHEM-ELEM-GROUP-PERIOD-001", "SFT-CHEM-ELEM-ION-001"),
        generation_rule="Generate the literal product of the registered known-boundary carrier, extent, identity, time, completeness, extension, record and rule choices.",
        grammar_boundary=PERIODIC_BOUNDARY_BOUNDARY,
        dimensions=PERIODIC_BOUNDARY_DIMENSIONS,
        exact_result="complete-source-bounded-census__greatest-listed-coordinate__element-record-retained__unobserved-successor-open",
        induction_base="One official release with one complete listed element support supplies a finite observation census, not a terminal theorem.",
        induction_step="Appending one officially validated element extends the source-bounded greatest coordinate and retains all prior rows without changing the open-successor status.",
        exclusions=_exclusions(PERIODIC_BOUNDARY_BOUNDARY),
        operational_witnesses=(("complete-release", "all listed element rows remain in the source census", True), ("current-extent", "the greatest listed coordinate is source and date bound", True), ("terminal-control", "absence beyond the release is rejected as proof of impossibility", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-PERIODIC-BOUNDARY-001",
        expected_observation_label="source-bounded-known-element-census__greatest-listed-atomic-number-118",
        target_rows=(_target("periodic-boundary-iupac-2022", "IUPAC-PERIODIC-TABLE-2022", "complete release dated 4 May 2022 through oganesson, atomic number 118"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the registered official release does not contain the complete stated current census through atomic number 118, or if a changed row is accepted.",
    ),
)

for _spec in ELEMENTS_PERIODICITY_BATCH_2_SPECS:
    _spec.validate()


__all__ = (
    "ELEMENTS_PERIODICITY_BATCH_2_SPECS",
    "OBSERVATION_REGISTRY_PATH",
    "SOURCE_RECORDS",
)
