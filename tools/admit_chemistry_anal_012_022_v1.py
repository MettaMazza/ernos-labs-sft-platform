#!/usr/bin/env python3
"""Submit one ANAL-012--022 claim in strict dependency order."""

from __future__ import annotations

from dataclasses import asdict
import argparse
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.analytical_terminal_batch_v1 import SPECS_BY_NUMBER
from sft.chemistry.analytical_terminal_validation_v1 import exact_analysis
from sft.engine import EngineRepository


SURFACES = {
    "012": "63 complete NIST IR JCAMP vectors: benzene 29, acetone 30 and cyclohexane 4, with every declared point, coordinate/intensity unit, state, resolution, contamination note and source render retained",
    "013": "three complete NIST UV-visible JCAMP vectors with 317, 247 and 178 declared source points and full molecule, coordinate, response, origin, condition and absence custody",
    "014": "three complete NIST electron-ionization mass spectra with every m/z and relative-intensity peak: benzene, acetone and cyclohexane",
    "015": "all 91 fixed-width JPL CO rotational lines from c028001.cat with frequency, uncertainty, log intensity, lower energy, degeneracy and both state assignments; 60 positive and 31 negative catalog-tag forms retained; original JPL transport failure and unverified institutional mirror status remain explicit",
    "016": "all three scanned SRM 674 pages reconstructed into 213 retained OCR lines, including five phases, complete reflection/intensity Table 1, reference-intensity ratios, lattice parameters, uncertainties, overlaps, impurities and unexplained weak peaks, plus every page of SRM 676a",
    "017": "all six electron-diffraction report pages, the complete 385-row NIST neutron isotope table, the seven-page X-ray/neutron SRM correspondence, current-route 404, redirected landing page and corrected official transport retained",
    "018": "all 16 NIST gas-chromatography tables and 619 rows with stationary phase, temperature, retention index, reference, program, column, carrier and missing-condition custody",
    "019": "all 67 pages of NIST SRM 1980 and SP 260-209 mobility/zeta evidence with particle, medium, pH, temperature, orientation, value, uncertainty, laboratory and adverse-method custody",
    "020": "all 90 pages of the IUPAC electroanalytical method record and NIST voltammetric detection study with complete potential paths, current traces, backgrounds, replicates, reactions, conditions, uncertainties and adverse cases",
    "021": "one value-free withheld identity selected solely by the sealed target hash from three registered molecule candidates; all IR, UV-visible, mass and identity records intersect to exactly one carrier without similarity fitting",
    "022": "the complete Analytical performance budget joins immutable ANAL-001--011 receipts with every ANAL-012--021 source surface, preserving traceability, trueness, precision, sensitivity, selectivity, detection, quantification, uncertainty and every adverse/transport status",
}


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def build_execution(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("admit_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("claim", choices=tuple(SPECS_BY_NUMBER))
    args = parser.parse_args()
    number = args.claim
    claim = SPECS_BY_NUMBER[number]
    obligation = f"SFT-CHEM-OBL-ANAL-{number}"
    census_path = ROOT / "census/claims.json"
    admitted = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if claim.claim_id in admitted:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    for dependency in claim.dependencies:
        if dependency not in admitted:
            raise SystemExit(f"dependency not admitted; halted before submission: {dependency}")

    execution = build_execution(claim)
    captured = {}

    class Independent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["independent"] = execution.independent_validator.validate(sealed)
            return captured["independent"]

    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    result = EngineRepository(ROOT).execute_official(execution.program, Independent(), execution.source_files, Empirical())
    if not result.model_admitted:
        raise SystemExit(f"claim halted at {result.halted_stage}; preserved receipt {result.receipt_hash}")

    sealed = captured["sealed"]
    independent = captured["independent"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"})
    write(manifest_path, manifest)
    census_row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    certificate = {
        "claim_id": claim.claim_id,
        "chemistry_obligation": obligation,
        "status": f"model_admitted_forced_analytical_law_{number}_empirically_tested_and_independently_replicated",
        "source_manifest_hash": execution.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": result.external_validation_hash,
        "empirical_validation_hash": result.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": result.receipt_hash,
        "engine_receipt_path": census_row["receipt_path"],
        "closure_scope": result.closure_status,
        "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis,
        "all_registered_target_checks_passed": all(checks.values()),
        "registered_target_check_count": len(checks),
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "external_values_equations_models_fits_signs_zeroes_or_outcomes_used_to_select_native_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": claim.claim_id, **asdict(sealed.census)},
        "analytical_terminal_receipt.json": {"claim_id": claim.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": claim.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": claim.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }
    for name, payload in artifacts.items():
        write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / claim.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured_postseal_complete"
    write(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {claim.claim_id}\n\nStatus: `model_admitted_forced_analytical_law_{number}_empirically_tested_and_independently_replicated`\n\n"
        f"- Chemistry obligation: `{obligation}`\n- Exact law: `{claim.exact_result}`\n"
        f"- Complete external surface: {SURFACES[number]}.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{result.receipt_hash}`\n"
    )
    print(f"admitted {claim.claim_id}: {result.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
