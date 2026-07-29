#!/usr/bin/env python3
"""Create all ANAL-012--022 value-free targets and derivation seals together."""

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.analytical_terminal_laws_v1 import LAW_ROWS


REGISTRY = "experiments/external_sources/chemistry/anal_012_022_whole_subfield_source_identity_registry_v1.json"
REGISTRY_HASH = "sha256:e4c01443156ba2e1367acd5427adac8a47239e36f768071ed45a81d3750eac41"
BOUNDARY = "audits/CHEMISTRY_ANAL_012_022_WHOLE_SUBFIELD_BATCH_BOUNDARY_2026-07-28.json"
BOUNDARY_HASH = "sha256:de8994198cf3dba8d07613481995e07d40aa59a109de2f5949a7cc39bfa26495"
LAW_PATH = "sft/chemistry/analytical_terminal_laws_v1.py"
LAW_HASH = "sha256:823f492e2424442534355fc2862ed3e61c49cbd891ef57a0d92e29b5c7941d75"

TARGETS = {
    "012": ("IDENTITY", "VIBRATIONAL-STATES", "COMPLETE-LINE-COORDINATES", "COMPLETE-INTENSITY-VECTOR", "SELECTION-CORRESPONDENCE", "UNCERTAINTY-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "013": ("IDENTITY", "ELECTRONIC-STATES", "COMPLETE-ABSORPTION-COORDINATES", "COMPLETE-INTENSITY-VECTOR", "TRANSITION-SUPPORT", "UNCERTAINTY-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "014": ("IDENTITY-COMPOSITION", "CHARGE-ISOTOPE", "COMPLETE-MASS-COORDINATES", "COMPLETE-FRAGMENT-VECTOR", "RESPONSE-RATIOS", "IONIZATION-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "015": ("IDENTITY-GEOMETRY-ISOTOPOLOGUE", "ROTATIONAL-STATES", "COMPLETE-FREQUENCY-VECTOR", "COMPLETE-INTENSITY-VECTOR", "ERROR-ENERGY-STATE-ASSIGNMENT", "CATALOG-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "016": ("CRYSTAL-PHASE-IDENTITY", "PHYSICS-PROBE-HANDOFF", "COMPLETE-REFLECTION-VECTOR", "LATTICE-CELL-SUPPORT", "STRUCTURE-CORRESPONDENCE", "UNCERTAINTY-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "017": ("MATERIAL-PROBE-IDENTITY", "PHYSICS-SCATTERING-HANDOFF", "COMPLETE-ELECTRON-VECTOR", "COMPLETE-NEUTRON-VECTOR", "PROBE-SPECIFIC-CORRESPONDENCE", "UNCERTAINTY-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "018": ("ANALYTE-PHASE-IDENTITY", "COMPLETE-RETENTION-VECTOR", "COMPLETE-PEAK-SUPPORT", "PAIRWISE-RESOLUTION", "TEMPERATURE-FLOW-COLUMN-CONDITION", "REFERENCE-ERROR-CUSTODY", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "019": ("SPECIES-CHARGE-IDENTITY", "MEDIUM-FIELD-CONDITION", "COMPLETE-MOBILITY-VECTOR", "TRAJECTORY-SEPARATION", "ORIENTATION-MAGNITUDE-TRANSLATION", "UNCERTAINTY-CONDITION", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "020": ("ANALYTE-ELECTRODE-CELL-IDENTITY", "ORDERED-POTENTIAL-PATH", "COMPLETE-CURRENT-TRACE", "REACTION-CORRESPONDENCE", "SCAN-MEDIUM-REFERENCE-CONDITION", "BACKGROUND-UNCERTAINTY", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
    "021": ("VALUE-FREE-WITHHELD-CASE", "COMPLETE-ORTHOGONAL-RECORDS", "COMPLETE-CANDIDATE-SET", "EXACT-RECORD-CANDIDATE-INCIDENCE", "COMPLETE-SUPPORT-INTERSECTION", "UNIQUE-IDENTITY-OR-HALT", "STATUS-CONFLICT-ABSENT", "COMPLETE-SOURCE"),
    "022": ("RESULT-TRACEABILITY-IDENTITY", "ACCURACY-TRUENESS", "PRECISION-REPEATABILITY", "SENSITIVITY-SELECTIVITY", "DETECTION-QUANTIFICATION", "COMPLETE-UNCERTAINTY-BUDGET", "STATUS-ADVERSE-ABSENT", "COMPLETE-SOURCE"),
}

SOURCES = {
    "012": ("NIST-WEBBOOK-SRD69-GUIDE", "NIST-WEBBOOK-BENZENE-MULTIMODAL", "NIST-WEBBOOK-ACETONE-MULTIMODAL", "NIST-WEBBOOK-CYCLOHEXANE-MULTIMODAL"),
    "013": ("NIST-WEBBOOK-SRD69-GUIDE", "NIST-WEBBOOK-BENZENE-MULTIMODAL", "NIST-WEBBOOK-ACETONE-MULTIMODAL"),
    "014": ("NIST-WEBBOOK-SRD69-GUIDE", "NIST-WEBBOOK-BENZENE-MULTIMODAL", "NIST-WEBBOOK-ACETONE-MULTIMODAL", "NIST-WEBBOOK-CYCLOHEXANE-MULTIMODAL"),
    "015": ("NASA-JPL-MOLECULAR-SPECTROSCOPY-CATALOG", "NASA-JPL-CO-ROTATIONAL-LINE-CATALOG-028001"),
    "016": ("NIST-SRM-674-XRAY-INTENSITY-SET", "NIST-SRM-676A-DIFFRACTION-STANDARD"),
    "017": ("NIST-ELECTRON-DIFFRACTION-DATABASE-REPORT", "NIST-NEUTRON-SCATTERING-LENGTHS", "NIST-SRM-676A-DIFFRACTION-STANDARD"),
    "018": ("NIST-WEBBOOK-GAS-CHROMATOGRAPHY", "NIST-WEBBOOK-BENZENE-MULTIMODAL", "NIST-WEBBOOK-CYCLOHEXANE-MULTIMODAL"),
    "019": ("NIST-SRM-1980-ELECTROPHORETIC-MOBILITY", "NIST-SP260-209-ZETA-MOBILITY"),
    "020": ("IUPAC-ELECTROCHEMICAL-METHODS-2019", "NIST-VOLTAMMETRIC-LOD-STUDY"),
    "021": ("NIST-WEBBOOK-BENZENE-MULTIMODAL", "NIST-WEBBOOK-ACETONE-MULTIMODAL", "NIST-WEBBOOK-CYCLOHEXANE-MULTIMODAL", "SFT-V3-ANAL-001-011-IMMUTABLE-EVIDENCE"),
    "022": ("SFT-V3-ANAL-001-011-IMMUTABLE-EVIDENCE", "NIST-VOLTAMMETRIC-LOD-STUDY", "NIST-SRM-1980-ELECTROPHORETIC-MOBILITY"),
}


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def write(path: Path, value: object):
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main():
    for relative, expected in ((REGISTRY, REGISTRY_HASH), (BOUNDARY, BOUNDARY_HASH), (LAW_PATH, LAW_HASH)):
        if digest(ROOT / relative) != expected:
            raise SystemExit(f"pre-seal authority changed: {relative}")
    for key, law in LAW_ROWS.items():
        target_path = Path(f"experiments/external_sources/chemistry/anal_{key}_target_identities_v1.json")
        target_ids = tuple(f"SFT-CHEM-ANAL-{key}-{name}" for name in TARGETS[key])
        target = {
            "schema": "sft-v3-value-free-target-identities/1",
            "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
            "claim_id": law["claim_id"], "obligation_id": f"SFT-CHEM-OBL-ANAL-{key}",
            "source_ids": list(SOURCES[key]), "target_ids": list(target_ids),
            "numeric_target_values_present": False, "target_content_opened": False,
        }
        write(ROOT / target_path, target)
        target_hash = digest(ROOT / target_path)
        seal = {
            "schema": "sft-v3-source-exposure-disclosed-derivation-seal/1",
            "sealed_date": "2026-07-28", "family": "ANAL-012-022-WHOLE-ANALYTICAL-CHEMISTRY-CONTINUATION",
            "branch": "chemistry", "claim_id": law["claim_id"], "obligation_id": f"SFT-CHEM-OBL-ANAL-{key}",
            "candidate_cardinality": 256, "operational_witness_count": 8,
            "derivation_path": LAW_PATH, "derivation_hash": LAW_HASH,
            "whole_subfield_batch_boundary_path": BOUNDARY, "whole_subfield_batch_boundary_hash": BOUNDARY_HASH,
            "predicted_unique_survivor": law["result"],
            "target_identity_path": target_path.as_posix(), "target_identity_hash": target_hash,
            "source_identity_registry_path": REGISTRY, "source_identity_registry_hash": REGISTRY_HASH,
            "source_exposure_before_seal": "database coverage counts, titles and categories; selected example GC, rotational, lattice, particle-dimension and qualitative method snippets; no complete registered value vector",
            "prior_source_exposure_never_relabelled_blind": True,
            "complete_postseal_source_capture_had_occurred_before_this_seal": False,
            "source_value_equation_outcome_or_conventional_model_used_by_candidate_generator_or_eliminator": False,
        }
        seal["sealed_payload_hash"] = canonical_digest(seal)
        write(ROOT / f"experiments/sealed_predictions/chemistry_anal_{key}_pre_source_v1.json", seal)
    print("sealed eleven ANAL-012--022 laws and 88 value-free targets as one subfield batch")


if __name__ == "__main__":
    main()
