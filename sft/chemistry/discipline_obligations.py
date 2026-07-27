"""Current-knowledge expansion obligations for the complete Chemistry branch.

This module registers scientific questions and required evidence surfaces only.
It does not import the admission engine, select a result, encode a measured
answer, or confer model admission.  Existing immutable Chemistry receipts are
merged with these obligations by ``tools/build_chemistry_discipline_census.py``.

The expansion follows Maria Smith's declared full-Chemistry boundary.  Each
obligation has exactly one categorical owner, an explicit evidence strength and
an exact handoff boundary.  A later claim may close an obligation only through
the unchanged canonical SFT admission engine.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChemistryDisciplineObligation:
    obligation_id: str
    field: str
    title: str
    owner: str
    required_strength: str
    required_external_surface: str
    exact_boundary: str


def gap(
    code: str,
    field: str,
    title: str,
    strength: str,
    external_surface: str,
    boundary: str,
) -> ChemistryDisciplineObligation:
    return ChemistryDisciplineObligation(
        obligation_id=f"SFT-CHEM-OBL-{code}",
        field=field,
        title=title,
        owner="chemistry",
        required_strength=strength,
        required_external_surface=external_surface,
        exact_boundary=boundary,
    )


QUANTITATIVE = "forced_exact_relation_plus_blind_external_value_vector"
STRUCTURAL = "forced_structural_law_plus_blind_external_structure_vector"
OPERATIONAL = "forced_algorithm_plus_exhaustive_operational_certificate"
HANDOFF = "exact_one_owner_dependency_and_cross_branch_handoff_certificate"


EXPANSION_OBLIGATIONS = (
    # Molecular electronic structure, molecular-state organization and
    # chemical quantum correspondence.
    gap("ELEC-001", "molecular_electronic_quantum", "Molecular electronic carrier and retained state identity", STRUCTURAL, "authoritative molecular-state assignments", "Finite molecular carriers and their chemically distinguishable electronic states."),
    gap("ELEC-002", "molecular_electronic_quantum", "Exact molecular electron-count and held-spin organization", STRUCTURAL, "measured multiplicities across neutral and ionic species", "Electron count and held orientation without negative or imaginary proof values."),
    gap("ELEC-003", "molecular_electronic_quantum", "Molecular orbital-support composition and occupancy", STRUCTURAL, "spectroscopic orbital assignments across representative species", "Fold-native support law; conventional orbitals appear only after sealing."),
    gap("ELEC-004", "molecular_electronic_quantum", "Ground and excited molecular-state ordering", QUANTITATIVE, "measured state-energy orderings", "Exact finite state order at declared molecular composition and geometry."),
    gap("ELEC-005", "molecular_electronic_quantum", "Electronic-state degeneracy and symmetry distinction", STRUCTURAL, "measured term and symmetry assignments", "Finite state equivalence and retained symmetry labels."),
    gap("ELEC-006", "molecular_electronic_quantum", "Molecular exclusion and exchange organization", STRUCTURAL, "spin-state and exchange-sensitive molecular observations", "Held-label composition derived from admitted exclusion support."),
    gap("ELEC-007", "molecular_electronic_quantum", "Electron-correlation composition beyond independent carriers", QUANTITATIVE, "correlation-sensitive energies and dissociation records", "Joint Fold support without fitted correction coefficients."),
    gap("ELEC-008", "molecular_electronic_quantum", "Multicentre and delocalized bonding support", STRUCTURAL, "measured multicentre bonding and delocalization records", "Connected molecular support not reducible to an imported two-centre model."),
    gap("ELEC-009", "molecular_electronic_quantum", "Molecular-state transformation and transition law", STRUCTURAL, "observed permitted and absent electronic transitions", "Fold transition structure before spectroscopic correspondence."),
    gap("ELEC-010", "molecular_electronic_quantum", "Chemical selection-rule structure", STRUCTURAL, "measured transition-presence vectors", "Retained/closed distinctions under exact molecular observation classes."),
    gap("ELEC-011", "molecular_electronic_quantum", "Potential-surface-equivalent molecular configuration order", QUANTITATIVE, "measured stable structures, barriers and reaction paths", "Generated finite configuration graph; no continuum surface premise."),
    gap("ELEC-012", "molecular_electronic_quantum", "Nuclear-electronic composition and lawful scale separation", STRUCTURAL, "isotopologue and vibronic state comparisons", "Exact compositional correspondence without importing a separation approximation."),
    gap("ELEC-013", "molecular_electronic_quantum", "Vibronic, rovibronic and spin-state joint composition", QUANTITATIVE, "resolved molecular spectra", "Complete finite joint-state support at the registered resolution."),
    gap("ELEC-014", "molecular_electronic_quantum", "Chemical measurement reduction for molecular quantum states", STRUCTURAL, "repeatable state-preparation and readout records", "Observation and retained-record law inherited from admitted Fold measurement."),
    gap("ELEC-015", "molecular_electronic_quantum", "Operational classical-quantum chemical correspondence", OPERATIONAL, "branchwise classical and quantum molecular execution", "Same chemical process reconstructed in both admitted computational modes."),

    # Quantitative molecular structure and properties across actual species.
    gap("PROP-001", "quantitative_molecular_properties", "Exact equilibrium bond-length relation", QUANTITATIVE, "blind gas-phase bond-length vector", "Named species, isotopologue, state and measurement condition retained."),
    gap("PROP-002", "quantitative_molecular_properties", "Exact bond-dissociation energy relation", QUANTITATIVE, "blind dissociation-energy vector", "Specified dissociation channel and product states retained."),
    gap("PROP-003", "quantitative_molecular_properties", "Exact molecular bond-angle relation", QUANTITATIVE, "blind molecular-angle vector", "Generated finite geometry at the registered observation resolution."),
    gap("PROP-004", "quantitative_molecular_properties", "Exact dihedral and torsional-state relation", QUANTITATIVE, "blind conformer and torsional-barrier vector", "Held orientation replaces signed proof angles."),
    gap("PROP-005", "quantitative_molecular_properties", "Exact molecular dipole organization and magnitude", QUANTITATIVE, "blind molecular dipole vector", "Orientation is held; reported conventional direction is correspondence only."),
    gap("PROP-006", "quantitative_molecular_properties", "Exact molecular polarizability relation", QUANTITATIVE, "blind static polarizability vector", "Response of a declared finite molecular state to a registered external distinction."),
    gap("PROP-007", "quantitative_molecular_properties", "Exact molecular ionization-energy relation", QUANTITATIVE, "blind molecular ionization-energy vector", "Chemical carrier and resulting ionic state both retained."),
    gap("PROP-008", "quantitative_molecular_properties", "Exact molecular electron-affinity relation", QUANTITATIVE, "blind molecular electron-affinity vector", "Held gain orientation; no negative proof magnitude."),
    gap("PROP-009", "quantitative_molecular_properties", "Exact vibrational-frequency relation", QUANTITATIVE, "blind fundamental-frequency vector", "Finite recurrence counts before frequency-unit translation."),
    gap("PROP-010", "quantitative_molecular_properties", "Exact rotational-constant relation", QUANTITATIVE, "blind rotational-constant vector", "Generated molecular geometry and held-axis recurrence."),
    gap("PROP-011", "quantitative_molecular_properties", "Exact intermolecular binding relation", QUANTITATIVE, "blind dimer and cluster binding vector", "Named constituent states and separation organization retained."),
    gap("PROP-012", "quantitative_molecular_properties", "Exact molecular magnetic-response relation", QUANTITATIVE, "blind magnetic susceptibility and moment vector", "Held spin/orientation support with conventional units only at comparison."),
    gap("PROP-013", "quantitative_molecular_properties", "Exact molecular formation-energy relation", QUANTITATIVE, "blind formation-energy vector", "Complete source/product identity and reference-state custody."),
    gap("PROP-014", "quantitative_molecular_properties", "Cross-property molecular prediction vector", QUANTITATIVE, "withheld multi-property records for the same species", "One sealed structural carrier must predict all registered properties without per-property fitting."),

    # Statistical and molecular thermodynamics, phase behaviour and transport.
    gap("THERMO-001", "statistical_molecular_thermodynamics_transport", "Finite chemical microstate-support law", STRUCTURAL, "calorimetric and state-population records", "Generated finite support; completed infinity and continuum ensembles prohibited."),
    gap("THERMO-002", "statistical_molecular_thermodynamics_transport", "Chemical temperature correspondence", QUANTITATIVE, "thermometric equilibrium records", "Chemistry consumes the Physics temperature carrier and owns composition-dependent consequences."),
    gap("THERMO-003", "statistical_molecular_thermodynamics_transport", "Internal-energy composition law", QUANTITATIVE, "blind thermochemical state vectors", "Exact positive parts and held transfer orientation."),
    gap("THERMO-004", "statistical_molecular_thermodynamics_transport", "Chemical heat and work transfer partition", QUANTITATIVE, "blind calorimetric and expansion-work records", "Path record distinguishes transfer classes without signed proof values."),
    gap("THERMO-005", "statistical_molecular_thermodynamics_transport", "Chemical entropy and multiplicity correspondence", QUANTITATIVE, "blind entropy and phase-transition vectors", "Derived from admitted information support without logarithmic or irrational proof values."),
    gap("THERMO-006", "statistical_molecular_thermodynamics_transport", "Enthalpy-equivalent chemical state relation", QUANTITATIVE, "blind enthalpy vectors", "Exact state and environment carrier; no imported thermodynamic equation."),
    gap("THERMO-007", "statistical_molecular_thermodynamics_transport", "Free-energy-equivalent reaction direction law", QUANTITATIVE, "blind equilibrium and reaction-direction vectors", "Exact retained energy and distinction accounting."),
    gap("THERMO-008", "statistical_molecular_thermodynamics_transport", "Chemical-potential-equivalent component law", QUANTITATIVE, "blind multicomponent equilibrium records", "Finite component exchange at fixed declared environment."),
    gap("THERMO-009", "statistical_molecular_thermodynamics_transport", "Activity and non-ideal composition law", QUANTITATIVE, "blind solution-activity vectors", "No fitted activity coefficient; condition and composition fully retained."),
    gap("THERMO-010", "statistical_molecular_thermodynamics_transport", "Fugacity-equivalent gas-mixture law", QUANTITATIVE, "blind real-gas equilibrium vectors", "Finite molecular support and declared pressure/temperature records."),
    gap("THERMO-011", "statistical_molecular_thermodynamics_transport", "Chemical phase-rule relation", STRUCTURAL, "blind component/phase/degree vectors", "Generated finite components, phases and independently variable held coordinates."),
    gap("THERMO-012", "statistical_molecular_thermodynamics_transport", "One-component phase-boundary relation", QUANTITATIVE, "blind coexistence curve points", "Exact registered substances and phase identities."),
    gap("THERMO-013", "statistical_molecular_thermodynamics_transport", "Multicomponent phase-diagram relation", QUANTITATIVE, "blind binary and ternary coexistence vectors", "Finite composition partitions; no continuum phase diagram premise."),
    gap("THERMO-014", "statistical_molecular_thermodynamics_transport", "Colligative composition-response law", QUANTITATIVE, "blind boiling, freezing and osmotic vectors", "Solvent and solute particle identities retained."),
    gap("THERMO-015", "statistical_molecular_thermodynamics_transport", "Solvation and dissolution free-order relation", QUANTITATIVE, "blind solvation and solubility vectors", "Solute, solvent, state and condition retained without fitted force field."),
    gap("THERMO-016", "statistical_molecular_thermodynamics_transport", "Molecular diffusion relation", QUANTITATIVE, "blind diffusion-coefficient vectors", "Counted transitions across generated spatial cells."),
    gap("THERMO-017", "statistical_molecular_thermodynamics_transport", "Viscous chemical transport relation", QUANTITATIVE, "blind viscosity vectors", "Retained momentum-transfer correspondence belongs to Physics; composition law belongs here."),
    gap("THERMO-018", "statistical_molecular_thermodynamics_transport", "Thermal-conductivity chemical relation", QUANTITATIVE, "blind molecular thermal-conductivity vectors", "Composition-dependent transport with physical carrier inherited explicitly."),
    gap("THERMO-019", "statistical_molecular_thermodynamics_transport", "Coupled mass, heat and charge transport law", QUANTITATIVE, "blind coupled-transport vectors", "Exact flux orientations are held labels; no signed proof magnitudes."),

    # Quantitative kinetics and reaction dynamics.
    gap("KIN-001", "quantitative_kinetics_reaction_dynamics", "Exact elementary-transition rate relation", QUANTITATIVE, "blind elementary-rate vectors", "Declared molecular states, conditions and counted transitions."),
    gap("KIN-002", "quantitative_kinetics_reaction_dynamics", "Exact concentration-dependence relation", QUANTITATIVE, "blind concentration/rate series", "All registered concentration rows preserved; no fitted exponent."),
    gap("KIN-003", "quantitative_kinetics_reaction_dynamics", "Exact temperature-dependence relation", QUANTITATIVE, "blind temperature/rate series", "No imported Arrhenius form or fitted prefactor/activation value."),
    gap("KIN-004", "quantitative_kinetics_reaction_dynamics", "Exact activation-barrier value relation", QUANTITATIVE, "blind barrier vectors", "Generated reaction path and state identities retained."),
    gap("KIN-005", "quantitative_kinetics_reaction_dynamics", "Transition-state-equivalent boundary law", STRUCTURAL, "measured kinetic isotope and barrier signatures", "Finite path-boundary carrier; no saddle-point continuum premise."),
    gap("KIN-006", "quantitative_kinetics_reaction_dynamics", "Competing-channel branching law", QUANTITATIVE, "blind branching-ratio vectors", "Complete registered product support, including unfavorable channels."),
    gap("KIN-007", "quantitative_kinetics_reaction_dynamics", "Sequential mechanism composition law", QUANTITATIVE, "blind time-resolved intermediate vectors", "Every elementary transition and intermediate retained."),
    gap("KIN-008", "quantitative_kinetics_reaction_dynamics", "Parallel mechanism composition law", QUANTITATIVE, "blind product-time vectors", "All competing paths enumerated; no favorable-path selection."),
    gap("KIN-009", "quantitative_kinetics_reaction_dynamics", "Reversible kinetic-equilibrium correspondence", QUANTITATIVE, "blind forward/reverse/equilibrium vectors", "Same exact transition graph supplies kinetics and equilibrium."),
    gap("KIN-010", "quantitative_kinetics_reaction_dynamics", "Catalytic turnover and cycle-frequency law", QUANTITATIVE, "blind catalytic turnover vectors", "Catalyst return and complete cycle trace required."),
    gap("KIN-011", "quantitative_kinetics_reaction_dynamics", "Diffusion-limited reaction boundary", QUANTITATIVE, "blind diffusion-controlled rate vectors", "Transport and reaction paths composed without an imported continuum limit."),
    gap("KIN-012", "quantitative_kinetics_reaction_dynamics", "Kinetic isotope-effect relation", QUANTITATIVE, "blind isotopologue rate-ratio vectors", "Isotope identity and complete reaction path retained."),
    gap("KIN-013", "quantitative_kinetics_reaction_dynamics", "Reaction-dynamics scattering and product-state law", QUANTITATIVE, "blind state-resolved product vectors", "Finite incoming/outgoing channel support and held orientation."),

    # Coordination, ligand, organometallic, solid-state and broader inorganic chemistry.
    gap("INORG-001", "inorganic_coordination_organometallic", "Coordination entity and retained metal-ligand identity", STRUCTURAL, "authoritative coordination-structure records", "Chemical ownership ends before bulk material properties."),
    gap("INORG-002", "inorganic_coordination_organometallic", "Coordination-number law", STRUCTURAL, "blind coordination-number vectors", "Generated ligand incidence around a retained central carrier."),
    gap("INORG-003", "inorganic_coordination_organometallic", "Ligand denticity and chelation law", STRUCTURAL, "blind ligand-binding topology vectors", "Exact connected donor-site support."),
    gap("INORG-004", "inorganic_coordination_organometallic", "Coordination-geometry law", QUANTITATIVE, "blind complex-geometry vectors", "Finite held orientation and adjacency; no imported geometry table."),
    gap("INORG-005", "inorganic_coordination_organometallic", "Coordination isomerism law", STRUCTURAL, "blind linkage, geometric and optical isomer records", "Complete graph and orientation equivalence classes."),
    gap("INORG-006", "inorganic_coordination_organometallic", "Ligand-field-equivalent splitting law", QUANTITATIVE, "blind spectral splitting vectors", "Derived Fold state interaction; conventional field models only after seal."),
    gap("INORG-007", "inorganic_coordination_organometallic", "Complex spin-state ordering law", QUANTITATIVE, "blind high/low-spin and crossover vectors", "Held orientation and exact state ordering."),
    gap("INORG-008", "inorganic_coordination_organometallic", "Inorganic colour and electronic-transition law", QUANTITATIVE, "blind absorption spectra of complexes", "Joint ligand/metal state transformation."),
    gap("INORG-009", "inorganic_coordination_organometallic", "Inorganic magnetic-state law", QUANTITATIVE, "blind magnetic-moment vectors", "Complete unpaired held-label support."),
    gap("INORG-010", "inorganic_coordination_organometallic", "Metal-carbon organometallic bond law", STRUCTURAL, "blind organometallic structure vectors", "Chemical bond topology and electron support."),
    gap("INORG-011", "inorganic_coordination_organometallic", "Organometallic electron-accounting law", STRUCTURAL, "blind stable-complex electron-count vectors", "Derived capacity and held labels; no imported counting rule."),
    gap("INORG-012", "inorganic_coordination_organometallic", "Oxidative-addition and reductive-elimination correspondence", STRUCTURAL, "blind organometallic mechanism vectors", "Held transfer orientations with conserved carriers."),
    gap("INORG-013", "inorganic_coordination_organometallic", "Insertion and elimination organometallic pathway law", STRUCTURAL, "blind mechanism and product vectors", "Complete adjacency transformation trace."),
    gap("INORG-014", "inorganic_coordination_organometallic", "Metal-cluster and metal-metal bonding law", STRUCTURAL, "blind cluster topology vectors", "Finite connected multi-centre support."),
    gap("INORG-015", "inorganic_coordination_organometallic", "Solid-state chemical formula and local-coordination law", STRUCTURAL, "blind crystal chemistry structure vectors", "Chemistry owns composition/local bonding; Materials owns bulk response."),
    gap("INORG-016", "inorganic_coordination_organometallic", "Defect chemistry and non-stoichiometry law", QUANTITATIVE, "blind defect/composition vectors", "Empty sites are explicit forms, never numerical zero."),
    gap("INORG-017", "inorganic_coordination_organometallic", "Inorganic acid-base and redox network law", STRUCTURAL, "blind inorganic reaction-network vectors", "Complete species and transfer paths."),

    # Aromaticity, conjugation, conformations and detailed organic mechanisms.
    gap("ORG-001", "organic_structure_mechanisms", "Conjugated-support law", STRUCTURAL, "blind conjugated structure and spectral vectors", "Connected alternating support derived without importing resonance notation."),
    gap("ORG-002", "organic_structure_mechanisms", "Resonance-equivalent representation law", STRUCTURAL, "blind equivalence and structure vectors", "Multiple encodings of one retained molecular carrier."),
    gap("ORG-003", "organic_structure_mechanisms", "Aromatic recurrence and stability law", QUANTITATIVE, "blind aromatic structure and energy vectors", "Generated cycle support; no imported electron-count rule."),
    gap("ORG-004", "organic_structure_mechanisms", "Antiaromatic and nonaromatic distinction law", QUANTITATIVE, "blind comparative structure/energy vectors", "All same-cycle alternatives retained."),
    gap("ORG-005", "organic_structure_mechanisms", "Conformer generation and equivalence law", OPERATIONAL, "exhaustive small-molecule conformer censuses", "Finite molecular graphs and held torsional states."),
    gap("ORG-006", "organic_structure_mechanisms", "Conformer population and ordering law", QUANTITATIVE, "blind conformer energy/population vectors", "Condition and observation-timescale retained."),
    gap("ORG-007", "organic_structure_mechanisms", "Nucleophilic substitution family law", STRUCTURAL, "blind substrate/product/mechanism vectors", "Generated bond breaking/forming paths; conventional family names after sealing."),
    gap("ORG-008", "organic_structure_mechanisms", "Electrophilic substitution family law", STRUCTURAL, "blind substrate/product/mechanism vectors", "Complete donor/acceptor and aromatic carrier trace."),
    gap("ORG-009", "organic_structure_mechanisms", "Addition reaction family law", STRUCTURAL, "blind addition product vectors", "Complete adjacency and stoichiometric transformation."),
    gap("ORG-010", "organic_structure_mechanisms", "Elimination reaction family law", STRUCTURAL, "blind elimination product vectors", "Complete carrier and bond-order transformation."),
    gap("ORG-011", "organic_structure_mechanisms", "Rearrangement reaction family law", STRUCTURAL, "blind rearrangement product vectors", "Composition conserved while adjacency changes."),
    gap("ORG-012", "organic_structure_mechanisms", "Pericyclic reaction-support law", QUANTITATIVE, "blind permitted/product stereochemistry vectors", "Finite cyclic transition support; imported orbital-symmetry rules prohibited."),
    gap("ORG-013", "organic_structure_mechanisms", "Radical reaction network law", STRUCTURAL, "blind initiation/propagation/termination vectors", "Held unpaired-label support and complete network trace."),
    gap("ORG-014", "organic_structure_mechanisms", "Organic chemoselectivity, regioselectivity and stereoselectivity law", QUANTITATIVE, "blind complete product-distribution vectors", "Every generated product retained; no major-product-only scoring."),
    gap("ORG-015", "organic_structure_mechanisms", "Protecting-group and reversible functional-state law", STRUCTURAL, "blind functional transformation vectors", "Target functionality and restoration trace retained."),
    gap("ORG-016", "organic_structure_mechanisms", "Retrosynthetic decomposition and forward-verification law", OPERATIONAL, "exhaustive bounded synthesis-graph checks", "Search proposes routes; only forward admitted chemistry verifies them."),

    # Electrochemical potentials, kinetics, transport and concentration.
    gap("ECHEM-001", "quantitative_electrochemistry", "Half-reaction identity and held transfer orientation", STRUCTURAL, "authoritative half-reaction records", "No negative electron-count proof value."),
    gap("ECHEM-002", "quantitative_electrochemistry", "Electrode-potential chemical relation", QUANTITATIVE, "blind standard-potential vector", "Reference electrode, species, phase and condition retained."),
    gap("ECHEM-003", "quantitative_electrochemistry", "Cell-potential composition law", QUANTITATIVE, "blind full-cell potential vector", "Two admitted half-cell carriers and path orientation."),
    gap("ECHEM-004", "quantitative_electrochemistry", "Concentration-dependent potential law", QUANTITATIVE, "blind concentration/potential series", "No imported logarithm or fitted coefficient."),
    gap("ECHEM-005", "quantitative_electrochemistry", "Electrochemical work and reaction-direction correspondence", QUANTITATIVE, "blind cell-work and equilibrium vectors", "Exact chemical and electrical transfer custody."),
    gap("ECHEM-006", "quantitative_electrochemistry", "Electrolysis and product-amount law", QUANTITATIVE, "blind charge/product amount vectors", "Counted transferred distinctions and stoichiometric carriers."),
    gap("ECHEM-007", "quantitative_electrochemistry", "Ionic conductivity relation", QUANTITATIVE, "blind conductivity/composition vectors", "Species-resolved counted transport."),
    gap("ECHEM-008", "quantitative_electrochemistry", "Ionic mobility and transference law", QUANTITATIVE, "blind mobility/transference vectors", "Held direction and species identity retained."),
    gap("ECHEM-009", "quantitative_electrochemistry", "Electrode reaction-rate law", QUANTITATIVE, "blind current/potential/condition vectors", "No imported exponential or fitted exchange-current parameter."),
    gap("ECHEM-010", "quantitative_electrochemistry", "Overpotential and polarization relation", QUANTITATIVE, "blind polarization curves", "Reference equilibrium state and path retained."),
    gap("ECHEM-011", "quantitative_electrochemistry", "Double-layer and interfacial charge organization", QUANTITATIVE, "blind interfacial capacitance vectors", "Finite interface support; continuum profile not a premise."),
    gap("ECHEM-012", "quantitative_electrochemistry", "Corrosion reaction-network law", QUANTITATIVE, "blind corrosion potential/rate vectors", "Coupled anodic/cathodic paths and material handoff."),
    gap("ECHEM-013", "quantitative_electrochemistry", "Electrochemical storage handoff law", HANDOFF, "cell chemistry and Materials performance records", "Chemistry owns reactions/species; Materials owns bulk device response; Engineering owns implementation."),

    # Nuclear chemistry, radioactive transformation and isotope chemistry.
    gap("NUCHEM-001", "nuclear_radiochemistry", "Nuclide chemical carrier beyond element identity", STRUCTURAL, "authoritative nuclide/species records", "Physics owns nuclear constitution; Chemistry owns chemical state and separation."),
    gap("NUCHEM-002", "nuclear_radiochemistry", "Radioactive chemical transformation network", STRUCTURAL, "blind parent/daughter chemical-state vectors", "Every nuclear and chemical carrier transition retained."),
    gap("NUCHEM-003", "nuclear_radiochemistry", "Activity and amount-of-substance relation", QUANTITATIVE, "blind activity/amount/time vectors", "Decay law inherited from Physics; chemical amount and measurement belong here."),
    gap("NUCHEM-004", "nuclear_radiochemistry", "Radioactive branching chemical-yield law", QUANTITATIVE, "blind daughter-yield vectors", "All registered decay branches and chemical recoveries preserved."),
    gap("NUCHEM-005", "nuclear_radiochemistry", "Transient and secular radiochemical equilibrium", QUANTITATIVE, "blind parent/daughter time-series", "Finite recurrence/transition support; no imported differential equation."),
    gap("NUCHEM-006", "nuclear_radiochemistry", "Isotope-exchange reaction law", QUANTITATIVE, "blind isotope-exchange equilibrium vectors", "Elemental identity and isotopic distinction retained."),
    gap("NUCHEM-007", "nuclear_radiochemistry", "Equilibrium isotope-fractionation law", QUANTITATIVE, "blind isotope-ratio vectors", "No fitted fractionation factor."),
    gap("NUCHEM-008", "nuclear_radiochemistry", "Kinetic isotope-fractionation law", QUANTITATIVE, "blind isotope/time/product vectors", "Complete reaction path and isotope identity."),
    gap("NUCHEM-009", "nuclear_radiochemistry", "Radiotracer custody and inference law", STRUCTURAL, "blind tracer recovery and localization records", "Tracer identity, transformation, loss and observation boundary retained."),
    gap("NUCHEM-010", "nuclear_radiochemistry", "Radiochemical separation and decontamination law", QUANTITATIVE, "blind separation-factor and recovery vectors", "Every initial/final nuclide carrier preserved."),
    gap("NUCHEM-011", "nuclear_radiochemistry", "Fission-product chemical distribution law", QUANTITATIVE, "blind fission-product chemistry vectors", "Physics supplies fission products; Chemistry owns subsequent species and partition."),
    gap("NUCHEM-012", "nuclear_radiochemistry", "Radiation-chemistry reaction network", QUANTITATIVE, "blind radiolysis species/yield vectors", "Energy deposition inherited from Physics; chemical network derived here."),

    # Spectroscopy, separation and measurement-performance laws.
    gap("ANAL-001", "analytical_spectroscopy_separation", "Analytical accuracy and trueness law", QUANTITATIVE, "certified-reference-material result vectors", "Reference identity, bias orientation and uncertainty retained."),
    gap("ANAL-002", "analytical_spectroscopy_separation", "Analytical precision and repeatability law", QUANTITATIVE, "blind replicate-measurement vectors", "Exact finite dispersion without irrational proof statistics."),
    gap("ANAL-003", "analytical_spectroscopy_separation", "Analytical sensitivity law", QUANTITATIVE, "blind response/concentration vectors", "No fitted calibration slope as a derivational parameter."),
    gap("ANAL-004", "analytical_spectroscopy_separation", "Detection and quantification boundary law", QUANTITATIVE, "blind blank/low-level measurement vectors", "Empty One is distinct from measured nondetection and reported conventional zero."),
    gap("ANAL-005", "analytical_spectroscopy_separation", "Measurement selectivity and interference matrix", QUANTITATIVE, "blind analyte/interferent response vectors", "All registered interferences retained."),
    gap("ANAL-006", "analytical_spectroscopy_separation", "NMR chemical-shift relation", QUANTITATIVE, "blind molecular NMR shift vectors", "Reference, nucleus, solvent and condition retained."),
    gap("ANAL-007", "analytical_spectroscopy_separation", "NMR spin-coupling relation", QUANTITATIVE, "blind scalar-coupling vectors", "Held spin and bonding-path support."),
    gap("ANAL-008", "analytical_spectroscopy_separation", "NMR relaxation and exchange law", QUANTITATIVE, "blind relaxation/exchange vectors", "Finite state transitions and observation timescale."),
    gap("ANAL-009", "analytical_spectroscopy_separation", "Raman transition and intensity relation", QUANTITATIVE, "blind Raman line/intensity vectors", "Polarizability-state transformation after molecular derivation."),
    gap("ANAL-010", "analytical_spectroscopy_separation", "Fluorescence emission and quantum-yield relation", QUANTITATIVE, "blind emission/yield/lifetime vectors", "All radiative and nonradiative channels retained."),
    gap("ANAL-011", "analytical_spectroscopy_separation", "Phosphorescence and intersystem transition law", QUANTITATIVE, "blind emission/lifetime vectors", "Held spin-state transformation."),
    gap("ANAL-012", "analytical_spectroscopy_separation", "Infrared line-position and intensity vector", QUANTITATIVE, "blind IR spectra across actual species", "Extends categorical IR recurrence to quantitative spectra."),
    gap("ANAL-013", "analytical_spectroscopy_separation", "UV-visible line-position and intensity vector", QUANTITATIVE, "blind electronic spectra across actual species", "Extends categorical absorption identity to quantitative spectra."),
    gap("ANAL-014", "analytical_spectroscopy_separation", "Mass-spectrum mass, isotope and fragmentation vector", QUANTITATIVE, "blind complete mass spectra", "All registered peaks, including weak fragments, preserved."),
    gap("ANAL-015", "analytical_spectroscopy_separation", "Rotational spectrum line vector", QUANTITATIVE, "blind microwave spectra", "Molecular geometry and isotopologue state retained."),
    gap("ANAL-016", "analytical_spectroscopy_separation", "X-ray diffraction structure relation", QUANTITATIVE, "blind diffraction/structure vectors", "Physics owns scattering carrier; Chemistry owns molecular/crystal chemical structure."),
    gap("ANAL-017", "analytical_spectroscopy_separation", "Electron and neutron diffraction chemical correspondence", QUANTITATIVE, "blind diffraction/structure vectors", "Probe Physics retained as explicit dependency."),
    gap("ANAL-018", "analytical_spectroscopy_separation", "Chromatographic retention and resolution law", QUANTITATIVE, "blind chromatographic vectors", "Analyte, stationary/mobile phases and conditions retained."),
    gap("ANAL-019", "analytical_spectroscopy_separation", "Electrophoretic mobility and separation law", QUANTITATIVE, "blind mobility/separation vectors", "Species charge label, medium and condition retained."),
    gap("ANAL-020", "analytical_spectroscopy_separation", "Electroanalytical response law", QUANTITATIVE, "blind voltammetric/amperometric vectors", "Electrochemical dependencies and complete response trace."),
    gap("ANAL-021", "analytical_spectroscopy_separation", "Multimodal molecular identity reconstruction", OPERATIONAL, "withheld cross-instrument identity cases", "One molecular carrier reconstructed from complete orthogonal records."),
    gap("ANAL-022", "analytical_spectroscopy_separation", "Complete analytical performance and uncertainty budget", QUANTITATIVE, "blind validation-study vectors", "Accuracy, precision, sensitivity, selectivity, detection and traceability jointly retained."),

    # Computational chemistry, graph generation and cheminformatics.
    gap("COMP-001", "computational_chemistry_cheminformatics", "Canonical finite molecular-graph encoding", OPERATIONAL, "exhaustive graph encoding/decoding corpus", "Data structure is mathematical organization, not a software-library artifact."),
    gap("COMP-002", "computational_chemistry_cheminformatics", "Molecular graph isomorphism and identity law", OPERATIONAL, "exhaustive bounded isomorphism census", "Same molecule iff the admitted chemical distinctions are preserved."),
    gap("COMP-003", "computational_chemistry_cheminformatics", "Chemical substructure relation", OPERATIONAL, "exhaustive bounded subgraph census", "Exact retained atom/bond labels and mapping certificate."),
    gap("COMP-004", "computational_chemistry_cheminformatics", "Constitutional-isomer enumeration law", OPERATIONAL, "exhaustive small-formula isomer censuses", "Complete generated molecular graph support."),
    gap("COMP-005", "computational_chemistry_cheminformatics", "Stereoisomer enumeration law", OPERATIONAL, "exhaustive small-graph stereoisomer censuses", "No unconditional imported power-of-two answer."),
    gap("COMP-006", "computational_chemistry_cheminformatics", "Conformer enumeration law", OPERATIONAL, "exhaustive bounded conformer censuses", "Generated held torsions and symmetry quotient."),
    gap("COMP-007", "computational_chemistry_cheminformatics", "Reaction-graph generation law", OPERATIONAL, "exhaustive bounded reaction censuses", "All identity-conserving graph transitions enumerated."),
    gap("COMP-008", "computational_chemistry_cheminformatics", "Atom-mapping and reaction-balance certificate", OPERATIONAL, "exhaustive reaction mapping cases", "Every elemental carrier has one source/product path."),
    gap("COMP-009", "computational_chemistry_cheminformatics", "Mechanism-search and proof-trace law", OPERATIONAL, "bounded mechanism search censuses", "Search may propose; only admitted transition laws accept."),
    gap("COMP-010", "computational_chemistry_cheminformatics", "Exact molecular similarity and distinction law", OPERATIONAL, "benchmark molecular comparison cases", "No learned metric or fitted weight selects similarity."),
    gap("COMP-011", "computational_chemistry_cheminformatics", "Chemical database identity and provenance law", OPERATIONAL, "cross-database identity/provenance cases", "Every representation links reversibly to source and observation boundary."),
    gap("COMP-012", "computational_chemistry_cheminformatics", "Symbolic chemical-property evaluation law", OPERATIONAL, "independent exact evaluator corpus", "Consumes admitted Chemistry laws only; no opaque model."),
    gap("COMP-013", "computational_chemistry_cheminformatics", "Chemical prediction uncertainty and applicability boundary", QUANTITATIVE, "blind in-domain/out-of-domain result vectors", "Missing distinctions and unsupported states halt rather than extrapolate silently."),
    gap("COMP-014", "computational_chemistry_cheminformatics", "Classical and quantum chemical algorithm correspondence", OPERATIONAL, "branchwise exact molecular computations", "Computational branches supply machines; Chemistry supplies only admitted chemical laws."),

    # Quantitative polymer chemistry.
    gap("POLY-001", "quantitative_polymer_chemistry", "Degree-of-polymerization relation", QUANTITATIVE, "blind chain-length vectors", "Monomer identity and chain termination retained."),
    gap("POLY-002", "quantitative_polymer_chemistry", "Number-average molecular-size law", QUANTITATIVE, "blind polymer population vectors", "Exact finite population ratios."),
    gap("POLY-003", "quantitative_polymer_chemistry", "Mass-weighted molecular-size law", QUANTITATIVE, "blind polymer mass-distribution vectors", "Exact positive rational weighting."),
    gap("POLY-004", "quantitative_polymer_chemistry", "Polymer dispersity relation", QUANTITATIVE, "blind distribution vectors", "Ratio of admitted population measures; no irrational proof statistics."),
    gap("POLY-005", "quantitative_polymer_chemistry", "Chain-growth polymerization network law", QUANTITATIVE, "blind conversion/time/distribution vectors", "Initiation, propagation, transfer and termination all retained."),
    gap("POLY-006", "quantitative_polymer_chemistry", "Step-growth polymerization network law", QUANTITATIVE, "blind conversion/distribution vectors", "Every reactive group and connectivity transition retained."),
    gap("POLY-007", "quantitative_polymer_chemistry", "Copolymer sequence-composition law", QUANTITATIVE, "blind sequence/composition vectors", "All monomer identities and sequence distinctions retained."),
    gap("POLY-008", "quantitative_polymer_chemistry", "Branched, star and network architecture law", STRUCTURAL, "blind polymer topology vectors", "Exact finite connected graph and branch identity."),
    gap("POLY-009", "quantitative_polymer_chemistry", "Crosslink and gelation boundary", QUANTITATIVE, "blind connectivity/gel-point vectors", "Finite network percolation certificate; no completed infinite network."),
    gap("POLY-010", "quantitative_polymer_chemistry", "Polymer conformation and size relation", QUANTITATIVE, "blind chain-dimension vectors", "Generated finite chain states; no continuum random-walk premise."),
    gap("POLY-011", "quantitative_polymer_chemistry", "Polymer phase and transition relation", QUANTITATIVE, "blind transition/phase vectors", "Chemistry owns molecular transition; Materials owns bulk performance."),
    gap("POLY-012", "quantitative_polymer_chemistry", "Polymer degradation and depolymerization network", QUANTITATIVE, "blind time/product/distribution vectors", "All scission and product paths retained."),
    gap("POLY-013", "quantitative_polymer_chemistry", "Polymer chemistry-to-materials handoff", HANDOFF, "paired molecular and bulk-property records", "Chemical architecture remains Chemistry-owned; bulk mechanics and device response remain Materials-owned."),

    # Required substantial blind validation matrices.  These are independent
    # obligations, not satisfied by one favorable row per law.
    gap("VALID-001", "blind_external_validation", "Substantial molecular geometry blind vector", QUANTITATIVE, "multi-species withheld bond-length/angle records", "Includes favorable, unfavorable, isotopologue and state-boundary rows."),
    gap("VALID-002", "blind_external_validation", "Substantial thermochemical blind vector", QUANTITATIVE, "multi-species withheld formation/reaction-energy records", "Complete authoritative rows and source hashes."),
    gap("VALID-003", "blind_external_validation", "Substantial equilibrium blind vector", QUANTITATIVE, "multi-reaction withheld equilibrium records", "Composition and condition grid retained."),
    gap("VALID-004", "blind_external_validation", "Substantial kinetic blind vector", QUANTITATIVE, "multi-reaction withheld rate records", "Temperature and concentration grids retained."),
    gap("VALID-005", "blind_external_validation", "Substantial spectroscopy blind vector", QUANTITATIVE, "multi-technique withheld full spectra", "All registered peaks/lines, not selected highlights."),
    gap("VALID-006", "blind_external_validation", "Substantial electrochemical blind vector", QUANTITATIVE, "multi-cell and concentration withheld records", "Potentials, currents and transport rows retained."),
    gap("VALID-007", "blind_external_validation", "Substantial inorganic and coordination blind vector", QUANTITATIVE, "multi-complex structure/spectra/magnetism records", "One sealed law surface tested across coordination families."),
    gap("VALID-008", "blind_external_validation", "Substantial organic reaction blind vector", QUANTITATIVE, "complete product distributions across reaction families", "No major-product-only validation."),
    gap("VALID-009", "blind_external_validation", "Substantial polymer blind vector", QUANTITATIVE, "conversion/distribution/architecture records", "Full registered populations retained."),
    gap("VALID-010", "blind_external_validation", "Cross-source chemical reproducibility vector", QUANTITATIVE, "independent authoritative records for overlapping targets", "Source disagreement is preserved, not averaged away."),
    gap("VALID-011", "blind_external_validation", "Deliberately adverse and out-of-bound chemical vector", QUANTITATIVE, "tampered, contradictory and unsupported cases", "Every unsupported input must halt or reject at its declared boundary."),
    gap("VALID-012", "blind_external_validation", "Chemistry empirical Grand Lock", QUANTITATIVE, "complete Chemistry empirical receipt vector", "Reconciles every Chemistry empirical claim and every preserved adverse row without replacing individual receipts."),

    # Exact cross-branch ownership and handoff certificates.
    gap("HAND-001", "cross_branch_handoffs", "Chemistry-to-Materials ownership handoff", HANDOFF, "paired chemical-structure/material-response records", "Chemistry owns species, bonds, reactions and local structure; Materials owns bulk response."),
    gap("HAND-002", "cross_branch_handoffs", "Chemistry-to-Biology ownership handoff", HANDOFF, "paired molecular/biological-function records", "Chemistry owns molecular identity and reaction; Biology owns living organization and function."),
    gap("HAND-003", "cross_branch_handoffs", "Chemistry-to-Medicine ownership handoff", HANDOFF, "paired molecular/clinical records", "Chemistry owns substance and transformations; Medicine owns intervention and health outcome."),
    gap("HAND-004", "cross_branch_handoffs", "Chemistry-to-Earth and Environmental Science ownership handoff", HANDOFF, "paired chemical/environmental-fate records", "Chemistry owns species and reactions; Earth Science owns system history, transport and planetary context."),
    gap("HAND-005", "cross_branch_handoffs", "Chemistry-to-Astronomy ownership handoff", HANDOFF, "paired molecular-spectra/astronomical-observation records", "Chemistry owns molecular structure and spectra; Astronomy owns source population and cosmic context."),
    gap("HAND-006", "cross_branch_handoffs", "Chemistry cross-branch one-owner completeness certificate", HANDOFF, "complete branch dependency and consumer graph", "Every atomic obligation has one owner; downstream branches may consume but never re-own it."),
)


# Added only after the named claim has received a canonical model-admission
# receipt at the obligation's required strength. The census builder opens and
# verifies each mapped receipt independently.
CLOSED_EXPANSION_MAPPINGS = {
    "SFT-CHEM-OBL-ELEC-001": ("SFT-CHEM-ELECTRONIC-STATE-IDENTITY-001",),
}


REQUIRED_FIELDS = (
    "molecular_electronic_quantum",
    "quantitative_molecular_properties",
    "statistical_molecular_thermodynamics_transport",
    "quantitative_kinetics_reaction_dynamics",
    "inorganic_coordination_organometallic",
    "organic_structure_mechanisms",
    "quantitative_electrochemistry",
    "nuclear_radiochemistry",
    "analytical_spectroscopy_separation",
    "computational_chemistry_cheminformatics",
    "quantitative_polymer_chemistry",
    "blind_external_validation",
    "cross_branch_handoffs",
)


def validate_expansion_obligations() -> None:
    ids = tuple(row.obligation_id for row in EXPANSION_OBLIGATIONS)
    if len(ids) != len(set(ids)):
        raise ValueError("Chemistry discipline expansion contains duplicate obligation identities")
    if tuple(dict.fromkeys(row.field for row in EXPANSION_OBLIGATIONS)) != REQUIRED_FIELDS:
        raise ValueError("Chemistry discipline expansion does not follow the declared field order")
    if any(row.owner != "chemistry" for row in EXPANSION_OBLIGATIONS):
        raise ValueError("Every Chemistry discipline obligation requires exactly one Chemistry owner")
    if any(not row.required_external_surface or not row.exact_boundary for row in EXPANSION_OBLIGATIONS):
        raise ValueError("Chemistry discipline obligation lacks evidence or boundary")
    if any(row.required_strength not in {QUANTITATIVE, STRUCTURAL, OPERATIONAL, HANDOFF} for row in EXPANSION_OBLIGATIONS):
        raise ValueError("Chemistry discipline obligation has an unclassified evidence strength")
    if not set(CLOSED_EXPANSION_MAPPINGS).issubset(set(ids)):
        raise ValueError("Chemistry discipline closure mapping names an unknown obligation")
    if any(not claims or len(claims) != len(set(claims)) for claims in CLOSED_EXPANSION_MAPPINGS.values()):
        raise ValueError("Chemistry discipline closure mapping is empty or duplicated")


validate_expansion_obligations()


__all__ = (
    "ChemistryDisciplineObligation",
    "CLOSED_EXPANSION_MAPPINGS",
    "EXPANSION_OBLIGATIONS",
    "HANDOFF",
    "OPERATIONAL",
    "QUANTITATIVE",
    "REQUIRED_FIELDS",
    "STRUCTURAL",
    "validate_expansion_obligations",
)
