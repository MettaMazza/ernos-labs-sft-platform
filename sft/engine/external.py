"""Run an implementation-distinct validator as a separate process."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from sft.engine.canonical import canonical_value, sha256_identity
from sft.engine.model import ExternalValidation, SealedDerivation
from sft.engine.portable import portable_subprocess_environment
from sft.engine.source import build_source_manifest


class ExternalValidatorError(RuntimeError):
    """Raised when an external certificate process cannot be trusted or parsed."""


class ExternalCommandValidator:
    """Adapter for generated C or another independently implemented executable."""

    def __init__(
        self,
        validator_id: str,
        command: tuple[str, ...],
        implementation_root: Path,
        implementation_files: tuple[Path, ...],
        timeout_seconds: int = 120,
    ):
        if not validator_id.strip() or not command:
            raise ExternalValidatorError("external validator requires identity and command")
        self.validator_id = validator_id
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.manifest = build_source_manifest(implementation_root, implementation_files)

    def validate(self, sealed: SealedDerivation) -> ExternalValidation:
        with tempfile.TemporaryDirectory(prefix="sft-external-validator-") as temporary:
            input_path = Path(temporary) / "sealed_derivation.json"
            input_path.write_text(
                json.dumps(canonical_value(sealed), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                (*self.command, str(input_path)),
                cwd=temporary,
                env=portable_subprocess_environment(),
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
            if completed.returncode != 0:
                raise ExternalValidatorError(
                    f"external validator exited {completed.returncode}: {completed.stderr.strip()}"
                )
            try:
                response = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                raise ExternalValidatorError("external validator did not emit one JSON certificate") from exc
            required = {
                "validated_seal_hash",
                "recomputed_from_declared_inputs",
                "passed",
                "certificate",
            }
            missing = sorted(required.difference(response))
            if missing:
                raise ExternalValidatorError("external validator omitted fields: " + ", ".join(missing))
            return ExternalValidation(
                validator_id=self.validator_id,
                implementation_hash=self.manifest.manifest_hash,
                validated_seal_hash=response["validated_seal_hash"],
                certificate_hash=sha256_identity(response["certificate"]),
                recomputed_from_declared_inputs=response["recomputed_from_declared_inputs"] is True,
                passed=response["passed"] is True,
            )
