#!/usr/bin/env python3
"""Admit and materialize the six Foundation prior-obligation reconstructions."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402


CLAIMS = (
    ("SFT-FOUNDATION-EXACT-OPERATIONS-001", "Exact cast, Fold, guarded Take, unison and root-bound trace on the exact positive domain."),
    ("SFT-FOUNDATION-HALF-ONE-001", "The unique first-Fold ground is one-of-two; it is self-complementary, Folds to the One and is distinct from phase translation."),
    ("SFT-FOUNDATION-FOLD-DYNAMICS-001", "Exact two-preimage phase-antipodal Fold dynamics, even-partition invariance and the first two-cycle."),
    ("SFT-FOUNDATION-PRIMITIVE-MAP-UNIQUENESS-001", "Four primitive map classes, 84 executed composition words and Fold as the unique least-size generator in the explicit grammar."),
    ("SFT-FOUNDATION-DERIVATION-TRACE-001", "Complete source- and dependency-bound exact replay trace for every generated finite derivation."),
    ("SFT-FOUNDATION-ADMISSION-ENFORCEMENT-001", "The sole complete fail-closed authority path among 2,048 generated admission paths."),
)


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("foundation_prior_" + claim_id.replace("-", "_"), path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    repository = EngineRepository(ROOT)
    for claim_id, _ in CLAIMS:
        execution = load_execution(claim_id)
        receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
        print(f"admitted {claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")); existing = {item["claim_id"] for item in manifest["claims"]}
    for claim_id, _ in CLAIMS:
        if claim_id not in existing: manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8")); rows = {row["claim_id"]: row for row in census["claims"]}
    for claim_id, exact_result in CLAIMS:
        completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), claim_id, exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
        if completed.returncode: raise RuntimeError(completed.stdout + completed.stderr)
        package = ROOT / "claims" / claim_id
        registration = json.loads((package / "registration.json").read_text(encoding="utf-8")); registration["status"] = "independently_replicated"; write_json(package / "registration.json", registration)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8")); row = rows[claim_id]
        (package / "STATUS.md").write_text(
            f"# {claim_id}\n\nStatus: `independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            "- Empirical status: not applicable to this formal theorem\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- External validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{row['receipt_hash']}`\n"
            f"- Receipt path: `{row['receipt_path']}`\n", encoding="utf-8")
        print(completed.stdout.strip())


if __name__ == "__main__": main()
