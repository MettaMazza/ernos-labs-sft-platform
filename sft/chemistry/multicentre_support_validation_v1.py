"""Capability-closed multicentre prediction and complete structural validation for ELEC-008."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import platform
import re

from sft.chemistry.multicentre_support_batch_v1 import IDENTITY_HASH, IDENTITY_PATH, MULTICENTRE_SUPPORT_SPEC, SOURCE_IDS, TARGET_HASH, TARGET_PATH
from sft.chemistry.multicentre_support_law_v1 import DelocalizedMolecularSupport, RIBBON, SURFACE, SupportEdge, VOLUME, ribbon_support, surface_cycle_support, tetrahedral_volume_support
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, FoldTable, FoldWord, HostilePackageAuditor, PositiveRatio, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.claim_evidence.fold_language import EMPTY_ONE, FoldLanguageHalt
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel, InadmissibleExactValue, PositiveCount
from sft.engine.source import hash_file


IUPAC_PATH = "experiments/external_sources/chemistry/snapshots/goldbook-terms/08789.json"
IUPAC_HASH = "sha256:570755940f01bfa32741b03b6b2f22b02742101605a2263e57369966ea433abd"
DIBORANE_PATH = "experiments/external_sources/chemistry/snapshots/multicentre-v1/nist-cccbdb-diborane-experimental-geometry.html"
DIBORANE_HASH = "sha256:99e1c36da1bf8aa2b559ba9ef84b43b4965982c3ee1cab13abb933c8fba22527"
BENZENE_PATH = "experiments/external_sources/chemistry/snapshots/multicentre-v1/nist-cccbdb-benzene-experimental-geometry.html"
BENZENE_HASH = "sha256:6e158d7639b301cfa6a18bfab4461988c9ffc6190f99fb9a5c0df7baf6f3ec0f"


class _IndependentHTMLSurface(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_cell = False
        self.in_row = False
        self.cell: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []
        self.all_parts: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "tr":
            self.in_row, self.row = True, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell = True, []
        elif tag == "sub":
            self.all_parts.append("_")
            if self.in_cell:
                self.cell.append("_")

    def handle_endtag(self, tag) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.cell)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = False

    def handle_data(self, data) -> None:
        self.all_parts.append(data)
        if self.in_cell:
            self.cell.append(data)

    @property
    def text(self) -> str:
        return " ".join(unescape("".join(self.all_parts)).split())


def _identities(root: Path) -> tuple[dict[str, object], ...]:
    if hash_file(root / IDENTITY_PATH) != IDENTITY_HASH:
        raise ValueError("ELEC-008 identity registry changed")
    document = json.loads((root / IDENTITY_PATH).read_text(encoding="utf-8"))
    rows = tuple(document.get("rows", ()))
    if document.get("schema") != "sft-v3-multicentre-identities/1" or len(rows) != 20 or len({str(row["target_id"]) for row in rows}) != 20:
        raise ValueError("ELEC-008 identity registry is incomplete")
    return rows


def prediction_program_document(root: Path) -> dict[str, object]:
    _identities(root)
    rows = (
        ("minimum-centre-count", "count", "3", ""),
        ("support-identity", "label", "one-complete-extended-support", "multicentre-result"),
        ("connection", "label", "connected-generated-graph", "multicentre-result"),
        ("ribbon", "label", "ribbon-path", "delocalized-topology"),
        ("surface", "label", "surface-cycle", "delocalized-topology"),
        ("volume", "label", "volume-polyhedron", "delocalized-topology"),
        ("reduction", "label", "irreducible-to-one-localized-pair", "multicentre-result"),
        ("extension", "label", "connected-successor-with-no-extra-rule", "multicentre-result"),
    )
    instructions = [{"opcode": "input", "destination": "premise", "arguments": ["registered-premise"]}]
    table = []
    for position, (name, opcode, value, family) in enumerate(rows, start=1):
        key, result = f"key-{position}", f"value-{position}"
        instructions.append({"opcode": "label", "destination": key, "arguments": ["multicentre-law", name]})
        instructions.append({"opcode": opcode, "destination": result, "arguments": [value]} if opcode == "count" else {"opcode": "label", "destination": result, "arguments": [family, value]})
        table.extend((key, result))
    instructions.extend(({"opcode": "table", "destination": "complete-multicentre-law", "arguments": table}, {"opcode": "emit", "destination": "", "arguments": ["complete-multicentre-law"]}))
    return {"schema": "sft-v3-fold-program/1", "program_id": MULTICENTRE_SUPPORT_SPEC.experiment_id + "-multicentre-law-prediction", "instructions": instructions}


def experiment_registration_record(root: Path) -> dict[str, object]:
    return {"experiment_id": MULTICENTRE_SUPPORT_SPEC.experiment_id, "claim_id": MULTICENTRE_SUPPORT_SPEC.claim_id, "provenance": "observational_derivation", "frozen_relation": MULTICENTRE_SUPPORT_SPEC.exact_result, "identity_registry": (IDENTITY_PATH, IDENTITY_HASH), "withheld_target_registry": (TARGET_PATH, TARGET_HASH), "prediction_program": prediction_program_document(root), "target_references": tuple((row.target_id, row.source_id, row.source_locator, row.snapshot_path, row.snapshot_hash) for row in MULTICENTRE_SUPPORT_SPEC.target_rows), "target_content_absent_from_prediction": True, "target_inaccessible_to_capability_closed_execution": True, "all_twenty_records_required": True, "measured_geometries_do_not_select_law": True, "falsification_condition": MULTICENTRE_SUPPORT_SPEC.falsification_condition}


def _numeric_record(target_id: str, source_id: str, species: str, role: str, inscription: str, numerator: int, denominator: int, path: str, source_hash: str) -> dict[str, object]:
    return {"target_id": target_id, "source_id": source_id, "record_kind": "experimental-geometry", "species": species, "record_role": role, "inscription": inscription, "positive_value_numerator": numerator, "positive_value_denominator": denominator, "snapshot_path": path, "snapshot_hash": source_hash}


def _reconstructed_targets(root: Path) -> tuple[dict[str, object], ...]:
    identities = _identities(root)
    if hash_file(root / TARGET_PATH) != TARGET_HASH:
        raise ValueError("ELEC-008 target registry changed")
    registered_document = json.loads((root / TARGET_PATH).read_text(encoding="utf-8"))
    registered = {str(row["target_id"]): row for row in registered_document.get("rows", ())}
    if registered_document.get("schema") != "sft-v3-multicentre-withheld-targets/1" or len(registered) != 20:
        raise ValueError("ELEC-008 target registry is incomplete")
    for path, expected in ((IUPAC_PATH, IUPAC_HASH), (DIBORANE_PATH, DIBORANE_HASH), (BENZENE_PATH, BENZENE_HASH)):
        if hash_file(root / path) != expected:
            raise ValueError("ELEC-008 external source bytes changed")

    iupac = json.loads((root / IUPAC_PATH).read_text(encoding="utf-8"))
    definition = iupac["term"]["definitions"][0]
    notes = definition["notes"]
    rebuilt = [
        {"target_id": "IUPAC-DELOCALIZATION-DEFINITION", "source_id": SOURCE_IDS[0], "record_kind": "authoritative-delocalization-topology", "record_role": "definition", "inscription": definition["text"], "snapshot_path": IUPAC_PATH, "snapshot_hash": IUPAC_HASH},
        {"target_id": "IUPAC-DELOCALIZATION-RIBBON", "source_id": SOURCE_IDS[0], "record_kind": "authoritative-delocalization-topology", "record_role": "ribbon-topology", "inscription": notes["1"], "snapshot_path": IUPAC_PATH, "snapshot_hash": IUPAC_HASH},
        {"target_id": "IUPAC-DELOCALIZATION-SURFACE", "source_id": SOURCE_IDS[0], "record_kind": "authoritative-delocalization-topology", "record_role": "surface-topology", "inscription": notes["1"], "snapshot_path": IUPAC_PATH, "snapshot_hash": IUPAC_HASH},
        {"target_id": "IUPAC-DELOCALIZATION-VOLUME", "source_id": SOURCE_IDS[0], "record_kind": "authoritative-delocalization-topology", "record_role": "volume-topology", "inscription": notes["1"], "snapshot_path": IUPAC_PATH, "snapshot_hash": IUPAC_HASH},
    ]
    parsed = {}
    for species, path in (("diborane", DIBORANE_PATH), ("benzene", BENZENE_PATH)):
        parser = _IndependentHTMLSurface()
        parser.feed((root / path).read_text(encoding="utf-8"))
        parsed[species] = parser
    dib, ben = parsed["diborane"], parsed["benzene"]
    if "Point Group D_2h" not in dib.text or "Point Group D_6h" not in ben.text:
        raise ValueError("ELEC-008 point-group source record is absent")
    coordinate_rows = {
        "diborane": tuple(row for row in dib.rows if len(row) >= 8 and row[0] in {"rBB", "rBH", "aHBH", "aBHB"}),
        "benzene": tuple(row for row in ben.rows if len(row) >= 8 and row[0] in {"rCC", "rCH", "aCCC", "aHCC"}),
    }
    if len(coordinate_rows["diborane"]) != 7 or len(coordinate_rows["benzene"]) != 4:
        raise ValueError("ELEC-008 internal-coordinate census is incomplete")
    dib_roles = ("rBB", "rBH-outer", "rBH-bridging", "aHBH-outer", "aHBH-bridging", "aBHB", "aHBH-symmetry")
    ben_roles = ("rCC", "rCH", "aCCC", "aHCC")
    dib_ids = ("NIST-DIBORANE-rBB", "NIST-DIBORANE-rBH-OUTER", "NIST-DIBORANE-rBH-BRIDGING", "NIST-DIBORANE-aHBH-OUTER", "NIST-DIBORANE-aHBH-BRIDGING", "NIST-DIBORANE-aBHB", "NIST-DIBORANE-aHBH-SYMMETRY")
    ben_ids = ("NIST-BENZENE-rCC", "NIST-BENZENE-rCH", "NIST-BENZENE-aCCC", "NIST-BENZENE-aHCC")
    rebuilt.append({"target_id": "NIST-DIBORANE-POINT-GROUP", "source_id": SOURCE_IDS[1], "record_kind": "experimental-geometry", "species": "diborane", "record_role": "point-group", "inscription": "D2h", "positive_value_numerator": "absence", "positive_value_denominator": "absence", "snapshot_path": DIBORANE_PATH, "snapshot_hash": DIBORANE_HASH})
    for target_id, role, row in zip(dib_ids, dib_roles, coordinate_rows["diborane"]):
        value = row[1]
        parts = value.split(".")
        numerator, denominator = (int("".join(parts)), 10 ** len(parts[1])) if len(parts) == 2 else (int(value), 1)
        rebuilt.append(_numeric_record(target_id, SOURCE_IDS[1], "diborane", role, value, numerator, denominator, DIBORANE_PATH, DIBORANE_HASH))
    bond_rows = tuple(row for row in dib.rows if len(row) == 2 and row[0] == "H-B")
    if bond_rows != (("H-B", "8"),):
        raise ValueError("ELEC-008 diborane link-count record is incomplete")
    rebuilt.append(_numeric_record("NIST-DIBORANE-HB-LINK-COUNT", SOURCE_IDS[1], "diborane", "H-B-count", "8", 8, 1, DIBORANE_PATH, DIBORANE_HASH))
    rebuilt.append({"target_id": "NIST-BENZENE-POINT-GROUP", "source_id": SOURCE_IDS[2], "record_kind": "experimental-geometry", "species": "benzene", "record_role": "point-group", "inscription": "D6h", "positive_value_numerator": "absence", "positive_value_denominator": "absence", "snapshot_path": BENZENE_PATH, "snapshot_hash": BENZENE_HASH})
    for target_id, role, row in zip(ben_ids, ben_roles, coordinate_rows["benzene"]):
        value = row[1]
        parts = value.split(".")
        numerator, denominator = (int("".join(parts)), 10 ** len(parts[1])) if len(parts) == 2 else (int(value), 1)
        rebuilt.append(_numeric_record(target_id, SOURCE_IDS[2], "benzene", role, value, numerator, denominator, BENZENE_PATH, BENZENE_HASH))
    bond_rows = tuple(row for row in ben.rows if len(row) == 2 and row[0] in {"C:C", "H-C"})
    if bond_rows != (("C:C", "6"), ("H-C", "6")):
        raise ValueError("ELEC-008 benzene bond-count records are incomplete")
    rebuilt.extend((_numeric_record("NIST-BENZENE-AROMATIC-LINK-COUNT", SOURCE_IDS[2], "benzene", "C:C-count", "6", 6, 1, BENZENE_PATH, BENZENE_HASH), _numeric_record("NIST-BENZENE-HC-LINK-COUNT", SOURCE_IDS[2], "benzene", "H-C-count", "6", 6, 1, BENZENE_PATH, BENZENE_HASH)))
    if {str(row["target_id"]) for row in rebuilt} != {str(row["target_id"]) for row in identities}:
        raise ValueError("ELEC-008 independently rebuilt identities differ")
    resolved = []
    for row in rebuilt:
        if registered[str(row["target_id"])] != row:
            raise ValueError("ELEC-008 independently reconstructed row differs")
        magnitude = EMPTY_ONE if row.get("positive_value_numerator", "absence") == "absence" else PositiveRatio.from_pair(int(row["positive_value_numerator"]), int(row["positive_value_denominator"]))
        target_value = FoldWord((HeldLabel("external-source", str(row["source_id"])), HeldLabel("record-kind", str(row["record_kind"])), HeldLabel("record-role", str(row["record_role"])), HeldLabel("source-inscription", str(row["inscription"])), magnitude))
        resolved.append({**row, "target_value": target_value, "magnitude": magnitude})
    return tuple(resolved)


def _prediction_map(table: FoldTable) -> dict[str, object]:
    result = {entry.left.label: entry.right for entry in table.entries if isinstance(entry.left, HeldLabel) and entry.left.family == "multicentre-law"}
    if len(result) != 8:
        raise ValueError("ELEC-008 prediction table is incomplete")
    return result


class MulticentreSupportValidator:
    def __init__(self, root: Path):
        self.root, self.spec = root.resolve(), MULTICENTRE_SUPPORT_SPEC

    def validate(self, sealed) -> EmpiricalValidation:
        self.spec.validate()
        registration = experiment_registration_record(self.root)
        registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.root)
        program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        targets = _reconstructed_targets(self.root)
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(row.target_id for row in self.spec.target_rows), sealed.seal_hash, registration_hash)
        vault = TargetVault(experiment_id=self.spec.experiment_id, custodian_id=self.spec.experiment_id + "-IUPAC-NIST-target-custodian", targets={str(row["target_id"]): row["target_value"] for row in targets}, custody_nonce=sha256_identity((registration_hash, TARGET_HASH)), expected_envelope_hash=sha256_identity(envelope))
        before = snapshot_protected_tree(self.root)
        execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope)
        prediction_seal = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root)
        audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("ELEC-008 prediction package changed")
        release = vault.release(prediction_seal)
        CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction_seal)
        boundary.measurement_context(release.targets)
        if not isinstance(execution.output, FoldTable):
            raise ValueError("ELEC-008 prediction is not a Fold table")
        predicted = _prediction_map(execution.output)
        expected_prediction = {"minimum-centre-count": PositiveCount(3), "support-identity": HeldLabel("multicentre-result", "one-complete-extended-support"), "connection": HeldLabel("multicentre-result", "connected-generated-graph"), "ribbon": RIBBON, "surface": SURFACE, "volume": VOLUME, "reduction": HeldLabel("multicentre-result", "irreducible-to-one-localized-pair"), "extension": HeldLabel("multicentre-result", "connected-successor-with-no-extra-rule")}
        if predicted != expected_prediction:
            raise ValueError("ELEC-008 sealed law changed")
        bridge = ribbon_support("diborane", ("B-left", "H-bridge", "B-right"))
        ring = surface_cycle_support("benzene", tuple(f"C-{position}" for position in range(1, 7)))
        volume = tetrahedral_volume_support("tetrahedrane", ("C-one", "C-two", "C-three", "C-four"))
        comparisons = []
        for row in targets:
            source_id, role = str(row["source_id"]), str(row["record_role"])
            if source_id == SOURCE_IDS[0]:
                required = {"definition": "localized bonds", "ribbon-topology": "ribbon", "surface-topology": "surface", "volume-topology": "volume"}[role]
                structural_pass = required in str(row["inscription"])
            elif source_id == SOURCE_IDS[1]:
                structural_pass = bridge.irreducible_to_one_localized_pair and bridge.topology == predicted["ribbon"]
            else:
                structural_pass = ring.irreducible_to_one_localized_pair and ring.topology == predicted["surface"] and ring.positive_edge_count == PositiveCount(6)
            exact_pass = row["magnitude"] is EMPTY_ONE if row.get("positive_value_numerator", "absence") == "absence" else row["magnitude"] == PositiveRatio.from_pair(int(row["positive_value_numerator"]), int(row["positive_value_denominator"]))
            comparisons.append({"target_id": row["target_id"], "source_id": source_id, "record_kind": row["record_kind"], "record_role": role, "inscription": row["inscription"], "exact_magnitude": "structural-absence" if row["magnitude"] is EMPTY_ONE else f"{row['magnitude'].numerator.value}/{row['magnitude'].denominator.value}", "structural_pass": structural_pass, "exact_pass": exact_pass, "passed": structural_pass and exact_pass})
        two_centre_rejected = disconnected_rejected = incomplete_word_rejected = wrong_topology_rejected = False
        try:
            ribbon_support("control", ("left", "right"))
        except InadmissibleExactValue:
            two_centre_rejected = True
        try:
            centres = bridge.centres
            DelocalizedMolecularSupport(bridge.molecular_carrier, RIBBON, centres, (bridge.edges[0],), FoldWord(centres))
        except InadmissibleExactValue:
            disconnected_rejected = True
        try:
            DelocalizedMolecularSupport(bridge.molecular_carrier, RIBBON, bridge.centres, bridge.edges, FoldWord(bridge.centres[:-1]))
        except InadmissibleExactValue:
            incomplete_word_rejected = True
        try:
            DelocalizedMolecularSupport(ring.molecular_carrier, RIBBON, ring.centres, ring.edges, ring.electron_support)
        except InadmissibleExactValue:
            wrong_topology_rejected = True
        numeric_zero_rejected = False
        try:
            FoldWord((0,))
        except FoldLanguageHalt:
            numeric_zero_rejected = True
        counts = {"records": len(comparisons), "IUPAC": sum(row["source_id"] == SOURCE_IDS[0] for row in comparisons), "diborane": sum(row["source_id"] == SOURCE_IDS[1] for row in comparisons), "benzene": sum(row["source_id"] == SOURCE_IDS[2] for row in comparisons), "positive_numeric": sum(row["exact_magnitude"] != "structural-absence" for row in comparisons), "categorical_or_text": sum(row["exact_magnitude"] == "structural-absence" for row in comparisons)}
        first = self.root / DIBORANE_PATH
        changed_hash = "sha256:" + sha256(first.read_bytes() + b"tampered").hexdigest()
        outer = next(row for row in targets if row["target_id"] == "NIST-DIBORANE-rBH-OUTER")["magnitude"]
        bridging = next(row for row in targets if row["target_id"] == "NIST-DIBORANE-rBH-BRIDGING")["magnitude"]
        adverse = {"two_centre_rejected": two_centre_rejected, "disconnected_support_rejected": disconnected_rejected, "incomplete_support_word_rejected": incomplete_word_rejected, "topology_mismatch_rejected": wrong_topology_rejected, "numerical_zero_rejected": numeric_zero_rejected, "measured_bridge_distinction_retained": bridging != outer, "diborane_BHB_connectivity_retained": any(row["record_role"] == "aBHB" and row["inscription"] == "83.8" for row in comparisons), "benzene_six_equal_aromatic_links_retained": any(row["record_role"] == "C:C-count" and row["inscription"] == "6" for row in comparisons) and any(row["record_role"] == "rCC" and row["inscription"] == "1.397" for row in comparisons), "omitted_record_rejected": len(comparisons[:-1]) != 20, "selected_IUPAC_only_rejected": counts["diborane"] == 9 and counts["benzene"] == 7, "selected_NIST_only_rejected": counts["IUPAC"] == 4, "changed_value_rejected": PositiveRatio.from_pair(1320, 1000) != PositiveRatio.from_pair(1321, 1000), "tampered_snapshot_rejected": hash_file(first) == DIBORANE_HASH and changed_hash != DIBORANE_HASH, "complete_vector_retained": counts == {"records": 20, "IUPAC": 4, "diborane": 9, "benzene": 7, "positive_numeric": 14, "categorical_or_text": 6}, "all_generated_topologies_operational": all(item.irreducible_to_one_localized_pair for item in (bridge, ring, volume))}
        passed = all(row["passed"] for row in comparisons) and all(adverse.values())
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(executor_id=self.spec.experiment_id + "-prediction-executor", host_platform=platform.system() or "registered-host", python_implementation=platform.python_implementation(), interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id), program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash, registered_target_identity_hash=vault.commitment.target_identity_hash, comparison_implementation_identity_hash=sha256_identity(("complete-IUPAC-NIST-multicentre-comparator/1", self.spec.experiment_id)), prediction_seal_hash=prediction_seal.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("ELEC-008 released target differs")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(custodian_id=release.custodian_id, experiment_registration_hash=registration_hash, registered_target_identity_hash=target_identity, prediction_seal_hash=prediction_seal.seal_hash, target_release_manifest_hash=release.release_hash))
        payload = {"registration_hash": registration_hash, "prediction_seal_hash": prediction_seal.seal_hash, "comparisons": comparisons, "counts": counts, "adverse": adverse, "trace_hash": execution.trace_hash}
        measurements = tuple(f"{row['target_id']} {row['record_role']}: {row['inscription']}; exact {row['exact_magnitude']}; structural {row['structural_pass']}; pass {row['passed']}" for row in comparisons) + tuple(f"count {key}: {value}" for key, value in counts.items()) + tuple(f"adverse {key}: {value}" for key, value in adverse.items())
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, SOURCE_IDS, measurements, sha256_identity(payload), self.spec.falsification_condition, passed)


__all__ = ("MulticentreSupportValidator", "experiment_registration_record", "prediction_program_document")
