"""Read-only explorer and independent replay for every registered Mathematics law.

This deliberately does not issue admission receipts.  It exposes calculator
users to the same declared grammar, dependencies, witnesses, survivor and
retained official receipt that the frozen engine uses, while clearly labelling
the local replay as a replay rather than a new admission.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from sft.mathematics.catalog import SPECS
from sft.mathematics.generated_law import candidate_records, survivor_id


@dataclass(frozen=True)
class MathematicsLawSummary:
    claim_id: str
    title: str
    statement: str
    dependencies: tuple[str, ...]
    grammar_boundary: str
    exact_result: str
    laws: tuple[str, ...]
    limitations: str
    candidate_count: int
    receipt_hash: str | None
    model_admitted: bool


@dataclass(frozen=True)
class MathematicsLawReplay:
    kind: str
    claim_id: str
    candidate_count: int
    eliminated_count: int
    survivor_id: str
    witness_results: tuple[tuple[str, bool], ...]
    dependency_chain: tuple[str, ...]
    official_receipt_hash: str | None
    locally_replayed: bool
    engine_admission_issued: bool

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True) + "\n"


class RegisteredMathematicsExplorer:
    def __init__(self, root: Path | None = None):
        self.root = root or Path(__file__).resolve().parents[3]
        self._specs = {spec.claim_id: spec for spec in SPECS}
        self._census = self._load_census()

    def _load_census(self) -> dict[str, dict[str, object]]:
        path = self.root / "census" / "claims.json"
        if not path.exists():
            return {}
        document = json.loads(path.read_text(encoding="utf-8"))
        return {row["claim_id"]: row for row in document["claims"]}

    def claim_ids(self) -> tuple[str, ...]:
        return tuple(self._specs)

    def _spec(self, claim_id: str):
        if claim_id not in self._specs:
            raise KeyError(f"unknown registered Mathematics claim {claim_id!r}")
        return self._specs[claim_id]

    def summary(self, claim_id: str) -> MathematicsLawSummary:
        spec = self._spec(claim_id)
        row = self._census.get(claim_id, {})
        count = 1
        for dimension in spec.dimensions:
            count *= len(dimension.choices)
        return MathematicsLawSummary(
            spec.claim_id,
            spec.title,
            spec.statement,
            spec.dependencies,
            spec.grammar_boundary,
            spec.exact_result,
            spec.laws,
            spec.limitations,
            count,
            row.get("receipt_hash"),
            bool(row.get("model_admitted", False)),
        )

    def summaries(self) -> tuple[MathematicsLawSummary, ...]:
        return tuple(self.summary(claim_id) for claim_id in self.claim_ids())

    def dependency_chain(self, claim_id: str) -> tuple[str, ...]:
        ordered: list[str] = []
        visited: set[str] = set()

        def visit(current: str) -> None:
            if current in visited:
                return
            visited.add(current)
            registration = self.root / "claims" / current / "registration.json"
            if registration.exists():
                payload = json.loads(registration.read_text(encoding="utf-8"))
                for dependency in payload.get("dependencies", ()):  # exact registered order
                    visit(dependency)
            elif current in self._specs:
                for dependency in self._specs[current].dependencies:
                    visit(dependency)
            ordered.append(current)

        visit(claim_id)
        return tuple(ordered)

    def replay(self, claim_id: str) -> MathematicsLawReplay:
        spec = self._spec(claim_id)
        records = candidate_records(spec)
        survivor = survivor_id(spec)
        survivors = tuple(row for row in records if row["candidate_id"] == survivor)
        witnesses = tuple((item.name, item.passed) for item in spec.witnesses)
        locally_replayed = len(survivors) == 1 and all(passed for _, passed in witnesses)
        row = self._census.get(claim_id, {})
        return MathematicsLawReplay(
            "calculator_law_replay_not_engine_admission",
            claim_id,
            len(records),
            len(records) - len(survivors),
            survivor,
            witnesses,
            self.dependency_chain(claim_id),
            row.get("receipt_hash"),
            locally_replayed,
            False,
        )


__all__ = (
    "MathematicsLawReplay",
    "MathematicsLawSummary",
    "RegisteredMathematicsExplorer",
)
