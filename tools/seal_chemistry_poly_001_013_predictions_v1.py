#!/usr/bin/env python3
"""Register value-free POLY-001--013 targets and seal all native laws."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.polymer_chemistry_laws_v1 import LAW_ROWS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


FAMILY = "POLY-001-013-QUANTITATIVE-POLYMER-CHEMISTRY"
BOUNDARY = "audits/CHEMISTRY_POLY_001_013_WHOLE_SUBFIELD_BATCH_BOUNDARY_2026-07-28.json"
LAW_PATH = "sft/chemistry/polymer_chemistry_laws_v1.py"
REGISTRY = "experiments/external_sources/chemistry/poly_001_013_whole_subfield_source_identity_registry_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1"


SOURCES = (
    {
        "source_id": "NIST-SRM-2888-POLYSTYRENE-CERTIFICATION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/certification-polystyrene-synthetic-polymer-srm-2888",
        "capture_url": "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication260-152.pdf",
        "purpose": "complete molecular-mass distribution, number-average, mass-average, end-group and interlaboratory measurement record",
    },
    {
        "source_id": "NIST-SRM-2886-POLYETHYLENE-CERTIFICATION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/certification-relative-molecular-mass-and-intrinsic-viscosity-srm-2886-polyethylene",
        "capture_url": "https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir6487.pdf",
        "purpose": "independent polyethylene molecular-mass, dispersity and chain-size-related measurement record",
    },
    {
        "source_id": "NIST-POLYMER-SRM-INDUSTRY-REVIEW",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/standard-reference-materials-polymers-industry-presented-spe-antec-2018",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=919903",
        "purpose": "polymer reference-material identities, architectures, molecular-mass distributions and cross-method measurement boundaries",
    },
    {
        "source_id": "NIST-BRANCH-PLACEMENT-DILUTE-SOLUTION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/importance-branch-placement-dilute-solution-properties-comb-macromolecules",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=958595",
        "purpose": "complete branch-placement, architecture and finite chain-size comparison surface",
    },
    {
        "source_id": "NIST-MACROMOLECULAR-ARCHITECTURES",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/programs-projects/macromolecular-architectures",
        "capture_url": "https://www.nist.gov/programs-projects/macromolecular-architectures",
        "purpose": "official sequence, chemistry, topology, architecture and measured-property ownership surface",
    },
    {
        "source_id": "NIST-POLYMER-PROCESSING-METROLOGY",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/programs-projects/polymer-processing",
        "capture_url": "repository:experiments/external_sources/materials/snapshots/nist-polymer-processing.html",
        "purpose": "immutable admitted Materials evidence for the Chemistry-to-Materials handoff; prior exposure disclosed",
    },
    {
        "source_id": "NIST-POLYMER-INTERFACE-CONSORTIUM",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/programs-projects/nist-polymer-interface-consortium",
        "capture_url": "repository:experiments/external_sources/materials/snapshots/nist-polymer-interface-consortium.html",
        "purpose": "immutable admitted Materials interface and bulk-response evidence; prior exposure disclosed",
    },
    {
        "source_id": "NIST-POLYMER-COMPOSITES",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/programs-projects/polymer-composites",
        "capture_url": "repository:experiments/external_sources/materials/snapshots/nist-polymer-composites.html",
        "purpose": "immutable admitted Materials composite-response evidence; prior exposure disclosed",
    },
    {
        "source_id": "NIST-PVOH-IONIC-LIQUID-GELATION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/preparation-and-characterization-physical-gels-based-ionic-liquid-and-polyvinyl-alcohol",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=907107",
        "purpose": "complete composition, gelation, transition, scattering and molecular/bulk paired record",
    },
    {
        "source_id": "NIST-THERMOREVERSIBLE-GELATION-PERCOLATION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/dynamical-arrest-percolation-gelation-and-glass-formation-model-nanoparticle",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=909486",
        "purpose": "complete finite concentration, transition, percolation, gelation and adverse-state vector",
    },
    {
        "source_id": "NIST-BRIDGING-GELATION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/gelation-large-hard-particles-short-range-attraction-induced-bridging-small-soft",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=917392",
        "purpose": "independent bridging/depletion gel-line and finite-connectivity comparison surface",
    },
    {
        "source_id": "NIST-POLYMER-PYROLYSIS-NETWORK",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/kinetics-and-mechanisms-elementary-reactive-processes-polymer-pyrolysis-nist-gcr-09-923",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=901834",
        "purpose": "complete chain-length, conformation, scission-rate, product, condition and unresolved-path record",
    },
    {
        "source_id": "NIST-POLYMER-THERMAL-DEGRADATION",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://www.nist.gov/publications/investigation-thermal-stability-and-charring-propensity-polymer-materials",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=913365",
        "purpose": "complete thermal degradation, depolymerization, residue and product-yield comparison surface",
    },
    {
        "source_id": "NIST-POLYMER-DEPOLYMERIZATION-KINETICS",
        "authority": "National Institute of Standards and Technology",
        "identity_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=861138",
        "capture_url": "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=861138",
        "purpose": "independent depolymerization and overall mass-loss kinetics record",
    },
    {
        "source_id": "IUPAC-GOLD-BOOK-POLYMER-TERMS",
        "authority": "International Union of Pure and Applied Chemistry",
        "identity_url": "https://goldbook.iupac.org/terms/search?term=polymer",
        "capture_url": "https://goldbook.iupac.org/terms/search?term=polymer",
        "purpose": "official terminology and measurement-boundary correspondence only; no definition selects a native law",
    },
)


TARGET_NAMES = {
    "001": ("CHAIN-CARRIER", "REPEAT-IDENTITY", "REPEAT-COUNT", "CHAIN-MASS", "END-MASS", "EXACT-RATIO", "POPULATION-BOUNDARY", "ADVERSE-MASS-CUSTODY"),
    "002": ("COMPLETE-POPULATION", "CHAIN-SIZES", "MULTIPLICITIES", "WEIGHTED-SUM", "CHAIN-COUNT", "NUMBER-AVERAGE", "METHOD-BOUNDARY", "CROSS-METHOD-RECORD"),
    "003": ("COMPLETE-POPULATION", "FIRST-MOMENT", "SECOND-MOMENT", "MASS-WEIGHTING", "MASS-AVERAGE", "EXACT-RATIO", "METHOD-BOUNDARY", "CROSS-METHOD-RECORD"),
    "004": ("SHARED-POPULATION", "NUMBER-AVERAGE", "MASS-AVERAGE", "DISPERSITY-RATIO", "EXACT-RATIONAL", "UNCERTAINTY-CUSTODY", "ADVERSE-METHOD-ROW", "CROSS-SOURCE-RECORD"),
    "005": ("INITIATION", "PROPAGATION", "TRANSFER", "TERMINATION", "CONVERSION-TIME", "CHAIN-DISTRIBUTION", "ALL-NETWORK-PATHS", "ADVERSE-INCOMPLETE-NETWORK"),
    "006": ("REACTIVE-GROUPS", "INTERMOLECULAR-BONDS", "COMPONENT-MERGES", "CHAIN-COUNT", "CONVERSION", "DISTRIBUTION", "CYCLE-DISTINCTION", "ADVERSE-UNBALANCED-GROUPS"),
    "007": ("MONOMER-LABELS", "ORDERED-SEQUENCE", "LABEL-COUNTS", "EXACT-COMPOSITION", "BLOCK-STATISTICAL-DISTINCTION", "POPULATION-BOUNDARY", "PROPERTY-CORRESPONDENCE", "ADVERSE-SEQUENCE-ERASURE"),
    "008": ("VERTEX-IDENTITIES", "EDGE-SUPPORT", "DEGREE-VECTOR", "COMPONENTS", "CYCLE-RANK", "LINEAR-BRANCHED-STAR-NETWORK", "PROPERTY-CORRESPONDENCE", "ADVERSE-DRAWING-IDENTITY"),
    "009": ("FINITE-GRAPH", "INLET-BOUNDARY", "OUTLET-BOUNDARY", "CONNECTING-COMPONENT", "FIRST-CONNECTING-STATE", "GEL-LINE", "NEAR-SPANNING-ADVERSE", "FINITE-SCOPE"),
    "010": ("CHAIN-WORD", "FINITE-POSITIONS", "EXACT-CENTROID", "SQUARED-SIZE", "CONFORMATION-SUPPORT", "ARCHITECTURE-SIZE", "METHOD-BOUNDARY", "ADVERSE-CONTINUUM-ROOT"),
    "011": ("POLYMER-CARRIER", "ORDERED-CONDITIONS", "PHASE-LABELS", "TRANSITION-STATE", "DIRECTION", "HYSTERESIS", "NO-CHANGE-ROWS", "CHEMISTRY-MATERIALS-BOUNDARY"),
    "012": ("SOURCE-CARRIER", "SCISSION", "TRANSFER", "UNZIPPING", "CROSSLINKING", "PRODUCT-PATHS", "CARRIER-BALANCE", "TIME-TEMPERATURE-ENVIRONMENT"),
    "013": ("CHEMISTRY-RECORD", "MATERIALS-RECORD", "EXACT-PAIRING", "CHEMISTRY-OWNER", "MATERIALS-OWNER", "DIRECTIONAL-HANDOFF", "UNPAIRED-HALT", "EXTENSION-BOUNDARY"),
}


def write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    if SNAPSHOT.exists():
        raise SystemExit("post-seal Polymer snapshot already exists; refusing to reseal")
    registry = {
        "schema": "sft-v3-source-identity-registry/1",
        "family": FAMILY,
        "registered_date": "2026-07-28",
        "registered_before_complete_source_capture": True,
        "selection_rule": "Capture every registered official record in full, preserve all tables, figures, appendices, method differences, uncertainties, adverse rows, absent fields and transport outcomes, and never allow a source value, equation, model, fit or outcome to select or alter a native law.",
        "development_exposure_disclosure": "The existence, titles and broad subject matter of the registered NIST and IUPAC records were known during source discovery. Search-result summaries exposed selected SRM 2886 and SRM 2888 mass, viscosity and dispersity values and qualitative findings concerning branching, gelation and degradation before sealing. Those rows are openly prior-exposed comparisons, never unknown-target predictions. Complete documents, tables, row vectors and claim-specific analysis were not captured before these seals. Three Materials snapshots and earlier IUPAC categorical polymer records were already repository-visible and remain explicitly prior-exposed immutable dependencies.",
        "numeric_values_or_outcomes_exposed_during_discovery": True,
        "discovery_exposure_never_relabelled_blind": True,
        "complete_registered_value_vectors_opened_before_derivation_seal": False,
        "values_equations_models_fits_or_outcomes_allowed_to_select_native_law": False,
        "sources": SOURCES,
    }
    registry_path = ROOT / REGISTRY
    write(registry_path, registry)
    registry_hash = hash_file(registry_path)
    boundary_hash = hash_file(ROOT / BOUNDARY)
    law_hash = hash_file(ROOT / LAW_PATH)
    source_ids = tuple(row["source_id"] for row in SOURCES)
    for number, law in LAW_ROWS.items():
        target_path = ROOT / f"experiments/external_sources/chemistry/poly_{number}_target_identities_v1.json"
        target = {
            "schema": "sft-v3-value-free-target-identities/1",
            "family": FAMILY,
            "claim_id": law["claim_id"],
            "obligation_id": f"SFT-CHEM-OBL-POLY-{number}",
            "source_ids": source_ids,
            "target_ids": tuple(f"SFT-CHEM-POLY-{number}-{name}" for name in TARGET_NAMES[number]),
            "numeric_target_values_present": False,
            "target_content_opened": False,
        }
        write(target_path, target)
        target_hash = hash_file(target_path)
        payload = {
            "claim_id": law["claim_id"], "obligation_id": f"SFT-CHEM-OBL-POLY-{number}",
            "predicted_unique_survivor": law["result"], "derivation_hash": law_hash,
            "target_identity_hash": target_hash, "source_identity_registry_hash": registry_hash,
            "whole_subfield_batch_boundary_hash": boundary_hash, "candidate_cardinality": 256,
            "operational_witness_count": 8,
        }
        seal = {
            "schema": "sft-v3-source-exposure-disclosed-derivation-seal/1", "sealed_date": "2026-07-28",
            "branch": "chemistry", "family": FAMILY, **payload, "derivation_path": LAW_PATH,
            "target_identity_path": str(target_path.relative_to(ROOT)), "source_identity_registry_path": REGISTRY,
            "whole_subfield_batch_boundary_path": BOUNDARY,
            "source_exposure_before_seal": registry["development_exposure_disclosure"],
            "prior_source_exposure_never_relabelled_blind": True,
            "complete_postseal_source_capture_had_occurred_before_this_seal": False,
            "source_value_equation_outcome_or_conventional_model_used_by_candidate_generator_or_eliminator": False,
            "sealed_payload_hash": sha256_identity(payload),
        }
        write(ROOT / f"experiments/sealed_predictions/chemistry_poly_{number}_pre_source_v1.json", seal)
    print(f"sealed {len(LAW_ROWS)} POLY claims; registry {registry_hash}; law {law_hash}; boundary {boundary_hash}")


if __name__ == "__main__":
    main()
