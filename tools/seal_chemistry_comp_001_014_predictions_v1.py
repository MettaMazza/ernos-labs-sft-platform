#!/usr/bin/env python3
"""Register value-free COMP-001--014 targets and seal all native laws."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.computational_chemistry_laws_v1 import LAW_ROWS
from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


FAMILY = "COMP-001-014-COMPUTATIONAL-CHEMISTRY-AND-CHEMINFORMATICS"
BOUNDARY = "audits/CHEMISTRY_COMP_001_014_WHOLE_SUBFIELD_BATCH_BOUNDARY_2026-07-28.json"
LAW_PATH = "sft/chemistry/computational_chemistry_laws_v1.py"
REGISTRY = "experiments/external_sources/chemistry/comp_001_014_whole_subfield_source_identity_registry_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1"


PUBCHEM_CIDS = (180, 241, 702, 887, 962, 1983, 2244, 2519, 3672, 5957, 8078, 5288826)


TARGET_NAMES = {
    "001": ("CARRIER", "ATOM-CUSTODY", "BOND-CUSTODY", "HELD-FIBRES", "ORDER-INVARIANCE", "DECODE-ROUNDTRIP", "PROVENANCE", "TAMPER-REJECTION"),
    "002": ("IDENTICAL-PAIR", "PERMUTED-PAIR", "BIJECTION", "ATOM-PRESERVATION", "BOND-PRESERVATION", "STEREO-ISOTOPE-CHARGE", "NONISOMORPH-PAIR", "TAMPER-REJECTION"),
    "003": ("QUERY-GRAPH", "TARGET-GRAPH", "INJECTIVE-MAPS", "ATOM-PRESERVATION", "BOND-PRESERVATION", "HELD-FIBRES", "ABSENT-QUERY", "COMPLETE-EMBEDDINGS"),
    "004": ("ELEMENT-SUPPORT", "CONNECTED-GRAPHS", "VALENCE-BOUND", "CANONICAL-QUOTIENT", "C3H8O-CENSUS", "MEMBER-CERTIFICATES", "REJECTED-FORMS", "FORMULA-COMPARISON"),
    "005": ("CONSTITUTION", "ORIENTATION-SITES", "FIBRE-ASSIGNMENTS", "AUTOMORPHISM-QUOTIENT", "ENANTIOMER-PAIR", "DIASTEREOMER-DISTINCTION", "ACHIRAL-ADVERSE", "COMPLETE-CENSUS"),
    "006": ("MOLECULAR-GRAPH", "ROTATABLE-BONDS", "FINITE-RESOLUTION", "COMPLETE-WORDS", "SYMMETRY-QUOTIENT", "CONFORMER-IDENTITIES", "NONROTOR-ADVERSE", "RESOURCE-BOUNDARY"),
    "007": ("REACTANT-GRAPHS", "REGISTERED-TRANSITIONS", "CARRIER-CONSERVATION", "BOND-CHANGE-TRACE", "PRODUCT-SUPPORT", "CANONICAL-PRODUCTS", "ADVERSE-PRODUCTS", "DEPTH-BOUNDARY"),
    "008": ("SOURCE-INVENTORY", "PRODUCT-INVENTORY", "ATOM-BIJECTION", "ELEMENT-BALANCE", "ISOTOPE-CUSTODY", "CHARGE-CUSTODY", "ALL-COMPONENTS", "TAMPERED-MAP-REJECTION"),
    "009": ("HELD-STATES", "ADMITTED-TRANSITIONS", "ALL-SIMPLE-PATHS", "CARRIER-TRACE", "PARALLEL-ROUTES", "CYCLE-BOUNDARY", "KERNEL-ACCEPTANCE", "COMPLETE-PROOF-TRACE"),
    "010": ("LEFT-GRAPH", "RIGHT-GRAPH", "EXACT-FEATURES", "SHARED-SUPPORT", "LEFT-DIFFERENCE", "RIGHT-DIFFERENCE", "IDENTITY-SEPARATION", "NEAR-NEIGHBOUR-ADVERSE"),
    "011": ("CANONICAL-CARRIER", "PUBCHEM-IDENTITY", "CHEBI-IDENTITY", "BYTE-VERSION", "REVERSIBLE-REPRESENTATION", "CROSS-SOURCE-MAP", "SUPERSESSION-CONFLICT", "UNAVAILABLE-ADVERSE"),
    "012": ("CANONICAL-INPUT", "ADMITTED-PROPERTY", "EXACT-ARITHMETIC", "DEPENDENCY-TRACE", "UNIT-CUSTODY", "UNCERTAINTY-CUSTODY", "UNSUPPORTED-HALT", "RESULT-CERTIFICATE"),
    "013": ("REGISTERED-DOMAIN", "COMPLETE-INPUT", "MISSING-DISTINCTIONS", "SUPPORT-INCLUSION", "OUT-OF-DOMAIN-HALT", "ADVERSE-CUSTODY", "APPEND-ONLY-EXTENSION", "SCOPE-CERTIFICATE"),
    "014": ("SHARED-CHEMICAL-LAW", "SHARED-INPUT", "CLASSICAL-TRACE", "REVERSIBLE-BRANCHES", "STATE-PROJECTION", "OBSERVATION-RECORD", "RESOURCE-ACCOUNT", "TERMINAL-IDENTITY"),
}


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    if SNAPSHOT.exists():
        raise SystemExit("post-seal snapshot already exists; refusing to reseal")
    sources = [
        {
            "source_id": "PUBCHEM-PUG-REST-AUTHORITY",
            "authority": "National Library of Medicine, National Center for Biotechnology Information",
            "identity_url": "https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest",
            "capture_url": "https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest",
            "purpose": "official API identity, record, structure, search, conformer and provenance semantics",
        },
        {
            "source_id": "PUBCHEM-C3H8O-FORMULA-CENSUS",
            "authority": "National Library of Medicine, National Center for Biotechnology Information",
            "identity_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/C3H8O/cids/JSON?MaxRecords=100",
            "capture_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastformula/C3H8O/cids/JSON?MaxRecords=100",
            "purpose": "post-seal external constitutional-isomer and database-support comparison",
        },
        {
            "source_id": "PUBCHEM-ASPIRIN-CONFORMERS",
            "authority": "National Library of Medicine, National Center for Biotechnology Information",
            "identity_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/conformers/JSON",
            "capture_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/conformers/JSON",
            "purpose": "post-seal external finite conformer record support",
        },
        {
            "source_id": "PUBCHEM-ASPIRIN-SUBSTRUCTURE",
            "authority": "National Library of Medicine, National Center for Biotechnology Information",
            "identity_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastsubstructure/cid/2244/cids/JSON?MaxRecords=100",
            "capture_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastsubstructure/cid/2244/cids/JSON?MaxRecords=100",
            "purpose": "post-seal external substructure-search comparison",
        },
        {
            "source_id": "PUBCHEM-ASPIRIN-SIMILARITY",
            "authority": "National Library of Medicine, National Center for Biotechnology Information",
            "identity_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastsimilarity_2d/cid/2244/cids/JSON?Threshold=95&MaxRecords=100",
            "capture_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/fastsimilarity_2d/cid/2244/cids/JSON?Threshold=95&MaxRecords=100",
            "purpose": "conventional similarity comparison only; never a native Fold law or survivor selector",
        },
        {
            "source_id": "CHEBI-REST-AUTHORITY",
            "authority": "EMBL-European Bioinformatics Institute",
            "identity_url": "https://www.ebi.ac.uk/chebi/webServices.do",
            "capture_url": "https://www.ebi.ac.uk/chebi/webServices.do",
            "purpose": "official ChEBI API, entity, structure and provenance semantics",
        },
        {
            "source_id": "RHEA-IMMUTABLE-REACTION-SMILES",
            "authority": "Rhea, SIB Swiss Institute of Bioinformatics and EMBL-EBI",
            "identity_url": "repository:experiments/external_sources/chemistry/snapshots/org-009-rhea-blind-v1/source-inventory-v1.json",
            "capture_url": "repository:experiments/external_sources/chemistry/snapshots/org-009-rhea-blind-v1/rhea-reaction-smiles.tsv",
            "purpose": "complete previously captured reaction graph surface; source exposure remains disclosed",
        },
        {
            "source_id": "USPTO-IMMUTABLE-REACTION-SURFACE",
            "authority": "public patent reaction corpus as preserved by the admitted Organic Chemistry evidence package",
            "identity_url": "repository:experiments/external_sources/chemistry/snapshots/org-009-uspto50k-blind-v2/source-inventory-v2.json",
            "capture_url": "repository:experiments/external_sources/chemistry/snapshots/org-009-uspto50k-blind-v2/USPTO_50K.csv",
            "purpose": "previously captured reaction and atom-map comparison; source exposure remains disclosed",
        },
    ]
    for cid in PUBCHEM_CIDS:
        sources.append({
            "source_id": f"PUBCHEM-CID-{cid}-FULL-2D",
            "authority": "National Library of Medicine, National Center for Biotechnology Information",
            "identity_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
            "capture_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/JSON?record_type=2d",
            "sdf_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=2d",
            "property_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula,ConnectivitySMILES,SMILES,InChI,InChIKey,HeavyAtomCount,AtomStereoCount,DefinedAtomStereoCount,UndefinedAtomStereoCount,BondStereoCount,ConformerCount/JSON",
            "purpose": "complete fixed-identity molecular record, exact graph reconstruction, round-trip, identity, stereo and property comparison",
        })
    for chebi in ("15377", "16236", "15347", "16716"):
        sources.append({
            "source_id": f"CHEBI-{chebi}-RECORD",
            "authority": "EMBL-European Bioinformatics Institute",
            "identity_url": f"https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:{chebi}",
            "capture_url": f"https://www.ebi.ac.uk/chebi/backend/api/public/compound/CHEBI:{chebi}/",
            "structure_url": f"https://www.ebi.ac.uk/chebi/backend/api/public/compound/CHEBI:{chebi}/structure/",
            "purpose": "fixed-identity cross-database entity and structure provenance comparison",
        })
    registry = {
        "schema": "sft-v3-source-identity-registry/1",
        "family": FAMILY,
        "registered_date": "2026-07-28",
        "registered_before_complete_source_capture": True,
        "selection_rule": "Capture every registered official PubChem and ChEBI response, including transport failures, absent fields, conflicting identifiers and superseded records; preserve the complete existing Rhea and USPTO surfaces by exact byte identity. No result may select or alter a native law.",
        "development_exposure_disclosure": "Public documentation established only available API operations and formats. PubChem CIDs, ChEBI IDs, formula C3H8O, aspirin search identity and existing Rhea/USPTO source identities are fixed targets. Familiar names and selected identifiers were known before sealing and remain disclosed; no captured response vector, graph reconstruction, search result, conformer list or cross-source outcome was opened for this batch before these seals.",
        "sources": sources,
        "numeric_values_or_outcomes_opened_before_derivation_seal": False,
        "complete_registered_value_vectors_opened_before_derivation_seal": False,
        "values_or_outcomes_allowed_to_select_native_law": False,
    }
    registry_path = ROOT / REGISTRY
    write(registry_path, registry)
    registry_hash = hash_file(registry_path)
    boundary_hash = hash_file(ROOT / BOUNDARY)
    law_hash = hash_file(ROOT / LAW_PATH)
    source_ids = tuple(row["source_id"] for row in sources)
    for number, law in LAW_ROWS.items():
        target_path = ROOT / f"experiments/external_sources/chemistry/comp_{number}_target_identities_v1.json"
        target = {
            "schema": "sft-v3-value-free-target-identities/1",
            "family": FAMILY,
            "claim_id": law["claim_id"],
            "obligation_id": f"SFT-CHEM-OBL-COMP-{number}",
            "source_ids": source_ids,
            "target_ids": tuple(f"SFT-CHEM-COMP-{number}-{name}" for name in TARGET_NAMES[number]),
            "numeric_target_values_present": False,
            "target_content_opened": False,
        }
        write(target_path, target)
        target_hash = hash_file(target_path)
        payload = {
            "claim_id": law["claim_id"],
            "obligation_id": f"SFT-CHEM-OBL-COMP-{number}",
            "predicted_unique_survivor": law["result"],
            "derivation_hash": law_hash,
            "target_identity_hash": target_hash,
            "source_identity_registry_hash": registry_hash,
            "whole_subfield_batch_boundary_hash": boundary_hash,
            "candidate_cardinality": 256,
            "operational_witness_count": 8,
        }
        seal = {
            "schema": "sft-v3-source-exposure-disclosed-derivation-seal/1",
            "sealed_date": "2026-07-28",
            "branch": "chemistry",
            "family": FAMILY,
            **payload,
            "derivation_path": LAW_PATH,
            "target_identity_path": str(target_path.relative_to(ROOT)),
            "source_identity_registry_path": REGISTRY,
            "whole_subfield_batch_boundary_path": BOUNDARY,
            "source_exposure_before_seal": "public API documentation, fixed record identities and disclosed prior Rhea/USPTO evidence identities; no COMP-001--014 response vector",
            "prior_source_exposure_never_relabelled_blind": True,
            "complete_postseal_source_capture_had_occurred_before_this_seal": False,
            "source_value_equation_outcome_or_conventional_model_used_by_candidate_generator_or_eliminator": False,
            "sealed_payload_hash": sha256_identity(payload),
        }
        write(ROOT / f"experiments/sealed_predictions/chemistry_comp_{number}_pre_source_v1.json", seal)
    print(f"sealed {len(LAW_ROWS)} COMP claims; registry {registry_hash}; law {law_hash}; boundary {boundary_hash}")


if __name__ == "__main__":
    main()
