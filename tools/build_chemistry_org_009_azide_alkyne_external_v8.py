#!/usr/bin/env python3
"""Open and compare all 93 sealed ORG-009 V8 azide-alkyne product vectors."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from select_chemistry_org_009_localmapper_sources_v5 import Graph, UnsupportedSmiles, parse_component


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/remapped_USPTO_FULL.csv"
SELECTION = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/azide-alkyne-source-selection-v8.json"
SELECTION_SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_azide_alkyne_source_selection_v8.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_product_v8.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/azide-alkyne-product-comparison-v8.json"
EXPECTED = {
    SOURCE: "sha256:7395b05af9d7e22189ac4f04498051226dde4b126d57f1ce56ff8819c2cbb63a",
    SELECTION: "sha256:3aae41be4a76102deef0a379c5768cb6b6a3867c5ff7182372242410a922359f",
    SELECTION_SEAL: "sha256:d7653d509d093d22989ae3fd41678cb5fb712bd9c3b930579010714b91494e64",
    PREDICTION: "sha256:b4fc02b305856c8d3efe88a96bfb637b607417e904459957c19e836e935a5571",
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


def external_graph(graphs: list[Graph]) -> tuple[list[int], dict[tuple[int, int], int | str]]:
    maps = []
    adjacency = {}
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


def source_graph(selected: dict) -> tuple[list[int], dict[tuple[int, int], int | str]]:
    maps = []
    adjacency = {}
    for name in ("azide_graph", "alkyne_graph"):
        record = selected[name]
        atoms = {row["ordinal"]: row for row in record["atoms"]}
        maps.extend(row["atom_map"] for row in record["atoms"] if row["element"] != "H")
        for bond in record["bonds"]:
            left = atoms[bond["left_ordinal"]]["atom_map"]
            right = atoms[bond["right_ordinal"]]["atom_map"]
            adjacency[pair(left, right)] = ORDER[bond["order"]]
    return sorted(maps), adjacency


def compare(selected: dict, product: str) -> dict:
    components = product.split(".") if product else []
    try:
        product_maps, product_edges = external_graph([parse_component(component) for component in components])
    except (UnsupportedSmiles, KeyError, ValueError) as error:
        return {"status": "unresolved", "product": product, "reason": str(error), "product_component_count": len(components)}
    source_maps, source_edges = source_graph(selected)
    orientation_rows = []
    for ordinal, orientation in enumerate(selected["generated_cross_adjacency_orientations"], start=1):
        expected_keys = set(source_edges) | {pair(left, right) for left, right in orientation}
        orientation_rows.append({
            "orientation_ordinal": ordinal,
            "generated_cross_adjacencies": orientation,
            "exact_complete_adjacency_match": set(product_edges) == expected_keys,
        })
    new_edges = sorted([list(key) for key in product_edges if key not in source_edges])
    removed_edges = sorted([list(key) for key in source_edges if key not in product_edges])
    changed = sorted(
        [
            {"atom_maps": list(key), "source_order": source_edges[key], "product_order": product_edges[key]}
            for key in source_edges.keys() & product_edges.keys()
            if source_edges[key] != product_edges[key]
        ],
        key=lambda row: row["atom_maps"],
    )
    checks = {
        "one_product_component": len(components) == 1,
        "exact_mapped_atom_inventory": product_maps == source_maps,
        "every_source_adjacency_retained": not removed_edges,
        "exact_two_new_cross_component_adjacencies": len(new_edges) == 2,
        "one_complete_generated_orientation_matches": sum(row["exact_complete_adjacency_match"] for row in orientation_rows) == 1,
        "positive_finite_source_multiplicity_change": bool(changed),
    }
    return {
        "status": "favorable" if all(checks.values()) else "adverse",
        "product": product,
        "product_component_count": len(components),
        "source_map_count": len(source_maps),
        "product_map_count": len(product_maps),
        "new_adjacencies": new_edges,
        "removed_adjacencies": removed_edges,
        "changed_multiplicities": changed,
        "orientation_results": orientation_rows,
        "checks": checks,
    }


def main() -> None:
    for path, expected in EXPECTED.items():
        if sha256_file(path) != expected:
            raise SystemExit(f"ORG-009 V8 frozen product input changed: {path}")
    if OUTPUT.exists():
        raise SystemExit("ORG-009 V8 product comparison already exists; replay prohibited")
    selected_rows = json.loads(SELECTION.read_text(encoding="utf-8"))["selected_sources_in_original_order"]
    selected = {row["source_row_ordinal"]: row for row in selected_rows}
    results = []
    with SOURCE.open(newline="", encoding="utf-8") as stream:
        for ordinal, row in enumerate(csv.DictReader(stream), start=1):
            if ordinal not in selected:
                continue
            parts = row["mapped_rxn"].split(">")
            if len(parts) != 3:
                comparison = {"status": "malformed", "reason": "reaction field does not have three sections"}
            else:
                comparison = compare(selected[ordinal], parts[2])
            results.append({
                "source_row_ordinal": ordinal,
                "external_confident_inscription": row["confident"],
                "source_selection": selected[ordinal],
                "comparison": comparison,
            })
    if len(results) != len(selected) or len(selected) != 93:
        raise SystemExit("ORG-009 V8 complete product census was not preserved")
    counts = {status: sum(row["comparison"]["status"] == status for row in results) for status in ("favorable", "adverse", "unresolved", "malformed")}
    output = {
        "schema": "sft-v3-chemistry-org-009-azide-alkyne-product-comparison/8",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "source_snapshot_sha256": EXPECTED[SOURCE],
        "source_selection_sha256": EXPECTED[SELECTION],
        "source_selection_seal_sha256": EXPECTED[SELECTION_SEAL],
        "prediction_seal_sha256": EXPECTED[PREDICTION],
        "comparison_program_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "comparison_program_sha256": sha256_file(Path(__file__).resolve()),
        "complete_selected_product_count": len(results),
        "status_counts": counts,
        "no_selected_row_omitted": len(results) == 93,
        "no_post_outcome_filter_applied": True,
        "aromatic_and_kekule_orders_preserved_as_external_inscriptions": True,
        "results_in_original_source_order": results,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "output_sha256": sha256_file(OUTPUT), "complete_selected_product_count": len(results), "status_counts": counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
