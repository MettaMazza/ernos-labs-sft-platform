#!/usr/bin/env python3
"""Seal independently labeled ORD azide-alkyne sources before product access."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
from ord_schema.proto import reaction_pb2

from select_chemistry_org_009_localmapper_sources_v5 import Graph, UnsupportedSmiles, graph_record, parse_component


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9"
INVENTORY = SNAPSHOT_ROOT / "source-inventory-v9.json"
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v9.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_ord_v9.json"
OUTPUT = SNAPSHOT_ROOT / "source-only-selection-v9.json"
SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_ord_source_selection_v9.json"
EXPECTED_INVENTORY = "sha256:a4fe3ee3452b423ae2fb41f1901767e6c6002604be73c7b75035fbeaf2a6dc03"
EXPECTED_IDENTITY = "sha256:763e26e4d60699e7af4ddffb71789b9535df2959259abfed8b29a67e650b7138"
EXPECTED_PREDICTION = "sha256:045b5a0960e729450a6b5d0670fe3d6337c6d066c97ede3e865550b12fdf98cc"
LABEL_TOKENS = ("click", "cuaac", "azide-alkyne", "azide alkyne", "cycloaddition", "triazole")
SMILES_TYPES = {reaction_pb2.CompoundIdentifier.SMILES, reaction_pb2.CompoundIdentifier.CXSMILES}


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def unique_three_nitrogen_path(graph: Graph) -> tuple[int, int, int] | None:
    adjacency: dict[int, set[int]] = defaultdict(set)
    for bond in graph.bonds:
        if graph.atoms[bond.left].element == "N" and graph.atoms[bond.right].element == "N":
            adjacency[bond.left].add(bond.right)
            adjacency[bond.right].add(bond.left)
    paths = []
    for middle, neighbors in adjacency.items():
        ordered = sorted(neighbors)
        for left_index in range(len(ordered)):
            for right_index in range(left_index + 1, len(ordered)):
                paths.append((ordered[left_index], middle, ordered[right_index]))
    return paths[0] if len(paths) == 1 else None


def unique_carbon_triple(graph: Graph):
    rows = [
        bond for bond in graph.bonds
        if bond.order == "triple"
        and graph.atoms[bond.left].element == "C"
        and graph.atoms[bond.right].element == "C"
        and not graph.atoms[bond.left].aromatic
        and not graph.atoms[bond.right].aromatic
    ]
    return rows[0] if len(rows) == 1 else None


def compound_smiles(compound) -> str | None:
    rows = [identifier.value for identifier in compound.identifiers if identifier.type in SMILES_TYPES and identifier.value]
    return rows[0] if len(rows) == 1 else None


def source_record(reaction) -> dict | None:
    reactants = []
    for input_row in reaction.inputs.values():
        for compound in input_row.components:
            if compound.reaction_role != reaction_pb2.ReactionRole.REACTANT:
                continue
            smiles = compound_smiles(compound)
            if smiles is None:
                return None
            if "." in smiles:
                return None
            try:
                graph = parse_component(smiles)
            except UnsupportedSmiles:
                return None
            reactants.append((smiles, graph))
    if len(reactants) != 2:
        return None
    azide_rows = [(index, unique_three_nitrogen_path(graph)) for index, (_, graph) in enumerate(reactants)]
    azide_rows = [(index, path) for index, path in azide_rows if path is not None]
    alkyne_rows = [(index, unique_carbon_triple(graph)) for index, (_, graph) in enumerate(reactants)]
    alkyne_rows = [(index, bond) for index, bond in alkyne_rows if bond is not None]
    pairs = [(azide, alkyne) for azide in azide_rows for alkyne in alkyne_rows if azide[0] != alkyne[0]]
    if len(pairs) != 1:
        return None
    (azide_index, path), (alkyne_index, triple) = pairs[0]
    azide_smiles, azide = reactants[azide_index]
    alkyne_smiles, alkyne = reactants[alkyne_index]
    return {
        "azide_reactant_ordinal": azide_index + 1,
        "alkyne_reactant_ordinal": alkyne_index + 1,
        "azide_smiles": azide_smiles,
        "alkyne_smiles": alkyne_smiles,
        "azide_outer_atom_ordinals": [path[0] + 1, path[2] + 1],
        "azide_middle_atom_ordinal": path[1] + 1,
        "alkyne_carbon_atom_ordinals": [triple.left + 1, triple.right + 1],
        "azide_graph": graph_record(azide),
        "alkyne_graph": graph_record(alkyne),
    }


def label_surfaces(reaction, dataset_name: str, dataset_description: str) -> tuple[list[str], list[str]]:
    surfaces = [dataset_name, dataset_description]
    surfaces.extend(identifier.value for identifier in reaction.identifiers if identifier.value)
    if reaction.HasField("notes") and reaction.notes.procedure_details:
        surfaces.append(reaction.notes.procedure_details)
    if reaction.HasField("provenance"):
        surfaces.extend(str(value) for value in reaction.provenance.reaction_metadata.values())
    lowered = "\n".join(surfaces).lower()
    matches = [token for token in LABEL_TOKENS if token in lowered]
    return matches, [sha256_bytes(surface.encode("utf-8")) for surface in surfaces if surface]


def main() -> None:
    if sha256_file(INVENTORY) != EXPECTED_INVENTORY or sha256_file(IDENTITY) != EXPECTED_IDENTITY or sha256_file(PREDICTION) != EXPECTED_PREDICTION:
        raise SystemExit("ORG-009 V9 frozen selection authority changed")
    if OUTPUT.exists() or SEAL.exists():
        raise SystemExit("ORG-009 V9 source selection already exists; replay prohibited")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    selected = []
    structural_unlabeled = []
    conventional_reaction_count = 0
    for source_ordinal, source in enumerate(inventory["rows"], start=1):
        path = ROOT / source["opened_snapshot_path"]
        if sha256_file(path) != source["opened_snapshot_sha256"]:
            raise SystemExit(f"ORG-009 V9 parquet changed: {path}")
        parquet = pq.ParquetFile(path)
        metadata = parquet.schema_arrow.metadata or {}
        dataset_name = metadata.get(b"ord.name", b"").decode("utf-8", errors="replace")
        dataset_description = metadata.get(b"ord.description", b"").decode("utf-8", errors="replace")
        table = parquet.read(columns=["reaction_id", "reaction"])
        for row_ordinal, (reaction_id, payload) in enumerate(zip(table["reaction_id"].to_pylist(), table["reaction"].to_pylist()), start=1):
            conventional_reaction_count += 1
            reaction = reaction_pb2.Reaction()
            reaction.ParseFromString(payload)
            source_topology = source_record(reaction)
            if source_topology is None:
                continue
            matches, surface_hashes = label_surfaces(reaction, dataset_name, dataset_description)
            row = {
                "payload_ordinal": source_ordinal,
                "config": source["config"],
                "row_ordinal": row_ordinal,
                "reaction_id": reaction_id,
                "independent_label_tokens": matches,
                "label_surface_hashes": surface_hashes,
                "source_topology": source_topology,
            }
            if matches:
                selected.append(row)
            else:
                structural_unlabeled.append(row)
    output = {
        "schema": "sft-v3-chemistry-org-009-ord-source-only-selection/9",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "complete_payload_count": 48,
        "complete_conventional_reaction_count": conventional_reaction_count,
        "independently_labeled_selected_count": len(selected),
        "structural_but_unlabeled_count": len(structural_unlabeled),
        "selection_accessed_product_outcomes": False,
        "product_outcomes_opened_before_selection_seal": False,
        "selected_in_payload_and_row_order": selected,
        "structural_unlabeled_in_payload_and_row_order": structural_unlabeled,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    seal = {
        "schema": "sft-v3-chemistry-org-009-ord-source-selection-seal/9",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "selector_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "selector_sha256": sha256_file(Path(__file__).resolve()),
        "selection_path": OUTPUT.relative_to(ROOT).as_posix(),
        "selection_sha256": sha256_file(OUTPUT),
        "independently_labeled_selected_count": len(selected),
        "structural_but_unlabeled_count": len(structural_unlabeled),
        "product_outcomes_opened_before_selection_seal": False,
    }
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(seal, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
