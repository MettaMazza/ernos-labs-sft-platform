"""Immutable first batch of elements-and-periodicity Chemistry laws.

These laws derive element identity, atomic-number order, isotope distinction
and the structural atomic-weight record before any periodic-table arrangement
or measured elemental value is opened.  Official IUPAC definitions are used
only by the post-seal validator.
"""

from __future__ import annotations

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.physics.generated_empirical_law import dimension


OBSERVATION_REGISTRY_PATH = (
    "experiments/external_sources/chemistry/observations_elements_periodicity_batch_1.json"
)

BASE_DEPENDENCIES = (
    "SFT-FOUNDATION-FORM-ENFORCEMENT-001",
    "SFT-MATH-EXACT-ARITHMETIC-001",
    "SFT-MATH-ORDER-LATTICE-001",
    "SFT-MATH-LOGIC-PROOF-001",
    "SFT-INFO-SYMBOL-DISTINCTION-001",
    "SFT-INFO-ENCODING-DECODING-001",
    "SFT-INFO-CONSERVATION-LOSS-001",
    "SFT-PHYS-MEAS-OBSERVATION-CARRIER-001",
    "SFT-PHYS-MEAS-QUANTITY-CARRIER-001",
    "SFT-PHYS-MEAS-VALUE-RECORD-001",
    "SFT-PHYS-MEAS-UNCERTAINTY-001",
    "SFT-PHYS-MATTER-CONSERVED-LABELS-001",
    "SFT-PHYS-MATTER-PARTICLE-SPECTRUM-001",
    "SFT-PHYS-NUCLEAR-LEVELS-001",
    "SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
    "SFT-CHEM-MEAS-CHEMICAL-SPECIES-001",
    "SFT-CHEM-MEAS-SUBSTANCE-001",
)

SOURCE_RECORDS = {
    "IUPAC-GOLD-BOOK-C01022-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/C01022/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/C01022.json",
        "snapshot_hash": "sha256:6d75c5b2d5299402b7f35243e248cb60d4972553d3bb622490236e7b889d9575",
    },
    "IUPAC-GOLD-BOOK-A00499-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/A00499/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/A00499.json",
        "snapshot_hash": "sha256:6ba53740329bcdde38d8a8734282fb9414a1c7e62fad09743d0890890ff3e127",
    },
    "IUPAC-GOLD-BOOK-I03331-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/I03331/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/I03331.json",
        "snapshot_hash": "sha256:7b5ca7fe293902804ca76194a6ac35a57a35bfa489245c93979eb81370a6635c",
    },
    "IUPAC-GOLD-BOOK-R05258-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/R05258/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/R05258.json",
        "snapshot_hash": "sha256:9a08b1dfe8699f2be546b1a0fcb9b359d49c78419099d853603c6c750a04f17a",
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
        "no IUPAC definition, periodic-table arrangement, measured element value or V2 answer may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no application result or opaque predictor",
        "official target content opens only through post-seal custody",
        boundary,
    )


ELEMENT_BOUNDARY = (
    "Every positive-finite atom-species class generated from one held nuclear proton-count identity, including "
    "all mass-number refinements and its separately recorded pure-substance correspondence."
)
ELEMENT_DIMENSIONS = (
    dimension("carrier", "substance-name-only", "A substance name does not define the atom class.", "atom-species-carrier", "The carrier is the complete generated class of atoms."),
    dimension("identity", "mass-selected-identity", "Mass can vary between isotopes of one element.", "common-proton-count", "One held proton count is common to every atom in the class."),
    dimension("location", "protons-without-nuclear-carrier", "An unlocated count does not preserve atomic constitution.", "nuclear-identity", "The common proton count is retained in the atomic nucleus record."),
    dimension("membership", "sampled-atom-list", "A sample cannot close the complete generated class.", "all-generated-atoms-with-identity", "Every generated atom with the held proton count belongs to the element class."),
    dimension("isotope", "one-mass-number-only", "Restricting an element to one mass number erases its isotopes.", "mass-refinement-permitted", "Mass number refines nuclides without changing element identity."),
    dimension("substance", "species-substance-conflation", "An atom species and a pure substance are related but not identical carriers.", "substance-carrier-correspondence", "The pure-substance use is retained as a separate correspondence."),
    dimension("record", "element-label-only", "A label alone cannot reproduce class membership.", "complete-nuclear-membership-trace", "Proton identity, atom membership and substance boundary remain held."),
    dimension("extension", "free-element-exception", "A discretionary exception can split or merge element classes.", "no-extra-rule", "The held nuclear count completely determines the class."),
)

ATOMIC_NUMBER_BOUNDARY = (
    "Every generated positive-finite nuclear proton collection and its one-to-one order coordinate over admitted "
    "chemical-element classes."
)
ATOMIC_NUMBER_DIMENSIONS = (
    dimension("carrier", "symbol-position-only", "A table position cannot define the nuclear quantity.", "exact-proton-count", "The number is the generated positive-finite count of protons."),
    dimension("location", "whole-atom-particle-count", "Counting every atomic particle changes across isotopes and charge states.", "nuclear-count-carrier", "Only protons in the atomic nucleus determine this coordinate."),
    dimension("order", "unordered-label", "An unordered label cannot supply periodic succession.", "positive-count-order", "Generated count succession gives an exact total order."),
    dimension("element_map", "many-elements-one-count", "Two element classes with one proton count violate their identity condition.", "one-count-one-element-class", "Each held proton count names exactly one element class."),
    dimension("isotope", "mass-dependent-number", "Mass-number variation must not alter element order.", "isotope-invariant", "Every isotope retains the same atomic number."),
    dimension("charge", "electron-count-dependent", "Ion formation changes electrons without changing the element.", "charge-state-invariant", "The proton count persists through admitted charge-state changes."),
    dimension("record", "number-without-nucleus", "A bare number loses the physical carrier and class mapping.", "count-nucleus-element-trace", "Count construction, nucleus and element class remain linked."),
    dimension("extension", "free-order-offset", "An offset can relabel the periodic order arbitrarily.", "no-extra-rule", "Generated count succession supplies the complete order."),
)

ISOTOPE_BOUNDARY = (
    "Every positive-finite family of admitted nuclides sharing one atomic-number identity while retaining each "
    "distinct generated mass-number coordinate and complete nuclear record."
)
ISOTOPE_DIMENSIONS = (
    dimension("carrier", "atom-label-without-nucleus", "An atom label alone does not establish nuclide identity.", "nuclide-carriers", "Each member retains its complete nuclear count record."),
    dimension("element", "mixed-atomic-numbers", "Different proton counts are different elements, not isotopes.", "element-identity-retained", "Every member shares one atomic number."),
    dimension("mass", "mass-number-erased", "Erasing mass number merges distinct nuclides.", "mass-number-distinction", "Each isotope retains its distinct nucleon-count coordinate."),
    dimension("neutron", "unrecorded-nuclear-difference", "The source of mass-number distinction cannot remain anonymous.", "complementary-nuclear-count-held", "The non-proton nuclear count remains a held coordinate."),
    dimension("chemistry", "different-element-chemistry", "Changing element identity does not define an isotope relation.", "common-element-chemistry-boundary", "Chemical element identity remains common while isotope effects may be observed separately."),
    dimension("observation", "always-indistinguishable", "Isotopic distinctions are resolvable in registered measurements.", "resolution-bounded-distinction", "The observation record states when mass distinction is retained."),
    dimension("record", "isotope-name-only", "A name cannot reconstruct proton and mass coordinates.", "complete-nuclide-family-trace", "Every family member retains both coordinates and class membership."),
    dimension("extension", "free-isotope-equivalence", "An arbitrary equivalence can merge different elements or erase mass distinctions.", "no-extra-rule", "Shared atomic number plus distinct mass number completely fixes the relation."),
)

ATOMIC_WEIGHT_BOUNDARY = (
    "Every finite source-bounded atom population with retained isotope membership, exact positive rational "
    "abundance parts, atomic-mass records and a separate unified-reference-unit comparison."
)
ATOMIC_WEIGHT_DIMENSIONS = (
    dimension("carrier", "decimal-answer-only", "A decimal answer hides population, isotope and reference provenance.", "exact-ratio-carrier", "The value is an exact ratio record before decimal reporting."),
    dimension("population", "single-atom-mass", "Atomic weight concerns a population average rather than an arbitrary single atom.", "average-atomic-mass", "The complete finite population and its parts determine the average."),
    dimension("isotopes", "isotope-mixture-erased", "Erasing isotope support loses the source of population variation.", "isotope-support-retained", "Every contributing isotope and abundance part remains held."),
    dimension("mass", "unbound-mass-labels", "Unbound masses cannot be paired with their isotope parts.", "isotope-mass-pairs", "Each atomic-mass record remains paired to its isotope carrier."),
    dimension("reference", "unit-as-derived-law", "A conventional unit scale cannot select the structural ratio.", "reference-unit-comparison", "The unified atomic mass unit remains a separate registered comparator."),
    dimension("source", "universal-fixed-composition", "Natural isotope composition can vary by source.", "source-bounded-population", "The population/source boundary remains explicit."),
    dimension("uncertainty", "exact-decimal-pretense", "A reported decimal must not erase its measurement interval.", "measurement-interval-retained", "Uncertainty remains a source-bound external record."),
    dimension("extension", "free-weight-adjustment", "An adjustable correction can force a measured target.", "no-extra-rule", "Population parts, mass records and reference comparison completely determine the record."),
)


ELEMENTS_PERIODICITY_BATCH_1_SPECS = (
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-ELEMENT-001",
        title="Chemical element identity",
        statement="A chemical element is the complete Fold class of generated atoms sharing one held nuclear proton count; isotope mass refinements preserve that identity, while pure-substance use remains a separate correspondence.",
        dependencies=BASE_DEPENDENCIES,
        generation_rule="Generate the literal product of the registered element carrier, identity, location, membership, isotope, substance, record and extension choices.",
        grammar_boundary=ELEMENT_BOUNDARY,
        dimensions=ELEMENT_DIMENSIONS,
        exact_result="atom-species-carrier__common-proton-count__nuclear-identity__substance-carrier-correspondence",
        induction_base="One admitted atom with one held nuclear proton count supplies the first element-class member.",
        induction_step="Appending one atom with the same proton count preserves element identity while retaining any distinct mass-number refinement and prior membership trace.",
        exclusions=_exclusions(ELEMENT_BOUNDARY),
        operational_witnesses=(("element-membership", "equal proton-count atoms enter one class", True), ("isotope-refinement", "mass-number variation preserves class identity", True), ("mass-identity-control", "mass alone is rejected as element identity", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-ELEMENT-001",
        expected_observation_label="atom-species-carrier__common-proton-count__nuclear-identity__substance-carrier-correspondence",
        target_rows=(_target("chemical-element-iupac-c01022", "IUPAC-GOLD-BOOK-C01022-2026", "term C01022, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC element record lacks an atom-species carrier, common proton count, nuclear identity or pure-substance correspondence, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-ATOMIC-NUMBER-001",
        title="Atomic-number ordering and element distinction",
        statement="Atomic number is the exact generated positive-finite count of protons in an atom's nucleus and therefore the unique order coordinate of its chemical-element class.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-ELEMENT-001",),
        generation_rule="Generate the literal product of the registered atomic-number carrier, location, order, element map, isotope, charge, record and extension choices.",
        grammar_boundary=ATOMIC_NUMBER_BOUNDARY,
        dimensions=ATOMIC_NUMBER_DIMENSIONS,
        exact_result="exact-proton-count__nuclear-count-carrier",
        induction_base="One nuclear proton supplies the first generated atomic-number count and one element-class coordinate.",
        induction_step="Appending one proton extends the exact count order while preserving every earlier count/class distinction without an offset.",
        exclusions=_exclusions(ATOMIC_NUMBER_BOUNDARY),
        operational_witnesses=(("count-order", "successor proton collections are strictly ordered", True), ("isotope-invariance", "mass-number change leaves proton count fixed", True), ("electron-control", "electron count is rejected as element order", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-ATOMIC-NUMBER-001",
        expected_observation_label="exact-proton-count__nuclear-count-carrier",
        target_rows=(_target("atomic-number-iupac-a00499", "IUPAC-GOLD-BOOK-A00499-2026", "term A00499, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC atomic-number record is not the proton count in the atomic nucleus, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-ISOTOPE-001",
        title="Isotope identity within an element",
        statement="Isotopes are the generated Fold family of nuclide carriers sharing one atomic number while retaining different exact mass-number coordinates.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-ELEM-ELEMENT-001", "SFT-CHEM-ELEM-ATOMIC-NUMBER-001"),
        generation_rule="Generate the literal product of the registered isotope carrier, element, mass, complementary nuclear count, chemistry, observation, record and extension choices.",
        grammar_boundary=ISOTOPE_BOUNDARY,
        dimensions=ISOTOPE_DIMENSIONS,
        exact_result="nuclide-carriers__element-identity-retained__mass-number-distinction",
        induction_base="Two generated nuclide records sharing one proton count and retaining distinct mass numbers supply the first isotope distinction.",
        induction_step="Appending one nuclide with the same atomic number and a new mass-number coordinate extends the family without changing element identity or erasing prior members.",
        exclusions=_exclusions(ISOTOPE_BOUNDARY),
        operational_witnesses=(("shared-element", "equal atomic numbers preserve one element class", True), ("mass-distinction", "different mass numbers remain separate nuclides", True), ("mixed-element-control", "different atomic numbers are rejected", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-ISOTOPE-001",
        expected_observation_label="nuclide-carriers__element-identity-retained__mass-number-distinction",
        target_rows=(_target("isotopes-iupac-i03331", "IUPAC-GOLD-BOOK-I03331-2026", "term I03331, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC isotope record does not retain nuclides, common atomic number and distinct mass numbers, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-ELEM-ATOMIC-WEIGHT-001",
        title="Atomic-weight record and isotopic composition boundary",
        statement="Relative atomic mass is the exact source-bounded Fold ratio of a finite atom population's retained average mass to a separately registered unified atomic-mass reference, with isotope support and measurement uncertainty preserved.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-AMOUNT-001", "SFT-CHEM-MEAS-TRACEABILITY-001", "SFT-CHEM-ELEM-ISOTOPE-001"),
        generation_rule="Generate the literal product of the registered atomic-weight carrier, population, isotope support, mass pairs, reference, source, uncertainty and extension choices.",
        grammar_boundary=ATOMIC_WEIGHT_BOUNDARY,
        dimensions=ATOMIC_WEIGHT_DIMENSIONS,
        exact_result="exact-ratio-carrier__average-atomic-mass__reference-unit-comparison",
        induction_base="One source-bounded atom population with retained isotope/mass records and one reference-unit comparison supplies the first relative atomic-mass record.",
        induction_step="Appending one registered isotope population part preserves the exact weighted total, every prior pair, source boundary, uncertainty and separate reference comparison.",
        exclusions=_exclusions(ATOMIC_WEIGHT_BOUNDARY),
        operational_witnesses=(("population-average", "isotope parts and paired masses reconstruct the average", True), ("source-boundary", "changed isotopic composition remains a distinct record", True), ("decimal-only-control", "an untraced decimal is rejected", True)),
        experiment_id="SFT-EXP-CHEM-ELEM-ATOMIC-WEIGHT-001",
        expected_observation_label="exact-ratio-carrier__average-atomic-mass__reference-unit-comparison",
        target_rows=(_target("relative-atomic-mass-iupac-r05258", "IUPAC-GOLD-BOOK-R05258-2026", "term R05258, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC relative-atomic-mass record lacks a ratio, average atomic mass or unified atomic-mass reference, or if an altered row is accepted.",
    ),
)

for _spec in ELEMENTS_PERIODICITY_BATCH_1_SPECS:
    _spec.validate()


__all__ = (
    "ELEMENTS_PERIODICITY_BATCH_1_SPECS",
    "OBSERVATION_REGISTRY_PATH",
    "SOURCE_RECORDS",
)
