"""Focused checks for the complete computation correspondence return family."""

from __future__ import annotations

import json
from pathlib import Path

from sft.computation.correspondence_return_laws import (
    CONDITIONAL_TRANSLATION,
    changed_encoding_rejects,
    transport_holds,
)
from sft.computation.generated_law import GeneratedComputationProgram, candidate_records, survivor_id


ROOT = Path(__file__).resolve().parents[1]


def test_whole_subcategory_boundary_is_frozen_at_four_obligations() -> None:
    boundary = json.loads((ROOT / "audits/COMPUTATION_CORRESPONDENCE_WHOLE_SUBCATEGORY_BOUNDARY_2026-07-28.json").read_text(encoding="utf-8"))
    assert boundary["subcategory_id"] == "COMP-CORRESPONDENCE"
    assert boundary["obligation_count"] == len(boundary["obligations"]) == 4
    assert boundary["engine_edit_authorized"] is False
    assert boundary["verification_authority_edit_authorized"] is False


def test_translation_candidate_product_has_one_survivor() -> None:
    records = candidate_records(CONDITIONAL_TRANSLATION)
    assert len(records) == len({row["candidate_id"] for row in records}) == 256
    program = GeneratedComputationProgram(CONDITIONAL_TRANSLATION, "sha256:" + "a" * 64)
    census = program.generate_candidates()
    decisions = tuple(program.decide_candidate(candidate) for candidate in census.candidates)
    assert sum(decision.survives for decision in decisions) == 1
    assert next(decision.candidate_id for decision in decisions if decision.survives) == survivor_id(CONDITIONAL_TRANSLATION)
    assert all(control.passed for control in program.run_controls())


def test_complete_external_family_transports_through_depth_seven() -> None:
    assert transport_holds(7)


def test_depth_successor_executes_through_fourteen() -> None:
    assert transport_holds(14)


def test_changed_encoding_is_adverse() -> None:
    assert changed_encoding_rejects()
