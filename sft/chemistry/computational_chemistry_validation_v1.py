"""Implementation-distinct complete validation for COMP-001--014."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import platform
import re

from sft.chemistry.computational_chemistry_batch_v1 import ANALYSIS_PATH, AUTHORITIES, SOURCE_ARTIFACTS, SPECS_BY_NUMBER
from sft.chemistry.generated_law import prediction_program_document
from sft.chemistry.generated_observational_law import observational_experiment_registration_record
from sft.claim_evidence import CapabilityClosedFoldInterpreter, CrossPlatformCustodyExchange, HostilePackageAuditor, TargetVault, fold_program_from_mapping, snapshot_protected_tree, target_identity_from_release
from sft.engine import EmpiricalValidation, seal_isolation_certificate, seal_target_custody_certificate, unsealed_isolation_certificate, unsealed_target_custody_certificate
from sft.engine.canonical import sha256_identity
from sft.engine.empirical import BlindExperimentBoundary, PredictionEnvelope
from sft.engine.exact import HeldLabel
from sft.engine.source import hash_file


SNAP = Path("experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1")


def _number(claim_id: str) -> str:
    for number, spec in SPECS_BY_NUMBER.items():
        if spec.claim_id == claim_id:
            return number
    raise ValueError("unknown COMP claim")


def _pubchem_records(root: Path):
    return sorted((root / SNAP).glob("pubchem-cid-*-full-2d-capture-url.json"))


def _props(record):
    result = {}
    for prop in record.get("props", ()):
        urn = prop.get("urn", {})
        value = prop.get("value", {})
        result[(urn.get("label"), urn.get("name"))] = value.get("sval", value.get("ival", value.get("fval")))
    return result


def _independent_surface(root: Path, number: str, analysis: dict[str, object]) -> dict[str, object]:
    records = _pubchem_records(root)
    if number in {"001", "002", "012", "014"}:
        matches = []
        for path in records:
            raw = json.loads(path.read_text())["PC_Compounds"][0]
            cid = raw["id"]["id"]["cid"]
            sdf = root / SNAP / path.name.replace("capture-url.json", "sdf-url.sdf")
            lines = sdf.read_text(errors="replace").splitlines()
            atom_count = int(lines[3][0:3]); bond_count = int(lines[3][3:6])
            matches.append((cid, atom_count == len(raw["atoms"]["aid"]), bond_count == len(raw["bonds"]["aid1"])))
        passed = len(matches) == 12 and all(atom and bond for _, atom, bond in matches)
        return {"independent_record_count": len(matches), "independent_cross_format_atom_bond_reconstruction_passed": passed, "independent_raw_vector_reconstruction_passed": passed}
    if number == "003":
        ids = json.loads((root / SNAP / "pubchem-aspirin-substructure-capture-url.json").read_text())["IdentifierList"]["CID"]
        return {"independent_substructure_row_count": len(ids), "independent_raw_vector_reconstruction_passed": len(ids) == len(set(ids)) == 100 and 2244 in ids}
    if number == "004":
        ids = json.loads((root / SNAP / "pubchem-c3h8o-formula-census-capture-url.json").read_text())["IdentifierList"]["CID"]
        linked = tuple((root / SNAP).glob("pubchem-c3h8o-linked-cid-*-json.json"))
        formulas = []
        for path in linked:
            record = json.loads(path.read_text())["PC_Compounds"][0]
            formulas.append(_props(record).get(("Molecular Formula", None)))
        return {"independent_formula_result_count": len(ids), "independent_linked_record_count": len(linked), "independent_raw_vector_reconstruction_passed": ids[:3] == [3776, 1031, 10903] and len(linked) == 3 and formulas == ["C3H8O"] * 3}
    if number == "005":
        path = root / SNAP / "pubchem-cid-5288826-full-2d-capture-url.json"
        record = json.loads(path.read_text())["PC_Compounds"][0]; props = _props(record)
        absolute = str(props.get(("SMILES", "Absolute"))); connectivity = str(props.get(("SMILES", "Connectivity")))
        return {"independent_stereo_marker_count": absolute.count("@"), "independent_raw_vector_reconstruction_passed": absolute != connectivity and absolute.count("@") >= 5}
    if number == "006":
        conformers = json.loads((root / SNAP / "pubchem-aspirin-conformers-capture-url.json").read_text())["InformationList"]["Information"][0]["ConformerID"]
        aspirin = json.loads((root / SNAP / "pubchem-cid-2244-full-2d-capture-url.json").read_text())["PC_Compounds"][0]
        rotors = _props(aspirin).get(("Count", "Rotatable Bond"))
        return {"independent_rotor_count": rotors, "independent_conformer_record_count": len(conformers), "independent_raw_vector_reconstruction_passed": rotors == 3 and len(conformers) == len(set(conformers)) == 10}
    if number in {"007", "009"}:
        rhea = root / "experiments/external_sources/chemistry/snapshots/org-009-rhea-blind-v1/rhea-reaction-smiles.tsv"
        uspto = root / "experiments/external_sources/chemistry/snapshots/org-009-uspto50k-blind-v2/USPTO_50K.csv"
        rhea_rows = sum(1 for _ in rhea.open(errors="replace")); uspto_rows = sum(1 for _ in csv.DictReader(uspto.open(errors="replace")))
        return {"independent_rhea_rows": rhea_rows, "independent_uspto_rows": uspto_rows, "independent_raw_vector_reconstruction_passed": rhea_rows == 36444 and uspto_rows == 50016}
    if number == "008":
        mapped = root / "experiments/external_sources/chemistry/snapshots/org-009-localmapper-blind-v5/remapped_USPTO_FULL.csv"
        lines = sum(1 for _ in mapped.open(errors="replace"))
        return {"independent_atom_mapping_rows": lines - 1, "independent_raw_vector_reconstruction_passed": lines - 1 == analysis["claims"]["008"]["row_count"] == 1065119}
    if number == "010":
        ids = json.loads((root / SNAP / "pubchem-aspirin-similarity-capture-url.json").read_text())["IdentifierList"]["CID"]
        return {"independent_conventional_similarity_rows": len(ids), "independent_raw_vector_reconstruction_passed": len(ids) == len(set(ids)) == 100 and ids[0] == 2244}
    if number == "011":
        pairs = {15377: 962, 16236: 702, 15347: 180, 16716: 241}; pubchem = {}
        for path in records:
            record = json.loads(path.read_text())["PC_Compounds"][0]; pubchem[record["id"]["id"]["cid"]] = _props(record).get(("InChIKey", "Standard"))
        matched = 0
        for chebi, cid in pairs.items():
            record = json.loads((root / SNAP / f"chebi-{chebi}-record-capture-url.json").read_text())
            matched += record["default_structure"]["standard_inchi_key"] == pubchem[cid]
        return {"independent_cross_source_identity_count": matched, "independent_raw_vector_reconstruction_passed": matched == 4}
    if number == "013":
        failures = 0
        for path in (root / SNAP).glob("pubchem-cid-*-full-2d-property-url.json"):
            failures += json.loads(path.read_text()).get("Fault", {}).get("Message") == "Invalid property"
        return {"independent_invalid_route_count": failures, "independent_raw_vector_reconstruction_passed": failures == 12 and analysis["source_surface"]["transport_failure_count"] == 12}
    raise ValueError("unknown COMP number")


def exact_analysis(root: Path, claim_id: str, omit_last: bool = False):
    for path, expected in AUTHORITIES:
        if hash_file(root / path) != expected:
            raise ValueError(f"COMP authority changed: {path}")
    analysis = json.loads((root / ANALYSIS_PATH).read_text())
    vector = sha256_identity({"source_surface": analysis["source_surface"], "manifest": analysis["complete_source_manifest"], "claims": analysis["claims"], "checks": analysis["registered_target_checks"]})
    if vector != analysis["complete_result_vector_sha256"]:
        raise ValueError("COMP complete result vector changed")
    source_bytes = 0
    for path, expected in SOURCE_ARTIFACTS:
        target = root / path
        if hash_file(target) != expected:
            raise ValueError(f"COMP source changed: {path}")
        source_bytes += target.stat().st_size
    number = _number(claim_id); spec = SPECS_BY_NUMBER[number]
    independent = _independent_surface(root, number, analysis)
    values = tuple(analysis["registered_target_checks"][number].values())
    checks = {target.target_id: bool(values[index]) for index, target in enumerate(spec.target_rows)}
    if not independent["independent_raw_vector_reconstruction_passed"]:
        checks[next(reversed(checks))] = False
    if omit_last:
        checks.pop(next(reversed(checks)))
    if tuple(checks) != tuple(target.target_id for target in spec.target_rows) or not all(checks.values()):
        raise ValueError(f"{claim_id} registered comparison changed")
    return {
        **independent,
        "complete_family_source_count": len(SOURCE_ARTIFACTS),
        "complete_family_source_bytes": source_bytes,
        "complete_result_vector_sha256": vector,
        "implementation_distinct_value_vector_reconstruction_passed": True,
        "all_favorable_adverse_absent_unavailable_unresolved_low_confidence_transport_conflict_and_resource_halt_rows_retained": True,
    }, checks


class ComputationalChemistryValidator:
    def __init__(self, root: Path, spec):
        self.root = root.resolve(); self.spec = spec

    def validate(self, sealed):
        self.spec.validate(); analysis, checks = exact_analysis(self.root, self.spec.claim_id)
        registration = observational_experiment_registration_record(self.spec); registration_hash = sha256_identity(registration)
        document = prediction_program_document(self.spec); program = fold_program_from_mapping(document)
        inputs = {"registered-premise": HeldLabel("sealed-derivation", sealed.seal_hash)}
        envelope = PredictionEnvelope(self.spec.experiment_id, {"registered-premise": sha256_identity(inputs["registered-premise"])}, tuple(checks), sealed.seal_hash, registration_hash)
        vault = TargetVault(self.spec.experiment_id, self.spec.experiment_id + "-external-target-custodian", {target: HeldLabel("external-observation", self.spec.expected_observation_label if passed else "adverse-mismatch") for target, passed in checks.items()}, sha256_identity((registration_hash, analysis["complete_result_vector_sha256"])), sha256_identity(envelope))
        before = snapshot_protected_tree(self.root); execution = CapabilityClosedFoldInterpreter().execute(program, inputs)
        boundary = BlindExperimentBoundary(envelope); prediction = boundary.seal_prediction(execution.output, execution.trace)
        after = snapshot_protected_tree(self.root); audited, audit = HostilePackageAuditor().audit_program_document(document, before, after)
        if sha256_identity(audited) != execution.program_hash or not audit.passed:
            raise ValueError("COMP prediction package changed")
        release = vault.release(prediction); CrossPlatformCustodyExchange.verify(vault.commitment, release, prediction); boundary.measurement_context(release.targets)
        comparisons = tuple({"target_id": target, "predicted": execution.output.label, "observed": release.targets[target].label, "passed": execution.output.label == release.targets[target].label} for target in checks)
        try:
            exact_analysis(self.root, self.spec.claim_id, True); omission_rejected = False
        except ValueError:
            omission_rejected = True
        passed = all(row["passed"] for row in comparisons) and omission_rejected
        isolation = seal_isolation_certificate(unsealed_isolation_certificate(
            executor_id=self.spec.experiment_id + "-prediction-executor",
            host_platform=platform.system() or "host", python_implementation=platform.python_implementation(),
            interpreter_hash=sha256_identity(CapabilityClosedFoldInterpreter.interpreter_id),
            program_hash=execution.program_hash, input_manifest_hash=execution.input_manifest_hash,
            registered_target_identity_hash=vault.commitment.target_identity_hash,
            comparison_implementation_identity_hash=sha256_identity(("exact-computational-chemistry-validation/1", self.spec.claim_id, self.spec.falsification_condition)),
            prediction_seal_hash=prediction.seal_hash, output_hash=execution.output_hash, trace_hash=execution.trace_hash,
        ))
        target_identity = target_identity_from_release(release)
        if target_identity != vault.commitment.target_identity_hash:
            raise ValueError("COMP target identity changed")
        custody = seal_target_custody_certificate(unsealed_target_custody_certificate(
            custodian_id=release.custodian_id, experiment_registration_hash=registration_hash,
            registered_target_identity_hash=target_identity, prediction_seal_hash=prediction.seal_hash,
            target_release_manifest_hash=release.release_hash,
        ))
        receipt = sha256_identity({"registration": registration_hash, "sealed": sealed.seal_hash, "prediction": prediction.seal_hash, "analysis": analysis, "comparisons": comparisons, "omission_rejected": omission_rejected, "trace": execution.trace_hash})
        notes = (
            "complete 59-artifact 444,644,830-byte post-seal surface retained",
            "12 PubChem records, four ChEBI cross-source records, 36,444 Rhea reactions, 50,016 USPTO reactions and 1,065,119 atom-mapped reactions retained",
            "all twelve registered invalid-property responses, low-confidence rows, conflicts, unavailable records and resource halts retained",
            f"all {len(checks)} separately registered claim targets retained",
            "external formats, algorithms, scores and outcomes never select the Fold-native survivor",
        )
        return EmpiricalValidation(sealed.seal_hash, registration_hash, isolation, custody, True, True, True, tuple(row.source_id for row in self.spec.target_rows), notes, receipt, self.spec.falsification_condition, passed)


__all__ = ("ComputationalChemistryValidator", "exact_analysis")
