"""Fail-closed verification of the canonical SFT admission-engine bytes.

This module is deliberately outside :mod:`sft.engine`.  It protects the frozen
authority boundary without changing a single engine byte or making a scientific
admission decision.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


ENGINE_SEAL_ID = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
ENGINE_GIT_TREE = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
SEAL_SCHEMA = "sft-v3-engine-seal/1"


class EngineSealHalt(RuntimeError):
    """Raised before engine import when the canonical byte seal is violated."""

    def __init__(self, violations: tuple[str, ...]):
        self.violations = violations
        super().__init__(
            "SFT ENGINE SEAL VIOLATION — VOID / INVALID / HALTED: "
            + "; ".join(violations)
        )


@dataclass(frozen=True)
class EngineSealAttestation:
    status: str
    seal_id: str
    engine_git_tree: str
    verified_file_count: int
    runtime_root: str
    violations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _canonical_identity(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _read_manifest(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = root / "governance" / "engine_seal_v1.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"canonical seal manifest cannot be read: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"canonical seal manifest is malformed: {exc}"]
    if not isinstance(payload, dict):
        return None, ["canonical seal manifest is not an object"]
    return payload, []


def verify_engine_seal(root: Path | None = None) -> EngineSealAttestation:
    """Hash actual runtime files and return a deterministic fail-closed result."""

    repository_root = (
        root.resolve()
        if root is not None
        else Path(__file__).resolve().parents[1]
    )
    manifest, violations = _read_manifest(repository_root)
    if manifest is None:
        return EngineSealAttestation(
            status="VOID_INVALID_HALTED",
            seal_id=ENGINE_SEAL_ID,
            engine_git_tree=ENGINE_GIT_TREE,
            verified_file_count=0,
            runtime_root=str(repository_root),
            violations=tuple(violations),
        )

    if manifest.get("schema") != SEAL_SCHEMA:
        violations.append("seal schema identity changed")
    if manifest.get("seal_id") != ENGINE_SEAL_ID:
        violations.append("published seal identity changed")
    if manifest.get("frozen_engine_git_tree") != ENGINE_GIT_TREE:
        violations.append("frozen Git tree identity changed")

    body = dict(manifest)
    body.pop("seal_id", None)
    if _canonical_identity(body) != ENGINE_SEAL_ID:
        violations.append("seal manifest contents do not match the canonical seal identity")

    rows = manifest.get("files")
    if not isinstance(rows, list):
        rows = []
        violations.append("seal manifest file support is malformed")

    expected: dict[str, tuple[str, int]] = {}
    for row in rows:
        if not isinstance(row, dict):
            violations.append("seal manifest contains a malformed file row")
            continue
        path = row.get("path")
        content_hash = row.get("sha256")
        byte_count = row.get("bytes")
        if not isinstance(path, str) or not path.startswith("sft/engine/"):
            violations.append("seal manifest contains an invalid engine path")
            continue
        if path in expected:
            violations.append(f"seal manifest repeats engine path: {path}")
            continue
        if not isinstance(content_hash, str) or not content_hash.startswith("sha256:"):
            violations.append(f"seal manifest has an invalid content identity: {path}")
            continue
        if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count < 1:
            violations.append(f"seal manifest has an invalid byte count: {path}")
            continue
        expected[path] = (content_hash, byte_count)

    declared_count = manifest.get("file_count")
    if declared_count != len(expected):
        violations.append("seal manifest file count differs from its exact support")

    engine_root = repository_root / "sft" / "engine"
    actual_paths: set[str] = set()
    if not engine_root.is_dir() or engine_root.is_symlink():
        violations.append("runtime engine boundary is missing or is a symbolic link")
    else:
        for path in sorted(engine_root.rglob("*")):
            relative_parts = path.relative_to(engine_root).parts
            if "__pycache__" in relative_parts or path.suffix in {".pyc", ".pyo"}:
                continue
            relative = path.relative_to(repository_root).as_posix()
            if path.is_symlink():
                violations.append(f"symbolic links are forbidden in the engine boundary: {relative}")
            elif path.is_file():
                actual_paths.add(relative)
            elif path.is_dir():
                continue
            else:
                violations.append(f"unsupported filesystem object in engine boundary: {relative}")

    missing = sorted(set(expected) - actual_paths)
    unexpected = sorted(actual_paths - set(expected))
    violations.extend(f"canonical engine file is missing: {path}" for path in missing)
    violations.extend(f"unexpected engine file is present: {path}" for path in unexpected)

    verified = 0
    for relative in sorted(set(expected).intersection(actual_paths)):
        path = repository_root / relative
        wanted_hash, wanted_bytes = expected[relative]
        try:
            actual_bytes = path.stat().st_size
            actual_hash = _sha256(path)
        except OSError as exc:
            violations.append(f"engine file cannot be read: {relative}: {exc}")
            continue
        if actual_bytes != wanted_bytes:
            violations.append(f"engine file byte count changed: {relative}")
        if actual_hash != wanted_hash:
            violations.append(f"engine file content changed: {relative}")
        if actual_bytes == wanted_bytes and actual_hash == wanted_hash:
            verified += 1

    return EngineSealAttestation(
        status="VALID_CANONICAL_ENGINE" if not violations else "VOID_INVALID_HALTED",
        seal_id=ENGINE_SEAL_ID,
        engine_git_tree=ENGINE_GIT_TREE,
        verified_file_count=verified,
        runtime_root=str(repository_root),
        violations=tuple(violations),
    )


def require_engine_seal(root: Path | None = None) -> EngineSealAttestation:
    """Return the attestation or halt before any engine code may execute."""

    attestation = verify_engine_seal(root)
    if attestation.violations:
        raise EngineSealHalt(attestation.violations)
    return attestation
