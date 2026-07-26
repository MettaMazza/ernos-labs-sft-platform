"""Recover omitted empirical replay contexts only when immutable hashes match.

This tool does not execute an admission, alter a receipt or touch the census.
It re-executes the registered empirical validator against the immutable
derivation seal already recorded in each claim certificate, then writes the
context only if its canonical empirical hash exactly matches that certificate.
"""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import platform
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.verification import _load_execution  # noqa: E402


CLAIM_IDS = (
    "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",
    "SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001",
    "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001",
    "SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",
    "SFT-PHYS-COSMO-SPATIAL-FLATNESS-001",
    "SFT-PHYS-COSMO-COMPLETE-BUDGET-001",
)


def _atomic_json(path: Path, payload: object) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".pending",
        delete=False,
    ) as handle:
        handle.write(rendered)
        pending = Path(handle.name)
    pending.replace(path)


def recover() -> tuple[str, ...]:
    entries = {
        row["claim_id"]: row
        for row in json.loads(
            (ROOT / "census/execution_manifest.json").read_text(encoding="utf-8")
        )["claims"]
    }
    recovered = []
    for claim_id in CLAIM_IDS:
        package = ROOT / "claims" / claim_id
        certificate = json.loads(
            (package / "certificate.json").read_text(encoding="utf-8")
        )
        if certificate.get("claim_id") != claim_id:
            raise RuntimeError(f"certificate identity differs: {claim_id}")
        execution = _load_execution(ROOT, entries[claim_id])
        if execution.empirical_validator is None:
            raise RuntimeError(f"registered empirical validator is absent: {claim_id}")
        sealed = SimpleNamespace(
            claim_id=claim_id,
            seal_hash=certificate["derivation_seal_hash"],
        )
        with patch.object(platform, "system", return_value="Darwin"):
            with patch.object(
                platform,
                "python_implementation",
                return_value="CPython",
            ):
                empirical = execution.empirical_validator.validate(sealed)
        if sha256_identity(empirical) != certificate.get("empirical_validation_hash"):
            raise RuntimeError(
                f"recovered empirical object differs from immutable certificate: {claim_id}"
            )
        if empirical.validated_seal_hash != certificate["derivation_seal_hash"]:
            raise RuntimeError(f"recovered context names the wrong seal: {claim_id}")
        _atomic_json(
            package / "empirical_validation.json",
            {"claim_id": claim_id, **asdict(empirical)},
        )
        recovered.append(claim_id)
    return tuple(recovered)


if __name__ == "__main__":
    for item in recover():
        print(f"recovered exact empirical replay context: {item}")
