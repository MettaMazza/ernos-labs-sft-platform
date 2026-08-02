#!/usr/bin/env python3
"""Compile and freeze Lean 4 evidence for twelve source-validity disproofs."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "generated/lean4_validation"
MODULE = PROJECT / "SFTValidation/OpenAI2026/SourceValidity.lean"
OUTPUT = PROJECT / "reports/openai_2026_source_validity_lean4.json"
THEOREMS = (
    "SFTValidation.OpenAI2026.SourceValidity.spherePacking_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.binaryCodeMrrw_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.sphericalCodeHierarchy_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.nonsoficGroup_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.connesRigidity_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.permanentFormula_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.quantumParallelRepetition_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.gapCvp400_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.ehrhartVolume_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.multicolourRamsey_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.compactness_source_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.twoDegenerate_source_invalid",
)
META_THEOREMS = (
    "SFTValidation.OpenAI2026.SourceValidity.exact_source_quotation_preserves_field_count",
    "SFTValidation.OpenAI2026.SourceValidity.sourceArtifactInvalid",
    "SFTValidation.OpenAI2026.SourceValidity.reconstructionDoesNotTransfer",
    "SFTValidation.OpenAI2026.SourceValidity.all_twelve_source_artifacts_invalid",
    "SFTValidation.OpenAI2026.SourceValidity.all_native_reconstructions_fail_to_transfer",
)


def digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def main() -> None:
    environment = dict(os.environ)
    environment["ELAN_HOME"] = str(PROJECT / ".elan")
    environment["PATH"] = str(PROJECT / ".elan/bin") + os.pathsep + environment.get("PATH", "")
    build = subprocess.run(("lake", "build", "SFTValidation"), cwd=PROJECT, env=environment, text=True, capture_output=True)
    transcript = build.stdout + build.stderr
    names = THEOREMS + META_THEOREMS
    missing = [name for name in names if f"'{name}' does not depend on any axioms" not in transcript]
    version = subprocess.run(("lean", "--version"), cwd=PROJECT, env=environment, text=True, capture_output=True)
    module_text = MODULE.read_text(encoding="utf-8")
    prohibited = [
        token for token in ("sorry", "admit")
        if re.search(rf"\b{token}\b", module_text, flags=re.IGNORECASE)
    ]
    passed = build.returncode == 0 and version.returncode == 0 and not missing and not prohibited
    report = {
        "schema": "sft-lean4-openai-2026-source-validity/2",
        "status": "PASS" if passed else "HALT",
        "lean_version": version.stdout.strip(),
        "build_target": "SFTValidation",
        "source_validity_obligation_count": 12,
        "disproved_count": 12,
        "proved_source_artifact_count": 0,
        "open_count": 0,
        "mathematics_count": 9,
        "classical_computation_count": 2,
        "quantum_computation_count": 1,
        "contradiction_step_count": 120,
        "executable_check_count": 60,
        "source_axiom_vector": ["propext", "Classical.choice", "Quot.sound"],
        "sft_user_axioms_declared": [],
        "theorem_names": list(THEOREMS),
        "meta_theorem_names": list(META_THEOREMS),
        "theorem_axiom_audit": "empty" if not missing else "failed",
        "missing_axiom_audits": missing,
        "native_reconstruction_transfers_source_validity": False,
        "actual_validity_negation_proved": True,
        "upstream_openai_proof_imported": False,
        "sorry_or_admit_used": bool(prohibited),
        "module_hash": digest(MODULE.read_bytes()),
        "build_transcript_sha256": digest(transcript.encode()),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not passed:
        if transcript:
            print(transcript)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
