import json
from pathlib import Path

from sft.chemistry.hand_001_006_external_v2 import check, load_surface
from sft.chemistry.hand_001_006_laws_v2 import IDS, REGISTRY, SPECS

ROOT = Path(__file__).resolve().parents[1]


def test_complete_whole_family_specs():
    assert len(IDS) == len(SPECS) == 6
    for claim_id in IDS:
        SPECS[claim_id].validate()


def test_value_free_registry_is_complete_and_root_traced():
    assert REGISTRY["target_content_present"] is False
    assert REGISTRY["base_claim_count"] == REGISTRY["unique_owner_count"] == REGISTRY["root_reachable_claim_count"] == 1484
    assert REGISTRY["dependency_edge_count"] == 25013
    assert REGISTRY["cross_branch_dependency_edge_count"] == 18553


def test_all_paired_and_graph_surfaces_reconstruct():
    for claim_id in IDS:
        registry, vector, summaries, sources = check(ROOT, SPECS[claim_id])
        assert summaries and sources
        assert vector["all_selected_external_rows_preserved"] is True
        assert registry["registry_identity"] == vector["registry_identity"]


def test_frozen_vector_counts_and_failed_route_preserved():
    _, vector = load_surface(ROOT)
    assert vector["paired_record_count"] == 17
    assert vector["source_identity_occurrence_count"] == 31
    assert vector["measurement_line_count"] == 53
    halt = json.loads((ROOT / "audits/CHEMISTRY_HAND_001_006_CENSUS_GRAPH_HALT_2026-07-29.json").read_text())
    assert halt["admission_credit"] == 0 and halt["scientific_result_retired"] is False
