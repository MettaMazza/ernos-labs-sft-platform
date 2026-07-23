"""Hostile-package controls for empirical prediction and authority artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Mapping

from sft.engine.canonical import sha256_identity
from sft.engine.fold_language import FoldLanguageHalt, FoldProgram, fold_program_from_mapping


class HostilePackageHalt(RuntimeError):
    """Raised when an empirical package can execute code or mutate authority."""


@dataclass(frozen=True)
class PackageAuditCertificate:
    auditor_id: str
    package_hash: str
    program_hash: str
    executable_source_present: bool
    additional_fields_present: bool
    protected_tree_unchanged: bool
    passed: bool
    certificate_hash: str


@dataclass(frozen=True)
class ProtectedTreeSnapshot:
    root_identity: str
    file_hashes: tuple[tuple[str, str], ...]
    snapshot_hash: str


class HostilePackageAuditor:
    """Accept data-only Fold programs and reject contributor execution hooks."""

    auditor_id = "sft-v3-hostile-empirical-package-auditor/1"

    def audit_program_document(
        self,
        document: Mapping[str, object],
        before: ProtectedTreeSnapshot,
        after: ProtectedTreeSnapshot,
    ) -> tuple[FoldProgram, PackageAuditCertificate]:
        executable_source_present = any(
            key in document for key in ("python", "source", "script", "command", "module", "callable")
        )
        additional_fields_present = set(document) != {"schema", "program_id", "instructions"}
        program: FoldProgram
        try:
            program = fold_program_from_mapping(document)
        except FoldLanguageHalt as exc:
            raise HostilePackageHalt(str(exc)) from exc
        protected_tree_unchanged = before == after
        passed = not executable_source_present and not additional_fields_present and protected_tree_unchanged
        payload = {
            "auditor_id": self.auditor_id,
            "package_hash": sha256_identity(document),
            "program_hash": sha256_identity(program),
            "executable_source_present": executable_source_present,
            "additional_fields_present": additional_fields_present,
            "protected_tree_unchanged": protected_tree_unchanged,
            "passed": passed,
        }
        certificate = PackageAuditCertificate(certificate_hash=sha256_identity(payload), **payload)
        if not passed:
            raise HostilePackageHalt("empirical package failed data-only or protected-tree audit")
        return program, certificate

    @staticmethod
    def reject_executable_prediction_source(source: str) -> None:
        if not isinstance(source, str) or not source.strip():
            raise HostilePackageHalt("prediction source is missing")
        raise HostilePackageHalt(
            "official empirical predictions accept data-only Fold programs, not executable contributor source"
        )


def snapshot_protected_tree(root: Path) -> ProtectedTreeSnapshot:
    """Hash the only repository trees that can project scientific authority."""

    resolved = root.resolve()
    rows: list[tuple[str, str]] = []
    for relative in ("census", "receipts/engine/model_admitted"):
        directory = resolved / relative
        if not directory.is_dir():
            raise HostilePackageHalt(f"protected authority directory is missing: {relative}")
        for path in sorted(item for item in directory.rglob("*") if item.is_file()):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append((path.relative_to(resolved).as_posix(), "sha256:" + digest))
    row_tuple = tuple(rows)
    payload = {"root_identity": resolved.name, "file_hashes": row_tuple}
    return ProtectedTreeSnapshot(
        root_identity=resolved.name,
        file_hashes=row_tuple,
        snapshot_hash=sha256_identity(payload),
    )
