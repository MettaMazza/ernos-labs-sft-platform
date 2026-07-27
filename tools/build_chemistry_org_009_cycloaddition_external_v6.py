#!/usr/bin/env python3
"""Open and compare every sealed ORG-009 V6 cycloaddition product vector."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from select_chemistry_org_009_localmapper_sources_v5 import Graph, UnsupportedSmiles, parse_component


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/remapped_USPTO_FULL.csv"
SELECTION = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-source-selection-v6.json"
SELECTION_SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_cycloaddition_source_selection_v6.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_product_v6.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/cycloaddition-product-comparison-v6.json"
EXPECTED = {
    SOURCE: "sha256:7395b05af9d7e22189ac4f04498051226dde4b126d57f1ce56ff8819c2cbb63a",
    SELECTION: "sha256:c3638fdb2a27d96d548e39ef5c5fd4e1a78381907b0e133e3af7be301d2cfc94",
    SELECTION_SEAL: "sha256:622b3e7c0228bb03c7d86de92ff6167056bce21f4ade78d0bfc46514a24dbb94",
    PREDICTION: "sha256:df33eb9572c08af0a88824c221889a8f8ea4399a77223f48a36cf41ae49f3895",
}
ORDER = {"single": 1, "double": 2, "triple": 3, "aromatic": "aromatic"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def pair(left: int, right: int) -> tuple[int, int]:
    return tuple(sorted((left, right)))


def mapped_graph_record(graphs: list[Graph]) -> tuple[list[int], dict[tuple[int, int], int | str]]:
    maps = []
    adjacency: dict[tuple[int, int], int | str] = {}
    for graph in graphs:
        for atom in graph.atoms:
            if atom.element != "H":
                if atom.atom_map is None:
                    raise UnsupportedSmiles("unmapped product heavy atom")
                maps.append(atom.atom_map)
        for bond in graph.bonds:
            left = graph.atoms[bond.left].atom_map
            right = graph.atoms[bond.right].atom_map
            if left is None or right is None:
                raise UnsupportedSmiles("unmapped product adjacency")
            key = pair(left, right)
            if key in adjacency:
                raise UnsupportedSmiles("duplicate mapped product adjacency")
            adjacency[key] = ORDER[bond.order]
    if len(set(maps)) != len(maps):
        raise UnsupportedSmiles("duplicate product atom map")
    return sorted(maps), adjacency


def source_adjacency(selected: dict) -> tuple[list[int], dict[tuple[int, int], int | str]]:
    graphs = []
    for name in ("diene_graph", "alkene_graph"):
        row = selected[name]
        atoms_by_ordinal = {atom["ordinal"]: atom for atom in row["atoms"]}
        maps = [atom["atom_map"] for atom in row["atoms"] if atom["element"] != "H"]
        adjacency = {}
        for bond in row["bonds"]:
            left = atoms_by_ordinal[bond["left_ordinal"]]["atom_map"]
            right = atoms_by_ordinal[bond["right_ordinal"]]["atom_map"]
            adjacency[pair(left, right)] = ORDER[bond["order"]]
        graphs.append((maps, adjacency))
    return sorted(graphs[0][0] + graphs[1][0]), {**graphs[0][1], **graphs[1][1]}


def expected_adjacency(selected: dict, source_edges: dict[tuple[int, int], int | str], orientation: list[list[int]]) -> dict[tuple[int, int], int | str]:
    expected = dict(source_edges)
    outer = selected["diene_outer_atom_maps"]
    inner = selected["diene_inner_atom_maps"]
    alkene = selected["alkene_atom_maps"]
    expected[pair(outer[0], inner[0])] = 1
    expected[pair(inner[0], inner[1])] = 2
    expected[pair(inner[1], outer[1])] = 1
    expected[pair(alkene[0], alkene[1])] = 1
    for left, right in orientation:
        expected[pair(left, right)] = 1
    return expected


def compare_product(selected: dict, product: str) -> dict:
    product_components = product.split(".") if product else []
    try:
        product_graphs = [parse_component(component) for component in product_components]
        product_maps, product_edges = mapped_graph_record(product_graphs)
    except (UnsupportedSmiles, KeyError, ValueError) as error:
        return {
            "status": "unresolved",
            "product": product,
            "product_component_count": len(product_components),
            "reason": str(error),
        }
    source_maps, source_edges = source_adjacency(selected)
    orientation_results = []
    for ordinal, orientation in enumerate(selected["generated_cross_adjacency_orientations"], start=1):
        expected = expected_adjacency(selected, source_edges, orientation)
        orientation_results.append(
            {
                "orientation_ordinal": ordinal,
                "generated_cross_adjacencies": orientation,
                "exact_complete_adjacency_match": product_edges == expected,
            }
        )
    new_edges = sorted([list(key) for key in product_edges if key not in source_edges])
    removed_edges = sorted([list(key) for key in source_edges if key not in product_edges])
    changed_orders = sorted(
        [
            {"atom_maps": list(key), "source_order": source_edges[key], "product_order": product_edges[key]}
            for key in source_edges.keys() & product_edges.keys()
            if source_edges[key] != product_edges[key]
        ],
        key=lambda row: row["atom_maps"],
    )
    checks = {
        "one_product_component": len(product_components) == 1,
        "exact_mapped_atom_inventory": product_maps == source_maps,
        "exact_two_new_cross_component_adjacencies": len(new_edges) == 2 and any(row["exact_complete_adjacency_match"] for row in orientation_results),
        "one_complete_generated_orientation_matches": sum(row["exact_complete_adjacency_match"] for row in orientation_results) == 1,
        "no_unpredicted_removed_adjacency": not removed_edges,
    }
    return {
        "status": "favorable" if all(checks.values()) else "adverse",
        "product": product,
        "product_component_count": len(product_components),
        "source_map_count": len(source_maps),
        "product_map_count": len(product_maps),
        "new_adjacencies": new_edges,
        "removed_adjacencies": removed_edges,
        "changed_multiplicities": changed_orders,
        "orientation_results": orientation_results,
        "checks": checks,
    }


def main() -> None:
    for path, expected in EXPECTED.items():
        observed = sha256_file(path)
        if observed != expected:
            raise SystemExit(f"ORG-009 V6 frozen product-comparison input changed: {path}: {observed}")
    if OUTPUT.exists():
        raise SystemExit("ORG-009 V6 product comparison already exists; replay prohibited")
    selected_payload = json.loads(SELECTION.read_text(encoding="utf-8"))
    selected = {row["source_row_ordinal"]: row for row in selected_payload["selected_sources_in_original_order"]}
    results = []
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        for ordinal, row in enumerate(reader, start=1):
            if ordinal not in selected:
                continue
            reaction = row["mapped_rxn"]
            parts = reaction.split(">")
            if len(parts) != 3:
                comparison = {"status": "malformed", "reason": "reaction field does not have three sections"}
                product = ""
            else:
                product = parts[2]
                comparison = compare_product(selected[ordinal], product)
            results.append(
                {
                    "source_row_ordinal": ordinal,
                    "external_confident_inscription": row["confident"],
                    "source_selection": selected[ordinal],
                    "comparison": comparison,
                }
            )
    if len(results) != len(selected) or len(selected) != 47:
        raise SystemExit("ORG-009 V6 complete selected product census was not preserved")
    counts = {status: sum(row["comparison"]["status"] == status for row in results) for status in ("favorable", "adverse", "unresolved", "malformed")}
    output = {
        "schema": "sft-v3-chemistry-org-009-cycloaddition-product-comparison/6",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "source_snapshot_sha256": EXPECTED[SOURCE],
        "source_selection_sha256": EXPECTED[SELECTION],
        "source_selection_seal_sha256": EXPECTED[SELECTION_SEAL],
        "prediction_seal_sha256": EXPECTED[PREDICTION],
        "comparison_program_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "comparison_program_sha256": sha256_file(Path(__file__).resolve()),
        "complete_selected_product_count": len(results),
        "status_counts": counts,
        "no_selected_row_omitted": len(results) == 47,
        "no_post_outcome_filter_applied": True,
        "results_in_original_source_order": results,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "output_sha256": sha256_file(OUTPUT), "complete_selected_product_count": len(results), "status_counts": counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
