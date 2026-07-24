"""Frozen current-knowledge obligation inventory for Smithian Fold Chemistry.

The names below define questions and comparison targets. They do not import a
chemical equation, fitted constant, observed answer or conventional model into
the derivation. An obligation becomes SFT science only after its own claim
package passes the single admission engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChemistryObligation:
    claim_id: str
    subbranch: str
    title: str
    evidence_mode: str
    external_source_ids: tuple[str, ...]


EMPIRICAL = "formal_forcing_plus_blind_external_measurement"
PREDICTION = "formal_forcing_plus_known-domain_validation_and_sealed_prediction"

GOLD = ("IUPAC-GOLD-BOOK-5.0.0-2025",)
GOLD_ENTITY = ("IUPAC-GOLD-BOOK-M03986-2026",)
GOLD_SPECIES = ("IUPAC-GOLD-BOOK-CT01038-2026",)
GOLD_SUBSTANCE = ("IUPAC-GOLD-BOOK-C01039-2026",)
COLOUR = ("IUPAC-COLOUR-BOOKS-2026",)
PERIODIC = ("IUPAC-PERIODIC-TABLE-2022", "CIAAW-ATOMIC-WEIGHTS-2024")
ATOMIC = ("NIST-ASD-5.12",)
WEBBOOK = ("NIST-CHEMISTRY-WEBBOOK-SRD69-2025",)
THERMO = ("NIST-JANAF-SRD13", "NIST-CHEMISTRY-WEBBOOK-SRD69-2025")
REFERENCE = ("NIST-CHEMISTRY-SRD-INDEX-2026",)


def obligation(claim_id: str, subbranch: str, title: str, evidence_mode: str, *sources: str) -> ChemistryObligation:
    return ChemistryObligation(claim_id, subbranch, title, evidence_mode, tuple(sources))


OBLIGATIONS = (
    # Chemical observation, identity and reporting.
    obligation("SFT-CHEM-MEAS-CHEMICAL-ENTITY-001", "measurement_identity", "Chemical entity and retained identity", EMPIRICAL, *GOLD_ENTITY),
    obligation("SFT-CHEM-MEAS-CHEMICAL-SPECIES-001", "measurement_identity", "Chemical species and observation-equivalence class", EMPIRICAL, *GOLD_SPECIES),
    obligation("SFT-CHEM-MEAS-SUBSTANCE-001", "measurement_identity", "Chemical substance and composition identity", EMPIRICAL, *GOLD_SUBSTANCE),
    obligation("SFT-CHEM-MEAS-AMOUNT-001", "measurement_identity", "Amount-of-substance count and reference carrier", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-MEAS-FORMULA-001", "measurement_identity", "Chemical formula as exact composition encoding", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-MEAS-NOMENCLATURE-001", "measurement_identity", "Reversible chemical nomenclature and identity boundary", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-MEAS-UNCERTAINTY-001", "measurement_identity", "Chemical measurement uncertainty and retained alternatives", EMPIRICAL, *REFERENCE),
    obligation("SFT-CHEM-MEAS-TRACEABILITY-001", "measurement_identity", "Chemical reference traceability and complete record", EMPIRICAL, *REFERENCE),

    # Elements and periodic structure.
    obligation("SFT-CHEM-ELEM-ELEMENT-001", "elements_periodicity", "Chemical element identity", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-ATOMIC-NUMBER-001", "elements_periodicity", "Atomic-number ordering and element distinction", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-ISOTOPE-001", "elements_periodicity", "Isotope identity within an element", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-ATOMIC-WEIGHT-001", "elements_periodicity", "Atomic-weight record and isotopic composition boundary", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-PERIODIC-ORDER-001", "elements_periodicity", "Periodic ordering by retained nuclear identity", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-PERIODIC-RECURRENCE-001", "elements_periodicity", "Periodic recurrence of outer chemical organization", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-GROUP-PERIOD-001", "elements_periodicity", "Group and period compositional coordinates", EMPIRICAL, *PERIODIC),
    obligation("SFT-CHEM-ELEM-VALENCE-001", "elements_periodicity", "Valence availability and chemical combination boundary", EMPIRICAL, *GOLD, *ATOMIC),
    obligation("SFT-CHEM-ELEM-ION-001", "elements_periodicity", "Ion formation with retained elemental identity", EMPIRICAL, *GOLD, *ATOMIC),
    obligation("SFT-CHEM-ELEM-PERIODIC-BOUNDARY-001", "elements_periodicity", "Known periodic-table observation boundary", EMPIRICAL, *PERIODIC),

    # Composition and stoichiometry.
    obligation("SFT-CHEM-STOICH-COMPOSITION-001", "composition_stoichiometry", "Exact chemical composition", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-STOICH-CONSERVATION-001", "composition_stoichiometry", "Conservation of elemental identity through reaction", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-STOICH-COEFFICIENT-001", "composition_stoichiometry", "Positive stoichiometric coefficient and reaction balance", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-STOICH-LIMITING-001", "composition_stoichiometry", "Limiting-component and complete-consumption boundary", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-STOICH-YIELD-001", "composition_stoichiometry", "Reaction yield as retained product share", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-STOICH-MIXTURE-001", "composition_stoichiometry", "Mixture components and composition support", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-STOICH-SOLUTION-001", "composition_stoichiometry", "Solution composition and solute-solvent distinction", EMPIRICAL, *WEBBOOK),

    # Bonding and molecular organization.
    obligation("SFT-CHEM-BOND-CHEMICAL-BOND-001", "bonding_molecular", "Chemical bond as retained interaction closure", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-BOND-COVALENT-001", "bonding_molecular", "Covalent shared-support bond", EMPIRICAL, *GOLD, *ATOMIC),
    obligation("SFT-CHEM-BOND-IONIC-001", "bonding_molecular", "Ionic transferred-label bond", EMPIRICAL, *GOLD, *ATOMIC),
    obligation("SFT-CHEM-BOND-METALLIC-001", "bonding_molecular", "Metallic collective-support bond", EMPIRICAL, *GOLD, *REFERENCE),
    obligation("SFT-CHEM-BOND-ORDER-001", "bonding_molecular", "Bond order as retained joining multiplicity", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-BOND-LENGTH-STRENGTH-001", "bonding_molecular", "Bond length, energy and identity correspondence", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-MOL-MOLECULE-001", "bonding_molecular", "Molecular identity and complete bonded carrier", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-MOL-GEOMETRY-001", "bonding_molecular", "Molecular geometry from held adjacency and orientation", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-MOL-ISOMER-001", "bonding_molecular", "Isomer distinction under equal composition", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-MOL-INTERMOLECULAR-001", "bonding_molecular", "Intermolecular interaction and residual joining", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-MOL-SUPRAMOLECULAR-001", "bonding_molecular", "Supramolecular organization by reversible recognition", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-MOL-NETWORK-001", "bonding_molecular", "Molecular network and connected chemical whole", EMPIRICAL, *GOLD),

    # Acids, bases, polarity, redox and electrochemistry.
    obligation("SFT-CHEM-AB-ACID-BASE-001", "acid_base_redox", "Conjugate acid-base partition", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-AB-PROTON-TRANSFER-001", "acid_base_redox", "Proton-transfer acid-base relation", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-AB-LEWIS-001", "acid_base_redox", "Electron-pair donor-acceptor relation", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-AB-AMPHOTERIC-001", "acid_base_redox", "Amphoteric dual-role relation", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-AB-BUFFER-001", "acid_base_redox", "Buffer response and conjugate-pair retention", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-ELECTRONEGATIVITY-001", "acid_base_redox", "Electronegativity ordering", EMPIRICAL, *GOLD, *ATOMIC),
    obligation("SFT-CHEM-BOND-POLARITY-001", "acid_base_redox", "Bond polarity from unequal held affinity", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-REDOX-OXIDATION-STATE-001", "acid_base_redox", "Oxidation-state accounting", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-REDOX-COUPLING-001", "acid_base_redox", "Coupled oxidation and reduction", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-ELECTROCHEM-CELL-001", "acid_base_redox", "Electrochemical cell and separated redox closure", EMPIRICAL, *GOLD, *REFERENCE),

    # Reaction, kinetics, thermochemistry and equilibrium.
    obligation("SFT-CHEM-RXN-IDENTITY-001", "reaction_kinetics_thermodynamics", "Chemical reaction as source-bound identity transformation", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-RXN-MECHANISM-001", "reaction_kinetics_thermodynamics", "Reaction mechanism as complete elementary-step trace", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-RXN-INTERMEDIATE-001", "reaction_kinetics_thermodynamics", "Reaction intermediate and retained path identity", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-KIN-ACTIVATION-001", "reaction_kinetics_thermodynamics", "Activation barrier and transition boundary", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-KIN-RATE-001", "reaction_kinetics_thermodynamics", "Reaction rate from counted transitions", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-KIN-ORDER-001", "reaction_kinetics_thermodynamics", "Kinetic order and dependency multiplicity", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-EQ-CHEMICAL-001", "reaction_kinetics_thermodynamics", "Chemical equilibrium as balanced reversible support", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-THERMO-REACTION-001", "reaction_kinetics_thermodynamics", "Reaction thermochemical accounting", EMPIRICAL, *THERMO),
    obligation("SFT-CHEM-THERMO-DIRECTION-001", "reaction_kinetics_thermodynamics", "Reaction direction under complete energy and distinction accounting", EMPIRICAL, *THERMO),
    obligation("SFT-CHEM-PHASE-CHEMICAL-001", "reaction_kinetics_thermodynamics", "Chemical phase and coexistence identity", EMPIRICAL, *THERMO),
    obligation("SFT-CHEM-SOLUTION-EQUILIBRIUM-001", "reaction_kinetics_thermodynamics", "Solution and solubility equilibrium", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-PHOTOCHEM-001", "reaction_kinetics_thermodynamics", "Photochemical excitation and reaction channel", EMPIRICAL, *GOLD, *WEBBOOK),

    # Catalysis, networks and interfaces.
    obligation("SFT-CHEM-CAT-CATALYST-001", "catalysis_networks_interfaces", "Catalyst identity conserved through a reaction cycle", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-CAT-PATHWAY-001", "catalysis_networks_interfaces", "Catalytic alternative-path relation", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-CAT-SELECTIVITY-001", "catalysis_networks_interfaces", "Catalytic selectivity among generated products", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-NET-REACTION-001", "catalysis_networks_interfaces", "Chemical reaction-network composition", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-NET-AUTOCATALYSIS-001", "catalysis_networks_interfaces", "Autocatalytic closure and self-amplifying path", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-SURFACE-ADSORPTION-001", "catalysis_networks_interfaces", "Adsorption at a retained interface", EMPIRICAL, *GOLD, *REFERENCE),
    obligation("SFT-CHEM-COLLOID-DISPERSION-001", "catalysis_networks_interfaces", "Colloidal dispersion and phase-interface support", EMPIRICAL, *GOLD, *REFERENCE),
    obligation("SFT-CHEM-INTERFACE-TRANSFER-001", "catalysis_networks_interfaces", "Chemical transfer across an interface", EMPIRICAL, *GOLD, *REFERENCE),

    # Stereochemistry, organic, polymer and biomolecular boundary.
    obligation("SFT-CHEM-STEREO-CHIRALITY-001", "stereochemistry_organic_polymer", "Chirality and non-superposable held orientation", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-STEREO-ENANTIOMER-001", "stereochemistry_organic_polymer", "Enantiomer pair and chiral observation boundary", EMPIRICAL, *GOLD, *WEBBOOK),
    obligation("SFT-CHEM-STEREO-DIASTEREOMER-001", "stereochemistry_organic_polymer", "Diastereomer distinction", EMPIRICAL, *GOLD),
    obligation("SFT-CHEM-ORGANIC-FUNCTIONAL-GROUP-001", "stereochemistry_organic_polymer", "Functional-group recurrence and reaction role", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-ORGANIC-REACTION-FAMILY-001", "stereochemistry_organic_polymer", "Organic reaction-family compositional law", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-POLYMER-CHAIN-001", "stereochemistry_organic_polymer", "Polymer chain from repeated monomer identity", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-POLYMER-DISTRIBUTION-001", "stereochemistry_organic_polymer", "Polymer population and retained chain-length distribution", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-BIOMOLECULAR-BOUNDARY-001", "stereochemistry_organic_polymer", "Chemistry-to-biology molecular handoff boundary", EMPIRICAL, *COLOUR),

    # Analytical and spectroscopic correspondence.
    obligation("SFT-CHEM-ANALYTICAL-SAMPLE-001", "analytical_spectroscopic", "Analytical sample, analyte and matrix distinction", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-ANALYTICAL-CALIBRATION-001", "analytical_spectroscopic", "Analytical calibration and traceable comparison", EMPIRICAL, *REFERENCE),
    obligation("SFT-CHEM-ANALYTICAL-SELECTIVITY-001", "analytical_spectroscopic", "Analytical selectivity and interference boundary", EMPIRICAL, *COLOUR),
    obligation("SFT-CHEM-SPEC-MASS-001", "analytical_spectroscopic", "Mass-spectral composition correspondence", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-SPEC-INFRARED-001", "analytical_spectroscopic", "Infrared recurrence and molecular distinction", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-SPEC-UVVIS-001", "analytical_spectroscopic", "Electronic absorption and molecular-state distinction", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-SPEC-ROT-VIB-001", "analytical_spectroscopic", "Rotational-vibrational molecular spectra", EMPIRICAL, *WEBBOOK),
    obligation("SFT-CHEM-ANALYTICAL-COMPLETE-RECORD-001", "analytical_spectroscopic", "Complete analytical result and falsification record", EMPIRICAL, *REFERENCE),

    # V2 reconciliation and explicit pre-observation predictions.
    obligation("SFT-CHEM-PRED-G-BLOCK-001", "gblock_smithium", "Generated g-block structural prediction", PREDICTION, *PERIODIC),
    obligation("SFT-CHEM-PRED-SMITHIUM-001", "gblock_smithium", "Smithium element-126 chemical prediction", PREDICTION, *PERIODIC),
    obligation("SFT-CHEM-PRED-PERIODIC-ENDPOINT-001", "gblock_smithium", "Generated periodic endpoint prediction and observation boundary", PREDICTION, *PERIODIC),
)


SUBBRANCH_ORDER = (
    "measurement_identity",
    "elements_periodicity",
    "composition_stoichiometry",
    "bonding_molecular",
    "acid_base_redox",
    "reaction_kinetics_thermodynamics",
    "catalysis_networks_interfaces",
    "stereochemistry_organic_polymer",
    "analytical_spectroscopic",
    "gblock_smithium",
)


def validate_inventory() -> None:
    if tuple(dict.fromkeys(row.subbranch for row in OBLIGATIONS)) != SUBBRANCH_ORDER:
        raise ValueError("Chemistry obligations do not follow the registered dependency order")
    claim_ids = tuple(row.claim_id for row in OBLIGATIONS)
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("Chemistry inventory contains duplicate claim identities")
    if any(not row.external_source_ids for row in OBLIGATIONS):
        raise ValueError("Every Chemistry obligation requires an external comparison body")
    if any(row.evidence_mode not in {EMPIRICAL, PREDICTION} for row in OBLIGATIONS):
        raise ValueError("Chemistry inventory contains an unclassified evidence mode")


validate_inventory()

__all__ = (
    "ChemistryObligation",
    "EMPIRICAL",
    "PREDICTION",
    "OBLIGATIONS",
    "SUBBRANCH_ORDER",
    "validate_inventory",
)
