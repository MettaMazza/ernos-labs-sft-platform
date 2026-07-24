"""Frozen-question surface for the V3 Materials Science reconstruction.

The rows state questions and structural preservation requirements only.  They
contain no external target values.  Familiar Materials terminology identifies
the reconciliation question; it does not select the Fold survivor.
"""

from __future__ import annotations

from dataclasses import dataclass


SUBBRANCH_ORDER = (
    "measurement_identity",
    "crystal_quasicrystal",
    "defects_microstructure",
    "electronic_semiconductor",
    "superconducting_superfluid_topological",
    "mechanical",
    "thermal_magnetic_optical",
    "material_classes_bulk",
    "processing_degradation",
    "advanced_functional_sustainable",
)


@dataclass(frozen=True)
class MaterialsObligation:
    claim_id: str
    title: str
    subbranch: str
    carrier: str
    relation: str
    organization: str
    observation: str
    statement: str


def row(
    suffix: str,
    title: str,
    subbranch: str,
    carrier: str,
    relation: str,
    organization: str,
    observation: str,
    statement: str,
) -> MaterialsObligation:
    return MaterialsObligation(
        f"SFT-MAT-{suffix}-001", title, subbranch, carrier, relation,
        organization, observation, statement,
    )


MATERIALS_OBLIGATIONS = (
    # Measurement, identity and traceability — 7
    row("MEAS-MATERIAL", "Material system and retained identity", "measurement_identity", "complete-constituent-carrier", "composition-and-bonding-retained", "material-boundary-held", "declared-scale-identity", "A material is the least complete constituent-and-relation carrier whose composition, bonding organization and declared observation boundary remain distinguishable."),
    row("MEAS-SPECIMEN", "Specimen and sampling relation", "measurement_identity", "source-bound-specimen-carrier", "specimen-to-material-provenance", "sampling-boundary-retained", "representativeness-declared", "A specimen is a source-bound finite part of a material with an explicit sampling map, retained preparation history and declared representativeness boundary."),
    row("MEAS-COMPOSITION", "Material composition record", "measurement_identity", "complete-component-support", "exact-part-to-whole-composition", "component-identities-retained", "basis-and-uncertainty-declared", "Material composition is the exact part-to-whole record of every retained component on one declared amount or support basis."),
    row("MEAS-PHASE", "Material phase identity", "measurement_identity", "complete-phase-support", "shared-recurrence-equivalence", "phase-boundary-retained", "condition-bounded-phase-class", "A material phase is a maximal connected support whose constituents share one stable recurrence and symmetry observation class at declared conditions."),
    row("MEAS-MICROSTRUCTURE", "Microstructure as mesoscale organization", "measurement_identity", "complete-mesoscale-carrier", "constituent-arrangement-relation", "interfaces-and-defects-retained", "resolution-bounded-record", "Microstructure is the complete declared-scale arrangement of phases, grains, interfaces and defects between constituent and bulk observation levels."),
    row("MEAS-PROPERTY", "Material property relation", "measurement_identity", "material-state-carrier", "stimulus-response-relation", "condition-and-direction-retained", "method-bounded-property", "A material property is a reproducible relation between a declared material state and stimulus/response records, conditional on direction, scale, history and method."),
    row("MEAS-TRACEABILITY", "Materials uncertainty and metrological traceability", "measurement_identity", "complete-measurement-record", "result-to-reference-chain", "uncertainty-components-retained", "calibration-and-condition-bounded", "A materials measurement is admissible only with a complete result, uncertainty, method, specimen, condition, calibration and unbroken reference chain."),

    # Crystal, reciprocal and quasicrystal organization — 10
    row("CRYST-LATTICE", "Generated lattice organization", "crystal_quasicrystal", "complete-site-carrier", "translation-recurrence-relation", "adjacency-word-repeated", "finite-support-lattice-class", "A lattice is a completely generated site-and-adjacency network whose local word recurs under retained translations."),
    row("CRYST-UNIT-CELL", "Primitive unit-cell identity", "crystal_quasicrystal", "minimal-cell-carrier", "translation-generates-whole", "no-redundant-site-copy", "basis-choice-canonicalized", "A primitive unit cell is the least complete labelled cell whose generated translations reproduce every lattice site and relation once."),
    row("CRYST-TRANSLATION", "Crystalline translational order", "crystal_quasicrystal", "complete-periodic-support", "integer-translation-action", "local-word-and-adjacency-invariant", "observation-depth-declared", "Crystalline translational order is invariance of the complete local constituent word and adjacency class under a generated integer translation basis."),
    row("CRYST-CUBIC-COORDINATION", "Simple-cubic nearest-neighbour coordination", "crystal_quasicrystal", "three-axis-site-carrier", "two-orientations-per-axis", "nearest-adjacency-complete", "coordination-count-six", "Three stable spatial generators with two held orientations per generator force six nearest neighbours for the simple-cubic adjacency class."),
    row("CRYST-ROTATION-RESTRICTION", "Crystallographic rotation restriction", "crystal_quasicrystal", "integer-lattice-action-carrier", "finite-order-rotation-relation", "translation-compatibility-retained", "orders-one-two-three-four-six", "A finite rotation preserves a periodic lattice only for generated orders 1, 2, 3, 4 and 6; five is the least excluded positive order."),
    row("CRYST-SYSTEMS", "Three-dimensional crystal-system classification", "crystal_quasicrystal", "rank-three-metric-carrier", "axis-length-angle-equivalence", "rotation-compatible-classes", "seven-system-partition", "Complete rank-three metric and crystallographic-rotation equivalence partitions periodic crystals into seven crystal-system classes."),
    row("CRYST-BRAVAIS", "Three-dimensional Bravais classification", "crystal_quasicrystal", "rank-three-translation-carrier", "centering-equivalence-relation", "primitive-lattice-classes", "fourteen-bravais-classes", "Complete rank-three translation lattices modulo basis and centering equivalence form fourteen Bravais classes."),
    row("CRYST-RECIPROCAL", "Reciprocal support and diffraction", "crystal_quasicrystal", "complete-scatterer-carrier", "path-phase-return-relation", "translation-dual-support", "peak-resolution-bounded", "Reciprocal support is the exact class of probe path labels whose phase returns coherently over the complete generated material organization; retained classes form diffraction peaks."),
    row("CRYST-QUASICRYSTAL", "Quasicrystalline aperiodic order", "crystal_quasicrystal", "complete-aperiodic-carrier", "long-range-recurrence-without-translation", "forbidden-periodic-order-retained", "sharp-nonperiodic-diffraction", "Quasicrystalline order is long-range coherent recurrence with sharp reciprocal support and no finite translation period; fivefold order is thereby admitted only outside periodic-lattice closure."),
    row("CRYST-PHONON", "Acoustic lattice excitation branches", "crystal_quasicrystal", "rank-three-displacement-carrier", "one-longitudinal-two-transverse", "collective-excitation-recurrence", "three-acoustic-branches", "A rank-three lattice has exactly one longitudinal and two transverse displacement orientations, forcing three acoustic excitation branches."),

    # Defects and microstructure — 8
    row("DEFECT-POINT", "Point-defect identity", "defects_microstructure", "site-and-occupant-carrier", "local-reference-difference", "defect-provenance-retained", "resolution-localized", "A point defect is the least localized retained difference between an actual site record and its declared reference-lattice word."),
    row("DEFECT-VACANCY", "Vacancy as structural absence", "defects_microstructure", "reference-site-carrier", "occupant-absence-held-label", "site-identity-preserved", "empty-one-not-numerical-zero", "A vacancy is a retained reference site carrying structural occupant absence, never deletion of the site or a numerical-zero material amount."),
    row("DEFECT-INTERSTITIAL-SUBSTITUTION", "Interstitial and substitutional defects", "defects_microstructure", "complete-local-site-carrier", "occupant-to-reference-comparison", "extra-site-versus-replaced-label", "defect-kind-distinguished", "Interstitial and substitutional defects are distinguished respectively by an added occupied site relation and a changed occupant label at a retained reference site."),
    row("DEFECT-DISLOCATION", "Dislocation line and slip", "defects_microstructure", "line-supported-mismatch-carrier", "closure-failure-around-loop", "burgers-path-record-retained", "slip-system-bounded", "A dislocation is a line-supported lattice mismatch whose complete circuit retains a nonclosing held translation and supplies a lawful slip path."),
    row("MICRO-GRAIN-BOUNDARY", "Grain and grain-boundary identity", "defects_microstructure", "orientation-coherent-region", "adjacent-orientation-mismatch", "interface-network-retained", "grain-scale-declared", "A grain is a maximal connected orientation-coherent crystal region; its boundary is the retained adjacency where two such orientation classes meet."),
    row("MICRO-INTERFACE", "Material interface law", "defects_microstructure", "two-material-boundary-carrier", "cross-boundary-compatibility", "traction-content-and-structure-ledger", "interface-scale-declared", "A material interface is the complete boundary relation joining distinct material or phase carriers with explicit structural, content and transfer compatibility records."),
    row("MICRO-DIFFUSION", "Diffusive constituent transport", "defects_microstructure", "labelled-constituent-carrier", "adjacent-site-transition-count", "global-content-conserved", "time-and-support-bounded", "Diffusion is counted adjacent-site redistribution of retained constituent labels with complete global content conservation and declared support/time recurrence."),
    row("MICRO-NUCLEATION-GROWTH", "Nucleation and phase growth", "defects_microstructure", "candidate-phase-cluster-carrier", "boundary-versus-interior-recurrence", "critical-persistence-and-growth", "condition-and-size-bounded", "A nucleus is the least generated cluster whose interior recurrence persists against its complete boundary relation; growth appends compatible cells while retaining phase and transfer provenance."),

    # Electronic structure and semiconductors — 9
    row("ELEC-BAND-GAP", "Electronic bands and structural gaps", "electronic_semiconductor", "complete-lattice-state-support", "phase-compatible-path-classes", "allowed-and-absent-support-retained", "energy-observation-bounded", "Electronic bands are complete phase-compatible recurrence classes on a material network; a band gap is a declared interval with no compatible generated state path."),
    row("ELEC-CONDUCTOR-CLASS", "Conductor, semiconductor and insulator distinction", "electronic_semiconductor", "carrier-access-support", "occupied-to-accessible-state-relation", "gap-and-filling-retained", "condition-bounded-transport-class", "Conductor, semiconductor and insulator classes are forced by whether occupied carrier support connects to accessible states directly, across a finite activation gap, or not within the declared conditions."),
    row("ELEC-CARRIER-DUALITY", "Electron and hole carrier duality", "electronic_semiconductor", "binary-occupation-carrier", "occupied-and-held-absence-pair", "charge-orientation-retained", "two-carrier-classes", "A binary exclusion-bounded state yields two transport descriptions: retained occupation and its held local absence, corresponding after sealing to electron and hole carriers."),
    row("ELEC-OCCUPATION", "Exclusion-bounded state occupation", "electronic_semiconductor", "canonical-mode-carrier", "empty-or-singly-held-support", "indistinguishable-duplication-rejected", "occupation-bound-one", "An exclusion-labelled canonical material mode admits structural absence or one retained indistinguishable occupation; a duplicate occupation is rejected."),
    row("SEMI-DOPING", "Doping as controlled constituent substitution", "electronic_semiconductor", "host-lattice-and-dopant-carrier", "valence-support-difference", "host-structure-and-provenance-retained", "concentration-bounded", "Doping is a source-bound substitution or addition that retains host organization while introducing an exact carrier-support difference."),
    row("SEMI-PN-TYPE", "p-type and n-type organization", "electronic_semiconductor", "doped-support-carrier", "excess-occupation-or-absence", "opposed-charge-orientations", "two-majority-carrier-classes", "The two held orientations of a doped carrier imbalance force occupation-majority and absence-majority semiconductor classes."),
    row("SEMI-JUNCTION", "p-n junction and depletion organization", "electronic_semiconductor", "opposed-doped-region-carrier", "cross-interface-carrier-transfer", "space-charge-and-field-retained", "equilibrium-and-bias-bounded", "Joining opposed doped regions forces interfacial carrier transfer until a retained depletion/space-charge organization balances transport and field response at declared conditions."),
    row("SEMI-TRANSPORT", "Semiconductor transport relation", "electronic_semiconductor", "labelled-mobile-carrier-support", "field-and-gradient-transition-count", "scattering-provenance-retained", "mobility-condition-bounded", "Semiconductor transport is the complete counted motion of occupied and held-absence carriers through accessible support under declared field, gradient and scattering conditions."),
    row("SEMI-OPTICAL", "Interband optical transition", "electronic_semiconductor", "initial-final-band-carrier", "probe-energy-compatible-transition", "occupation-gap-and-momentum-retained", "selection-and-resolution-bounded", "An interband optical response exists only when a probe supplies a complete compatible transition between retained occupied and accessible band states under the material selection rules."),

    # Superconducting, superfluid and topological matter — 9
    row("SC-PAIR", "Coherent paired-carrier state", "superconducting_superfluid_topological", "two-fermion-joint-carrier", "opposed-label-pairing", "integer-composite-recurrence", "pair-support-bounded", "The least exclusion-compatible collective carrier joins two opposed fermionic labels into one integer-composite recurrence class."),
    row("SC-ZERO-RESISTANCE", "Dissipation-closed superconducting transport", "superconducting_superfluid_topological", "phase-locked-pair-network", "collective-translation-recurrence", "momentum-randomizing-paths-absent", "critical-condition-bounded", "Superconducting zero-resistance transport is phase-locked pair recurrence on complete connected support with no retained label-compatible dissipative transition."),
    row("SC-MEISSNER", "Magnetic flux exclusion in the superconducting phase", "superconducting_superfluid_topological", "coherent-boundary-current-carrier", "applied-field-response-relation", "bulk-phase-lock-retained", "penetration-boundary-declared", "A phase-locked charged carrier network generates a boundary response whose complete bulk recurrence closes an incompatible applied magnetic distinction, yielding flux exclusion apart from the declared penetration boundary."),
    row("SC-FLUX-QUANTIZATION", "Superconducting flux quantization", "superconducting_superfluid_topological", "closed-phase-loop-carrier", "whole-return-winding-relation", "paired-charge-label-retained", "integer-flux-classes", "Single-valued return of a paired-carrier phase around a closed path forces whole winding classes and therefore discrete flux support."),
    row("SC-JOSEPHSON", "Weak-link coherent transfer", "superconducting_superfluid_topological", "two-condensate-and-link-carrier", "phase-difference-transfer-recurrence", "pair-identity-retained-across-link", "junction-condition-bounded", "A weak link between phase-locked pair supports carries a coherent transfer recurrence determined by their retained phase distinction without dissolving pair identity."),
    row("SF-SUPERFLUID", "Dissipation-closed superfluid transport", "superconducting_superfluid_topological", "neutral-coherent-fluid-carrier", "shared-phase-flow-recurrence", "loss-paths-below-gap-absent", "critical-condition-bounded", "Superfluid flow is shared-phase recurrence of a neutral collective carrier when the complete accessible transition census contains no allowed dissipative path below its first retained excitation boundary."),
    row("SF-CIRCULATION", "Quantized superfluid circulation", "superconducting_superfluid_topological", "closed-superflow-loop-carrier", "whole-phase-return-winding", "vortex-core-boundary-retained", "integer-circulation-classes", "Single-valued return of a superfluid phase around a closed path forces whole winding and discrete circulation classes with a retained vortex-core boundary."),
    row("TOPO-INVARIANT", "Topological material invariant", "superconducting_superfluid_topological", "complete-global-path-carrier", "connectivity-preserving-equivalence", "local-deformations-quotiented", "integer-path-class", "A material invariant is topological when its complete global path class is unchanged by every generated local deformation that retains connectivity and boundary records."),
    row("TOPO-BULK-BOUNDARY", "Bulk-boundary protected transport", "superconducting_superfluid_topological", "bulk-and-boundary-joint-carrier", "global-class-boundary-obstruction", "local-backscatter-paths-excluded", "gap-and-boundary-bounded", "A nontrivial bulk path class forces a boundary recurrence whose removal would require closing the retained bulk distinction; compatible local backscattering paths are therefore absent within the declared gap."),

    # Mechanical response — 8
    row("MECH-STRESS-STRAIN", "Stress and strain records", "mechanical", "material-region-and-boundary-carrier", "load-transfer-and-shape-change", "direction-support-and-reference-retained", "method-and-scale-bounded", "Stress is oriented load transfer per generated boundary support; strain is the exact retained change of internal separation relative to the same reference material state."),
    row("MECH-ELASTICITY", "Elastic recovery", "mechanical", "bond-network-state-carrier", "reversible-displacement-path", "original-adjacency-class-restored", "elastic-boundary-declared", "Elastic response is a material transition path whose load release returns every retained constituent and adjacency relation to the original canonical state."),
    row("MECH-PLASTICITY", "Plastic deformation", "mechanical", "bond-and-defect-network-carrier", "irreversible-same-material-reorganization", "content-retained-adjacency-changed", "yield-boundary-declared", "Plastic response retains material content and phase identity while a defect-mediated transition changes the canonical adjacency organization after load release."),
    row("MECH-SLIP", "Dislocation-mediated slip", "mechanical", "dislocation-and-slip-plane-carrier", "whole-translation-advance", "burgers-label-and-content-retained", "slip-system-bounded", "Slip is a counted whole-lattice translation propagated by a retained dislocation along a compatible plane/direction without requiring simultaneous rupture of the complete plane."),
    row("MECH-MODULUS", "Elastic modulus as response ratio", "mechanical", "elastic-state-pair-carrier", "stress-to-strain-exact-relation", "direction-condition-and-range-retained", "linear-window-bounded", "An elastic modulus is the exact stress/strain response relation for one declared material direction, condition, reference state and reversible response window."),
    row("MECH-STRENGTH-HARDNESS", "Strength and hardness boundaries", "mechanical", "material-and-test-carrier", "load-to-persistent-change-threshold", "method-geometry-and-scale-retained", "threshold-not-universal-constant", "Strength and hardness are method-bounded thresholds at which a declared loading path first produces retained plastic, indentation or failure organization."),
    row("MECH-FRACTURE", "Fracture and toughness", "mechanical", "crack-and-bond-network-carrier", "advance-versus-resistance-relation", "new-boundary-and-energy-ledger-retained", "geometry-and-rate-bounded", "Fracture is connected bond-path separation creating new retained boundary support; toughness is the declared resistance relation for crack initiation or advance with a complete work ledger."),
    row("MECH-FATIGUE-CREEP", "Fatigue and creep", "mechanical", "history-labelled-material-carrier", "cyclic-or-sustained-transition-accumulation", "damage-defect-and-time-provenance", "load-temperature-time-bounded", "Fatigue and creep are distinct history-dependent material processes: recurrence-counted damage under cyclic load and retained deformation under sustained load and time/temperature conditions."),

    # Thermal, magnetic and optical response — 8
    row("THERM-HEAT-CAPACITY", "Heat capacity and excitation storage", "thermal_magnetic_optical", "material-excitation-support", "energy-to-state-count-change", "condition-and-phase-retained", "temperature-window-bounded", "Material heat capacity is the exact relation between supplied thermal carrier change and the resulting accessible excitation-support change at declared conditions."),
    row("THERM-CONDUCTION", "Thermal conduction", "thermal_magnetic_optical", "energy-labelled-cell-network", "adjacent-energy-transfer-count", "total-energy-ledger-retained", "gradient-time-support-bounded", "Thermal conduction is counted adjacent transfer of retained energy labels through connected material support with complete source, boundary and scattering provenance."),
    row("THERM-EXPANSION", "Thermal expansion", "thermal_magnetic_optical", "bond-separation-network", "excitation-conditioned-separation-change", "material-identity-retained", "direction-and-temperature-bounded", "Thermal expansion is the condition-bounded change of recurrent constituent separation with excitation while material identity and complete adjacency provenance remain retained."),
    row("MAG-FERROMAGNETISM", "Ferromagnetic order", "thermal_magnetic_optical", "local-moment-network", "aligned-shared-orientation-recurrence", "connected-net-moment-retained", "ordering-condition-bounded", "Ferromagnetism is connected recurrence of aligned local held-moment orientations producing a retained macroscopic orientation class."),
    row("MAG-ANTIFERROMAGNETISM", "Antiferromagnetic order", "thermal_magnetic_optical", "bipartite-moment-network", "opposed-sublattice-recurrence", "local-order-global-closure-retained", "ordering-condition-bounded", "Antiferromagnetism is stable opposed recurrence on distinguishable sublattices that retains local order while the complete macroscopic moment distinction closes."),
    row("DIEL-POLARIZATION", "Dielectric polarization", "thermal_magnetic_optical", "bound-charge-orientation-carrier", "applied-field-displacement-relation", "charge-conservation-and-relaxation-retained", "frequency-condition-bounded", "Dielectric polarization is a retained field-conditioned redistribution or orientation of bound held-charge labels with complete conservation and relaxation records."),
    row("OPT-REFRACTIVE", "Optical propagation and refractive response", "thermal_magnetic_optical", "probe-and-material-excitation-carrier", "coherent-delay-and-transfer-relation", "frequency-phase-and-loss-retained", "spectral-condition-bounded", "Material refractive response is the source-bound phase/delay relation produced by coherent probe coupling to accessible material excitations while propagation, loss and dispersion records remain separate."),
    row("PHASE-TRANSITION", "Material phase transition", "thermal_magnetic_optical", "initial-final-phase-carrier", "stable-macro-fibre-change", "symmetry-content-and-path-ledger", "condition-and-hysteresis-bounded", "A material phase transition is a provenance-retaining change between stable macro-recurrence and symmetry classes with explicit conditions, path and hysteresis boundary."),

    # Material classes and molecular-to-bulk correspondence — 9
    row("CLASS-METAL", "Metallic material organization", "material_classes_bulk", "connected-atomic-network", "delocalized-carrier-access", "translation-and-bonding-retained", "condition-bounded-metal-class", "A metallic material is a connected atomic organization with delocalized carrier access across multiple constituent cells and no declared transport gap at its operating conditions."),
    row("CLASS-CERAMIC", "Ceramic material organization", "material_classes_bulk", "inorganic-network-carrier", "localized-ionic-covalent-joining", "phase-and-grain-structure-retained", "processing-condition-bounded", "A ceramic is an inorganic nonmetallic material whose bulk carrier is a localized ionic/covalent network with retained phase, porosity and grain/interface organization."),
    row("CLASS-POLYMER", "Polymeric material organization", "material_classes_bulk", "repeated-unit-chain-carrier", "covalent-backbone-recurrence", "sequence-length-branching-and-entanglement", "distribution-bounded", "A polymeric material is a population of covalently recurrent chain carriers with explicit repeat identity, sequence, length/branching distribution and interchain organization."),
    row("CLASS-COMPOSITE", "Composite material organization", "material_classes_bulk", "multiple-constituent-carriers", "interface-mediated-load-transfer", "constituent-identities-retained", "architecture-and-scale-bounded", "A composite is a joint material whose distinguishable constituent carriers persist while interfaces and architecture compose their load, transport or barrier responses."),
    row("CLASS-GLASS", "Glass and amorphous organization", "material_classes_bulk", "connected-nonperiodic-network", "local-order-without-translation", "history-and-relaxation-retained", "observation-time-bounded", "A glass is a connected material with retained local structural recurrence but no crystalline translation class, whose macrostate depends on preparation and observation-time relaxation."),
    row("CLASS-POROUS", "Porous material organization", "material_classes_bulk", "solid-and-empty-support-carrier", "connected-phase-and-pore-network", "interface-topology-retained", "resolution-and-access-bounded", "A porous material is a joint solid/structural-absence support whose pore connectivity, interface and accessibility are retained at a declared resolution."),
    row("BULK-CORRESPONDENCE", "Molecular-to-bulk correspondence", "material_classes_bulk", "complete-constituent-ensemble", "local-relation-to-network-composition", "fluctuation-interface-and-history-retained", "representative-scale-bounded", "A bulk material law is admitted only when the complete constituent/interaction network composes to a scale-stable observation while fluctuations, interfaces and preparation history remain explicitly bounded."),
    row("BULK-ANISOTROPY", "Material anisotropy", "material_classes_bulk", "direction-labelled-structure-carrier", "orientation-dependent-response", "same-material-identity-retained", "coordinate-and-symmetry-bounded", "Anisotropy is inequality of response relations across retained material directions after specimen, condition and method identities are held fixed."),
    row("BULK-SIZE-SURFACE", "Size and surface effects", "material_classes_bulk", "finite-bulk-and-boundary-carrier", "boundary-to-interior-support-ratio", "surface-state-and-curvature-retained", "size-shape-bounded", "A material size effect occurs when the exact boundary/interior support relation changes the accessible state, transfer or mechanical census; it is never a free scale correction."),

    # Processing and degradation — 8
    row("PROC-PATH", "Processing–structure–property path", "processing_degradation", "history-labelled-material-carrier", "process-to-structure-to-response-map", "intermediate-states-retained", "route-condition-bounded", "A materials process is a complete ordered path from input carrier through retained structural states to property relations; endpoint labels alone cannot erase the path."),
    row("PROC-PHASE-DIAGRAM", "Phase stability and coexistence organization", "processing_degradation", "composition-condition-support", "stable-phase-minimality-relation", "coexisting-fractions-and-boundaries", "declared-domain-bounded", "A phase map partitions generated composition/condition support by the stable material recurrence class, retaining coexistence, fraction and transition boundaries without fitted extrapolation beyond its domain."),
    row("PROC-SOLIDIFICATION", "Solidification", "processing_degradation", "liquid-and-solid-phase-carrier", "nucleation-growth-and-rejection-path", "latent-transfer-and-composition-ledger", "rate-gradient-bounded", "Solidification is the ordered nucleation and growth path from mobile to position-retaining organization with complete energy, constituent rejection and interface provenance."),
    row("PROC-SINTERING", "Sintering and densification", "processing_degradation", "particle-and-pore-network", "interface-driven-material-transfer", "content-conserved-pore-reorganized", "temperature-time-load-bounded", "Sintering is interface-mediated constituent transport that joins particles and reorganizes structural absence while conserving material content and retaining the processing path."),
    row("PROC-HEAT-TREATMENT", "Heat treatment", "processing_degradation", "history-labelled-phase-network", "thermal-path-to-microstructure-map", "time-temperature-transition-record", "cooling-and-specimen-bounded", "Heat treatment is a declared thermal/time path whose phase, defect and microstructure transitions are retained and whose property consequence is path-bound."),
    row("DEGR-CORROSION", "Corrosion", "processing_degradation", "material-environment-joint-carrier", "interfacial-redox-and-transport-path", "mass-charge-and-product-ledger", "environment-time-bounded", "Corrosion is an interfacial reaction/transport process that transforms a material and environment jointly while retaining complete constituent, charge, product and boundary provenance."),
    row("DEGR-WEAR", "Wear and tribological material transfer", "processing_degradation", "contacting-surface-carriers", "load-motion-interface-transition", "debris-transfer-and-surface-ledger", "contact-history-bounded", "Wear is retained material transfer or surface reorganization produced by a declared contact/load/motion path; frictional response and material loss remain separately recorded."),
    row("DEGR-RADIATION", "Radiation damage", "processing_degradation", "material-and-probe-carrier", "energy-transfer-defect-generation", "displacement-transmutation-and-recovery", "dose-rate-spectrum-bounded", "Radiation damage is the complete source-bound path from probe energy transfer to retained displacement, excitation or transmutation defects and their subsequent migration/recovery."),

    # Advanced functional and sustainable materials — 8
    row("FUNC-PIEZOELECTRIC", "Piezoelectric coupling", "advanced_functional_sustainable", "noncentrosymmetric-structure-carrier", "mechanical-electric-cross-response", "orientation-and-charge-ledger", "field-stress-condition-bounded", "Piezoelectricity is a reversible cross-relation between mechanical deformation and held electric polarization permitted only when the retained material symmetry does not close the orientation distinction."),
    row("FUNC-FERROELECTRIC", "Ferroelectric order and switching", "advanced_functional_sustainable", "polar-domain-network", "stable-opposed-polarization-classes", "field-driven-domain-path-retained", "hysteresis-condition-bounded", "Ferroelectricity is a material phase with stable opposed polarization recurrence classes and a retained field-driven switching path between them."),
    row("FUNC-THERMOELECTRIC", "Thermoelectric coupling", "advanced_functional_sustainable", "charge-and-energy-carrier-network", "temperature-gradient-charge-transfer", "joint-energy-charge-ledger", "direction-condition-bounded", "Thermoelectric response is the joint conserved relation between energy-gradient transport and held-charge transport on the same material network."),
    row("FUNC-PHOTONIC", "Photonic material organization", "advanced_functional_sustainable", "electromagnetic-cell-network", "wave-recurrence-and-gap-support", "geometry-frequency-and-boundary-retained", "spectral-scale-bounded", "A photonic material organizes electromagnetic recurrence support so that allowed propagation classes and structural gaps follow from complete generated geometry and boundary relations."),
    row("FUNC-MAGNETIC", "Functional magnetic material response", "advanced_functional_sustainable", "moment-domain-and-field-carrier", "field-history-response-map", "domain-wall-loss-and-remanence", "frequency-temperature-bounded", "A functional magnetic response is the complete relation among applied field, domain transition path, retained orientation, loss and remanence at declared frequency and temperature."),
    row("FUNC-NANOMATERIAL", "Nanoscale material boundary", "advanced_functional_sustainable", "finite-constituent-boundary-carrier", "boundary-support-comparable-to-interior", "discrete-state-and-interface-retained", "size-shape-resolution-bounded", "A nanomaterial regime begins when boundary and finite-support distinctions remain in the material state/property census and cannot be closed by the bulk observation quotient."),
    row("FUNC-BIOMATERIAL", "Biomaterial interface boundary", "advanced_functional_sustainable", "material-biological-interface-carrier", "bidirectional-response-and-transfer", "material-and-biological-identities-retained", "exposure-function-bounded", "A biomaterial claim is a joint material/biological interface relation with explicit exposure, transfer, response and function boundaries; biological outcomes cannot select the material law."),
    row("SUST-LIFECYCLE", "Material lifecycle and recyclability", "advanced_functional_sustainable", "source-process-use-recovery-carrier", "complete-material-flow-path", "loss-transformation-and-quality-ledger", "system-boundary-declared", "A material lifecycle is the complete source-to-processing-to-use-to-recovery flow ledger; recyclability requires an explicit identity-preserving recovery path and records every transformation, loss and quality boundary."),
)

# The short alias is used by branch tooling; the descriptive name remains the
# public API so the inventory cannot be mistaken for admitted claims.
OBLIGATIONS = MATERIALS_OBLIGATIONS


def validate_inventory() -> None:
    if len(MATERIALS_OBLIGATIONS) != 84:
        raise ValueError("Materials inventory must contain exactly 84 registered obligations")
    if len({item.claim_id for item in MATERIALS_OBLIGATIONS}) != len(MATERIALS_OBLIGATIONS):
        raise ValueError("Materials inventory contains duplicate claim identities")
    observed = tuple(dict.fromkeys(item.subbranch for item in MATERIALS_OBLIGATIONS))
    if observed != SUBBRANCH_ORDER:
        raise ValueError("Materials inventory is not in declared dependency order")
    if any(not item.statement.strip() for item in MATERIALS_OBLIGATIONS):
        raise ValueError("Materials inventory contains an empty theorem statement")


validate_inventory()

__all__ = (
    "MaterialsObligation",
    "MATERIALS_OBLIGATIONS",
    "OBLIGATIONS",
    "SUBBRANCH_ORDER",
    "validate_inventory",
)
