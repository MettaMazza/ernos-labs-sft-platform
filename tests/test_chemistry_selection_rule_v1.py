from pathlib import Path
from types import SimpleNamespace

import pytest

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.selection_rule_batch_v1 import SELECTION_RULE_SPEC
from sft.chemistry.selection_rule_law_v1 import CLOSED, DIRECT, MEDIATED, classify_observation, direct_observation_allowed, signature
from sft.chemistry.selection_rule_validation_v1 import SelectionRuleValidator
from sft.engine.exact import InadmissibleExactValue
from sft.engine.source import build_source_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_direct_fold_observation_retains_and_changes_forced_distinctions():
    assert direct_observation_allowed(signature("G", 1, "g", "Σ"), signature("C", 1, "u", "Π"))
    assert not direct_observation_allowed(signature("G", 1, "g", "Σ"), signature("C", 3, "u", "Π"))
    assert not direct_observation_allowed(signature("G", 1, "g", "Σ"), signature("C", 1, "g", "Π"))


def test_nonadjacent_axis_observation_requires_retained_mediator():
    first, second = signature("J", 1, "g", "Δ"), signature("B", 1, "u", "Σ")
    with pytest.raises(InadmissibleExactValue):
        classify_observation(first, second, "erased-mediator")
    assert classify_observation(first, second, "retained", mediator="uncoupling").observation_class == MEDIATED


def test_absence_is_closed_emptyone_class():
    assert classify_observation(signature("X", 1, "g", "Σ"), None, "closed", observed=False).observation_class == CLOSED


def test_forced_candidate_census_is_unique_and_depth_independent():
    files = (ROOT / "sft/chemistry/selection_rule_law_v1.py",)
    program = GeneratedObservationalChemistryProgram(SELECTION_RULE_SPEC, build_source_manifest(ROOT, files).manifest_hash)
    census = program.generate_candidates()
    decisions = tuple(program.decide_candidate(row) for row in census.candidates)
    closure = program.closure_evidence(decisions)
    assert len(census.candidates) == 256
    assert sum(row.survives for row in decisions) == 1
    assert closure.scope.value == "depth_independent"


def test_complete_external_selection_surface_passes_after_seal():
    result = SelectionRuleValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:" + "e" * 64))
    assert result.passed
    assert result.all_rows_preserved
    assert len(result.measurements) == 75
