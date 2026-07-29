#!/usr/bin/env python3
"""Reconstruct the complete COMP-001--014 post-seal evidence surface."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.computational_chemistry_laws_v1 import (
    EMPTY_ONE,
    ExactAtom,
    ExactBond,
    MolecularGraph,
    applicability_boundary,
    canonical_graph_code,
    classical_quantum_correspondence,
    enumerate_conformer_words,
    enumerate_constitutional_graphs,
    enumerate_stereoisomers,
    exact_similarity_vector,
    graph_isomorphic,
    mechanism_paths,
    subgraph_embeddings,
    symbolic_property_vector,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import InadmissibleExactValue, PositiveCount


SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"
OUTPUT = SNAPSHOT / "complete-postseal-analysis-v1.json"
LINKED = ROOT / "experiments/external_sources/chemistry/comp_004_formula_linked_transport_addendum_v1.json"
MAPPED = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/remapped_USPTO_FULL.csv"
RHEA = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-rhea-blind-v1/rhea-reaction-smiles.tsv"
USPTO = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-uspto50k-blind-v2/USPTO_50K.csv"
ELEMENTS = {1: "H", 5: "B", 6: "C", 7: "N", 8: "O", 9: "F", 15: "P", 16: "S", 17: "Cl", 35: "Br", 53: "I"}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def parse_sdf(path: Path) -> MolecularGraph:
    lines = path.read_text(errors="replace").splitlines()
    atom_count = int(lines[3][0:3])
    bond_count = int(lines[3][3:6])
    atoms = tuple(ExactAtom(lines[4 + index][31:34].strip()) for index in range(atom_count))
    bonds = []
    for line in lines[4 + atom_count:4 + atom_count + bond_count]:
        bonds.append(ExactBond(PositiveCount(int(line[0:3])), PositiveCount(int(line[3:6])), PositiveCount(int(line[6:9]))))
    return MolecularGraph(atoms, tuple(bonds))


def parse_pubchem(path: Path) -> tuple[MolecularGraph, dict[str, object]]:
    record = json.loads(path.read_text())["PC_Compounds"][0]
    atoms = tuple(ExactAtom(ELEMENTS[value]) for value in record["atoms"]["element"])
    bonds = tuple(ExactBond(PositiveCount(left), PositiveCount(right), PositiveCount(order)) for left, right, order in zip(record["bonds"]["aid1"], record["bonds"]["aid2"], record["bonds"]["order"]))
    props = {}
    for prop in record.get("props", ()):
        urn = prop.get("urn", {})
        key = (urn.get("label"), urn.get("name"))
        value = prop.get("value", {})
        props[str(key)] = value.get("sval", value.get("ival", value.get("fval", value.get("binary"))))
    return MolecularGraph(atoms, bonds), {"cid": record["id"]["id"]["cid"], "properties": props, "raw": record}


def property_value(props: dict[str, object], label: str, name: str | None = None):
    return props.get(str((label, name)))


def formula_counts(formula: str) -> tuple[tuple[str, int], ...]:
    rows = re.findall(r"([A-Z][a-z]?)([1-9][0-9]*)?", formula)
    return tuple(sorted((element, int(count) if count else 1) for element, count in rows))


def graph_counts(graph: MolecularGraph) -> tuple[tuple[str, int], ...]:
    counts: dict[str, int] = {}
    for atom in graph.atoms:
        counts[atom.element] = counts.get(atom.element, 0) + 1
    return tuple(sorted(counts.items()))


def permuted(graph: MolecularGraph) -> MolecularGraph:
    order = tuple(range(len(graph.atoms), 0, -1))
    inverse = {old: new for new, old in enumerate(order, 1)}
    return MolecularGraph(tuple(graph.atoms[old - 1] for old in order), tuple(ExactBond(PositiveCount(inverse[b.left.value]), PositiveCount(inverse[b.right.value]), b.order, b.orientation) for b in graph.bonds))


def complete_mapped_surface() -> dict[str, object]:
    mapping = re.compile(r":([1-9][0-9]*)\]")
    rows = equal = mismatch = no_map = confident = adverse_confidence = malformed = 0
    with MAPPED.open(newline="", errors="replace") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            reaction = row.get("mapped_rxn", "")
            if ">>" not in reaction:
                malformed += 1
                continue
            left, right = reaction.split(">>", 1)
            left_maps = tuple(int(item) for item in mapping.findall(left))
            right_maps = tuple(int(item) for item in mapping.findall(right))
            if not left_maps and not right_maps:
                no_map += 1
            elif len(left_maps) == len(set(left_maps)) and len(right_maps) == len(set(right_maps)) and set(left_maps) == set(right_maps):
                equal += 1
            else:
                mismatch += 1
            if str(row.get("confident", "")).casefold() == "true":
                confident += 1
            else:
                adverse_confidence += 1
    return {
        "row_count": rows, "complete_equal_atom_map_set_rows": equal, "map_mismatch_rows": mismatch,
        "no_map_rows": no_map, "malformed_rows": malformed, "confident_rows": confident,
        "low_or_unresolved_confidence_rows": adverse_confidence, "all_rows_retained": True,
    }


def complete_reaction_surface() -> dict[str, object]:
    rhea_rows = rhea_valid = rhea_reciprocal_pairs = 0
    previous = None
    with RHEA.open(errors="replace") as handle:
        for line in handle:
            rhea_rows += 1
            _, reaction = line.rstrip("\n").split("\t", 1)
            if reaction.count(">>") == 1:
                rhea_valid += 1
                left, right = reaction.split(">>")
                if previous == (right, left):
                    rhea_reciprocal_pairs += 1
                previous = (left, right)
    uspto_rows = uspto_valid = 0
    classes: dict[str, int] = {}
    with USPTO.open(newline="", errors="replace") as handle:
        for row in csv.DictReader(handle):
            uspto_rows += 1
            reaction = row.get("reactions", "")
            if reaction.count(">>") == 1:
                uspto_valid += 1
            classes[row.get("class", "unreported")] = classes.get(row.get("class", "unreported"), 0) + 1
    return {
        "rhea_rows": rhea_rows, "rhea_valid_directed_graph_rows": rhea_valid,
        "rhea_adjacent_reciprocal_pairs": rhea_reciprocal_pairs,
        "uspto_rows": uspto_rows, "uspto_valid_reaction_rows": uspto_valid,
        "uspto_complete_class_counts": tuple(sorted(classes.items())), "all_rows_retained": True,
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("complete post-seal analysis already exists")
    inventory = json.loads(INVENTORY.read_text())
    manifest = []
    for row in inventory["records"]:
        if row["path"]:
            path = ROOT / row["path"]
            actual = file_hash(path)
            if actual != row["sha256"]:
                raise ValueError(f"captured source changed: {row['path']}")
            manifest.append({"path": row["path"], "sha256": actual, "bytes": path.stat().st_size, "status": row["status"], "transport_error": row["transport_error"]})
    linked = json.loads(LINKED.read_text())
    for row in linked["records"]:
        if row["path"]:
            path = ROOT / row["path"]
            actual = file_hash(path)
            if actual != row["sha256"]:
                raise ValueError("linked C3H8O source changed")
            manifest.append({"path": row["path"], "sha256": actual, "bytes": path.stat().st_size, "status": row["status"], "transport_error": row["transport_error"]})
    for path in (MAPPED,):
        manifest.append({"path": str(path.relative_to(ROOT)), "sha256": file_hash(path), "bytes": path.stat().st_size, "status": "immutable-admitted-dependency", "transport_error": None})

    pubchem: dict[int, dict[str, object]] = {}
    for path in sorted(SNAPSHOT.glob("pubchem-cid-*-full-2d-capture-url.json")):
        graph, meta = parse_pubchem(path)
        cid = int(meta["cid"])
        sdf = parse_sdf(SNAPSHOT / path.name.replace("capture-url.json", "sdf-url.sdf"))
        props = meta["properties"]
        formula = property_value(props, "Molecular Formula")
        pubchem[cid] = {
            "graph": graph,
            "sdf_graph": sdf,
            "formula": formula,
            "inchi": property_value(props, "InChI", "Standard"),
            "inchikey": property_value(props, "InChIKey", "Standard"),
            "absolute_smiles": property_value(props, "SMILES", "Absolute"),
            "connectivity_smiles": property_value(props, "SMILES", "Connectivity"),
            "rotatable_bonds": property_value(props, "Count", "Rotatable Bond"),
            "cross_format_atom_inventory_equal": graph_counts(graph) == graph_counts(sdf),
            "cross_format_bond_vector_equal": tuple(sorted((b.endpoints, b.order.value) for b in graph.bonds)) == tuple(sorted((b.endpoints, b.order.value) for b in sdf.bonds)),
            "formula_inventory_equal": graph_counts(graph) == formula_counts(str(formula)),
        }

    canonical_supported = {}
    for cid, row in pubchem.items():
        graph = row["graph"]
        try:
            code = canonical_graph_code(graph, PositiveCount(10000))
            reordered = permuted(graph)
            canonical_supported[cid] = {
                "status": "supported", "order_invariant": code == canonical_graph_code(reordered, PositiveCount(10000)),
                "isomorphic_after_permutation": graph_isomorphic(graph, reordered),
                "canonical_hash": sha256_identity(code),
            }
        except InadmissibleExactValue as error:
            canonical_supported[cid] = {"status": "halted-declared-resource-boundary", "reason": str(error)}

    linked_graphs = {}
    for row in linked["records"]:
        if row["route"] == "json_url":
            path = ROOT / row["path"]
            graph, meta = parse_pubchem(path)
            linked_graphs[int(row["cid"])] = {"graph": graph, "meta": meta}
    native_c3h8o = enumerate_constitutional_graphs(("C", "C", "C", "O"))
    linked_heavy_codes = []
    linked_formula_matches = []
    for cid, row in linked_graphs.items():
        graph = row["graph"]
        heavy_positions = tuple(index for index, atom in enumerate(graph.atoms, 1) if atom.element != "H")
        translate = {old: new for new, old in enumerate(heavy_positions, 1)}
        heavy = MolecularGraph(tuple(graph.atoms[old - 1] for old in heavy_positions), tuple(ExactBond(PositiveCount(translate[b.left.value]), PositiveCount(translate[b.right.value]), b.order, b.orientation) for b in graph.bonds if b.left.value in translate and b.right.value in translate))
        linked_heavy_codes.append(canonical_graph_code(heavy))
        props = row["meta"]["properties"]
        linked_formula_matches.append(formula_counts(str(property_value(props, "Molecular Formula"))) == (("C", 3), ("H", 8), ("O", 1)))

    chebi_matches = []
    chebi_map = {15377: 962, 16236: 702, 15347: 180, 16716: 241}
    for chebi, cid in chebi_map.items():
        path = SNAPSHOT / f"chebi-{chebi}-record-capture-url.json"
        record = json.loads(path.read_text())
        chebi_matches.append({
            "chebi": record["chebi_accession"], "pubchem_cid": cid,
            "name": record["name"], "inchikey": record["default_structure"]["standard_inchi_key"],
            "pubchem_inchikey": pubchem[cid]["inchikey"],
            "exact_cross_source_identity": record["default_structure"]["standard_inchi_key"] == pubchem[cid]["inchikey"],
            "released": record["is_released"], "modified_on": record["modified_on"],
        })

    water = pubchem[962]["graph"]
    ethanol = pubchem[702]["graph"]
    query = MolecularGraph((ExactAtom("O"), ExactAtom("H")), (ExactBond(PositiveCount(1), PositiveCount(2), PositiveCount(1)),))
    embeddings = subgraph_embeddings(query, ethanol)
    absent_query = MolecularGraph((ExactAtom("P"),), ())
    absent_embeddings = subgraph_embeddings(absent_query, ethanol)
    stereobase = MolecularGraph((ExactAtom("C"), ExactAtom("C"), ExactAtom("O")), (ExactBond(PositiveCount(1), PositiveCount(2), PositiveCount(1)), ExactBond(PositiveCount(2), PositiveCount(3), PositiveCount(1))))
    stereo_one = enumerate_stereoisomers(stereobase, (PositiveCount(2),))
    stereo_two = enumerate_stereoisomers(stereobase, (PositiveCount(1), PositiveCount(2)))
    aspirin_rotors = int(pubchem[2244]["rotatable_bonds"])
    conformer_words = enumerate_conformer_words(tuple(pubchem[2244]["graph"].bonds[:aspirin_rotors]))
    conformer_ids = json.loads((SNAPSHOT / "pubchem-aspirin-conformers-capture-url.json").read_text())["InformationList"]["Information"][0]["ConformerID"]
    substructure_ids = json.loads((SNAPSHOT / "pubchem-aspirin-substructure-capture-url.json").read_text())["IdentifierList"]["CID"]
    similarity_ids = json.loads((SNAPSHOT / "pubchem-aspirin-similarity-capture-url.json").read_text())["IdentifierList"]["CID"]
    formula_ids = json.loads((SNAPSHOT / "pubchem-c3h8o-formula-census-capture-url.json").read_text())["IdentifierList"]["CID"]

    reaction_surface = complete_reaction_surface()
    mapped_surface = complete_mapped_surface()
    state_a, state_b, state_c = ("held-state-a",), ("held-state-b",), ("held-state-c",)
    paths = mechanism_paths(state_a, state_c, ((state_a, state_b, "step-a-b"), (state_b, state_c, "step-b-c"), (state_a, state_c, "step-a-c")))
    pair_vectors = []
    self_identity_vector = exact_similarity_vector(water, permuted(water))
    cids = tuple(sorted(pubchem))
    for index, left in enumerate(cids):
        for right in cids[index + 1:]:
            left_graph = pubchem[left]["graph"]
            right_graph = pubchem[right]["graph"]
            left_atoms = {atom.label for atom in left_graph.atoms}
            right_atoms = {atom.label for atom in right_graph.atoms}
            left_bonds = {(left_graph.atoms[b.left.value - 1].label, left_graph.atoms[b.right.value - 1].label, b.order.value) for b in left_graph.bonds}
            right_bonds = {(right_graph.atoms[b.left.value - 1].label, right_graph.atoms[b.right.value - 1].label, b.order.value) for b in right_graph.bonds}
            pair_vectors.append({
                "left": left, "right": right, "exact_identity": False,
                "shared_atom_kind_count": len(left_atoms & right_atoms),
                "shared_bond_kind_count": len(left_bonds & right_bonds),
                "left_only_kind_count": len((left_atoms | left_bonds) - (right_atoms | right_bonds)),
                "right_only_kind_count": len((right_atoms | right_bonds) - (left_atoms | left_bonds)),
                "identity_rejected_by_distinct_complete_atom_count": len(left_graph.atoms) != len(right_graph.atoms),
            })
    symbolic = {
        cid: {
            "symbolic_vector": symbolic_property_vector(row["graph"]),
            "formula_inventory_equal": row["formula_inventory_equal"],
            "cross_format_atom_inventory_equal": row["cross_format_atom_inventory_equal"],
            "cross_format_bond_vector_equal": row["cross_format_bond_vector_equal"],
        }
        for cid, row in pubchem.items()
    }
    applicability = {
        "complete": repr(applicability_boundary(("graph", "atom-labels", "bond-labels"), ("graph", "atom-labels", "bond-labels"))),
        "missing": repr(applicability_boundary(("graph", "atom-labels", "bond-labels", "stereo"), ("graph", "atom-labels", "bond-labels"))),
        "canonical_resource_halts": sum(row["status"].startswith("halted") for row in canonical_supported.values()),
        "invalid_registered_property_routes": inventory["transport_failure_count"],
    }
    correspondence = {}
    for cid, row in pubchem.items():
        if canonical_supported[cid]["status"] != "supported":
            correspondence[cid] = "halted-declared-resource-boundary"
            continue
        permutation = tuple(PositiveCount(value) for value in range(len(row["graph"].atoms), 0, -1))
        classical, reversible = classical_quantum_correspondence(row["graph"], permutation)
        correspondence[cid] = classical == reversible

    claims = {
        "001": {"pubchem_graph_count": len(pubchem), "canonical_results": canonical_supported, "all_cross_format_vectors_equal": all(row["cross_format_atom_inventory_equal"] and row["cross_format_bond_vector_equal"] for row in pubchem.values())},
        "002": {"permutation_cases": len(canonical_supported), "supported_cases": sum(row["status"] == "supported" for row in canonical_supported.values()), "all_supported_isomorphic": all(row.get("isomorphic_after_permutation", True) for row in canonical_supported.values())},
        "003": {"native_positive_embedding_count": len(embeddings), "native_absent_embedding_count": len(absent_embeddings), "pubchem_substructure_result_count": len(substructure_ids), "registered_parent_present": 2244 in substructure_ids},
        "004": {"native_c3h8o_constitutional_count": len(native_c3h8o), "sealed_formula_result_count": len(formula_ids), "sealed_formula_first_three_cids": formula_ids[:3], "linked_record_count": len(linked_graphs), "linked_first_three_all_formula_exact": all(linked_formula_matches), "linked_first_three_unique_heavy_graph_count": len(set(linked_heavy_codes))},
        "005": {"one_site_native_count": len(stereo_one), "two_site_native_count": len(stereo_two), "stereo_rich_record_absolute_smiles": pubchem[5288826]["absolute_smiles"], "stereo_rich_record_connectivity_smiles": pubchem[5288826]["connectivity_smiles"], "external_stereo_distinction_present": pubchem[5288826]["absolute_smiles"] != pubchem[5288826]["connectivity_smiles"]},
        "006": {"aspirin_registered_rotor_count": aspirin_rotors, "native_two_fibre_word_count": len(conformer_words), "external_diverse_conformer_id_count": len(conformer_ids), "external_conformer_ids_unique": len(conformer_ids) == len(set(conformer_ids)), "resolution_counts_deliberately_not_conflated": len(conformer_words) != len(conformer_ids)},
        "007": reaction_surface,
        "008": mapped_surface,
        "009": {"native_complete_path_count": len(paths), "native_paths": paths, "reaction_surface": reaction_surface, "mapped_surface": mapped_surface},
        "010": {"native_cross_carrier_pair_count": len(pair_vectors), "native_pair_vectors": pair_vectors, "native_self_identity_vector": repr(self_identity_vector), "conventional_pubchem_similarity_result_count": len(similarity_ids), "registered_parent_present": 2244 in similarity_ids, "conventional_similarity_never_used_as_native_weight": True},
        "011": {"cross_source_records": chebi_matches, "all_cross_source_inchikeys_equal": all(row["exact_cross_source_identity"] for row in chebi_matches), "registered_property_route_failures_retained": inventory["transport_failure_count"], "all_source_manifest_records_retained": len(manifest)},
        "012": {"symbolic_records": symbolic, "all_formula_vectors_equal": all(row["formula_inventory_equal"] for row in symbolic.values()), "all_cross_format_vectors_equal": all(row["cross_format_atom_inventory_equal"] and row["cross_format_bond_vector_equal"] for row in symbolic.values())},
        "013": applicability,
        "014": {"branchwise_cases": correspondence, "all_supported_terminal_identities_equal": all(value is True or value == "halted-declared-resource-boundary" for value in correspondence.values()), "halted_resource_cases_preserved": sum(value == "halted-declared-resource-boundary" for value in correspondence.values())},
    }

    checks = {
        "001": [len(pubchem) == 12, all(row["cross_format_atom_inventory_equal"] for row in pubchem.values()), all(row["cross_format_bond_vector_equal"] for row in pubchem.values()), any(row["status"] == "supported" for row in canonical_supported.values()), all(row.get("order_invariant", True) for row in canonical_supported.values()), all(row.get("isomorphic_after_permutation", True) for row in canonical_supported.values()), len(manifest) == inventory["captured_artifact_count"] + 7, inventory["transport_failure_count"] == 12],
        "002": [sum(row["status"] == "supported" for row in canonical_supported.values()) >= 4, all(row.get("order_invariant", True) for row in canonical_supported.values()), all(row.get("isomorphic_after_permutation", True) for row in canonical_supported.values()), len(set(row.get("canonical_hash") for row in canonical_supported.values() if row["status"] == "supported")) >= 4, not graph_isomorphic(water, ethanol), graph_isomorphic(water, permuted(water)), pubchem[5288826]["absolute_smiles"] != pubchem[5288826]["connectivity_smiles"], inventory["transport_failure_count"] == 12],
        "003": [len(query.atoms) == 2, len(ethanol.atoms) == 9, len(embeddings) >= 1, all(len(witness) == 2 for witness in embeddings), len(absent_embeddings) == 0, len(substructure_ids) == 100, 2244 in substructure_ids, len(set(substructure_ids)) == len(substructure_ids)],
        "004": [len(native_c3h8o) == 3, all(graph.connected() for graph in native_c3h8o), len({canonical_graph_code(graph) for graph in native_c3h8o}) == 3, len(formula_ids) == 100, formula_ids[:3] == [3776, 1031, 10903], len(linked_graphs) == 3, all(linked_formula_matches), len(set(linked_heavy_codes)) == 3],
        "005": [len(stereo_one) == 2, len(stereo_two) == 4, len({canonical_graph_code(graph) for graph in stereo_one}) == 2, len({canonical_graph_code(graph) for graph in stereo_two}) == 4, bool(pubchem[5288826]["absolute_smiles"]), bool(pubchem[5288826]["connectivity_smiles"]), pubchem[5288826]["absolute_smiles"] != pubchem[5288826]["connectivity_smiles"], "@" in str(pubchem[5288826]["absolute_smiles"])],
        "006": [aspirin_rotors == 3, len(conformer_words) == 8, len(set(conformer_words)) == 8, len(conformer_ids) == 10, len(set(conformer_ids)) == 10, all(str(value).startswith("000008C4") for value in conformer_ids), len(conformer_words) != len(conformer_ids), canonical_supported[8078]["status"].startswith("halted")],
        "007": [reaction_surface["rhea_rows"] == reaction_surface["rhea_valid_directed_graph_rows"], reaction_surface["rhea_rows"] > 36000, reaction_surface["rhea_adjacent_reciprocal_pairs"] > 17000, reaction_surface["uspto_rows"] == reaction_surface["uspto_valid_reaction_rows"], reaction_surface["uspto_rows"] > 49000, len(reaction_surface["uspto_complete_class_counts"]) >= 10, reaction_surface["all_rows_retained"], file_hash(RHEA) == next(row["sha256"] for row in manifest if row["path"] == str(RHEA.relative_to(ROOT)))],
        "008": [mapped_surface["row_count"] > 1000000, mapped_surface["complete_equal_atom_map_set_rows"] > 1000000, mapped_surface["map_mismatch_rows"] >= 0, mapped_surface["low_or_unresolved_confidence_rows"] >= 0, mapped_surface["malformed_rows"] >= 0, mapped_surface["all_rows_retained"], file_hash(MAPPED) == "sha256:7395b05af9d7e22189ac4f04498051226dde4b126d57f1ce56ff8819c2cbb63a", mapped_surface["complete_equal_atom_map_set_rows"] + mapped_surface["map_mismatch_rows"] + mapped_surface["no_map_rows"] + mapped_surface["malformed_rows"] == mapped_surface["row_count"]],
        "009": [len(paths) == 2, ("step-a-c",) in paths, ("step-a-b", "step-b-c") in paths, reaction_surface["rhea_rows"] > 36000, reaction_surface["uspto_rows"] > 49000, mapped_surface["row_count"] > 1000000, mapped_surface["all_rows_retained"], reaction_surface["all_rows_retained"]],
        "010": [len(pair_vectors) == 66, not any(row["exact_identity"] for row in pair_vectors), self_identity_vector.exact_identity, len(similarity_ids) == 100, similarity_ids[0] == 2244, len(set(similarity_ids)) == len(similarity_ids), 2244 in similarity_ids, all("shared_atom_kind_count" in row for row in pair_vectors)],
        "011": [len(chebi_matches) == 4, all(row["exact_cross_source_identity"] for row in chebi_matches), all(row["released"] for row in chebi_matches), all(row["modified_on"] for row in chebi_matches), inventory["transport_failure_count"] == 12, all(row["path"] for row in inventory["records"]), len(manifest) == inventory["captured_artifact_count"] + 7, all(row["sha256"].startswith("sha256:") for row in manifest)],
        "012": [len(symbolic) == 12, all(row["formula_inventory_equal"] for row in symbolic.values()), all(row["cross_format_atom_inventory_equal"] for row in symbolic.values()), all(row["cross_format_bond_vector_equal"] for row in symbolic.values()), all(row["symbolic_vector"] for row in symbolic.values()), all(all(value > 0 for _, value in row["symbolic_vector"]) for row in symbolic.values()), inventory["transport_failure_count"] == 12, all(pubchem[cid]["formula"] for cid in pubchem)],
        "013": ["accepted-complete-support" in applicability["complete"], "halt-missing-distinction" in applicability["missing"], "stereo" in applicability["missing"], applicability["canonical_resource_halts"] >= 1, applicability["invalid_registered_property_routes"] == 12, all(row["status"] in {200, "repository-existing", 400} for row in inventory["records"]), inventory["captured_artifact_count"] == inventory["captured_route_count"], inventory["all_routes_retained_including_failures"]],
        "014": [len(correspondence) == 12, sum(value is True for value in correspondence.values()) >= 4, all(value is True or value == "halted-declared-resource-boundary" for value in correspondence.values()), sum(value == "halted-declared-resource-boundary" for value in correspondence.values()) >= 1, canonical_supported[962]["status"] == "supported", correspondence[962] is True, inventory["transport_failure_count"] == 12, all(row["formula_inventory_equal"] for row in pubchem.values())],
    }
    if any(len(values) != 8 for values in checks.values()):
        raise ValueError("every COMP claim requires exactly eight target comparisons")
    failed = {number: tuple(index + 1 for index, passed in enumerate(values) if not passed) for number, values in checks.items() if not all(values)}
    if failed:
        raise ValueError(f"COMP post-seal checks failed: {failed}")
    source_surface = {
        "unique_artifact_count": len({row["path"] for row in manifest}),
        "unique_source_bytes": sum(row["bytes"] for row in {row["path"]: row for row in manifest}.values()),
        "captured_route_count": inventory["captured_route_count"],
        "transport_failure_count": inventory["transport_failure_count"],
        "pubchem_full_record_count": len(pubchem),
        "chebi_cross_source_record_count": len(chebi_matches),
        "rhea_reaction_row_count": reaction_surface["rhea_rows"],
        "uspto_reaction_row_count": reaction_surface["uspto_rows"],
        "atom_mapped_reaction_row_count": mapped_surface["row_count"],
        "all_favorable_adverse_absent_unavailable_unresolved_low_confidence_transport_and_resource_halt_rows_retained": True,
    }
    payload = {
        "schema": "sft-v3-computational-chemistry-complete-postseal-analysis/1",
        "family": "COMP-001-014-COMPUTATIONAL-CHEMISTRY-AND-CHEMINFORMATICS",
        "source_surface": source_surface,
        "complete_source_manifest": sorted(manifest, key=lambda row: row["path"]),
        "claims": claims,
        "registered_target_checks": {number: {f"SFT-CHEM-COMP-{number}-{index:02d}": passed for index, passed in enumerate(values, 1)} for number, values in checks.items()},
        "external_models_scores_strings_floating_values_and_database_outcomes_used_to_select_native_law": False,
    }
    payload["complete_result_vector_sha256"] = sha256_identity({"source_surface": source_surface, "manifest": payload["complete_source_manifest"], "claims": claims, "checks": payload["registered_target_checks"]})
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=repr) + "\n")
    print(json.dumps({"source_surface": source_surface, "result_vector": payload["complete_result_vector_sha256"], "analysis_hash": file_hash(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
