"""Repository coordinator: preserve every receipt and admit only closed results."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Optional

from sft.engine.authority import AuthorityLedger
from sft.engine.engine import SFTAdmissionEngine
from sft.engine.errors import EngineHalt
from sft.engine.model import DerivationProgram, EmpiricalValidator, EngineReceipt, IndependentValidator
from sft.engine.receipt_io import read_receipt, write_receipt
from sft.engine.source import build_source_manifest


class CensusAdmissionError(RuntimeError):
    """Raised when a receipt cannot lawfully alter the model census."""


class EngineRepository:
    """Make engine receipts the sole write path into the v3 model census."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.census_path = self.root / "census" / "claims.json"
        if not self.census_path.is_file():
            raise CensusAdmissionError("repository has no claim census")
        self.authority = self._load_authority()
        self.engine = SFTAdmissionEngine(self.authority)

    def execute(
        self,
        program: DerivationProgram,
        independent_validator: IndependentValidator,
        empirical_validator: Optional[EmpiricalValidator] = None,
    ) -> EngineReceipt:
        return self._execute(program, independent_validator, empirical_validator, None)

    def execute_official(
        self,
        program: DerivationProgram,
        independent_validator: IndependentValidator,
        source_files: tuple[Path, ...],
        empirical_validator: Optional[EmpiricalValidator] = None,
    ) -> EngineReceipt:
        manifest = build_source_manifest(self.root, source_files)
        return self._execute(
            program,
            independent_validator,
            empirical_validator,
            manifest.manifest_hash,
        )

    def _execute(
        self,
        program: DerivationProgram,
        independent_validator: IndependentValidator,
        empirical_validator: Optional[EmpiricalValidator],
        executed_source_hash: Optional[str],
    ) -> EngineReceipt:
        claim_id = program.registration.claim_id
        try:
            receipt = self.engine.run(
                program,
                independent_validator,
                empirical_validator,
                executed_source_hash=executed_source_hash,
            )
        except EngineHalt as halted:
            self._preserve("rejected", claim_id, halted.receipt)
            raise

        category = "model_admitted" if receipt.model_admitted else "conditional_evidence"
        relative_receipt = self._preserve(category, claim_id, receipt)
        if receipt.model_admitted:
            self._admit(program, receipt, relative_receipt)
            self.authority.admit(receipt)
        return receipt

    def _load_authority(self) -> AuthorityLedger:
        try:
            census = json.loads(self.census_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CensusAdmissionError("claim census cannot be loaded") from exc
        claims = census.get("claims")
        if not isinstance(claims, list):
            raise CensusAdmissionError("claim census is malformed")
        authority = AuthorityLedger()
        for row in claims:
            if not isinstance(row, dict):
                raise CensusAdmissionError("claim census contains a malformed row")
            relative = row.get("receipt_path")
            if not isinstance(relative, str):
                raise CensusAdmissionError("claim census row lacks a receipt path")
            receipt_path = (self.root / relative).resolve()
            try:
                receipt_path.relative_to(self.root)
            except ValueError as exc:
                raise CensusAdmissionError("claim census receipt escapes the repository") from exc
            try:
                receipt = read_receipt(receipt_path)
                authority.admit(receipt)
            except (OSError, ValueError, TypeError) as exc:
                raise CensusAdmissionError(f"claim census receipt is invalid: {relative}") from exc
            if row.get("claim_id") != receipt.claim_id:
                raise CensusAdmissionError("claim census and receipt identities differ")
            if row.get("receipt_hash") != receipt.receipt_hash:
                raise CensusAdmissionError("claim census and receipt hashes differ")
        return authority

    def _preserve(self, category: str, claim_id: str, receipt: EngineReceipt) -> Path:
        safe_claim_id = "".join(
            character if character.isalnum() or character in "-_." else "_"
            for character in claim_id
        )
        short_hash = receipt.receipt_hash.removeprefix("sha256:")[:16]
        relative = Path("receipts") / "engine" / category / f"{safe_claim_id}-{short_hash}.json"
        write_receipt(self.root / relative, receipt)
        return relative

    def _admit(self, program: DerivationProgram, receipt: EngineReceipt, receipt_path: Path) -> None:
        if not receipt.accepted_evidence or not receipt.model_admitted:
            raise CensusAdmissionError("unclosed receipt cannot enter the model census")
        registration = program.registration
        if registration.claim_id != receipt.claim_id:
            raise CensusAdmissionError("registration and receipt claim identities differ")

        census = json.loads(self.census_path.read_text(encoding="utf-8"))
        claims = census.get("claims")
        if not isinstance(claims, list):
            raise CensusAdmissionError("claim census is malformed")

        existing = [item for item in claims if item.get("claim_id") == receipt.claim_id]
        if existing:
            if existing[0].get("receipt_hash") == receipt.receipt_hash:
                return
            raise CensusAdmissionError("claim already has a different admitted receipt")

        claims.append(
            {
                "claim_id": receipt.claim_id,
                "title": registration.title,
                "branch": registration.branch,
                "statement": registration.statement,
                "closure_status": receipt.closure_status,
                "external_status": receipt.external_status,
                "model_admitted": True,
                "receipt_path": receipt_path.as_posix(),
                "receipt_hash": receipt.receipt_hash,
            }
        )
        claims.sort(key=lambda item: item["claim_id"])
        self._atomic_json_write(self.census_path, census)

    @staticmethod
    def _atomic_json_write(path: Path, payload: object) -> None:
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
