#!/usr/bin/env python3
"""Consolidate open atomic Physics obligations into independent law families.

This is dependency planning, not claim admission.  It reads the categorical
atomic audit, requires every open Physics atom exactly once, and emits no
scientific receipt or census promotion.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audits/physics_v1_v2_atomic_ownership.json"
OUTPUT = ROOT / "census/physics_v1_v2_gap_families.json"
REPORT = ROOT / "audits/physics_v1_v2_gap_families.md"


def members(*values: str) -> tuple[str, ...]:
    return values


FAMILIES = ()


COMPLETED_FAMILIES = (
    {
        "family_id": "PHYS-GAP-FAMILY-033",
        "title": "Grand Lock all-constant dependency, perturbation and no-omission certificate",
        "source_members": [
            "SFT-PRIOR-V1-XVIII-8-PHYS-NO-OMISSION",
            "SFT-PRIOR-V1-XVIII-8-PHYS-EMPIRICAL-VECTOR",
            "SFT-PRIOR-V1-U3-PHYS-DEPENDENCY-DICTIONARY",
            "SFT-PRIOR-V2-274-PHYS-GENERATOR-PERTURBATION",
            "SFT-PRIOR-V2-274-PHYS-CROSS-DOMAIN-LOCKS",
        ],
        "claim_id": "SFT-PHYS-GRAND-LOCK-TERMINAL-075",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-GRAND-LOCK-076",
        "status": "model_admitted_complete_ownership_root_trace_21_value_generator_adverse_cross_domain_identity_and_234_claim_147_source_empirical_reconciliation_with_extension_open",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-029",
        "title": "gravitational-wave chirp and ringdown",
        "source_members": ["v1:IX-6"],
        "claim_id": "SFT-PHYS-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-TERMINAL-073",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074",
        "inherited_claim_ids": [
            "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
            "SFT-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012",
            "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003"
        ],
        "status": "model_admitted_depth_independent_rising_chirp_first_contact_two_to_one_merger_positive_finite_ringdown_and_complete_observational_postseal_vector_with_explicit_preseal_context",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-028",
        "title": "degenerate compact-object limits and black-hole thermodynamics",
        "source_members": ["v1:IX-5", "v1:IX-3", "v2:255"],
        "claim_id": "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-COMPACT-HORIZON-THERMODYNAMICS-072",
        "inherited_claim_ids": [
            "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
            "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003",
            "SFT-PHYS-QUANTUM-EXCLUSION-001",
            "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023"
        ],
        "status": "model_admitted_exact_q4_q6_exclusion_scaling_three_quarter_to_half_One_threshold_two_fibre_endpoint_families_inverse_mass_temperature_quarter_area_information_and_complete_postseal_compact_object_boundary_without_rewarding_Hawking_nonobservation",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-027",
        "title": "stellar nuclear chain, collapse and heavy-element channels",
        "source_members": ["v1:IX-4", "v1:IX-2", "v2:128", "v2:140", "v2:150"],
        "claim_id": "SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-STELLAR-NUCLEAR-COLLAPSE-070",
        "inherited_claim_ids": ["SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006", "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005"],
        "status": "model_admitted_depth_independent_stage_access_unique_binding_terminal_support_loss_collapse_thermonuclear_unbinding_and_neutral_capture_rebalance_with_complete_stage_neutrino_gamma_and_strontium_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-026",
        "title": "stellar hydrostatics, galactic response and tidal locking",
        "source_members": ["v1:IX-8", "v1:IX-7", "v1:IX-1", "v2:152", "v2:153", "v2:291/TULLY-FISHER"],
        "claim_id": "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-STELLAR-GALACTIC-TIDAL-068",
        "inherited_claim_ids": ["SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009", "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061"],
        "status": "model_admitted_exact_hydrostatic_restoration_three_four_stellar_endpoints_flat_curve_support_fourth_power_BTFR_and_finite_tidal_terminal_with_complete_seven_source_vector_and_retained_nonmatching_rows",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-024",
        "title": "symmetry breaking and Higgs terminal values",
        "source_members": ["v1:D11d", "v2:287"],
        "claim_id": "SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-HIGGS-SYMMETRY-TERMINAL-066",
        "inherited_claim_ids": ["SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-STRUCT-GENERATOR-THREE-001", "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051"],
        "status": "model_admitted_unique_half_One_displaced_ground_retained_leading_rungs_six_five_cross_lock_exact_terminal_mass_ratio_native_self_coupling_and_complete_postseal_mass_and_direct_coupling_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-022",
        "title": "strong CP alignment and baryon/proton stability",
        "source_members": ["v1:XVIII-2", "v1:N5", "v1:N2"],
        "claim_id": "SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-STRONG-CP-BARYON-STABILITY-064",
        "inherited_claim_ids": ["SFT-PHYS-WEAK-PARITY-FIBRE-002", "SFT-PHYS-NEUTRINO-CP-PHASE-002", "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-BARYOGENESIS-DEPENDENCY-TERMINAL-021"],
        "status": "model_admitted_unique_vectorial_aligned_One_no_extra_compensator_83_same_fibre_mediators_202_cross_fibre_exclusions_baryon_One_finite_composition_and_complete_postseal_EDM_six_mode_proton_search_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-021",
        "title": "dark relic, Smithion spectra and flavour-violation signatures",
        "source_members": ["v1:B-9N", "v1:N8", "v2:271", "v2:296", "v2:297", "v2:299"],
        "claim_id": "SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062",
        "inherited_claim_ids": ["SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001", "SFT-PHYS-FIELD-INVERSE-SQUARE-001", "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003"],
        "status": "model_admitted_four_exact_Smithion_cubics_twelve_rational_root_enclosures_neutral_lightest_relic_27_over_5_abundance_and_complete_LFV_table_with_postseal_Planck_SPARC_and_search_status_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-020",
        "title": "particle modes, generation sites and mass-pattern transport",
        "source_members": ["v1:G5", "v1:M3", "v1:M10", "v1:M12", "v1:M19", "v2:87", "v2:104", "v2:106", "v2:113", "v2:212", "v2:221", "v2:222", "v2:242", "v2:246", "v2:250"],
        "claim_id": "SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052",
        "status": "model_admitted_depth_independent_particle_mode_generation_transport_with_complete_postseal_generation_mass_mixing_lifetime_and_search_boundary_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-015",
        "title": "quantum joint support, measurement depth and uncertainty product",
        "source_members": ["v1:D6b", "v1:D6", "v2:76", "v2:159", "v2:260", "SFT-PRIOR-V2-164-PHYS-JOINT-NONLOCAL-CORRELATION"],
        "claim_id": "SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050",
        "inherited_claim_ids": [
            "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
            "SFT-PHYS-QUANTUM-NO-SIGNALLING-001"
        ],
        "status": "model_admitted_depth_independent_dyadic_support_preparation_depth_joint_factorability_projection_and_Bell_boundary_with_complete_postseal_superconducting_circuit_test_and_assumption_limits",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-013",
        "title": "phase criticality, universality exponents and turbulence scaling",
        "source_members": ["v1:XIII-2", "v1:I-6", "v2:103", "v2:279", "v2:280", "v2:289", "v2:191/PHYSICAL-UNIVERSALITY"],
        "claim_id": "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-CRITICALITY-MEASURED-VALUE-056",
        "inherited_claim_ids": [
            "SFT-PHYS-THERMO-PHASE-EQUILIBRIUM-001",
            "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008",
            "SFT-PHYS-FLUID-TURBULENCE-001"
        ],
        "status": "model_admitted_exact_binary_critical_exponents_and_generator_three_cascade_with_complete_measured_value_erbium_manganite_and_turbulence_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-012",
        "title": "spin statistics and Bose-Einstein condensation",
        "source_members": ["v1:I-9", "v1:I-5", "v2:23", "v2:51", "v2:100"],
        "claim_id": "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046",
        "inherited_claim_ids": [
            "SFT-PHYS-MATTER-FERMION-BOSON-001",
            "SFT-PHYS-QUANTUM-EXCLUSION-001",
            "SFT-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006"
        ],
        "status": "model_admitted_complete_finite_Bose_Fermi_occupation_spin_return_and_condensation_law_with_postseal_BEC_Pauli_and_neutron_spinor_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-011",
        "title": "temperature, canonical equilibrium and fluctuation-response",
        "source_members": ["v1:I-7", "v1:I-3", "v1:I-1", "v2:88", "v2:102", "v2:155"],
        "claim_id": "SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044",
        "status": "model_admitted_exact_finite_temperature_equilibrium_and_fluctuation_response_law_with_complete_postseal_acoustic_and_Johnson_noise_thermometry_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-010",
        "title": "blackbody, acoustic, laser and plasma collective response",
        "source_members": ["v1:VII-7", "v1:VII-5", "v1:VII-1", "v2:48", "v2:81", "v2:111", "v2:146", "v2:170"],
        "claim_id": "SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042",
        "status": "model_admitted_exact_finite_occupation_radiation_acoustic_laser_plasma_Alfven_relations_and_complete_postseal_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-008",
        "title": "inflationary exit, primordial tilt and structure-growth transport",
        "source_members": ["v1:VIII-6", "v1:VIII-5", "v1:N7", "v2:31", "v2:42"],
        "claim_id": "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
        "status": "model_admitted_exact_generator_volume_cover_primordial_partition_growth_transport_and_complete_postseal_scalar_tensor_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-007",
        "title": "thermal history, freeze-out, nucleosynthesis and recombination physics",
        "source_members": ["v1:VIII-1", "v1:VIII-2", "v1:VIII-3", "v2:58", "v2:139", "v2:197"],
        "claim_id": "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-THERMAL-HISTORY-MEASURED-VALUE-058",
        "inherited_claim_ids": ["SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037", "SFT-PHYS-THERMAL-HELIUM-ISOTOPE-TERMINAL-057"],
        "status": "model_admitted_exact_transport_physical_helium_59_over_240_and_complete_measured_value_temperature_abundance_recombination_acoustic_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-006",
        "title": "vacuum density magnitude and cosmological-constant correspondence",
        "source_members": ["v1:XVIII-3", "v1:N1c", "v2:35", "v2:40", "v2:274/LAMBDA-FLOOR"],
        "claim_id": "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
        "inherited_claim_ids": [
            "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
            "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
            "SFT-PHYS-VALIDATION-VACUUM-FLOOR-003"
        ],
        "status": "model_admitted_exact_local_floor_finite_radiative_ledger_typed_cosmological_transport_and_complete_postseal_Planck_CODATA_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-034",
        "title": "exact positive relativistic velocity composition",
        "source_members": ["v2:126"],
        "claim_id": "SFT-PHYS-SPACETIME-VELOCITY-COMPOSITION-TERMINAL-033",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-VELOCITY-COMPOSITION-034",
        "status": "model_admitted_exact_bilinear_uniqueness_closed_with_postseal_Fizeau_discriminator_and_systematic_boundaries",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-000",
        "title": "finite accumulated coupling separation",
        "source_members": ["v1:B10", "v2:259"],
        "claim_id": "SFT-PHYS-COUPLING-ACCUMULATED-SEPARATION-TERMINAL-015",
        "status": "model_admitted_and_same_strength_closed",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-017",
        "title": "symmetry-conservation equivalence and Fold least action",
        "source_members": ["v1:XIII-5", "v1:XIII-4"],
        "claim_id": "SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016",
        "status": "model_admitted_and_same_strength_closed",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-025",
        "title": "scattering partition and reciprocal mean-free-path geometry",
        "source_members": ["v2:91"],
        "claim_id": "SFT-PHYS-SCATTERING-PARTITION-PATH-TERMINAL-017",
        "status": "model_admitted_and_same_strength_closed",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-032",
        "title": "physical Regge trajectory correspondence",
        "source_members": ["v2:290"],
        "claim_id": "SFT-PHYS-HADRON-REGGE-DIMENSIONAL-TERMINAL-059",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-HADRON-REGGE-MEASURED-VALUE-060",
        "inherited_claim_ids": ["SFT-PHYS-HADRON-REGGE-TERMINAL-005"],
        "status": "model_admitted_zero_parameter_dimensional_Regge_law_with_complete_five_row_measured_resonance_support_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-014",
        "title": "Landauer erasure and Maxwell-demon cycle ledger",
        "source_members": ["v1:I-10", "v2:123"],
        "claim_id": "SFT-PHYS-THERMO-LANDAUER-EMPIRICAL-019",
        "dependency_claim_id": "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018",
        "status": "model_admitted_empirically_tested_and_same_strength_closed",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-001",
        "title": "massive/massless mediator range and preserved/broken channel",
        "source_members": ["v1:D11a", "v1:D11c", "v1:D11f", "v2:70", "v2:240"],
        "claim_id": "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
            "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005"
        ],
        "status": "model_admitted_and_same_strength_closed_with_inherited_postseal_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-009",
        "title": "baryogenesis and Sakharov dependency chain",
        "source_members": ["v1:VIII-4"],
        "claim_id": "SFT-PHYS-BARYOGENESIS-DEPENDENCY-TERMINAL-021",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-MATTER-CKM-TERMINAL-004",
            "SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004"
        ],
        "status": "model_admitted_and_same_strength_closed_with_inherited_postseal_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-016",
        "title": "one-, two- and three-dimensional lattice operators",
        "source_members": ["v1:D1", "v1:D1c", "v1:D1d", "v2:110", "v2:205"],
        "claim_id": "SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-WAVE-DISPERSION-001",
            "SFT-PHYS-VALIDATION-ATOMIC-CUBIC-SUPPORT-004"
        ],
        "status": "model_admitted_and_same_strength_closed_with_inherited_postseal_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-018",
        "title": "finite quantum-gravity composition",
        "source_members": ["v1:G4"],
        "claim_id": "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-VALIDATION-FINITE-LOOPS-003",
            "SFT-PHYS-VALIDATION-GRAVITY-HORIZONS-003",
            "SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010"
        ],
        "status": "model_admitted_and_same_strength_closed_with_inherited_postseal_comparison",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-019",
        "title": "Fold-universe composition and inter-universe transport boundary",
        "source_members": ["v1:G7", "v1:G8"],
        "claim_id": "SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
            "SFT-PHYS-QUANTUM-NO-SIGNALLING-001",
            "SFT-PHYS-FIELD-LOCALITY-CAUSALITY-001"
        ],
        "status": "model_admitted_arithmetic_network_closed_and_literal_physical_transport_resolved_adversely",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-003",
        "title": "interaction unification, period dictionary and sector ordering",
        "source_members": ["v1:B-4N", "v1:B1", "v1:B13", "v1:M1", "v2:183", "v2:243"],
        "claim_id": "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003",
            "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
            "SFT-PHYS-VALIDATION-VACUUM-POLARIZATION-003"
        ],
        "status": "model_admitted_same_strength_closed_with_inherited_comparison_and_adverse_prior_slope_resolution",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-030",
        "title": "Yang-Mills colour-singlet mass gap",
        "source_members": ["v1:XII-5", "v2:119"],
        "claim_id": "SFT-PHYS-YANG-MILLS-SINGLET-GAP-EMPIRICAL-027",
        "dependency_claim_id": "SFT-PHYS-YANG-MILLS-SINGLET-GAP-TERMINAL-026",
        "status": "model_admitted_finite_fold_theorem_and_complete_postseal_lattice_spectrum_boundary",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-031",
        "title": "Parker proton energy-share correspondence",
        "source_members": ["v2:283"],
        "claim_id": "SFT-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028",
        "status": "model_admitted_exact_terminal_relation_with_complete_postseal_range_comparison_and_precision_overclaim_rejected",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-023",
        "title": "probe-independent proton radius",
        "source_members": ["v1:XVIII-1", "v2:165"],
        "claim_id": "SFT-PHYS-PROTON-RADIUS-TERMINAL-029",
        "status": "model_admitted_exact_probe_independent_coefficient_complete_current_vector_and_retained_historical_conflict",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-002",
        "title": "common scale axis, running sectors and electroweak transport",
        "source_members": [
            "v1:B3", "v1:B4", "v1:B5", "v1:B7", "v1:B11",
            "v1:B12", "v1:XIII-6", "v1:B17", "v1:B15", "v2:108",
            "v2:214", "v2:254"
        ],
        "claim_id": "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-COMMON-SCALE-MEASURED-VALUE-054",
        "dependency_claim_id": "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "inherited_empirical_claim_ids": [
            "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
            "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003"
        ],
        "status": "model_admitted_same_strength_closed_with_unique_common_axis_terminal_weak_transport_and_complete_postseal_vector",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-004",
        "title": "composite confining sector census",
        "source_members": ["v1:B-10N", "v1:B-11N", "v1:B-12N", "v1:B-13N", "v1:B-14N"],
        "claim_id": "SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031",
        "inherited_empirical_claim_ids": ["SFT-PHYS-VALIDATION-FORCE-SECTOR-ANCHORS-003"],
        "status": "model_admitted_depth_independent_same_strength_closed_with_complete_orbit_pair_and_coupling_census",
    },
    {
        "family_id": "PHYS-GAP-FAMILY-005",
        "title": "cosmic component dilution, expansion and threshold relations",
        "source_members": [
            "v1:VIII-11", "v1:VIII-10", "v1:VIII-9", "v1:VIII-8",
            "v1:N1d", "v1:N1f", "v2:46", "v2:61", "v2:85", "v2:109",
            "v2:114", "v2:188", "v2:202"
        ],
        "claim_id": "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
        "empirical_claim_id": "SFT-PHYS-VALIDATION-COSMIC-TRANSPORT-MEASURED-VALUE-055",
        "dependency_claim_ids": [
            "SFT-PHYS-COSMO-COMPLETE-BUDGET-001",
            "SFT-PHYS-SPACE-DIMENSION-THREE-001"
        ],
        "status": "model_admitted_empirically_tested_same_strength_closed_with_terminal_budget_successor_complete_32_row_vector_and_adverse_DESI_retention",
    },
)


COMPLETED_COMPONENTS = ()


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    open_atoms = {}
    source_to_open_atoms: dict[str, list[str]] = {}
    for row in audit["source_rows"]:
        source_key = f"{row['source']}:{row['source_entry']}"
        for atom in row["physics_atoms"]:
            if atom["same_strength_closed"]:
                continue
            atom_id = atom["atom_id"]
            if atom_id in open_atoms:
                raise SystemExit(f"duplicate open atom identifier: {atom_id}")
            open_atoms[atom_id] = {"source_key": source_key, "atom": atom}
            source_to_open_atoms.setdefault(source_key, []).append(atom_id)

    def resolve(selector: str) -> str:
        if selector in open_atoms:
            return selector
        candidates = source_to_open_atoms.get(selector, [])
        if len(candidates) != 1:
            raise SystemExit(
                "family selector must resolve to exactly one open atom: "
                f"{selector} -> {candidates}"
            )
        return candidates[0]

    assigned: dict[str, str] = {}
    output_families = []
    for order, (family_id, title, selectors, evidence) in enumerate(FAMILIES, 1):
        member_atom_ids = [resolve(selector) for selector in selectors]
        for atom_id in member_atom_ids:
            if atom_id in assigned:
                raise SystemExit(f"duplicate family assignment: {atom_id}")
            assigned[atom_id] = family_id
        output_families.append(
            {
                "order": order,
                "family_id": family_id,
                "title": title,
                "member_atom_ids": member_atom_ids,
                "source_members": list(dict.fromkeys(open_atoms[atom_id]["source_key"] for atom_id in member_atom_ids)),
                "source_atom_count": len(member_atom_ids),
                "required_evidence": evidence,
                "status": "not_yet_same_strength_closed",
                "member_gaps": {
                    atom_id: open_atoms[atom_id]["atom"]["remaining_gap"]
                    for atom_id in member_atom_ids
                },
            }
        )
    missing = sorted(set(open_atoms) - set(assigned))
    extra = sorted(set(assigned) - set(open_atoms))
    if missing or extra:
        raise SystemExit(
            "family plan is not one-to-one with the open audit: "
            f"missing={missing}; extra={extra}"
        )
    payload = {
        "schema": "sft.physics.v1-v2-gap-families.v2",
        "status": "current_evidence_closed_extension_open" if not output_families else "dependency_plan_open",
        "authority_boundary": (
            "Planning artifact only. It neither admits a claim nor changes the "
            "engine, census, receipt, protocol or scientific disposition."
        ),
        "source_audit_path": str(AUDIT.relative_to(ROOT)),
        "source_audit_summary": audit["summary"],
        "completed_families": list(COMPLETED_FAMILIES),
        "completed_family_components": list(COMPLETED_COMPONENTS),
        "remaining_family_count": len(output_families),
        "remaining_open_atom_count": len(open_atoms),
        "all_open_atoms_assigned_once": True,
        "families": output_families,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Physics V1/V2 gap-family closure plan",
        "",
        f"The categorical audit contains {len(open_atoms)} remaining open Physics atoms. "
        f"They consolidate into {len(output_families)} independent law families. "
        "Every open atom occurs exactly once below. This document plans submissions; "
        "it does not admit them.",
        "",
        f"{len(COMPLETED_FAMILIES)} families are resolved through untouched-engine "
        "receipts and are retained in the machine-readable completed-family ledger.",
        "",
        "| Order | Family | Open atoms | Required evidence |",
        "|---:|---|---:|---|",
    ]
    for row in output_families:
        lines.append(
            f"| {row['order']} | `{row['family_id']}` — {row['title']} | "
            f"{row['source_atom_count']} | {row['required_evidence']} |"
        )
    lines.extend(
        (
            "",
            "## Exact member allocation",
            "",
        )
    )
    for row in output_families:
        lines.extend(
            (
                f"### {row['family_id']}: {row['title']}",
                "",
                ", ".join(f"`{member}`" for member in row["member_atom_ids"]) + ".",
                "",
            )
        )
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(
        f"wrote {OUTPUT.relative_to(ROOT)}: {len(output_families)} families, "
        f"{len(open_atoms)} open atoms, one-to-one allocation"
    )


if __name__ == "__main__":
    main()
