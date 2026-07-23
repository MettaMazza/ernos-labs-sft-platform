"""Bind engine registrations to the exact source files loaded by an official run."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sft.engine.canonical import sha256_identity


@dataclass(frozen=True)
class SourceArtifact:
    path: str
    content_hash: str


@dataclass(frozen=True)
class SourceManifest:
    artifacts: tuple[SourceArtifact, ...]
    manifest_hash: str


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def build_source_manifest(root: Path, paths: Iterable[Path]) -> SourceManifest:
    root = root.resolve()
    resolved = sorted({path.resolve() for path in paths}, key=str)
    if not resolved:
        raise ValueError("official source manifest cannot be empty")
    artifacts = []
    for path in resolved:
        if not path.is_file():
            raise ValueError(f"source artifact is not a file: {path}")
        try:
            relative = path.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"source artifact lies outside the official repository: {path}") from exc
        artifacts.append(SourceArtifact(relative.as_posix(), hash_file(path)))
    artifact_tuple = tuple(artifacts)
    return SourceManifest(artifact_tuple, sha256_identity(artifact_tuple))
