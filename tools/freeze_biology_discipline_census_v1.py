#!/usr/bin/env python3
"""Freeze the dated Biology and Life Sciences full-field obligation census.

The open rows name questions and evidential surfaces only.  They contain no
external outcome values and cannot select a survivor.  Existing admitted
foundation and prior-return claims are carried forward by their live receipts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/biology_discipline_obligations.json"
BASE = ROOT / "publications/inventories/biology.json"

PRIOR_RETURN_IDS = (
    "SFT-BIO-ORIGIN-AUTOCATALYTIC-IGNITION-002",
    "SFT-BIO-HOMOCHIRAL-AMPLIFICATION-002",
    "SFT-BIO-SOMATIC-GERMLINE-ORBIT-SPLIT-002",
    "SFT-BIO-NEURAL-HALF-ONE-THRESHOLD-002",
    "SFT-BIO-DIFFERENTIATION-LOSS-CANCER-002",
    "SFT-BIO-BOUNDED-ORBIT-ECOSYSTEM-002",
    "SFT-BIO-VALIDATION-PRIOR-MECHANISMS-COMPLETE-FAMILY-002",
)


# Dependency ordered, field-wide Biology question surface.  Titles are
# deliberately value-free; empirical outcomes may be opened only after the
# corresponding formal prediction has been sealed.
FAMILIES = {
    "MOLX": (
        "living_biochemistry_and_molecular_processes",
        [
            "Biological reaction-network stoichiometry and carrier balance",
            "Enzyme-catalysed transition and substrate-specificity boundary",
            "Enzyme saturation, inhibition and finite-rate comparison",
            "Biological redox-carrier and electron-transfer ledger",
            "ATP-equivalent coupling and cellular work accounting",
            "Chemiosmotic gradient and coupled transport relation",
            "Carbon-fixation pathway organization",
            "Central carbon-flow and branch-point allocation",
            "Nitrogen, sulfur and phosphorus biological cycling",
            "Lipid synthesis, remodelling and degradation",
            "Carbohydrate synthesis, storage and mobilization",
            "Amino-acid synthesis and catabolic routing",
            "Cofactor, vitamin and prosthetic-group dependence",
            "Metabolome identity, flux and missing-carrier custody",
        ],
    ),
    "STRU": (
        "structural_biology_biophysics_and_measurement",
        [
            "Macromolecular conformation and ensemble occupancy",
            "Structure-resolution and coordinate-uncertainty ledger",
            "Macromolecular binding stoichiometry and affinity comparison",
            "Cooperativity and allosteric-state organization",
            "Protein-nucleic-acid recognition boundary",
            "Membrane-protein topology and insertion",
            "Macromolecular assembly, symmetry and interface organization",
            "Intrinsically disordered state and conditional structure",
            "Single-molecule trajectory and state-transition reconstruction",
            "Force, extension and biological-mechanics handoff",
            "Diffusion, crowding and compartment-scale transport",
            "Fluorescence and spectroscopic biological-observation ledger",
            "Cryogenic, diffraction and resonance structure correspondence",
            "Biophysical model-to-measurement uncertainty propagation",
        ],
    ),
    "GENX": (
        "genetics_genomics_epigenetics_and_inheritance",
        [
            "Chromosome identity, ploidy and segregation",
            "Mendelian inheritance and segregation-ratio boundary",
            "Linkage, recombination and crossover organization",
            "Mutation class, origin and lineage retention",
            "DNA replication, proofreading and repair",
            "Genome assembly, gaps and structural-variant custody",
            "Gene annotation and transcript-boundary evidence",
            "Regulatory sequence and condition-dependent activity",
            "Chromatin accessibility and nucleosome organization",
            "DNA methylation and heritable-state boundary",
            "Histone-state and chromatin-transition relation",
            "Imprinting and parent-of-origin distinction",
            "Dosage compensation and copy-number response",
            "Horizontal gene transfer and carrier provenance",
            "Pangenome, population variation and reference bias",
            "Genotype-to-phenotype causal and associative boundary",
        ],
    ),
    "RNAP": (
        "rna_proteins_folding_interactions_and_cellular_machinery",
        [
            "Transcription initiation, elongation and termination",
            "RNA processing, splicing and isoform identity",
            "RNA editing and post-transcriptional modification",
            "RNA structure, folding and ensemble relation",
            "Noncoding-RNA regulation and target evidence",
            "Ribosome composition and translation-cycle organization",
            "Genetic-code decoding and tRNA assignment",
            "Translation fidelity, pausing and termination",
            "Protein folding pathway and kinetic partition",
            "Chaperone-assisted folding and rescue",
            "Post-translational modification and proteoform identity",
            "Protein targeting, trafficking and localization",
            "Protein-complex assembly and disassembly",
            "Proteostasis, quality control and degradation",
            "Protein interaction-network observation boundary",
            "Sequence-structure-function causal correspondence",
        ],
    ),
    "CELL": (
        "cellular_organization_cycles_signalling_and_death",
        [
            "Plasma-membrane composition and asymmetric orientation",
            "Organelle identity, biogenesis and inheritance",
            "Cytoskeleton organization, force and transport",
            "Vesicle formation, targeting, fusion and cargo custody",
            "Nuclear transport and compartment exchange",
            "Cell-cycle phase and checkpoint organization",
            "Chromosome segregation and cytokinesis",
            "Receptor-ligand recognition and signal initiation",
            "Signal-transduction cascade and pathway crosstalk",
            "Second-messenger production, transport and termination",
            "Cell polarity, migration and directional sensing",
            "Cell-cell junction and tissue-interface organization",
            "Programmed cell-death route distinction",
            "Autophagy, recycling and stress response",
            "Stem-cell self-renewal and potency boundary",
            "Cell-state transition and lineage-memory reconstruction",
        ],
    ),
    "MICR": (
        "microbiology_virology_and_host_microbe_systems",
        [
            "Prokaryotic cell organization and division",
            "Microbial growth phase and resource limitation",
            "Microbial metabolism and respiratory diversity",
            "Biofilm formation, structure and dispersal",
            "Quorum sensing and population-response boundary",
            "Microbial community interaction and cross-feeding",
            "Virus particle, genome and host-range identity",
            "Virus entry, replication, assembly and release",
            "Lytic, latent and persistent infection distinction",
            "Viral mutation, reassortment and recombination",
            "Host-microbiome composition and functional evidence",
            "Pathogen transmission and infectious-dose boundary",
            "Antimicrobial susceptibility and resistance evolution",
            "Microbial and viral observation, culture and sequencing bias",
        ],
    ),
    "TAXX": (
        "taxonomy_systematics_phylogeny_and_comparative_classification",
        [
            "Taxon identity and diagnostic-character boundary",
            "Species-concept plurality and explicit criterion custody",
            "Homology and analogy distinction",
            "Character-state coding and missing-data retention",
            "Phylogenetic tree and network representation",
            "Common-ancestry and convergence alternatives",
            "Molecular-clock calibration and rate-variation boundary",
            "Horizontal transfer, hybridization and reticulate history",
            "Ancestral-state reconstruction and uncertainty",
            "Biological nomenclature and specimen linkage",
            "Comparative-method dependence and non-independence",
            "Taxonomic revision, synonymy and provenance ledger",
        ],
    ),
    "DEVX": (
        "development_differentiation_morphology_and_regeneration",
        [
            "Gamete identity, fertilization and zygote formation",
            "Cleavage, axis formation and embryonic patterning",
            "Morphogen production, transport and response boundary",
            "Gene-regulatory network control of differentiation",
            "Cell-fate commitment and lineage restriction",
            "Tissue induction and reciprocal signalling",
            "Organogenesis and spatially coordinated growth",
            "Developmental timing and heterochrony",
            "Mechanical morphogenesis and tissue rearrangement",
            "Growth scaling and final-size regulation",
            "Metamorphosis and life-stage transformation",
            "Regeneration source, positional information and restoration",
            "Developmental plasticity and environmental response",
            "Congenital-variation handoff without clinical reownership",
        ],
    ),
    "EVOX": (
        "evolution_adaptation_and_population_genetics",
        [
            "Allele-frequency carrier and population support",
            "Selection coefficient as an observed recurrence comparison",
            "Mutation-selection balance boundary",
            "Genetic drift and finite-population sampling",
            "Gene flow and population subdivision",
            "Inbreeding, mating structure and relatedness",
            "Effective population-size evidence boundary",
            "Hard and soft selective-sweep distinction",
            "Balancing, purifying and directional selection",
            "Neutral and nearly neutral alternatives",
            "Quantitative-trait inheritance and response",
            "Phenotypic plasticity and reaction norms",
            "Local adaptation and reciprocal-environment controls",
            "Speciation, isolation and lineage divergence",
            "Extinction, turnover and fossil-record incompleteness",
            "Major evolutionary transition and level-of-selection custody",
        ],
    ),
    "KING": (
        "plant_fungal_animal_and_comparative_biology",
        [
            "Plant cell wall, plastid and vacuole organization",
            "Photosynthesis, photorespiration and carbon allocation",
            "Plant water transport and stomatal regulation",
            "Plant mineral uptake and nutrient allocation",
            "Plant growth, tropism and developmental plasticity",
            "Plant reproduction, pollination and seed dispersal",
            "Fungal hypha, mycelium and growth organization",
            "Fungal nutrition, decomposition and symbiosis",
            "Fungal reproduction and spore dispersal",
            "Animal tissue, organ and body-plan organization",
            "Animal circulation, respiration and exchange surfaces",
            "Animal digestion, excretion and osmoregulation",
            "Animal locomotion and biomechanical coordination",
            "Animal reproduction and parental investment",
            "Comparative anatomy and functional correspondence",
            "Symbiosis, mutualism, commensalism and parasitism distinction",
            "Host-associated holobiont claim boundary",
            "Kingdom-scale common and lineage-specific process ledger",
        ],
    ),
    "ENVX": (
        "marine_freshwater_terrestrial_and_extreme_environment_biology",
        [
            "Marine pelagic and benthic biological organization",
            "Freshwater lotic and lentic biological organization",
            "Terrestrial biome and habitat organization",
            "Soil biological community and nutrient transformation",
            "Deep-sea and hydrothermal biological adaptation",
            "Polar and cryospheric biological adaptation",
            "Desert and desiccation-tolerance organization",
            "High-pressure and high-temperature life boundary",
            "Acidic, alkaline and hypersaline life boundary",
            "Seasonality, dormancy and migration response",
            "Habitat connectivity and metapopulation structure",
            "Environmental sample-to-biological inference boundary",
        ],
    ),
    "PHYX": (
        "physiology_endocrinology_metabolism_and_homeostasis",
        [
            "Respiratory exchange and gas-transport ledger",
            "Circulatory flow and tissue-delivery organization",
            "Digestive transformation and nutrient absorption",
            "Renal filtration, reabsorption and excretion",
            "Osmoregulation, ion balance and acid-base custody",
            "Thermoregulation and heat-balance response",
            "Endocrine signal production, transport and receptor response",
            "Feedback, feedforward and hormonal-axis organization",
            "Energy intake, storage, expenditure and metabolic state",
            "Glucose and substrate homeostasis",
            "Muscle excitation, contraction and fatigue",
            "Cardiorespiratory integration and exercise response",
            "Reproductive endocrine cycle and fertility boundary",
            "Circadian and seasonal physiological timing",
            "Stress response, adaptation and allostatic boundary",
            "Comparative physiology and environment-dependent scaling",
        ],
    ),
    "NEUR": (
        "neuroscience_biological_substrate",
        [
            "Neuron identity, morphology and compartment organization",
            "Membrane potential and ionic-gradient custody",
            "Action-potential initiation and propagation",
            "Chemical and electrical synaptic transmission",
            "Excitation-inhibition balance and circuit state",
            "Synaptic plasticity and retained change",
            "Neural development, migration and connectivity",
            "Sensory receptor transduction",
            "Motor circuit and effector coordination",
            "Neural population coding observation boundary",
            "Oscillation, synchrony and network recurrence",
            "Glial support, signalling and metabolic coupling",
            "Neural injury, degeneration and biological repair boundary",
            "Biological substrate handoff to consciousness science",
        ],
    ),
    "IMMX": (
        "immunology_defence_tolerance_and_pathogen_dynamics",
        [
            "Innate recognition and immediate defence",
            "Adaptive receptor diversity and clonal identity",
            "Antigen processing, presentation and recognition",
            "B-cell activation, antibody production and affinity change",
            "T-cell activation, differentiation and effector response",
            "Immune memory and secondary response",
            "Self-tolerance and autoimmune boundary",
            "Inflammation initiation, propagation and resolution",
            "Complement and soluble-effector organization",
            "Mucosal and barrier immunity",
            "Host-pathogen coevolution and immune escape",
            "Vaccination biological mechanism handoff",
            "Immunodeficiency and dysregulation boundary",
            "Immune-assay specificity, sensitivity and cross-reactivity",
        ],
    ),
    "BEHX": (
        "behaviour_learning_and_organism_environment_interaction",
        [
            "Behavioral act and observation-unit identity",
            "Stimulus-response and alternative-cause boundary",
            "Habituation and sensitization",
            "Associative learning and contingency",
            "Operant consequence and action selection",
            "Spatial learning, navigation and memory evidence",
            "Developmental and social learning",
            "Foraging, risk and resource-choice behavior",
            "Reproductive and parental behavior",
            "Collective behavior and individual-rule correspondence",
            "Behavioral plasticity and stable individual difference",
            "Behavioral experiment, observer and missing-act custody",
        ],
    ),
    "ETHX": (
        "ethology_sensory_biology_and_communication",
        [
            "Sensory modality, receptor range and detection boundary",
            "Signal production, transmission and reception",
            "Communication code and receiver-response evidence",
            "Honest, deceptive and incidental signal distinction",
            "Territoriality, dominance and social-structure observation",
            "Courtship, mate choice and sexual-selection evidence",
            "Navigation, orientation and migration",
            "Predator-prey detection and defensive response",
            "Cooperation, conflict and kin-recognition boundary",
            "Tool use and environmental modification",
            "Cross-species comparative cognition handoff",
            "Field observation, individual identity and effort correction",
        ],
    ),
    "ECOX": (
        "ecology_biodiversity_communities_and_ecosystems",
        [
            "Population abundance, density and detection correction",
            "Population growth, regulation and carrying boundary",
            "Age, stage and spatial population structure",
            "Metapopulation colonization and local extinction",
            "Competition, predation and facilitation networks",
            "Food-web energy and matter transfer",
            "Community assembly and succession",
            "Diversity richness, evenness and sampling boundary",
            "Functional and phylogenetic biodiversity",
            "Ecosystem production, respiration and storage",
            "Nutrient cycling and decomposition",
            "Disturbance, resistance, resilience and recovery",
            "Invasion and range-shift dynamics",
            "Landscape connectivity and habitat fragmentation",
            "Species-distribution inference and extrapolation boundary",
            "Ecological scale, aggregation and cross-level correspondence",
        ],
    ),
    "SYSX": (
        "systems_synthetic_and_computational_biology",
        [
            "Biological network node, edge and condition identity",
            "Regulatory-network dynamics and attractor boundary",
            "Metabolic-network flux and feasibility",
            "Signalling-network modularity and crosstalk",
            "Multiscale cell-to-organism model composition",
            "Parameter identifiability and biological model nonuniqueness",
            "Perturbation, sensitivity and causal intervention",
            "Synthetic circuit composition and host context",
            "Engineered biological containment and failure modes",
            "Genome editing, off-target and lineage custody",
            "Minimal-cell and essential-function boundary",
            "Digital biological simulation correspondence",
            "Opaque-predictor comparator and non-law boundary",
            "Computational-to-biological validation handoff",
        ],
    ),
    "BINF": (
        "bioinformatics_and_biological_data_inference",
        [
            "Biological sequence encoding and alphabet custody",
            "Sequence alignment, gap and homology boundary",
            "Genome assembly and read-to-contig provenance",
            "Variant calling and reference-dependence",
            "Transcript abundance and isoform inference",
            "Single-cell state, batch and dropout custody",
            "Protein sequence and structure database identity",
            "Phylogenomic inference and model-choice boundary",
            "Metagenomic composition and unclassified-read retention",
            "Image-derived biological feature and segmentation boundary",
            "Biological database versioning and identifier provenance",
            "Training, validation and held-out biological data separation",
            "Multiple-testing, uncertainty and false-discovery custody",
            "Algorithmic output as evidence comparator rather than law",
        ],
    ),
    "ORIG": (
        "origins_of_life_and_major_transitions",
        [
            "Prebiotic chemical-network to living-process boundary",
            "Compartment-first, metabolism-first and template-first alternatives",
            "Autocatalytic-set formation and resource closure",
            "Template replication and heredity emergence",
            "Homochiral selection, amplification and retention",
            "Genetic-code emergence evidence boundary",
            "Protocell growth, competition and division",
            "Cellularization and common-ancestor inference",
            "Endosymbiosis and organelle-origin evidence",
            "Multicellularity and division-of-labour transition",
            "Major transition in individuality and conflict control",
            "Origin hypothesis, current absence and standing-prediction ledger",
        ],
    ),
    "AGEX": (
        "ageing_senescence_and_biological_longevity",
        [
            "Replicative and chronological ageing distinction",
            "Damage accumulation, repair and maintenance allocation",
            "Genome instability and cellular senescence",
            "Proteostasis loss and aggregate custody",
            "Mitochondrial state and metabolic ageing",
            "Stem-cell exhaustion and tissue renewal",
            "Inflammatory and immune ageing",
            "Reproductive investment and life-history tradeoff",
            "Mortality, survival, censoring and hazard evidence",
            "Negligible senescence and lineage-specific longevity",
            "Intervention-to-lifespan and healthspan causal boundary",
            "Somatic transient and germ-line recurrence correspondence",
        ],
    ),
    "CONSV": (
        "conservation_biology_and_biosphere_processes",
        [
            "Population viability and extinction-risk boundary",
            "Genetic diversity and inbreeding conservation",
            "Habitat loss, fragmentation and restoration",
            "Threat identification and causal evidence",
            "Protected-area coverage and ecological representation",
            "Harvest, exploitation and sustainable-yield boundary",
            "Invasive-species control and adverse ecological effects",
            "Reintroduction, translocation and lineage provenance",
            "Ecosystem-service measurement and ownership boundary",
            "Biosphere productivity and carbon-cycle handoff",
            "Global biodiversity observation and missing-taxon custody",
            "Conservation intervention, monitoring and adaptive revision",
        ],
    ),
    "ASTRO": (
        "astrobiology_and_life_detection_handoffs",
        [
            "Habitability condition and life-presence distinction",
            "Biosignature production, transport and persistence",
            "Abiotic false-positive and biological false-negative controls",
            "Planetary-environment to biological-viability handoff",
            "Extremophile evidence and extrapolation boundary",
            "Remote spectral observation and source uncertainty",
            "Sample-return provenance and contamination control",
            "Technosignature distinction from biological evidence",
            "Current non-observation and standing-prediction retention",
            "Astrobiology ownership across Biology, Earth and Astronomy",
        ],
    ),
    "VALID": (
        "complete_biology_external_validation",
        [
            "Molecular and biochemical validation vector",
            "Structural, biophysical and measurement validation vector",
            "Genetic, genomic and epigenetic validation vector",
            "RNA, protein and cellular-machinery validation vector",
            "Cellular, microbial and viral validation vector",
            "Taxonomic, developmental and evolutionary validation vector",
            "Comparative organismal and environmental validation vector",
            "Physiological, neural and immune validation vector",
            "Behavioral, sensory and communication validation vector",
            "Ecological, biodiversity and conservation validation vector",
            "Systems, synthetic and bioinformatic validation vector",
            "Origins, ageing and astrobiology validation vector",
            "Complete adverse, absent, unavailable and standing-prediction vector",
            "Biology empirical Grand Lock",
        ],
    ),
    "HAND": (
        "cross_branch_handoffs",
        [
            "Chemistry-to-Biology molecular-identity handoff",
            "Materials-to-Biology interface and scaffold handoff",
            "Biology-to-Medicine mechanism and efficacy boundary",
            "Biology-to-Consciousness substrate boundary",
            "Biology-to-Earth biosphere-process handoff",
            "Biology-to-Social organism and collective boundary",
            "Biology-to-Engineering translation boundary",
            "Biology cross-branch one-owner completeness certificate",
        ],
    ),
}


def canonical(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("Biology discipline census already frozen")

    base = json.loads(BASE.read_text())
    claims = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    rows = {row["claim_id"]: row for row in claims}
    obligations: list[dict[str, object]] = []

    for position, item in enumerate(base["obligations"], 1):
        claim_id = item["claim_id"]
        row = rows.get(claim_id)
        if not row or row["branch"] != "biology" or not row.get("model_admitted"):
            raise SystemExit(f"missing admitted foundational Biology claim {claim_id}")
        receipt = ROOT / row["receipt_path"]
        if not receipt.is_file():
            raise SystemExit(f"missing live receipt {row['receipt_path']}")
        obligations.append(
            {
                "obligation_id": f"SFT-BIO-OBL-BASE-{position:03d}",
                "field": item["subbranch"],
                "title": item["title"],
                "exact_boundary": item["statement"],
                "required_strength": "existing_exact_unique_survivor_independent_reconstruction_postseal_external_comparison",
                "required_external_surface": "current receipt-bound Biology empirical package",
                "owner": "biology",
                "status": "closed_current_model_admitted_receipt",
                "current_claim_ids": [claim_id],
                "receipt_hashes": [row["receipt_hash"]],
                "receipt_paths": [row["receipt_path"]],
            }
        )

    for position, claim_id in enumerate(PRIOR_RETURN_IDS, 1):
        row = rows.get(claim_id)
        if not row or row["branch"] != "biology" or not row.get("model_admitted"):
            raise SystemExit(f"missing admitted prior-return Biology claim {claim_id}")
        receipt = ROOT / row["receipt_path"]
        if not receipt.is_file():
            raise SystemExit(f"missing live receipt {row['receipt_path']}")
        obligations.append(
            {
                "obligation_id": f"SFT-BIO-OBL-PRIOR-{position:03d}",
                "field": "mandatory_prior_corpus_return",
                "title": row["title"],
                "exact_boundary": row["statement"],
                "required_strength": "existing_exact_unique_survivor_independent_reconstruction_postseal_external_comparison",
                "required_external_surface": "current receipt-bound Biology prior-return empirical package",
                "owner": "biology",
                "status": "closed_current_model_admitted_receipt",
                "current_claim_ids": [claim_id],
                "receipt_hashes": [row["receipt_hash"]],
                "receipt_paths": [row["receipt_path"]],
            }
        )

    for code, (field, titles) in FAMILIES.items():
        for number, title in enumerate(titles, 1):
            strength = "exact_zero_parameter_unique_survivor_independent_reconstruction_postseal_external_comparison"
            if code == "VALID":
                strength = "complete_receipt_bound_empirical_vector_with_all_result_classes"
            elif code == "HAND":
                strength = "exact_one_owner_dependency_and_cross_branch_handoff_certificate"
            obligations.append(
                {
                    "obligation_id": f"SFT-BIO-OBL-{code}-{number:03d}",
                    "field": field,
                    "title": title,
                    "exact_boundary": (
                        f"Biology owns the exact generated living carrier, organization, transition, lineage or evidence relation for {title}; "
                        "organism, taxon, life stage, environment, observation method, uncertainty and downstream ownership remain explicit."
                    ),
                    "required_strength": strength,
                    "required_external_surface": f"complete authoritative measured, structural and observational record for {title}",
                    "owner": "biology",
                    "status": "open_requires_derivation_and_external_validation",
                    "current_claim_ids": [],
                    "receipt_hashes": [],
                    "receipt_paths": [],
                }
            )

    base_fields = list(base["subbranch_order"])
    field_order = base_fields + ["mandatory_prior_corpus_return"] + [field for field, _ in FAMILIES.values()]
    if len(field_order) != len(set(field_order)):
        raise SystemExit("Biology field order contains duplicate ownership identities")

    payload: dict[str, object] = {
        "schema": "sft-v3-biology-discipline-obligation-census/1",
        "date": "2026-07-29",
        "authority": "Maria Smith",
        "branch": "biology",
        "frozen": True,
        "open_obligation_target_content_present": False,
        "ownership_boundary": (
            "Biology owns living organization from molecular process through organism, lineage, population, ecosystem and biosphere. "
            "Physics, Chemistry and Materials are admitted dependencies. Clinical efficacy belongs to Medicine; subjective experience belongs "
            "to Consciousness and Cognitive Science; planetary context belongs to Earth and Environmental Science; implementation belongs to Engineering."
        ),
        "base_claim_count": len(base["obligations"]),
        "prior_return_claim_count": len(PRIOR_RETURN_IDS),
        "field_order": field_order,
        "field_counts": {},
        "obligations": obligations,
        "completion_rule": (
            "A dated obligation closes only with a model-admitted receipt after complete candidate enumeration, exactly one survivor, adverse controls, "
            "implementation-distinct reconstruction and post-seal authoritative external comparison wherever practicable. A failed route retires nothing."
        ),
        "empirical_rule": (
            "Every practicably observable consequence is compared after sealing with authoritative external evidence. Exact values, structures, units, "
            "conditions, uncertainty and provenance are retained together with favorable, adverse, absent, unavailable and standing-prediction rows."
        ),
        "extension_policy": "Complete to the registered current standard remains open to lawful versioned discoveries and stronger evidence.",
    }
    field_counts: dict[str, int] = {}
    for obligation in obligations:
        field = str(obligation["field"])
        field_counts[field] = field_counts.get(field, 0) + 1
    payload["field_counts"] = field_counts
    payload["registered_obligation_count"] = len(obligations)
    payload["closed_obligation_count_at_freeze"] = sum(
        str(row["status"]).startswith("closed") for row in obligations
    )
    payload["open_obligation_count_at_freeze"] = len(obligations) - int(payload["closed_obligation_count_at_freeze"])
    payload["census_identity"] = canonical(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "registered_obligation_count",
                    "closed_obligation_count_at_freeze",
                    "open_obligation_count_at_freeze",
                    "field_counts",
                    "census_identity",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
