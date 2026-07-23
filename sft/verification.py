"""One-command revalidation of the engine and every admitted derivation."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Optional

from sft.engine import AuthorityLedger, EngineReceipt, SFTAdmissionEngine
from sft.engine.model import DerivationProgram, EmpiricalValidator, IndependentValidator
from sft.engine.receipt_io import read_receipt
from sft.engine.source import build_source_manifest


class VerificationError(RuntimeError):
    """Raised when any repository, engine, coverage or derivation check fails."""


@dataclass(frozen=True)
class ClaimExecution:
    program: DerivationProgram
    independent_validator: IndependentValidator
    source_files: tuple[Path, ...]
    empirical_validator: Optional[EmpiricalValidator] = None


@dataclass(frozen=True)
class CoverageReport:
    tests_run: int
    modules: int
    executable_lines: int
    executed_lines: int

    @property
    def percent(self) -> int:
        return 100 if self.executable_lines == self.executed_lines else 0


@dataclass(frozen=True)
class VerificationReport:
    coverage: CoverageReport
    rerun_claims: int


def run_repository_validation(root: Path) -> None:
    command = (sys.executable, str(root / "tools" / "validate_repository.py"))
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise VerificationError("repository validation failed:\n" + completed.stdout + completed.stderr)


def run_core_coverage(root: Path) -> CoverageReport:
    """Run all unit/E2E tests and require every executable engine line."""

    engine_modules = tuple(sorted((root / "sft" / "engine").glob("*.py")))
    with tempfile.TemporaryDirectory(prefix="sft-core-coverage-") as temporary:
        cover_directory = Path(temporary)
        command = (
            sys.executable,
            "-m",
            "trace",
            "--count",
            "--missing",
            "--coverdir",
            str(cover_directory),
            "--module",
            "unittest",
            "discover",
            "-s",
            "tests",
        )
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise VerificationError("unit/E2E suite failed:\n" + completed.stdout + completed.stderr)

        executable_lines = 0
        executed_lines = 0
        missing: list[str] = []
        for module in engine_modules:
            module_name = "sft.engine." + module.stem
            cover_path = cover_directory / f"{module_name}.cover"
            if not cover_path.is_file():
                missing.append(f"{module_name}: module was not executed")
                continue
            for line_number, line in enumerate(cover_path.read_text(encoding="utf-8").splitlines(), 1):
                if line.startswith(">>>>>>"):
                    executable_lines += 1
                    missing.append(f"{module_name}:{line_number}")
                elif re.match(r"^\s*\d+:", line):
                    executable_lines += 1
                    executed_lines += 1
        if missing:
            raise VerificationError(
                "core-engine executable-line coverage is below 100%:\n" + "\n".join(missing)
            )
        test_output = completed.stdout + completed.stderr
        match = re.search(r"Ran (\d+) tests?", test_output)
        if match is None:
            raise VerificationError("unit/E2E suite did not report its executed test count")
        return CoverageReport(int(match.group(1)), len(engine_modules), executable_lines, executed_lines)


def _load_execution(root: Path, entry: dict[str, object]) -> ClaimExecution:
    relative = entry.get("execution_file")
    if not isinstance(relative, str):
        raise VerificationError("claim execution entry lacks execution_file")
    execution_path = (root / relative).resolve()
    try:
        execution_path.relative_to(root)
    except ValueError as exc:
        raise VerificationError("claim execution file escapes the repository") from exc
    if not execution_path.is_file():
        raise VerificationError(f"claim execution file is missing: {relative}")
    module_name = "sft_claim_execution_" + re.sub(r"[^A-Za-z0-9_]", "_", str(entry.get("claim_id")))
    specification = importlib.util.spec_from_file_location(module_name, execution_path)
    if specification is None or specification.loader is None:
        raise VerificationError(f"claim execution file cannot be loaded: {relative}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    factory = getattr(module, "build_execution", None)
    if not callable(factory):
        raise VerificationError(f"claim execution file has no build_execution factory: {relative}")
    execution = factory(root)
    if not isinstance(execution, ClaimExecution):
        raise VerificationError(f"claim execution factory returned the wrong object: {relative}")
    return execution


def rerun_registered_claims(root: Path) -> int:
    """Recompute all admitted claims in census order without modifying evidence."""

    execution_manifest = json.loads(
        (root / "census" / "execution_manifest.json").read_text(encoding="utf-8")
    )
    census = json.loads((root / "census" / "claims.json").read_text(encoding="utf-8"))
    entries = execution_manifest.get("claims")
    rows = census.get("claims")
    if not isinstance(entries, list) or not isinstance(rows, list):
        raise VerificationError("claim census or execution manifest is malformed")
    entry_ids = [entry.get("claim_id") for entry in entries if isinstance(entry, dict)]
    row_ids = [row.get("claim_id") for row in rows if isinstance(row, dict)]
    if len(entry_ids) != len(entries) or entry_ids != row_ids:
        raise VerificationError("execution manifest does not match the complete ordered claim census")

    authority = AuthorityLedger()
    engine = SFTAdmissionEngine(authority)
    for entry, row in zip(entries, rows):
        execution = _load_execution(root, entry)
        if execution.program.registration.claim_id != entry["claim_id"]:
            raise VerificationError("execution factory and manifest claim identities differ")
        source_manifest = build_source_manifest(root, execution.source_files)
        receipt = engine.run(
            execution.program,
            execution.independent_validator,
            execution.empirical_validator,
            executed_source_hash=source_manifest.manifest_hash,
        )
        receipt_path = (root / row["receipt_path"]).resolve()
        stored = read_receipt(receipt_path)
        if receipt.receipt_hash != row.get("receipt_hash") or receipt != stored:
            raise VerificationError(f"recomputed receipt differs from census evidence: {entry['claim_id']}")
        authority.admit(receipt)
    return len(rows)


def verify_all(root: Path) -> VerificationReport:
    run_repository_validation(root)
    coverage = run_core_coverage(root)
    rerun_claims = rerun_registered_claims(root)
    return VerificationReport(coverage, rerun_claims)
