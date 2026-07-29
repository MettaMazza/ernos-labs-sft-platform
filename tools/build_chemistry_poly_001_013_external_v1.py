#!/usr/bin/env python3
"""Reconstruct the complete post-seal POLY-001--013 empirical surface."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

from bs4 import BeautifulSoup
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.polymer_chemistry_laws_v1 import (
    LAW_ROWS, PolymerGraph, PolymerNetwork, PolymerPopulation, PolymerTransition,
    chemistry_materials_handoff, degree_of_polymerization, degradation_balance,
    labelled_composition, phase_transition_trace, squared_radius_of_gyration,
    step_growth_chain_count,
)
from sft.engine.canonical import sha256_identity
from sft.engine.exact import HeldLabel, PositiveCount


MAIN = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/source-inventory-v1.json"
ADDENDUM = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-quantitative-addendum-v1/source-inventory-v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1/complete-postseal-analysis-v1.json"


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def exact(value: str | int) -> Fraction:
    return Fraction(str(value))


def rational(value: Fraction) -> dict[str, object]:
    return {"numerator": value.numerator, "denominator": value.denominator, "exact_inscription": str(value)}


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def source_text(path: Path) -> tuple[str, int, tuple[int, ...]]:
    if path.suffix.casefold() == ".pdf":
        reader = PdfReader(path)
        pages = tuple((page.extract_text() or "") for page in reader.pages)
        return "\n".join(pages), len(pages), tuple(len(page) for page in pages)
    text = BeautifulSoup(path.read_text(errors="replace"), "html.parser").get_text("\n")
    return text, 1, (len(text),)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("Polymer complete post-seal analysis already exists")
    inventories = (json.loads(MAIN.read_text()), json.loads(ADDENDUM.read_text()))
    captured: dict[str, dict[str, object]] = {}
    source_manifest = []
    extraction_adverse = []
    for inventory in inventories:
        for row in inventory["complete_source_manifest"]:
            if row["status"] not in {"captured", "preserved_existing_immutable_artifact"}:
                source_manifest.append(dict(row)); continue
            path = ROOT / row["path"]
            if sha(path) != row["sha256"]:
                raise SystemExit(f"source changed: {row['path']}")
            text, page_count, page_characters = source_text(path)
            captured[row["source_id"]] = {"text": text, "normalized": normalized(text), "path": row["path"], "sha256": row["sha256"]}
            item = dict(row)
            item.update({"extracted_page_count": page_count, "extracted_character_count": len(text), "page_character_counts": page_characters, "extraction_sha256": "sha256:" + hashlib.sha256(text.encode()).hexdigest()})
            source_manifest.append(item)
            if len(text.strip()) < 100:
                extraction_adverse.append({"source_id": row["source_id"], "status": "captured_bytes_text_extraction_unavailable_preserved", "extracted_character_count": len(text)})

    def require(source_id: str, *fragments: str) -> bool:
        if source_id not in captured:
            return False
        body = captured[source_id]["normalized"]
        return all(normalized(fragment) in body for fragment in fragments)

    # Complete post-seal value vectors. Decimal and signed inscriptions remain
    # source provenance; native reconstructions below use exact fractions only.
    srm2888 = {
        "classical": {"mn_g_mol": "6960", "mn_uncertainty_g_mol": "400", "mw_g_mol": "7190", "mw_uncertainty_g_mol": "570", "method_pair": ("NMR end groups", "static light scattering")},
        "maldi_interlaboratory": {"laboratory_count": 23, "mn_g_mol": "6610", "mn_sd_g_mol": "120", "mw_g_mol": "6740", "mw_sd_g_mol": "110", "mz_g_mol": "6860", "mz_sd_g_mol": "100"},
        "nmr_individual_mn_g_mol": ("7050", "6950", "6850", "6980", "6950"),
        "end_group_mass_u": "58",
        "method_direction": "all MALDI-TOF-MS experimental molecular-mass values reported lower than classical values",
    }
    srm2886 = {
        "mw_g_mol": "87000", "mw_expanded_uncertainty_g_mol": "6000",
        "intrinsic_viscosity_ml_g": "157.8", "intrinsic_viscosity_uncertainty_ml_g": "2.1",
        "dispersity_uncorrected": "1.21", "dispersity_column_broadening_corrected": "1.12",
        "adverse_status": "uncorrected value explicitly expected to be an overestimate",
    }
    pams_table4 = (
        ("A", "0", None, "1030", "1081", "1.05"), ("A", "2.9", None, "890", "1011", "1.24"),
        ("A", "8.9", None, "730", "920", "1.26"), ("A", "16.5", None, "603", "829", "1.37"),
        ("A", "42.5", "270", "270", "515", "1.91"), ("A", "73.4", "120", "114", "231", "2.03"),
        ("A", "81", "75", "74", "163", "2.20"),
        ("B", "0", "410", "410", "430", "1.05"), ("B", "6.5", "370", "357", "400", "1.12"),
        ("B", "10", "349", "346", "393", "1.14"), ("B", "39.5", "158", "149", "255", "1.71"),
        ("B", "49.5", "135", "139", "238", "1.71"), ("B", "58", "93", "88", "175", "1.98"),
        ("C", "0", "107", "104", "107", "1.03"), ("C", "4.0", "98", "97", "105", "1.08"),
        ("C", "8.1", "97", "94", "104", "1.11"), ("C", "18.9", "90", "85", "97", "1.14"),
        ("C", "27.3", "85", "80", "94", "1.18"), ("C", "32", "68", "75", "90", "1.20"),
        ("C", "40", "61", "69", "87", "1.26"),
    )
    pams_rows = tuple({"sample": row[0], "conversion_percent": row[1], "mn_osmometry_x1000_g_mol": row[2], "mn_gpc_x1000_g_mol": row[3], "mw_gpc_x1000_g_mol": row[4], "reported_dispersity": row[5]} for row in pams_table4)
    pams_ratio_checks = []
    for row in pams_rows:
        ratio = exact(row["mw_gpc_x1000_g_mol"]) / exact(row["mn_gpc_x1000_g_mol"])
        reported = exact(row["reported_dispersity"])
        delta = abs(ratio - reported)
        pams_ratio_checks.append({"sample": row["sample"], "conversion_percent": row["conversion_percent"], "reconstructed": rational(ratio), "reported": rational(reported), "within_display_resolution_one_hundredth": delta <= Fraction(1, 200), "absolute_difference": rational(delta)})
    pams_conflicts = tuple(row for row in pams_ratio_checks if not row["within_display_resolution_one_hundredth"])

    gel_phi = ("0.06", "0.09", "0.12", "0.17", "0.24", "0.28", "0.34", "0.37", "0.41", "0.46", "0.52")
    gel_temperature = ("27.7", "27.9", "28.2", "28.5", "28.6", "28.7", "28.9", "29.1", "29.4", "30.0", "30.8")
    gel_tau_fluid = ("0.130", "0.19", "0.27", "0.4", "0.45", "0.75", "0.76", "1.1", "1.2", "1.6", "1.8")
    gel_tau = ("0.096", "0.102", "0.132", "0.19", "0.28", "0.36", "0.55", "0.75", "0.9", "1.1", None)
    gel_rows = tuple({"volume_fraction": gel_phi[i], "transition_temperature_c": gel_temperature[i], "fluid_tau": gel_tau_fluid[i], "gel_tau": gel_tau[i], "gel_tau_status": "measured" if gel_tau[i] is not None else "absent_in_extracted_table_preserved"} for i in range(len(gel_phi)))

    pvoh_compositions = ("PVOH", "1/9", "2/8", "3/7", "4/6", "5/5", "6/4", "7/3")
    pvoh_phase_rows = tuple({"composition": pvoh_compositions[i], "tm_as_cast_c": value, "tg_heating_c": ("82", "62", "36", "28", "0", "-9", "-21", "-59")[i], "tg_cooling_c": ("68", "55", "29", "20", "9", "-2", "-30", None)[i], "tc_as_cast_c": ("199", "192", "164", "150", "121", "124", "66", "63")[i]} for i, value in enumerate(("224", "215", "192", "185", "163", "166", "133", "123")))

    deuterated_rows = tuple(dict(zip(("entry", "mn_theoretical_kg_mol", "mn_ri_kg_mol", "mn_ir_kg_mol", "dispersity_ri", "dispersity_ir", "d_theoretical_percent", "d_nmr_percent", "d_raman_percent", "cc_wavenumber_cm_inverse", "tm_c"), row)) for row in (
        ("I", "17.8", "16.7", "16.1", "1.25", "1.25", "100", "98.5", "95", "1144", "127.8"),
        ("II", "18.5", "20.3", "20.3", "1.16", "1.20", "74", "74.7", "73", "1142", "130.7"),
        ("III", "19.3", "17.6", "17.8", "1.18", "1.20", "50", "50.3", "53", "1139", "131.7"),
        ("IV", "17.6", "13.4", "13.4", "1.32", "1.36", "25", "25.0", "28", "1128", "130.4"),
    ))

    blend_phase = {
        "pla_mass_percent": ("0", "10", "30", "50", "70", "100"),
        "pla_2k_tg_c": ("-55.0", "-51.2", "-40.9", "-29.2", "-7.8", "27.1"),
        "pla_63k_tg1_c": ("-55.0", None, "-55.0", "-46.4", "-46.0", None),
        "pla_63k_tg2_c": (None, None, "-9.2", "-1.5", "22.4", "40.9"),
    }
    paired_handoff = tuple(dict(zip(("material", "break_strength_mpa", "break_strength_uncertainty_mpa", "break_strain_percent", "break_strain_uncertainty_percent", "elastic_modulus_mpa", "elastic_modulus_uncertainty_mpa", "work_of_fracture_j_m", "work_uncertainty_j_m"), row)) for row in (
        ("crosslinked-PEGDMA", "1.3", "0.1", "5.4", "0.7", "28.8", "3.2", "3.6", "0.5"),
        ("50-percent-PLA-2K", "1.0", "0.1", "14.4", "0.5", "9.4", "0.5", "7.2", "0.2"),
        ("30-percent-PLA-63K", "3.7", "0.5", "17.3", "2.2", "65.6", "13.9", "32.1", "5.7"),
        ("PLA-32-reference", "34.0", None, "4.0", None, "2600.0", None, None, None),
    ))

    # Native operational witnesses, independently of all conventional equations.
    population = PolymerPopulation(((Fraction(2), PositiveCount(3)), (Fraction(5), PositiveCount(2))))
    network = PolymerNetwork(("inactive", "active", "grown", "transferred", "terminal"), (
        PolymerTransition("inactive", "active", "initiation"), PolymerTransition("active", "grown", "propagation"),
        PolymerTransition("grown", "transferred", "transfer"), PolymerTransition("transferred", "terminal", "termination"),
    ))
    # The first pre-admission attempt used one degree-three vertex and therefore
    # correctly classified itself as a star/single-branch-centre.  This distinct
    # witness has two degree-three vertices and is the intended branched-acyclic
    # class.  The failed attempt is preserved in the POLY-008 correction audit.
    graph = PolymerGraph(
        tuple(HeldLabel("polymer-unit", str(i)) for i in range(1, 7)),
        (
            (PositiveCount(1), PositiveCount(2)),
            (PositiveCount(2), PositiveCount(3)),
            (PositiveCount(3), PositiveCount(4)),
            (PositiveCount(2), PositiveCount(5)),
            (PositiveCount(3), PositiveCount(6)),
        ),
    )
    native = {
        "001": degree_of_polymerization(Fraction(1042), Fraction(104), Fraction(2)) == 10,
        "002": population.number_average() == Fraction(16, 5),
        "003": population.mass_average() == Fraction(31, 8),
        "004": population.dispersity() == Fraction(155, 128),
        "005": network.operation_support() == ("initiation", "propagation", "termination", "transfer") and len(network.paths("inactive", "terminal")) == 1,
        "006": step_growth_chain_count(PositiveCount(5), PositiveCount(3)) == PositiveCount(2),
        "007": labelled_composition((HeldLabel("polymer-monomer", "a"), HeldLabel("polymer-monomer", "b"), HeldLabel("polymer-monomer", "a"))) == (("a", Fraction(2, 3)), ("b", Fraction(1, 3))),
        "008": graph.architecture().label == "branched-acyclic",
        "009": graph.finite_gel_certificate((PositiveCount(1),), (PositiveCount(5),))[0].label == "finite-boundaries-connected",
        "010": squared_radius_of_gyration(((Fraction(1),), (Fraction(3),))) == 1,
        "011": phase_transition_trace(((PositiveCount(1), HeldLabel("polymer-phase", "a")), (PositiveCount(2), HeldLabel("polymer-phase", "b")))) == ((2, "a", "b"),),
        "012": degradation_balance(PositiveCount(5), (PositiveCount(2), PositiveCount(3))),
        "013": chemistry_materials_handoff(("architecture",), ("bulk-property",))[1:] == ("chemistry", "materials"),
    }

    anchors = {
        "001": (("NIST-SRM-2888-POLYSTYRENE-CERTIFICATION", "molecular mass distribution", "end groups"), ("NIST-PRECISION-DEUTERATED-POLYETHYLENE", "degree of polymerization", "assuming 100 % conversion")),
        "002": (("NIST-SRM-2888-POLYSTYRENE-CERTIFICATION", "number-average molar mass", "interlaboratory comparison"), ("NIST-QUINTUPLE-DETECTOR-COPOLYMER", "number-average", "molar mass")),
        "003": (("NIST-SRM-2888-POLYSTYRENE-CERTIFICATION", "mass-average molar mass", "static light scattering"), ("NIST-SRM-2886-POLYETHYLENE-CERTIFICATION", "mass-average molar mass", "light scattering")),
        "004": (("NIST-SRM-2886-POLYETHYLENE-CERTIFICATION", "polydispersity index", "column broadening"), ("NIST-MONODISPERSE-PAMS-KINETIC-NETWORK", "molecular weight distribution", "conversion")),
        "005": (("NIST-STOCHASTIC-PHOTOPOLYMER-NETWORK-GROWTH", "initiation", "propagation"), ("NIST-MONODISPERSE-PAMS-KINETIC-NETWORK", "transfer", "termination")),
        "006": (("NIST-STOCHASTIC-PHOTOPOLYMER-NETWORK-GROWTH", "crosslink density", "network structure"), ("NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION", "degree of conversion", "cross-linked")),
        "007": (("NIST-RING-OPENING-COPOLYMER-SEQUENCE", "sequence distributions", "quantitative 13C NMR"), ("NIST-PRECISION-DEUTERATED-POLYETHYLENE", "statistical copolymerizations", "deuterium content")),
        "008": (("NIST-BRANCH-PLACEMENT-DILUTE-SOLUTION", "branch fraction", "branch spacing"), ("NIST-MACROMOLECULAR-ARCHITECTURES", "chain topologies", "sequence")),
        "009": (("NIST-THERMOREVERSIBLE-GELATION-PERCOLATION", "gel transition", "percolation"), ("NIST-BRIDGING-GELATION", "gelation boundaries", "bridging")),
        "010": (("NIST-QUINTUPLE-DETECTOR-COPOLYMER", "radius of gyration", "hydrodynamic radius"), ("NIST-BRANCH-PLACEMENT-DILUTE-SOLUTION", "radius of gyration", "branch fraction")),
        "011": (("NIST-PVOH-IONIC-LIQUID-GELATION", "glass transition temperature", "melting temperature"), ("NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION", "glass transition temperatures", "two Tgs")),
        "012": (("NIST-POLYMER-PYROLYSIS-NETWORK", "backbone scission", "products"), ("NIST-POLYMER-DEPOLYMERIZATION-KINETICS", "depolymerization", "monomer")),
        "013": (("NIST-CROSSLINKED-PHOTOPOLYMER-CONVERSION", "mechanical properties", "molecular mass"), ("NIST-POLYMER-PROCESSING-METROLOGY", "polymer", "processing")),
    }
    anchor_checks = {number: tuple({"source_id": source_id, "required_fragments": fragments, "passed": require(source_id, *fragments)} for source_id, *fragments in rows) for number, rows in anchors.items()}
    for number in LAW_ROWS:
        if not native[number] or not all(row["passed"] for row in anchor_checks[number]):
            raise SystemExit(f"POLY-{number} native or source reconstruction failed")

    target_results = {}
    for number in LAW_ROWS:
        identity = json.loads((ROOT / f"experiments/external_sources/chemistry/poly_{number}_target_identities_v1.json").read_text())
        checks = []
        for index, target_id in enumerate(identity["target_ids"]):
            anchor = anchor_checks[number][index % len(anchor_checks[number])]
            checks.append({"target_id": target_id, "source_id": anchor["source_id"], "native_operational_witness_passed": native[number], "source_anchor_passed": anchor["passed"], "passed": native[number] and anchor["passed"], "observed_label": f"complete-poly-{number}-postseal-source-vector"})
        target_results[LAW_ROWS[number]["claim_id"]] = checks

    analysis = {
        "schema": "sft-v3-polymer-chemistry-complete-postseal-analysis/1",
        "family": "POLY-001-013-QUANTITATIVE-POLYMER-CHEMISTRY",
        "complete_source_manifest": source_manifest,
        "complete_source_artifact_count": len(source_manifest),
        "complete_source_byte_count": sum(int(row.get("bytes", 0)) for row in source_manifest),
        "complete_source_page_count": sum(int(row.get("extracted_page_count", 0)) for row in source_manifest),
        "extraction_adverse_rows": extraction_adverse,
        "measurement_vectors": {
            "srm_2888": srm2888, "srm_2886": srm2886, "pams_table4_complete_rows": pams_rows,
            "pams_dispersity_reconstructions": pams_ratio_checks, "pams_extraction_or_display_conflicts_preserved": pams_conflicts,
            "thermoreversible_gel_table_complete_rows": gel_rows, "pvoh_phase_table_complete_rows": pvoh_phase_rows,
            "deuterated_polyethylene_complete_rows": deuterated_rows, "crosslinked_blend_phase_complete_rows": blend_phase,
            "chemistry_materials_paired_handoff_rows": paired_handoff,
        },
        "exact_postseal_reconstructions": {
            "srm_2888_classical_dispersity": rational(exact("7190") / exact("6960")),
            "srm_2888_maldi_dispersity": rational(exact("6740") / exact("6610")),
            "srm_2886_uncorrected_dispersity": rational(exact("1.21")),
            "srm_2886_column_broadening_corrected_dispersity": rational(exact("1.12")),
            "pams_complete_row_count": len(pams_rows), "pams_preserved_conflict_count": len(pams_conflicts),
            "gel_complete_state_count": len(gel_rows), "gel_absent_cell_count": sum(row["gel_tau"] is None for row in gel_rows),
            "pvoh_complete_composition_count": len(pvoh_phase_rows), "deuterated_complete_composition_count": len(deuterated_rows),
            "paired_handoff_material_count": len(paired_handoff),
        },
        "native_operational_witnesses": native,
        "source_anchor_checks": anchor_checks,
        "target_results": target_results,
        "registered_target_count": sum(len(rows) for rows in target_results.values()),
        "registered_targets_passed": sum(row["passed"] for rows in target_results.values() for row in rows),
        "prior_exposure_disclosed": True,
        "unknown_target_forward_prediction_claimed": False,
        "external_value_equation_model_fit_sign_zero_or_outcome_selected_native_law": False,
        "all_favorable_adverse_absent_unavailable_conflicting_and_unresolved_rows_preserved": True,
    }
    vector = {claim_id: tuple((row["target_id"], row["source_id"], row["passed"], row["observed_label"]) for row in rows) for claim_id, rows in sorted(target_results.items())}
    analysis["complete_result_vector_sha256"] = sha256_identity(vector)
    OUTPUT.write_text(json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"analysis": sha(OUTPUT), "result_vector": analysis["complete_result_vector_sha256"], "sources": len(source_manifest), "bytes": analysis["complete_source_byte_count"], "pages": analysis["complete_source_page_count"], "targets": analysis["registered_target_count"], "passed": analysis["registered_targets_passed"], "preserved_conflicts": len(pams_conflicts), "extraction_adverse": len(extraction_adverse)}, sort_keys=True))


if __name__ == "__main__":
    main()
