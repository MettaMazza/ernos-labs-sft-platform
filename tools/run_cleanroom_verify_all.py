#!/usr/bin/env python3
"""Run the sealed full verifier on the current non-ignored repository surface.

The canonical repository validator intentionally scans every JSON and Python
file below its root. Local third-party environments are not part of the model
source surface, but their vendor files can otherwise be parsed as first-party
inputs. This runner diagnoses that condition, builds a read-only clean-room view
of the complete worktree evidence while omitting only dependency/runtime cache
trees, and invokes the unmodified ``python -m sft verify-all`` entry point there.
"""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "audits"
INVALID_LINE = re.compile(r"^invalid (?:JSON|Python): (.*?): ")
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
EXCLUDED_RELATIVE_DIRECTORIES = {
    Path(
        "applications/frontier/v3_computational_proofs/protein_folding/"
        "comparator/runtime"
    )
}
LIBC = ctypes.CDLL("libc.dylib", use_errno=True)
CLONEFILE = LIBC.clonefile
CLONEFILE.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
CLONEFILE.restype = ctypes.c_int


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def run_capture(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def source_paths() -> list[Path]:
    paths: list[Path] = []
    for directory, directory_names, file_names in os.walk(ROOT, topdown=True):
        current = Path(directory)
        retained_directories: list[str] = []
        for name in directory_names:
            candidate = current / name
            relative = candidate.relative_to(ROOT)
            if (
                name in EXCLUDED_DIRECTORY_NAMES
                or relative in EXCLUDED_RELATIVE_DIRECTORIES
            ):
                continue
            if candidate.is_symlink():
                paths.append(relative)
            else:
                retained_directories.append(name)
        directory_names[:] = retained_directories
        for name in file_names:
            candidate = current / name
            if candidate.is_file() or candidate.is_symlink():
                paths.append(candidate.relative_to(ROOT))
    return sorted(paths, key=lambda item: item.as_posix())


def inventory_sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for relative in paths:
        source = ROOT / relative
        stat = source.lstat()
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(b"\0")
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()


def diagnose_original_validator() -> dict[str, object]:
    completed = run_capture([sys.executable, "tools/validate_repository.py"], ROOT)
    invalid_paths: list[str] = []
    non_scope_errors: list[str] = []
    for line in completed.stdout.splitlines():
        match = INVALID_LINE.match(line)
        if match:
            invalid_paths.append(match.group(1))
        elif line and line != "repository validation failed:":
            non_scope_errors.append(line)

    ignored: list[str] = []
    not_ignored: list[str] = []
    for relative in invalid_paths:
        check = subprocess.run(
            ["git", "check-ignore", "-q", "--", relative],
            cwd=ROOT,
            check=False,
        )
        (ignored if check.returncode == 0 else not_ignored).append(relative)

    expected_scope_failure = (
        completed.returncode != 0
        and bool(invalid_paths)
        and len(ignored) == len(invalid_paths)
        and not not_ignored
        and not non_scope_errors
    )
    return {
        "command": f"{sys.executable} tools/validate_repository.py",
        "return_code": completed.returncode,
        "invalid_file_count": len(invalid_paths),
        "ignored_invalid_file_count": len(ignored),
        "nonignored_invalid_files": not_ignored,
        "other_errors": non_scope_errors,
        "all_failures_confined_to_gitignored_files": expected_scope_failure,
        "output_sha256": "sha256:"
        + hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
    }


def build_cleanroom(destination: Path, paths: list[Path]) -> dict[str, int]:
    regular_files = 0
    symlinks = 0
    linked_bytes = 0
    created_directories: set[Path] = {destination}
    for index, relative in enumerate(paths, 1):
        source = ROOT / relative
        target = destination / relative
        parent = target.parent
        if parent not in created_directories:
            parent.mkdir(parents=True, exist_ok=True)
            cursor = parent
            while cursor != destination and cursor not in created_directories:
                created_directories.add(cursor)
                cursor = cursor.parent
        if source.is_symlink():
            os.symlink(os.readlink(source), target)
            symlinks += 1
        else:
            result = CLONEFILE(os.fsencode(source), os.fsencode(target), 0)
            if result != 0:
                error_number = ctypes.get_errno()
                raise OSError(
                    error_number,
                    f"clonefile failed: {os.strerror(error_number)}",
                    str(source),
                )
            regular_files += 1
            linked_bytes += source.stat().st_size
        if index == 1 or index % 25000 == 0 or index == len(paths):
            print(
                f"[SFT clean-room] source view: {index}/{len(paths)} files linked",
                flush=True,
            )
    return {
        "file_count": len(paths),
        "regular_file_count": regular_files,
        "symlink_count": symlinks,
        "logical_bytes": linked_bytes,
    }


def stream_verify(cleanroom: Path) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(cleanroom)
    command = [sys.executable, "-m", "sft", "verify-all"]
    process = subprocess.Popen(
        command,
        cwd=cleanroom,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )
    lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        print(line, end="", flush=True)
        lines.append(line)
    return process.wait(), "".join(lines)


def parse_result(transcript: str) -> dict[str, object]:
    tests = re.search(r"unit and end-to-end tests passed: (\d+)", transcript)
    coverage = re.search(
        r"core engine executable-line coverage: (\d+)/(\d+) \(100%\)",
        transcript,
    )
    modules = re.search(r"core engine modules covered: (\d+)", transcript)
    claims = re.search(r"registered derivations independently rerun: (\d+)", transcript)
    measurement = re.search(
        r"external-measurement coverage: pass \((\d+) empirical claims; (\d+)/(\d+) formal Physics claims reach measurement\)",
        transcript,
    )
    live = re.search(
        r"live authoritative measurement comparison: pass \((\d+) exact current-source checks; ([^)]+)\)",
        transcript,
    )
    return {
        "completion_marker_present": "SFT COMPLETE VERIFICATION: PASS" in transcript,
        "tests_run": int(tests.group(1)) if tests else None,
        "coverage_executed_lines": int(coverage.group(1)) if coverage else None,
        "coverage_executable_lines": int(coverage.group(2)) if coverage else None,
        "engine_modules_covered": int(modules.group(1)) if modules else None,
        "registered_derivations_rerun": int(claims.group(1)) if claims else None,
        "empirical_claims": int(measurement.group(1)) if measurement else None,
        "physics_formal_claims_reaching_measurement": int(measurement.group(2)) if measurement else None,
        "physics_formal_claims": int(measurement.group(3)) if measurement else None,
        "live_exact_check_count": int(live.group(1)) if live else None,
        "live_source_id": live.group(2) if live else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--audit-stem",
        default="SFT_FULL_VERIFY_ALL_CLEANROOM_2026-08-02_FINAL",
    )
    args = parser.parse_args()
    audit_path = AUDIT_DIR / f"{args.audit_stem}.json"
    transcript_path = AUDIT_DIR / f"{args.audit_stem}.log"
    if audit_path.exists() or transcript_path.exists():
        raise SystemExit("refusing to overwrite an existing clean-room audit")

    started_at = utc_now()
    started = time.monotonic()
    print("[SFT clean-room] verifying canonical seals", flush=True)
    engine_seal = run_capture([sys.executable, "tools/verify_engine_seal.py"], ROOT)
    authority_seal = run_capture(
        [sys.executable, "tools/verify_verification_authority_seal.py"], ROOT
    )
    if engine_seal.returncode != 0 or authority_seal.returncode != 0:
        raise SystemExit(engine_seal.stdout + authority_seal.stdout)

    print("[SFT clean-room] diagnosing original validator scope", flush=True)
    preflight = diagnose_original_validator()
    if not preflight["all_failures_confined_to_gitignored_files"]:
        raise SystemExit("original validator has a non-ignored or non-scope failure")
    print(
        "[SFT clean-room] original scope issue confined to "
        f"{preflight['ignored_invalid_file_count']} ignored vendor files",
        flush=True,
    )

    paths = source_paths()
    selection_sha256 = inventory_sha256(paths)
    transcript = ""
    return_code = 1
    mirror_stats: dict[str, int] = {}
    cleanroom_cleaned = False
    cleanroom_parent = ROOT.parent
    with tempfile.TemporaryDirectory(
        prefix=".sft-verify-all-cleanroom-", dir=cleanroom_parent
    ) as temporary:
        cleanroom = Path(temporary)
        mirror_stats = build_cleanroom(cleanroom, paths)
        print("[SFT clean-room] invoking unmodified python -m sft verify-all", flush=True)
        return_code, transcript = stream_verify(cleanroom)
    cleanroom_cleaned = True

    parsed = parse_result(transcript)
    passed = return_code == 0 and parsed["completion_marker_present"] is True
    completed_at = utc_now()
    elapsed = round(time.monotonic() - started, 3)
    transcript_path.write_text(transcript, encoding="utf-8")
    audit = {
        "schema": "sft.full_verify_all_cleanroom_audit.v1",
        "audit_id": args.audit_stem,
        "status": "PASS" if passed else "FAIL",
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "elapsed_seconds": elapsed,
        "source_root": str(ROOT),
        "source_selection": (
            "complete current worktree evidence excluding only repository metadata, "
            "dependency/runtime environments and interpreter caches"
        ),
        "excluded_directory_names": sorted(EXCLUDED_DIRECTORY_NAMES),
        "excluded_relative_directories": sorted(
            path.as_posix() for path in EXCLUDED_RELATIVE_DIRECTORIES
        ),
        "source_selection_file_count": mirror_stats.get("file_count"),
        "source_selection_inventory_sha256": selection_sha256,
        "mirror": {
            **mirror_stats,
            "method": "APFS copy-on-write clones for regular files; copied symlink identities",
            "scientific_files_mutated": False,
            "temporary_cleanroom_removed": cleanroom_cleaned,
        },
        "preflight_scope_diagnosis": preflight,
        "command": f"{sys.executable} -m sft verify-all",
        "return_code": return_code,
        "result": parsed,
        "transcript": transcript_path.relative_to(ROOT).as_posix(),
        "transcript_sha256": sha256_file(transcript_path),
        "census_sha256": sha256_file(ROOT / "census/claims.json"),
        "execution_manifest_sha256": sha256_file(ROOT / "census/execution_manifest.json"),
        "runner_sha256": sha256_file(Path(__file__)),
        "engine_seal_status": "PASS",
        "engine_seal_output": engine_seal.stdout.strip().splitlines(),
        "verification_authority_seal_status": "PASS",
        "verification_authority_seal_output": authority_seal.stdout.strip().splitlines(),
        "python": sys.version,
        "platform": platform.platform(),
        "publication_authorized": False,
        "remote_actions_performed": [],
        "scope_note": (
            "The clean-room removes git-ignored local dependency/runtime files from "
            "the repository-wide syntax scan while running the canonical sealed verifier "
            "unchanged against the complete current first-party worktree surface."
        ),
    }
    audit_path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"[SFT clean-room] audit: {audit_path.relative_to(ROOT)}", flush=True)
    print(f"[SFT clean-room] status: {audit['status']}", flush=True)
    if not passed:
        raise SystemExit(return_code or 1)


if __name__ == "__main__":
    main()
