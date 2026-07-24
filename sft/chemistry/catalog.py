"""Dependency-ordered Chemistry specifications that are ready for execution.

The frozen branch inventory is intentionally larger than this module.  A claim
enters ``CHEMISTRY_SPECS`` only when it has a content-specific generated grammar
and a source-derived target whose content is absent from this derivation file.
There is no generic fallback that can manufacture apparent closure.
"""

from __future__ import annotations

import json
from pathlib import Path

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.chemistry.obligations import OBLIGATIONS
from sft.physics.generated_empirical_law import dimension


ROOT = Path(__file__).resolve().parents[2]
SOURCE_REGISTRY = json.loads(
    (ROOT / "experiments/external_sources/chemistry/authoritative_sources.json").read_text(encoding="utf-8")
)
SOURCES = {row["source_id"]: row for row in SOURCE_REGISTRY["sources"]}
OBSERVATION_REGISTRY_PATH = "experiments/external_sources/chemistry/observations.json"

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
)


def _target(target_id: str, source_id: str, locator: str) -> ChemistryTargetReference:
    source = SOURCES[source_id]
    return ChemistryTargetReference(
        target_id=target_id,
        source_id=source_id,
        source_locator=source["source_uri"] + " :: " + locator,
        snapshot_path=source["snapshot_path"],
        snapshot_hash=source["snapshot_hash"],
    )


def _common_exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no IUPAC definition, conventional chemistry model or target content may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no application result or opaque predictor",
        "external target content is absent from this specification and opens only through post-seal custody",
        boundary,
    )


ENTITY_BOUNDARY = (
    "Every finite singular chemical carrier formed from admitted distinctions and any generated positive-finite "
    "extension of its constitution, isotope, state or contextual precision record."
)
ENTITY_DIMENSIONS = (
    dimension("carrier", "ensemble-without-member", "An ensemble alone does not identify one chemical entity.", "singular-carrier", "One entity is one retained carrier before any ensemble quotient."),
    dimension("constitution", "constitution-erased", "Erasing constitution merges chemically distinct carriers.", "constitution-retained", "Constitution is a required chemical identity coordinate."),
    dimension("isotope", "isotope-erased", "Erasing isotopic identity merges distinguishable entities.", "isotope-retained", "Isotopic distinction remains available whenever the observation resolves it."),
    dimension("distinction", "indistinguishable-answer-label", "An answer label without a retained distinction cannot identify an entity.", "separately-distinguishable", "The carrier must remain separately distinguishable at the registered observation boundary."),
    dimension("precision", "unbounded-or-fixed-precision", "A fixed universal precision either loses a required distinction or adds an unforced one.", "context-bounded-precision", "Only distinctions required by the declared observation context are retained."),
    dimension("record", "result-without-observation-record", "Without an observation record the identity boundary cannot be audited.", "held-observation-record", "The observation class and retained coordinates remain held."),
    dimension("provenance", "unbound-provenance", "Unbound identity cannot be traced to the Fold dependency spine.", "source-bound-proof-trace", "The derivation and later correspondence retain separate source identities."),
    dimension("extension", "free-extra-identity-rule", "An extra identity rule can arbitrarily split or merge entities.", "no-extra-rule", "Generated distinctions alone determine the identity carrier."),
)

SPECIES_BOUNDARY = (
    "Every finite observation-equivalence class formed from admitted singular chemical entities under an exact "
    "declared experiment-timescale relation and any positive-finite successor extension."
)
SPECIES_DIMENSIONS = (
    dimension("carrier", "singular-only", "One member alone is not a chemical species class.", "ensemble-carrier", "A species is the generated support of equivalent chemical entities."),
    dimension("member_identity", "mixed-chemical-identities", "Mixed chemical identities do not form one species.", "chemical-identity-equivalence", "Every member preserves the same registered chemical identity coordinates."),
    dimension("support", "energy-support-erased", "Erasing accessible-state support merges experimentally distinct species.", "shared-energy-support", "Members share the same accessible molecular energy support at the boundary."),
    dimension("timescale", "timeless-equivalence", "Interconversion can change whether two forms are experimentally distinct.", "experiment-timescale-boundary", "The observation timescale is retained as part of the equivalence relation."),
    dimension("solid_support", "isolated-molecule-only", "A species law limited to isolable molecules loses solid structural units.", "molecular-or-solid-unit-support", "The carrier permits molecular and solid-array structural units."),
    dimension("record", "class-without-member-trace", "A quotient without member trace cannot be reconstructed.", "held-member-and-class-record", "Members and their observation quotient remain separately auditable."),
    dimension("provenance", "unbound-provenance", "An unbound class can silently change its equivalence rule.", "source-bound-proof-trace", "The generated relation and external record retain distinct identities."),
    dimension("extension", "free-extra-equivalence", "A discretionary equivalence can force any desired species partition.", "no-extra-rule", "Only generated identity, support and timescale determine the class."),
)

SUBSTANCE_BOUNDARY = (
    "Every finite chemical substance carrier formed from one generated constant-composition support of chemical "
    "entities plus any positive-finite extension of its source-bound property record."
)
SUBSTANCE_DIMENSIONS = (
    dimension("composition", "variable-unrecorded-composition", "Unrecorded variable composition cannot identify one substance.", "constant-composition", "The constituent relation is held constant at the declared identity boundary."),
    dimension("constituents", "anonymous-matter", "Matter without retained constituent entities loses chemical identity.", "constituent-entity-support", "Atoms, molecules or formula units remain the composition carriers."),
    dimension("properties", "composition-only-answer", "Composition alone can leave observation-equivalent candidates unresolved.", "property-characterization", "Registered physical-property observations characterize the substance carrier."),
    dimension("source", "source-free-substance-label", "A source-free label cannot distinguish sample and convention boundaries.", "source-bounded-substance-identity", "The substance identity retains its sample/reference source boundary."),
    dimension("phase", "phase-silently-collapsed", "Silently collapsing phase can erase an observed substance distinction.", "phase-record-retained", "Phase is retained whenever it participates in the registered observation class."),
    dimension("record", "property-selection-only", "Selecting one favorable property is not a complete characterization record.", "complete-property-record", "Every registered favorable and unfavorable property row is retained."),
    dimension("provenance", "unbound-provenance", "Unbound composition and property claims cannot be audited.", "source-bound-proof-trace", "Derivation and external characterization remain separately source-bound."),
    dimension("extension", "free-extra-substance-rule", "A discretionary rule can split or merge substances after observation.", "no-extra-rule", "Generated composition and observation distinctions alone determine the carrier."),
)


CHEMISTRY_SPECS = (
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",
        title="Chemical entity and retained identity",
        statement=(
            "A chemical entity is the least singular Fold carrier that remains separately distinguishable after "
            "constitution, isotopic identity and the observation context's required precision are retained."
        ),
        dependencies=BASE_DEPENDENCIES,
        generation_rule="Generate the literal product of the registered entity carrier, constitution, isotope, distinction, precision, record, provenance and extension choices.",
        grammar_boundary=ENTITY_BOUNDARY,
        dimensions=ENTITY_DIMENSIONS,
        exact_result="singular-carrier__constitution-and-isotope-retained__separately-distinguishable__context-bounded-precision",
        induction_base="One registered chemical carrier retains one constitution/isotope/context identity record.",
        induction_step="Adding one generated identity coordinate preserves the singular carrier and every earlier distinction without installing a new equivalence rule.",
        exclusions=_common_exclusions(ENTITY_BOUNDARY),
        operational_witnesses=(("entity-distinction", "constitutionally distinct carriers remain distinct", True), ("entity-context", "context may require an additional retained state coordinate", True), ("entity-collapse-control", "erased identity coordinate is rejected", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-CHEMICAL-ENTITY-001",
        expected_observation_label="singular-carrier__constitution-and-isotope-retained__separately-distinguishable__context-bounded-precision",
        target_rows=(_target("chemical-entity-iupac-m03986", "IUPAC-GOLD-BOOK-M03986-2026", "term M03986, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the current source-derived IUPAC entity record lacks singular distinguishability, constitution/isotope identity or contextual precision, or if any altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-CHEMICAL-SPECIES-001",
        title="Chemical species and observation-equivalence class",
        statement=(
            "A chemical species is the least Fold quotient whose support is an ensemble of chemically identical "
            "entities sharing accessible state support at one declared experimental timescale."
        ),
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-CHEMICAL-ENTITY-001",),
        generation_rule="Generate the literal product of the registered species carrier, member identity, state support, timescale, solid support, record, provenance and extension choices.",
        grammar_boundary=SPECIES_BOUNDARY,
        dimensions=SPECIES_DIMENSIONS,
        exact_result="ensemble-carrier__chemical-identity-equivalence__shared-energy-support__experiment-timescale-boundary",
        induction_base="One admitted chemical entity supplies the first member of one exact observation-equivalence class.",
        induction_step="Adding one chemically identical entity with the same accessible support preserves the class at the declared experimental timescale.",
        exclusions=_common_exclusions(SPECIES_BOUNDARY),
        operational_witnesses=(("species-ensemble", "two equivalent entity members form one retained class", True), ("species-timescale", "changed observational timescale may refine the class", True), ("species-mixed-control", "a chemically distinct member is rejected", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-CHEMICAL-SPECIES-001",
        expected_observation_label="ensemble-carrier__chemical-identity-equivalence__shared-energy-support__experiment-timescale-boundary",
        target_rows=(_target("chemical-species-iupac-ct01038", "IUPAC-GOLD-BOOK-CT01038-2026", "term CT01038, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC species record does not retain ensemble identity, common accessible support and experimental timescale, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-SUBSTANCE-001",
        title="Chemical substance and composition identity",
        statement=(
            "A chemical substance is the least source-bounded Fold carrier that retains constant composition, "
            "its constituent entity support and the complete registered property characterization."
        ),
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-CHEMICAL-ENTITY-001", "SFT-CHEM-MEAS-CHEMICAL-SPECIES-001"),
        generation_rule="Generate the literal product of the registered substance composition, constituents, properties, source, phase, record, provenance and extension choices.",
        grammar_boundary=SUBSTANCE_BOUNDARY,
        dimensions=SUBSTANCE_DIMENSIONS,
        exact_result="constant-composition__constituent-entity-support__property-characterization__source-bounded-substance-identity",
        induction_base="One constant-composition entity support with one registered property record supplies a substance carrier.",
        induction_step="Adding one generated constituent or property observation preserves composition and source identity while retaining every earlier row.",
        exclusions=_common_exclusions(SUBSTANCE_BOUNDARY),
        operational_witnesses=(("substance-composition", "constant constituent composition reconstructs the carrier", True), ("substance-property", "a registered property refines characterization without selecting the law", True), ("substance-variable-control", "unrecorded variable composition is rejected", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-SUBSTANCE-001",
        expected_observation_label="constant-composition__constituent-entity-support__property-characterization__source-bounded-substance-identity",
        target_rows=(_target("chemical-substance-iupac-c01039", "IUPAC-GOLD-BOOK-C01039-2026", "term C01039, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC substance record lacks constant composition, constituent entities or property characterization, or if an altered row is accepted.",
    ),
)

for _spec in CHEMISTRY_SPECS:
    _spec.validate()

_ready_ids = {spec.claim_id for spec in CHEMISTRY_SPECS}
PENDING_CHEMISTRY_CLAIM_IDS = tuple(row.claim_id for row in OBLIGATIONS if row.claim_id not in _ready_ids)

__all__ = (
    "BASE_DEPENDENCIES",
    "CHEMISTRY_SPECS",
    "PENDING_CHEMISTRY_CLAIM_IDS",
)
