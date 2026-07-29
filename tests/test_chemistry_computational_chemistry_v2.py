"""Post-admission checks for the preserved COMP v2 retry path."""

import importlib.util
import json
from pathlib import Path

import pytest

from sft.chemistry.computational_chemistry_batch_v1 import SPECS
from sft.chemistry.computational_chemistry_validation_v1 import exact_analysis


ROOT = Path(__file__).resolve().parents[1]
IDS = tuple(f"comp-v2-{number:03d}" for number in range(1, 15))


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_receipt_and_certificate_are_model_admitted(claim):
    certificate = json.loads((ROOT / "claims" / claim.claim_id / "certificate.json").read_text())
    receipt = json.loads((ROOT / certificate["engine_receipt_path"]).read_text())
    assert receipt["model_admitted"] is True
    assert receipt["receipt_hash"] == certificate["engine_receipt_hash"]
    assert certificate["candidate_count"] == 256
    assert certificate["unique_survivor_count"] == 1


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_manifest_points_to_the_admitted_v2_source(claim):
    manifest = json.loads((ROOT / "census/execution_manifest.json").read_text())["claims"]
    row = next(item for item in manifest if item["claim_id"] == claim.claim_id)
    assert row["execution_file"] == f"claims/{claim.claim_id}/execution_v2.py"
    path = ROOT / row["execution_file"]
    module_spec = importlib.util.spec_from_file_location("post_admit_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    execution = module.build_execution(ROOT)
    certificate = json.loads((ROOT / "claims" / claim.claim_id / "certificate.json").read_text())
    assert execution.program.registration.source_hash == certificate["source_manifest_hash"]


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_complete_postseal_surface_still_reconstructs(claim):
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    assert len(checks) == 8 and all(checks.values())
    assert analysis["complete_family_source_count"] == 59
    assert analysis["complete_family_source_bytes"] == 444644830


@pytest.mark.parametrize("claim", SPECS, ids=IDS)
def test_v2_execution_still_has_one_survivor_and_all_controls(claim):
    path = ROOT / "claims" / claim.claim_id / "execution_v2.py"
    module_spec = importlib.util.spec_from_file_location("v2_candidate_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    execution = module.build_execution(ROOT); census = execution.program.generate_candidates()
    assert len(census.candidates) == 256
    assert sum(execution.program.decide_candidate(candidate).survives for candidate in census.candidates) == 1
    assert all(control.passed for control in execution.program.run_controls())
