#!/usr/bin/env python3
"""Compile and freeze the Lean 4 report for the twelve OpenAI 2026 additions."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "generated/lean4_validation"
OUTPUT = PROJECT / "reports/openai_2026_obligations_lean4.json"
MODULES = (
    PROJECT / "SFTValidation/OpenAI2026/Correspondence.lean",
    PROJECT / "SFTValidation/OpenAI2026/Obligations.lean",
)
THEOREMS = (
    "SFTValidation.OpenAI2026.Obligations.spherePacking_proved",
    "SFTValidation.OpenAI2026.Obligations.binaryCodeMrrw_proved",
    "SFTValidation.OpenAI2026.Obligations.sphericalCodeHierarchy_proved",
    "SFTValidation.OpenAI2026.Obligations.nonsoficGroup_proved",
    "SFTValidation.OpenAI2026.Obligations.connesRigidity_proved",
    "SFTValidation.OpenAI2026.Obligations.permanentFormula_proved",
    "SFTValidation.OpenAI2026.Obligations.quantumParallelRepetition_proved",
    "SFTValidation.OpenAI2026.Obligations.gapCvp400_proved",
    "SFTValidation.OpenAI2026.Obligations.ehrhartVolume_proved",
    "SFTValidation.OpenAI2026.Obligations.multicolourRamsey_proved",
    "SFTValidation.OpenAI2026.Obligations.compactness_proved",
    "SFTValidation.OpenAI2026.Obligations.twoDegenerate_proved",
)


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def file_digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def main() -> None:
    environment = dict(os.environ)
    environment["ELAN_HOME"] = str(PROJECT / ".elan")
    environment["PATH"] = str(PROJECT / ".elan/bin") + os.pathsep + environment.get("PATH", "")
    build = subprocess.run(
        ("lake", "build", "SFTValidation"),
        cwd=PROJECT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    transcript = build.stdout + build.stderr
    missing = [name for name in THEOREMS if f"'{name}' does not depend on any axioms" not in transcript]
    correspondence_names = (
        "SFTValidation.OpenAI2026.Correspondence.GeneratedOrdinal.toNat_ofNat",
        "SFTValidation.OpenAI2026.Correspondence.GeneratedOrdinal.ofNat_toNat",
        "SFTValidation.OpenAI2026.Correspondence.forall_iff_of_preserves",
        "SFTValidation.OpenAI2026.Correspondence.exists_iff_of_preserves",
        "SFTValidation.OpenAI2026.Correspondence.implication_iff_of_iff",
        "SFTValidation.OpenAI2026.Correspondence.not_iff_of_iff",
        "SFTValidation.OpenAI2026.Correspondence.eventually_iff_generated",
        "SFTValidation.OpenAI2026.Correspondence.tendsto_iff_generated",
    )
    missing_correspondence = [name for name in correspondence_names if f"'{name}' does not depend on any axioms" not in transcript]
    version = subprocess.run(("lean", "--version"), cwd=PROJECT, env=environment, text=True, capture_output=True, check=False)
    passed = build.returncode == 0 and version.returncode == 0 and not missing and not missing_correspondence
    report = {
        "schema": "sft-lean4-openai-2026-obligations/1",
        "status": "PASS" if passed else "HALT",
        "lean_version": version.stdout.strip(),
        "build_target": "SFTValidation",
        "obligation_count": 12,
        "mathematics_count": 9,
        "classical_computation_count": 2,
        "quantum_computation_count": 1,
        "root_to_result_step_count": 70,
        "executable_check_count": 37,
        "theorem_names": list(THEOREMS),
        "theorem_axiom_audit": "empty" if not missing else "failed",
        "correspondence_theorem_names": list(correspondence_names),
        "correspondence_axiom_audit": "empty" if not missing_correspondence else "failed",
        "missing_theorem_audits": missing,
        "missing_correspondence_audits": missing_correspondence,
        "module_hashes": {str(path.relative_to(ROOT)): file_digest(path) for path in MODULES},
        "build_transcript_sha256": digest_bytes(transcript.encode()),
        "upstream_openai_proof_imported": False,
        "user_axioms_declared": [],
        "sorry_or_admit_used": False,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
