"""Frozen categorical obligation inventory for the complete Physics branch.

The inventory names work; it does not assert that an unadmitted row is true.
Conventional subject names are correspondence labels added at the inventory
boundary.  They cannot select a Fold candidate or a measured result.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicsObligation:
    claim_id: str
    subbranch: str
    title: str
    evidence_mode: str
    external_source_ids: tuple[str, ...]


FORMAL = "formal_forcing"
EMPIRICAL = "formal_forcing_plus_blind_external_measurement"

BIPM = ("BIPM-SI-BROCHURE-9-2026",)
CODATA = ("NIST-CODATA-2022-ALL-CONSTANTS",)
ATOMIC = ("NIST-ASD-5.12",)
PARTICLE = ("PDG-2025-SUMMARY-TABLES", "CERN-OPEN-DATA-DATASET-API-2026-07-23")
NUCLEAR = ("IAEA-ENSDF-CURRENT-2026-07-23", "IAEA-ENDF-CURRENT-2026-07-23")
THERMO = ("IAPWS-RELEASES-2026-07-23", "NIST-CHEMISTRY-WEBBOOK-2026-07-23")
REFERENCE = ("NIST-SRD-INDEX-2026-07-23",)
GRAVITY = ("GWOSC-V2-CATALOGS-2026-07-23", "NIST-CODATA-2022-ALL-CONSTANTS")
COSMOLOGY = ("NASA-LAMBDA-2026-07-23", "GWOSC-V2-CATALOGS-2026-07-23")


def obligation(claim_id: str, subbranch: str, title: str, evidence_mode: str, *sources: str) -> PhysicsObligation:
    return PhysicsObligation(claim_id, subbranch, title, evidence_mode, tuple(sources))


OBLIGATIONS = (
    # Measurement, metrology and empirical custody.
    obligation("SFT-PHYS-MEAS-CAPABILITY-PREDICTION-001", "measurement_metrology", "Capability-closed exact Fold prediction form", FORMAL),
    obligation("SFT-PHYS-MEAS-TARGET-CUSTODY-001", "measurement_metrology", "Portable target commitment and post-seal custody", FORMAL),
    obligation("SFT-PHYS-MEAS-HOSTILE-PACKAGE-001", "measurement_metrology", "Hostile empirical-package and authority protection", FORMAL),
    obligation("SFT-PHYS-MEAS-OBSERVATION-CARRIER-001", "measurement_metrology", "Physical observation and retained distinction", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-QUANTITY-CARRIER-001", "measurement_metrology", "Physical quantity as reference-equivalence carrier", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001", "measurement_metrology", "Dimension composition and independence", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-UNIT-COMPARISON-001", "measurement_metrology", "Unit comparison and exact scale transport", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-REFERENCE-REALIZATION-001", "measurement_metrology", "Reference realization and traceability", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-VALUE-RECORD-001", "measurement_metrology", "Measured-value record separated from proof value", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-UNCERTAINTY-001", "measurement_metrology", "Measurement uncertainty as retained admissible alternatives", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-CALIBRATION-001", "measurement_metrology", "Calibration chain and comparison closure", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MEAS-DIMENSIONAL-CONSISTENCY-001", "measurement_metrology", "Dimensional consistency and lawful conversion", EMPIRICAL, *BIPM),

    # Relational mechanics.
    obligation("SFT-PHYS-MECH-EVENT-CHANGE-001", "mechanics", "Physical event and generated change", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-DURATION-001", "mechanics", "Duration from ordered recurrence", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MECH-LOCATION-DISPLACEMENT-001", "mechanics", "Location, separation and held displacement orientation", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-MECH-SPEED-VELOCITY-001", "mechanics", "Speed and oriented velocity", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-ACCELERATION-001", "mechanics", "Change of velocity and acceleration", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-INERTIA-001", "mechanics", "Inertial persistence", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-MOMENTUM-001", "mechanics", "Momentum carrier and transfer", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-FORCE-001", "mechanics", "Force as constrained momentum transfer", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-WORK-ENERGY-001", "mechanics", "Work, kinetic change and energy carrier", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-POWER-001", "mechanics", "Power as ordered energy transfer", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-ANGULAR-MOTION-001", "mechanics", "Angular motion and cyclic orientation", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-ANGULAR-MOMENTUM-001", "mechanics", "Angular momentum and torque", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-COMPOSITE-CENTRE-001", "mechanics", "Composite motion and centre relation", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-CONSERVATION-001", "mechanics", "Mechanical conservation under closed transfer", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MECH-CONSTRAINT-OSCILLATION-001", "mechanics", "Constrained motion, restoration and oscillation", EMPIRICAL, *REFERENCE),

    # Interactions and fields.
    obligation("SFT-PHYS-FIELD-SOURCE-RESPONSE-001", "interactions_fields", "Source, response and field carrier", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-GEOMETRIC-DILUTION-001", "interactions_fields", "Generated support and geometric dilution", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-GRAVITATIONAL-INTERACTION-001", "interactions_fields", "Gravitational interaction at the weak relational boundary", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-FIELD-ELECTRIC-DISTINCTION-001", "interactions_fields", "Electric distinction and held charge orientation", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-ELECTRIC-POTENTIAL-001", "interactions_fields", "Electric field, potential and work correspondence", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-MAGNETIC-001", "interactions_fields", "Magnetic response to oriented change", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-INDUCTION-001", "interactions_fields", "Induction from changing linked support", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-ELECTROMAGNETIC-COMPOSITION-001", "interactions_fields", "Electric-magnetic compositional closure", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-FIELD-GAUGE-EQUIVALENCE-001", "interactions_fields", "Gauge-equivalent descriptions and retained observables", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-FIELD-LOCALITY-CAUSALITY-001", "interactions_fields", "Local propagation and causal accessibility", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-FIELD-RADIATION-001", "interactions_fields", "Radiative transport and source detachment", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-FIELD-INTERACTION-CLASSES-001", "interactions_fields", "Empirical closure of physical interaction classes", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-FIELD-CONSERVED-SOURCE-001", "interactions_fields", "Source continuity and field conservation", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-FIELD-ACTION-REACTION-001", "interactions_fields", "Reciprocal interaction and transferred distinction", EMPIRICAL, *CODATA),

    # Waves and propagation.
    obligation("SFT-PHYS-WAVE-PERIOD-FREQUENCY-001", "waves", "Period, recurrence and frequency", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-WAVE-PROPAGATION-001", "waves", "Generated wave propagation", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-WAVE-SPEED-LENGTH-FREQUENCY-001", "waves", "Propagation speed, wavelength and frequency relation", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-WAVE-SUPERPOSITION-001", "waves", "Wave superposition", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-WAVE-INTERFERENCE-001", "waves", "Wave interference and predecessor merging", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-WAVE-DIFFRACTION-001", "waves", "Diffraction at constrained support", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-WAVE-POLARIZATION-001", "waves", "Polarization as held transverse orientation", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-WAVE-DISPERSION-001", "waves", "Dispersion and support-dependent propagation", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-WAVE-RESONANCE-001", "waves", "Resonance and recurrence matching", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-WAVE-ENERGY-MOMENTUM-001", "waves", "Wave energy and momentum transport", EMPIRICAL, *CODATA),

    # Thermodynamics and statistical physics.
    obligation("SFT-PHYS-THERMO-MICRO-MACRO-001", "thermodynamics", "Microstate-to-macrostate observation", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-TEMPERATURE-001", "thermodynamics", "Temperature carrier and thermal ordering", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-EQUILIBRIUM-001", "thermodynamics", "Thermal equilibrium equivalence", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-HEAT-WORK-001", "thermodynamics", "Heat and work as distinct energy-transfer traces", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-FIRST-LAW-001", "thermodynamics", "Closed energy accounting", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-ENTROPY-001", "thermodynamics", "Thermodynamic entropy from unresolved support", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-SECOND-LAW-001", "thermodynamics", "Irreversible observation and entropy orientation", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-THIRD-LAW-001", "thermodynamics", "Finite unattainability boundary", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-STATISTICAL-WEIGHT-001", "thermodynamics", "Exact finite statistical weight", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-STATE-RELATION-001", "thermodynamics", "Thermodynamic state relation", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-PHASE-EQUILIBRIUM-001", "thermodynamics", "Phase coexistence and transition", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-KINETIC-TRANSPORT-001", "thermodynamics", "Kinetic transport and collision mixing", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-FLUCTUATION-001", "thermodynamics", "Finite fluctuation and recurrence", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-IRREVERSIBILITY-001", "thermodynamics", "Macroscopic irreversibility with retained microtrace", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-THERMO-RESPONSE-001", "thermodynamics", "Susceptibility, response and transport correspondence", EMPIRICAL, *REFERENCE),

    # Quantum physics, distinct from the already closed computation model.
    obligation("SFT-PHYS-QUANTUM-PHYSICAL-STATE-001", "quantum_physics", "Physical quantum state correspondence", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-EVOLUTION-001", "quantum_physics", "Reversible physical quantum evolution", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-OBSERVABLE-001", "quantum_physics", "Observable and measurement record", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-WEIGHT-001", "quantum_physics", "Measurement weights from exact branch support", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-INCOMPATIBILITY-001", "quantum_physics", "Incompatible observations and uncertainty", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-SPIN-001", "quantum_physics", "Spin and finite cyclic label action", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001", "quantum_physics", "Identical physical constituents", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-QUANTUM-EXCLUSION-001", "quantum_physics", "Exclusion from antisymmetric composition", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-TUNNELLING-001", "quantum_physics", "Barrier traversal on complete support", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-QUANTUM-DISCRETE-SPECTRA-001", "quantum_physics", "Discrete bound-state spectra", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-QUANTUM-ENTANGLEMENT-001", "quantum_physics", "Physical entanglement correlations", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-QUANTUM-BELL-001", "quantum_physics", "Bell correlation and local-hidden-record boundary", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-QUANTUM-CONTEXTUALITY-001", "quantum_physics", "Context-dependent joint observation", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-QUANTUM-DECOHERENCE-001", "quantum_physics", "Decoherence through environmental record distribution", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-QUANTUM-CLASSICAL-LIMIT-001", "quantum_physics", "Operational quantum-to-classical physical limit", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-QUANTUM-NO-SIGNALLING-001", "quantum_physics", "Entanglement and no-signalling boundary", EMPIRICAL, *PARTICLE),

    # Matter, particles and nuclei.
    obligation("SFT-PHYS-MATTER-MASS-ENERGY-001", "matter_particles_nuclei", "Mass-energy correspondence", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-MATTER-PARTICLE-ANTIPARTICLE-001", "matter_particles_nuclei", "Particle-antiparticle held orientation", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-FERMION-BOSON-001", "matter_particles_nuclei", "Fermion and boson composition classes", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-CONSERVED-LABELS-001", "matter_particles_nuclei", "Conserved physical labels", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-PARTICLE-SPECTRUM-001", "matter_particles_nuclei", "Observed elementary-particle spectrum", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-COMPOSITE-HADRONS-001", "matter_particles_nuclei", "Composite hadron organization", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-SCATTERING-001", "matter_particles_nuclei", "Scattering and cross-section measure", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-DECAY-001", "matter_particles_nuclei", "Particle transition and decay", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-MATTER-MIXING-001", "matter_particles_nuclei", "State mixing and oscillation", EMPIRICAL, *PARTICLE),
    obligation("SFT-PHYS-NUCLEAR-BINDING-001", "matter_particles_nuclei", "Nuclear binding and mass relation", EMPIRICAL, *NUCLEAR),
    obligation("SFT-PHYS-NUCLEAR-LEVELS-001", "matter_particles_nuclei", "Nuclear levels and transitions", EMPIRICAL, *NUCLEAR),
    obligation("SFT-PHYS-NUCLEAR-RADIOACTIVITY-001", "matter_particles_nuclei", "Radioactive transition support", EMPIRICAL, *NUCLEAR),
    obligation("SFT-PHYS-NUCLEAR-REACTIONS-001", "matter_particles_nuclei", "Nuclear reaction and channel accounting", EMPIRICAL, *NUCLEAR),
    obligation("SFT-PHYS-NUCLEAR-FISSION-001", "matter_particles_nuclei", "Fission decomposition", EMPIRICAL, *NUCLEAR),
    obligation("SFT-PHYS-NUCLEAR-FUSION-001", "matter_particles_nuclei", "Fusion composition", EMPIRICAL, *NUCLEAR),

    # Spacetime and gravitation.
    obligation("SFT-PHYS-SPACETIME-EVENT-RELATION-001", "spacetime_gravitation", "Relational spacetime event", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-SPACETIME-INTERVAL-001", "spacetime_gravitation", "Invariant event interval", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-SPACETIME-CAUSAL-ORDER-001", "spacetime_gravitation", "Causal order and accessibility cone", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-SPACETIME-INERTIAL-TRANSFORMATION-001", "spacetime_gravitation", "Inertial frame correspondence", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-SPACETIME-LIMIT-SPEED-001", "spacetime_gravitation", "Invariant limiting propagation speed", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-SPACETIME-CLOCK-RATE-001", "spacetime_gravitation", "Relative clock-rate relation", EMPIRICAL, *BIPM),
    obligation("SFT-PHYS-SPACETIME-LENGTH-RELATION-001", "spacetime_gravitation", "Relative spatial-extent relation", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-GRAVITY-EQUIVALENCE-001", "spacetime_gravitation", "Inertial-gravitational equivalence", EMPIRICAL, *CODATA),
    obligation("SFT-PHYS-GRAVITY-CURVATURE-001", "spacetime_gravitation", "Source-linked relational curvature", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-GRAVITY-GEODESIC-001", "spacetime_gravitation", "Free propagation on curved relation", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-GRAVITY-FIELD-SOURCE-001", "spacetime_gravitation", "Gravitational field-source closure", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-GRAVITY-WAVE-001", "spacetime_gravitation", "Gravitational-wave propagation", EMPIRICAL, *GRAVITY),
    obligation("SFT-PHYS-GRAVITY-HORIZON-001", "spacetime_gravitation", "Causal horizon boundary", EMPIRICAL, *GRAVITY),

    # Fluids, plasmas and condensed structures.
    obligation("SFT-PHYS-CONTINUUM-COARSE-GRAIN-001", "continua_collective_matter", "Finite coarse-grained continuum correspondence", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-FLUID-DENSITY-001", "continua_collective_matter", "Density as exact content-to-support relation", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-FLUID-PRESSURE-STRESS-001", "continua_collective_matter", "Pressure and stress transport", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-FLUID-CONSERVATION-001", "continua_collective_matter", "Flow conservation", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-FLUID-INVISCID-001", "continua_collective_matter", "Inviscid flow correspondence", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-FLUID-VISCOSITY-001", "continua_collective_matter", "Viscous momentum transport", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-FLUID-TURBULENCE-001", "continua_collective_matter", "Finite turbulence and cascade boundary", EMPIRICAL, *THERMO),
    obligation("SFT-PHYS-PLASMA-COLLECTIVE-001", "continua_collective_matter", "Plasma collective response", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-PLASMA-OSCILLATION-001", "continua_collective_matter", "Plasma oscillation and screening", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-PLASMA-MHD-001", "continua_collective_matter", "Magnetofluid composition", EMPIRICAL, *ATOMIC),
    obligation("SFT-PHYS-CONDENSED-LATTICE-001", "continua_collective_matter", "Lattice order and excitation", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-CONDENSED-BAND-001", "continua_collective_matter", "Band support and transport", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-CONDENSED-PHASE-ORDER-001", "continua_collective_matter", "Collective order and phase transition", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-CONDENSED-SUPERCONDUCTIVITY-001", "continua_collective_matter", "Superconducting coherent transport", EMPIRICAL, *REFERENCE),
    obligation("SFT-PHYS-CONDENSED-TOPOLOGICAL-001", "continua_collective_matter", "Topological collective-state correspondence", EMPIRICAL, *REFERENCE),

    # Physical relations required at the boundary of the later Astronomy/Cosmology branch.
    obligation("SFT-PHYS-COSMO-REDSHIFT-001", "cosmological_boundary", "Propagation redshift relation", EMPIRICAL, *COSMOLOGY),
    obligation("SFT-PHYS-COSMO-EXPANSION-001", "cosmological_boundary", "Relational expansion observation", EMPIRICAL, *COSMOLOGY),
    obligation("SFT-PHYS-COSMO-BACKGROUND-001", "cosmological_boundary", "Background-radiation field relation", EMPIRICAL, *COSMOLOGY),
    obligation("SFT-PHYS-COSMO-LENSING-001", "cosmological_boundary", "Gravitational lensing relation", EMPIRICAL, *COSMOLOGY),
    obligation("SFT-PHYS-COSMO-DISTANCE-001", "cosmological_boundary", "Causal distance and observation-time relation", EMPIRICAL, *COSMOLOGY),
    obligation("SFT-PHYS-COSMO-STRUCTURE-GROWTH-001", "cosmological_boundary", "Finite structure-growth relation", EMPIRICAL, *COSMOLOGY),
    obligation("SFT-PHYS-COSMO-BRANCH-BOUNDARY-001", "cosmological_boundary", "Physics-to-astronomy/cosmology handoff boundary", FORMAL),
)


SUBBRANCH_ORDER = (
    "measurement_metrology",
    "mechanics",
    "interactions_fields",
    "waves",
    "thermodynamics",
    "quantum_physics",
    "matter_particles_nuclei",
    "spacetime_gravitation",
    "continua_collective_matter",
    "cosmological_boundary",
)


def validate_inventory() -> None:
    if tuple(dict.fromkeys(row.subbranch for row in OBLIGATIONS)) != SUBBRANCH_ORDER:
        raise ValueError("Physics obligations do not follow the frozen dependency order")
    claim_ids = tuple(row.claim_id for row in OBLIGATIONS)
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("Physics inventory contains duplicate claim identities")
    if any(row.evidence_mode not in {FORMAL, EMPIRICAL} for row in OBLIGATIONS):
        raise ValueError("Physics inventory contains an unclassified evidence mode")
    if any(row.evidence_mode == EMPIRICAL and not row.external_source_ids for row in OBLIGATIONS):
        raise ValueError("Every empirical Physics obligation requires an external measurement body")
    if any(row.evidence_mode == FORMAL and row.external_source_ids for row in OBLIGATIONS):
        raise ValueError("Formal Physics prerequisites cannot import measurement sources")


validate_inventory()

__all__ = ("EMPIRICAL", "FORMAL", "OBLIGATIONS", "SUBBRANCH_ORDER", "PhysicsObligation", "validate_inventory")
