#!/usr/bin/env python3
"""Freeze the complete dated Materials Science full-field obligation census."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/materials_discipline_obligations.json"
BASE = ROOT / "publications/inventories/materials.json"

FAMILIES = {
"CRYS": ("quantitative_crystallography_diffraction_disorder", ["Exact diffraction amplitude and intensity ledger", "Finite structure-factor composition", "Polycrystal texture and orientation distribution", "Short-range order and diffuse-scattering relation", "Stacking-fault sequence and diffraction consequence", "Crystal twinning and domain relation", "Incommensurate and modulated structure organization", "Total-scattering pair-distribution reconstruction"]),
"MICRO": ("defects_microstructure_interfaces_multiscale", ["Defect population and site-fraction balance", "Defect migration and retained path", "Dislocation reaction, climb and cross-slip", "Curvature-driven grain growth", "Interface and grain-boundary segregation", "Precipitation and coherent-incoherent inclusion boundary", "Ostwald-type coarsening as exact carrier transfer", "Interface migration and mobility record", "Microstructure-to-bulk multiscale correspondence"]),
"PHASE": ("phase_equilibria_transformations_metastability", ["Complete multiphase fraction ledger", "Tie-line and lever-partition relation", "Component potential and phase-coexistence handoff", "Metastable-state retention boundary", "Spinodal-equivalent instability organization", "Displacive and martensitic transformation", "Reconstructive transformation path", "Order-disorder transition", "Glass-transition and kinetic-arrest boundary", "Transformation kinetics and time-temperature path"]),
"MECH": ("mechanical_fracture_fatigue_creep_tribology_rheology", ["Tensor-resolved stress-strain response", "Transverse-to-longitudinal strain relation", "Viscoelastic memory and recovery", "Viscoplastic flow relation", "Yield-surface and loading-path boundary", "Work hardening and retained deformation history", "Fracture energy and toughness ledger", "Stable and unstable crack-growth relation", "Cyclic fatigue initiation and propagation", "Creep mechanism and rupture-time custody", "Impact and high-rate mechanical response", "Friction and contact-state relation", "Lubrication and tribofilm organization", "Rheological flow and relaxation classes"]),
"THERM": ("thermal_transport_storage_expansion_thermoelectric", ["Thermal diffusivity relation", "Interfacial thermal-boundary resistance", "Phonon scattering and mean-path ledger", "Radiative thermal transport in materials", "Thermoelectric coupled-response performance boundary", "Phase-change thermal-storage ledger", "Thermal-shock and thermal-fatigue boundary"]),
"ELEC": ("electronic_dielectric_semiconductor_ionic_transport", ["Electrical conductivity and resistivity relation", "Carrier mobility and concentration separation", "Hall-response carrier ledger", "Dielectric permittivity and loss relation", "Ionic conductivity and transference", "Mixed ionic-electronic transport", "Tunnelling through a finite material barrier", "Band-alignment and interface offset", "Heterostructure carrier confinement", "Defect and trap electronic states", "Charge screening and depletion length", "Electrochemical insertion and material-state response"]),
"MAGSC": ("magnetism_spin_superconductivity_superfluidity", ["Paramagnetic response", "Diamagnetic response", "Spin-glass freezing and history", "Magnetic domains and walls", "Magnetic hysteresis loop ledger", "Magnetocrystalline anisotropy", "Magnetoresistance and field-response relation", "Spin transport and relaxation", "Superconducting critical-field organization", "Superconducting vortex matter and pinning", "Superconducting coherence-length boundary", "Superfluid excitation and critical-flow ledger"]),
"OPT": ("optics_photonics_polarization_electromagnetic_materials", ["Optical absorption and extinction", "Reflection and transmission ledger", "Luminescence and quantum-yield custody", "Elastic and inelastic light scattering", "Birefringence and optical anisotropy", "Nonlinear optical mixing response", "Waveguide confinement and loss", "Photonic-band-gap and defect mode", "Plasmonic collective response", "Exciton generation, transport and recombination"]),
"CLASS": ("metals_alloys_ceramics_glasses_polymers_composites", ["Solid-solution and alloy phase organization", "Intermetallic ordered-compound organization", "Compositionally complex and high-entropy alloy boundary", "Refractory and ultra-high-temperature material class", "Cementitious and concrete composite organization", "Fibre-reinforced composite load transfer", "Particle-reinforced composite load transfer", "Metallic-glass organization", "Structural and functional ceramic subclasses", "Thermoplastic, thermoset and elastomer distinction", "Gradient and functionally graded materials", "Architected and cellular material organization"]),
"SOFT": ("soft_colloidal_liquid_crystalline_granular_materials", ["Colloidal stability and aggregation", "Gelation and percolated soft network", "Foam cell and drainage organization", "Liquid-crystal orientational order", "Emulsion and multiphase droplet organization", "Membrane and thin-film soft matter", "Granular packing and force-chain support", "Jamming and unjamming boundary", "Responsive and stimuli-sensitive soft materials", "Active-material nonequilibrium organization"]),
"BIO": ("biomaterials_biologically_derived_materials", ["Biocompatibility as a material-interface boundary", "Bioresorption and degradation ledger", "Tissue-scaffold porosity and connectivity", "Cell-material adhesion handoff", "Mechanical matching at a biological interface", "Controlled-release material transport boundary", "Mineralized biological material organization", "Biologically derived and biofabricated material identity"]),
"NANO": ("nanomaterials_two_dimensional_quantum_materials", ["Nanoparticle size and shape distribution", "Nanowire and one-dimensional confinement", "Two-dimensional layer and stacking organization", "Quantum-dot finite confinement", "Surface-to-volume dominance relation", "Nanoscale phase and melting boundary", "Quantum-material collective-state classification", "Moiré and twisted-layer superstructure", "Nanocomposite interface density", "Nanomaterial aggregation and dispersion custody"]),
"SURF": ("surfaces_coatings_adhesion_interfacial_response", ["Surface free-state and energy relation", "Wetting and contact-angle custody", "Adhesion and work-of-separation ledger", "Coating layer and substrate organization", "Surface roughness and scale boundary", "Surface reaction and catalysis handoff", "Tribofilm formation and retention", "Interface fracture and delamination"]),
"DEGR": ("corrosion_oxidation_wear_radiation_ageing", ["Oxidation scale growth and transport", "Corrosion-rate and electrochemical-path ledger", "Passivation and film-breakdown boundary", "Stress-corrosion cracking", "Hydrogen uptake and embrittlement", "Abrasive, adhesive and erosive wear distinction", "Radiation-defect accumulation and recovery", "Physical ageing and property drift", "Environmental attack and weathering", "Service-life and failure-time evidence boundary"]),
"PROC": ("processing_solidification_sintering_heat_treatment_additive", ["Casting and mould-filling material history", "Thermomechanical forming and texture", "Machining-induced surface and damage state", "Additive layer-build and melt-pool history", "Thin-film deposition and growth", "Epitaxial growth and lattice matching", "Welding, brazing and joining interface", "Polymer processing and orientation history", "Powder processing and compaction", "Process-window, provenance and reproducibility ledger"]),
"COMP": ("computational_materials_structure_property_inference", ["Exact material-structure data representation", "Structure-property computation boundary", "Finite numerical material simulation", "Multiscale model composition", "Numerical stability and error propagation in materials", "Inverse materials problem", "Machine-learning materials inference boundary", "Materials database identity and provenance", "Phase-field computational correspondence", "Molecular-dynamics computational correspondence", "Electronic-structure computational correspondence", "Simulation-to-experiment validation ledger"]),
"EXT": ("materials_under_extreme_conditions", ["High-pressure material state", "High-temperature material state", "Cryogenic material response", "High-electric-field material response", "High-magnetic-field material response", "High-strain-rate and shock response", "Extreme-radiation material response", "Combined-extreme condition and path custody"]),
"SUST": ("sustainable_material_cycles_lifecycle", ["Embodied material and energy ledger", "Critical-material availability boundary", "Material reuse and remanufacture", "Recycling separation and recovery yield", "Circular material-flow organization", "Durability and life-extension relation", "Material toxicity and health handoff", "Material substitution and function preservation", "End-of-life fate and residual custody"]),
"VALID": ("complete_materials_external_validation", ["Crystallography and diffraction validation vector", "Defect and microstructure validation vector", "Phase and transformation validation vector", "Mechanical and tribological validation vector", "Thermal and transport validation vector", "Electronic, ionic and dielectric validation vector", "Magnetic, superconducting and topological validation vector", "Optical and photonic validation vector", "Material-class and processing validation vector", "Cross-source reproducibility vector", "Complete adverse, absent and out-of-bound vector", "Materials empirical Grand Lock"]),
"HAND": ("cross_branch_handoffs", ["Materials-to-Engineering ownership handoff", "Materials-to-Biology ownership handoff", "Materials-to-Medicine ownership handoff", "Materials-to-Earth and Environmental Science ownership handoff", "Materials-to-Astronomy ownership handoff", "Materials cross-branch one-owner completeness certificate"]),
}


def canonical(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main():
    if OUTPUT.exists(): raise SystemExit("Materials discipline census already frozen")
    base = json.loads(BASE.read_text())
    census = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    rows = {row["claim_id"]: row for row in census}
    obligations = []
    for position, item in enumerate(base["obligations"], 1):
        cid = item["claim_id"]
        if cid not in rows or rows[cid]["branch"] != "materials": raise SystemExit(f"missing base Materials claim {cid}")
        obligations.append({
            "obligation_id": f"SFT-MAT-OBL-BASE-{position:03d}", "field": item["subbranch"], "title": item["title"],
            "exact_boundary": item["statement"], "required_strength": "existing_exact_unique_survivor_independent_reconstruction_postseal_external_comparison",
            "required_external_surface": "current receipt-bound Materials empirical package", "owner": "materials",
            "status": "closed_current_model_admitted_receipt", "current_claim_ids": [cid], "receipt_hashes": [rows[cid]["receipt_hash"]], "receipt_paths": [rows[cid]["receipt_path"]],
        })
    for code, (field, titles) in FAMILIES.items():
        for number, title in enumerate(titles, 1):
            strength = "exact_zero_parameter_unique_survivor_independent_reconstruction_postseal_external_comparison"
            if code == "VALID": strength = "complete_receipt_bound_empirical_vector_with_all_result_classes"
            if code == "HAND": strength = "exact_one_owner_dependency_and_cross_branch_handoff_certificate"
            obligations.append({
                "obligation_id": f"SFT-MAT-OBL-{code}-{number:03d}", "field": field, "title": title,
                "exact_boundary": f"Materials owns the exact generated structure, state, path or property relation for {title}; specimen, method, condition, scale, uncertainty and downstream ownership remain explicit.",
                "required_strength": strength, "required_external_surface": f"complete authoritative measured and structural record for {title}",
                "owner": "materials", "status": "open_requires_derivation_and_external_validation", "current_claim_ids": [], "receipt_hashes": [], "receipt_paths": [],
            })
    payload = {
        "schema": "sft-v3-materials-discipline-obligation-census/1", "date": "2026-07-29", "authority": "Maria Smith",
        "branch": "materials", "frozen": True, "target_content_present": False,
        "ownership_boundary": "Materials owns organized matter at specimen, microstructure, phase and property scales. Physics and Chemistry are admitted dependencies; engineering implementation, biological function, clinical outcome, Earth-system context and astronomical source context remain downstream owners.",
        "base_claim_count": len(base["obligations"]), "field_order": [base_field for base_field in base["subbranch_order"]] + [field for field, _ in FAMILIES.values()],
        "field_counts": {}, "obligations": obligations,
        "completion_rule": "A dated obligation closes only with a model-admitted receipt after complete enumeration, one survivor, controls, independent reconstruction and post-seal external comparison wherever practicable. A failed route retires nothing.",
        "extension_policy": "Complete to the registered current standard remains open to lawful versioned discoveries and stronger evidence.",
    }
    for row in obligations: payload["field_counts"][row["field"]] = payload["field_counts"].get(row["field"], 0) + 1
    payload["registered_obligation_count"] = len(obligations)
    payload["closed_obligation_count_at_freeze"] = sum(row["status"].startswith("closed") for row in obligations)
    payload["open_obligation_count_at_freeze"] = len(obligations) - payload["closed_obligation_count_at_freeze"]
    payload["census_identity"] = canonical(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: payload[k] for k in ("registered_obligation_count", "closed_obligation_count_at_freeze", "open_obligation_count_at_freeze", "field_counts", "census_identity")}, indent=2))


if __name__ == "__main__": main()
