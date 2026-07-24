"""Immutable second batch of Chemistry measurement-and-identity laws.

The first three Chemistry admissions bind ``catalog.py`` and
``observations.json`` into immutable derivation and empirical identities.  This
module therefore contains only the next five content-specific laws, and its
targets are reconstructed from a separate post-seal observation batch.  No
official definition or observed feature label is loaded by this module.
"""

from __future__ import annotations

from sft.chemistry.generated_law import ChemistryTargetReference, EmpiricalChemistrySpec
from sft.physics.generated_empirical_law import dimension


OBSERVATION_REGISTRY_PATH = (
    "experiments/external_sources/chemistry/observations_measurement_identity_batch_2.json"
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
)

SOURCE_RECORDS = {
    "IUPAC-GOLD-BOOK-A00297-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/A00297/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/A00297.json",
        "snapshot_hash": "sha256:ddf59230caa12b510125795af6f624797e904a1724fe970b3c144af47167077e",
    },
    "IUPAC-GOLD-BOOK-M03987-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/M03987/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/M03987.json",
        "snapshot_hash": "sha256:b33959596338e0e2797247c379e8214ecd6a58abd3e929a4dfad36f42b081704",
    },
    "IUPAC-GOLD-BOOK-S06236-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/S06236/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/S06236.json",
        "snapshot_hash": "sha256:a3163fe9e9694283c7280d87679fb49286dd44631d908c19fcc164ce8f2984ac",
    },
    "IUPAC-GOLD-BOOK-08133-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/08133/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/08133.json",
        "snapshot_hash": "sha256:014b6b034695f2b25c07cd4e5474b856aeecf8907e4022595cc93df2f6674dc1",
    },
    "IUPAC-GOLD-BOOK-08013-2026": {
        "body": "International Union of Pure and Applied Chemistry",
        "source_uri": "https://goldbook.iupac.org/terms/view/08013/json",
        "snapshot_path": "experiments/external_sources/chemistry/snapshots/goldbook-terms/08013.json",
        "snapshot_hash": "sha256:34656c42ec7d741c00a0006b462487115d51dcd3d918d2fa64982ce100e24868",
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


def _common_exclusions(boundary: str) -> tuple[str, ...]:
    return (
        "no IUPAC definition, conventional chemistry model or target content may select a candidate",
        "no numerical zero, negative, irrational, imaginary or floating proof quantity",
        "no free, fitted, learned or target-derived parameter",
        "no application result or opaque predictor",
        "external target content is absent from this specification and opens only through post-seal custody",
        boundary,
    )


AMOUNT_BOUNDARY = (
    "Every positive-finite generated collection of one specified admitted chemical-entity kind, together with "
    "its exact member/reference trace and separately registered unit comparison."
)
AMOUNT_DIMENSIONS = (
    dimension("carrier", "answer-only-amount", "An answer label does not retain the entities being counted.", "amount-carrier", "The quantity remains attached to a generated chemical collection."),
    dimension("entity_reference", "unspecified-entities", "A count without a specified elementary-entity kind changes meaning under substitution.", "specified-entity-reference", "One held reference identifies the elementary entity kind."),
    dimension("count", "mass-proxy-count", "A mass proxy can vary with isotope and cannot establish entity cardinality.", "generated-cardinality", "The exact positive-finite member construction fixes cardinality."),
    dimension("measure", "unrelated-count-and-quantity", "An unrelated quantity does not measure how many referenced entities occur.", "count-measure", "Amount is the measure carried by the generated entity count."),
    dimension("support", "single-presupposed-entity-kind", "Presupposing one conventional entity kind excludes other generated elementary carriers.", "generated-entity-support", "Atoms, molecules, ions, electrons, particles and specified groups enter through the same held-reference form."),
    dimension("record", "total-without-members", "A total without its entity reference cannot be independently reconstructed.", "member-and-reference-trace", "The member construction and entity kind remain auditable."),
    dimension("unit", "unit-scale-as-proof", "A conventional scale cannot select the amount law.", "separate-unit-comparison", "The exact count relation is derived before any unit realization."),
    dimension("extension", "free-amount-factor", "An extra multiplier is a free answer-selecting parameter.", "no-extra-rule", "Generated membership and the held entity reference completely fix the amount carrier."),
)

FORMULA_BOUNDARY = (
    "Every positive-finite discrete-molecule composition word generated from admitted entity labels, exact "
    "multiplicities and a held structural-order record."
)
FORMULA_DIMENSIONS = (
    dimension("domain", "unbounded-object-label", "A formula without a declared chemical carrier domain can encode unrelated objects.", "discrete-molecule-domain", "The molecular-formula claim is bounded to compounds formed from discrete molecules."),
    dimension("carrier", "name-only-string", "A name alone does not retain exact constituent multiplicity.", "formula-encoding", "The formula is a generated composition word."),
    dimension("constituents", "anonymous-symbols", "Anonymous symbols erase chemical-entity identity.", "held-entity-symbols", "Every constituent symbol refers to an admitted entity class."),
    dimension("multiplicity", "unrecorded-repetition", "Unrecorded repetition cannot reconstruct composition or relative mass.", "exact-positive-multiplicity", "Each constituent has an exact generated positive count."),
    dimension("mass", "mass-unrelated-to-composition", "A mass label not reconstructed from the constituent record is not a formula consequence.", "composition-mass-correspondence", "Relative molecular mass is determined by the retained composition record at the comparison boundary."),
    dimension("structure", "order-erased", "Equal counts can represent distinct molecular structures.", "structure-correspondence", "A held order/adjacency record distinguishes structural encodings when required."),
    dimension("decode", "nondecodable-inscription", "An inscription that cannot return its constituent record is not an exact encoding.", "composition-decodable", "Decoding returns every held entity, count and structural coordinate."),
    dimension("extension", "free-formula-exception", "A discretionary exception can manufacture a desired formula.", "no-extra-rule", "Generated symbols, counts and held order supply the complete formula."),
)

NOMENCLATURE_BOUNDARY = (
    "Every positive-finite ordered chemical-name word assembled wholly from registered syllable labels and "
    "optional generated count prefixes, with an explicit injective-decoding boundary."
)
NOMENCLATURE_DIMENSIONS = (
    dimension("carrier", "partial-name-fragment", "A fragment alone does not carry one complete registered chemical name.", "complete-name-carrier", "The name is one complete ordered carrier."),
    dimension("parts", "unregistered-free-text", "Free text can import arbitrary answer-bearing distinctions.", "generated-name-parts", "Every part is a registered coined or selected syllable label."),
    dimension("prefix", "implicit-count", "An implicit multiplicity cannot be recovered from the name.", "count-prefix-support", "Optional numerical prefixes are generated exact count labels."),
    dimension("order", "unordered-syllable-bag", "Unordered parts can merge names with distinct composition.", "held-name-order", "Every syllable retains its generated position."),
    dimension("binding", "name-detached-from-formula", "A detached name cannot preserve chemical identity.", "formula-bound-name", "The name record is bound to the admitted formula carrier."),
    dimension("decode", "unconditional-reversibility", "Not every conventional name is uniquely decodable, so reversibility cannot be assumed.", "injective-boundary-decoding", "Reversibility is claimed exactly when one name maps to one retained identity record."),
    dimension("record", "surface-name-only", "A surface name alone hides its assembly and decoding boundary.", "complete-name-trace", "Parts, order, prefixes, formula binding and decoder result remain held."),
    dimension("extension", "free-naming-exception", "A discretionary naming exception can select any desired identity.", "no-extra-rule", "Only registered parts, order and count-prefix construction are admitted."),
)

UNCERTAINTY_BOUNDARY = (
    "Every source-bounded finite chemical measurement record whose unresolved alternatives, exact upper bound, "
    "intended use and result identity are retained without entering the derivation as proof values."
)
UNCERTAINTY_DIMENSIONS = (
    dimension("carrier", "single-answer-without-resolution", "A lone answer erases the unresolved observation class.", "uncertainty-carrier", "The record retains the measurement and its resolution boundary."),
    dimension("alternatives", "discarded-alternatives", "Discarding compatible alternatives falsely turns resolution into exact identity.", "retained-alternative-class", "Every alternative admitted by the registered resolution remains held."),
    dimension("bound", "unbounded-vagueness", "Unbounded uncertainty cannot falsify a measured correspondence.", "upper-bound-support", "The registered target uncertainty is an exact upper-limit record."),
    dimension("use", "context-free-resolution", "Required resolution depends on the declared purpose of the result.", "use-bounded-resolution", "The intended use fixes the acceptable observation class before evaluation."),
    dimension("result", "bound-detached-from-result", "A bound detached from its result cannot be applied or audited.", "result-record-boundary", "The uncertainty remains bound to the exact measurement-result identity."),
    dimension("source", "source-free-bound", "A source-free bound can be changed after comparison.", "source-bound-uncertainty", "Source, method and registered boundary remain held."),
    dimension("record", "favourable-row-only", "Selected rows cannot test uncertainty transport.", "complete-uncertainty-record", "Every registered result, bound and unfavorable control is retained."),
    dimension("extension", "free-uncertainty-margin", "An adjustable margin can force agreement with any target.", "no-extra-rule", "Only the preregistered resolution and use boundary are admitted."),
)

TRACEABILITY_BOUNDARY = (
    "Every positive-finite certified chemical-property chain whose reference material, property identity, "
    "uncertainty, predecessor links and certificate record are retained to an admitted reference realization."
)
TRACEABILITY_DIMENSIONS = (
    dimension("property", "value-without-property", "A value without a property identity cannot be traced.", "reference-material-property", "The record binds one property to one reference material."),
    dimension("reference", "anonymous-reference", "An anonymous comparison object cannot anchor a trace chain.", "identified-reference-realization", "Every chain terminates at an admitted identified reference realization."),
    dimension("uncertainty", "uncertainty-erased", "Erasing uncertainty overstates what each comparison preserves.", "uncertainty-retained", "Every comparison retains its associated uncertainty record."),
    dimension("trace", "broken-predecessor-chain", "A missing predecessor prevents reconstruction to the reference.", "traceability-retained", "Every calibration or examination link retains its predecessor identity."),
    dimension("certificate", "uncertified-result-label", "A result label alone does not bind property, reference and trace.", "certificate-bound-record", "The certificate binds the complete property and trace record."),
    dimension("identity", "substitutable-sample", "Silent sample substitution breaks traceability while preserving a surface value.", "material-identity-held", "Reference-material and sample identities remain distinct and held."),
    dimension("record", "terminal-value-only", "A terminal value cannot reproduce the chain.", "complete-chain-record", "Every link, uncertainty and certificate identity is retained."),
    dimension("extension", "free-trace-link", "An unregistered link can hide a discontinuity.", "no-extra-rule", "Only registered predecessor links extend the trace chain."),
)


MEASUREMENT_IDENTITY_BATCH_2_SPECS = (
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-AMOUNT-001",
        title="Amount-of-substance count and reference carrier",
        statement="Amount of substance is the exact Fold measure carried by a positive-finite generated count of one specified elementary-entity kind, with the entity reference and count trace retained.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-SUBSTANCE-001",),
        generation_rule="Generate the literal product of the registered amount carrier, entity reference, count, measure, support, record, unit and extension choices.",
        grammar_boundary=AMOUNT_BOUNDARY,
        dimensions=AMOUNT_DIMENSIONS,
        exact_result="amount-carrier__count-measure__specified-entity-reference__generated-entity-support",
        induction_base="One admitted specified chemical entity supplies the first exact amount carrier and its complete reference trace.",
        induction_step="Appending one generated entity of the same held kind extends cardinality while preserving the reference, prior members and separate unit boundary.",
        exclusions=_common_exclusions(AMOUNT_BOUNDARY),
        operational_witnesses=(("entity-reference", "one held kind remains attached to every generated member", True), ("count-successor", "one appended member extends exact cardinality", True), ("mass-proxy-control", "isotope-dependent mass is rejected as entity count", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-AMOUNT-001",
        expected_observation_label="amount-carrier__count-measure__specified-entity-reference__generated-entity-support",
        target_rows=(_target("amount-of-substance-iupac-a00297", "IUPAC-GOLD-BOOK-A00297-2026", "term A00297, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC amount record lacks number measure, specified entities or general elementary-entity support, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-FORMULA-001",
        title="Chemical formula as exact composition encoding",
        statement="A molecular formula is the least decodable Fold word that retains a discrete molecule's constituent entity labels, exact positive multiplicities and any structure coordinate required by the declared identity boundary.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-CHEMICAL-ENTITY-001", "SFT-CHEM-MEAS-CHEMICAL-SPECIES-001", "SFT-CHEM-MEAS-SUBSTANCE-001", "SFT-CHEM-MEAS-AMOUNT-001"),
        generation_rule="Generate the literal product of the registered formula domain, carrier, constituents, multiplicity, mass, structure, decoding and extension choices.",
        grammar_boundary=FORMULA_BOUNDARY,
        dimensions=FORMULA_DIMENSIONS,
        exact_result="discrete-molecule-domain__formula-encoding__composition-mass-correspondence__structure-correspondence",
        induction_base="One admitted entity label with one generated multiplicity supplies the first decodable molecular-composition word.",
        induction_step="Appending one held entity/count coordinate preserves every prior constituent and extends composition, relative-mass and optional structure reconstruction.",
        exclusions=_common_exclusions(FORMULA_BOUNDARY),
        operational_witnesses=(("formula-decode", "held entity/count pairs reconstruct composition", True), ("formula-structure", "held adjacency distinguishes equal-composition structures", True), ("name-only-control", "a name without counts is rejected as formula", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-FORMULA-001",
        expected_observation_label="discrete-molecule-domain__formula-encoding__composition-mass-correspondence__structure-correspondence",
        target_rows=(_target("molecular-formula-iupac-m03987", "IUPAC-GOLD-BOOK-M03987-2026", "term M03987, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC molecular-formula record lacks its discrete-molecule domain, formula carrier, relative-mass or structure correspondence, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-NOMENCLATURE-001",
        title="Reversible chemical nomenclature and identity boundary",
        statement="A systematic chemical name is a complete ordered Fold word assembled from registered name parts and optional count prefixes; exact reversibility is admitted only on the generated injective name-to-identity boundary.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-FORMULA-001",),
        generation_rule="Generate the literal product of the registered name carrier, parts, prefix, order, formula binding, decoding, record and extension choices.",
        grammar_boundary=NOMENCLATURE_BOUNDARY,
        dimensions=NOMENCLATURE_DIMENSIONS,
        exact_result="complete-name-carrier__generated-name-parts__count-prefix-support",
        induction_base="One registered syllable label supplies the first complete one-part systematic name and its assembly trace.",
        induction_step="Appending one registered syllable or generated count prefix preserves order, formula binding and injective decoding wherever uniqueness remains certified.",
        exclusions=_common_exclusions(NOMENCLATURE_BOUNDARY),
        operational_witnesses=(("name-assembly", "ordered registered syllables generate a complete name", True), ("prefix-count", "optional prefixes retain exact multiplicity", True), ("noninjective-control", "ambiguous name-to-identity maps are excluded from reversible scope", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-NOMENCLATURE-001",
        expected_observation_label="complete-name-carrier__generated-name-parts__count-prefix-support",
        target_rows=(_target("systematic-name-iupac-s06236", "IUPAC-GOLD-BOOK-S06236-2026", "term S06236, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC systematic-name record lacks complete name composition, selected syllable parts or optional numerical prefixes, or if reversibility is claimed outside the registered injective boundary.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-UNCERTAINTY-001",
        title="Chemical measurement uncertainty and retained alternatives",
        statement="Chemical target uncertainty is a source-bound Fold record of unresolved measurement alternatives with a preregistered upper limit fixed by intended use and attached to the exact result identity.",
        dependencies=BASE_DEPENDENCIES + ("SFT-CHEM-MEAS-AMOUNT-001",),
        generation_rule="Generate the literal product of the registered uncertainty carrier, alternatives, bound, use, result, source, record and extension choices.",
        grammar_boundary=UNCERTAINTY_BOUNDARY,
        dimensions=UNCERTAINTY_DIMENSIONS,
        exact_result="uncertainty-carrier__upper-bound-support__use-bounded-resolution__result-record-boundary",
        induction_base="One source-bound measurement result and one retained compatible-alternative class supply the first exact uncertainty record.",
        induction_step="Adding one registered result or compatible alternative preserves its source, intended-use bound and every prior row without widening the margin after target release.",
        exclusions=_common_exclusions(UNCERTAINTY_BOUNDARY),
        operational_witnesses=(("alternative-class", "compatible results remain retained rather than collapsed", True), ("use-bound", "the intended use fixes the upper limit before evaluation", True), ("adjustable-margin-control", "post-release widening is rejected", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-UNCERTAINTY-001",
        expected_observation_label="uncertainty-carrier__upper-bound-support__use-bounded-resolution__result-record-boundary",
        target_rows=(_target("target-uncertainty-iupac-08133", "IUPAC-GOLD-BOOK-08133-2026", "term 08133, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC target-uncertainty record lacks an upper limit, intended-use boundary or measurement-result attachment, or if an altered row is accepted.",
    ),
    EmpiricalChemistrySpec(
        claim_id="SFT-CHEM-MEAS-TRACEABILITY-001",
        title="Chemical reference traceability and complete record",
        statement="Chemical traceability is the complete Fold predecessor chain binding a property value to an identified reference material while retaining uncertainty, material identity and its certificate record at every link.",
        dependencies=BASE_DEPENDENCIES + ("SFT-PHYS-MEAS-REFERENCE-REALIZATION-001", "SFT-PHYS-MEAS-CALIBRATION-001", "SFT-CHEM-MEAS-UNCERTAINTY-001"),
        generation_rule="Generate the literal product of the registered property, reference, uncertainty, trace, certificate, identity, record and extension choices.",
        grammar_boundary=TRACEABILITY_BOUNDARY,
        dimensions=TRACEABILITY_DIMENSIONS,
        exact_result="reference-material-property__uncertainty-retained__traceability-retained__certificate-bound-record",
        induction_base="One identified reference material, property value, uncertainty record and certificate supply the first complete traceable record.",
        induction_step="Appending one registered comparison link retains predecessor identity, associated uncertainty, material identity and certificate provenance to the same reference realization.",
        exclusions=_common_exclusions(TRACEABILITY_BOUNDARY),
        operational_witnesses=(("trace-chain", "every comparison link retains its predecessor", True), ("certificate-binding", "property, reference, uncertainty and trace share one certificate record", True), ("silent-substitution-control", "changed material identity breaks the chain", True)),
        experiment_id="SFT-EXP-CHEM-MEAS-TRACEABILITY-001",
        expected_observation_label="reference-material-property__uncertainty-retained__traceability-retained__certificate-bound-record",
        target_rows=(_target("certified-property-iupac-08013", "IUPAC-GOLD-BOOK-08013-2026", "term 08013, current definition"),),
        observation_registry_path=OBSERVATION_REGISTRY_PATH,
        falsification_condition="The claim fails if the source-derived IUPAC certified-property record lacks reference material, associated uncertainty, traceability or certificate binding, or if an altered row is accepted.",
    ),
)

for _spec in MEASUREMENT_IDENTITY_BATCH_2_SPECS:
    _spec.validate()


__all__ = (
    "MEASUREMENT_IDENTITY_BATCH_2_SPECS",
    "OBSERVATION_REGISTRY_PATH",
    "SOURCE_RECORDS",
)
