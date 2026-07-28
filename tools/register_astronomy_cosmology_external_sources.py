#!/usr/bin/env python3
"""Preregister primary Astronomy evidence custodians after derivation seal."""

from __future__ import annotations

import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "experiments/astronomy_cosmology/source_registry.json"
BIND = ROOT / "experiments/astronomy_cosmology/claim_source_bindings.json"
TARGET = ROOT / "experiments/sealed_predictions/astronomy_cosmology_external_targets.json"

def digest(x): return "sha256:" + hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def source(sid, custodian, title, locator, families, features, kind="authoritative_public_archive"):
    row = {"source_id": sid, "custodian": custodian, "title": title, "locator": locator, "source_kind": kind, "families": list(families), "registered_features": list(features), "access_class": "public_https", "outcome_values_registered": False, "selected_by": "purpose-matched sealed Astronomy question and primary custody"}; row["source_identity"] = digest(row); return row

SOURCES = (
    source("ESA-GAIA-ARCHIVE-001", "European Space Agency", "Gaia ESA Archive", "https://gea.esac.esa.int/archive/", ("observation_geometry","object_identity_classification","radiation_motion_time","stellar_systems","galaxies_populations"), ("source identity","positions and parallaxes","proper and radial motion","photometry and spectra","release and known-issue boundary")),
    source("NASA-EXOPLANET-ARCHIVE-001", "NASA Exoplanet Science Institute", "NASA Exoplanet Archive", "https://exoplanetarchive.ipac.caltech.edu/", ("planetary_small_body","stellar_systems"), ("planet and candidate distinction","host identity","detection method","parameter uncertainty","archive release")),
    source("STSCI-MAST-001", "Space Telescope Science Institute", "Mikulski Archive for Space Telescopes", "https://archive.stsci.edu/", ("observation_geometry","radiation_motion_time","stellar_systems","interstellar_enrichment_formation","galaxies_populations"), ("mission and instrument identity","image spectrum and time series","calibration product level","programme and observation identity")),
    source("CDS-SIMBAD-001", "Centre de Donnees astronomiques de Strasbourg", "SIMBAD astronomical database", "https://simbad.cds.unistra.fr/simbad/", ("object_identity_classification","observation_geometry"), ("object identifiers","cross-identifications","bibliography","measurements","database-not-catalogue boundary")),
    source("MPC-DATA-SERVICES-001", "International Astronomical Union Minor Planet Center", "MPC Data Services", "https://data.minorplanetcenter.net/", ("planetary_small_body","observation_geometry"), ("designation identity","observations","orbits","submission status","negative observations")),
    source("SPARC-BTFR-001", "SPARC collaboration / Case Western Reserve University", "SPARC baryonic Tully-Fisher data", "https://astroweb.case.edu/SPARC/BTFR_Lelli2019.mrt", ("galaxies_populations",), ("galaxy identity","baryonic mass","rotation velocity","uncertainties","complete machine-readable rows"), "primary_measurement_dataset"),
    source("GWOSC-PUBLIC-001", "LIGO Virgo KAGRA collaborations", "Gravitational Wave Open Science Center", "https://gwosc.org/about/", ("compact_high_energy_multimessenger",), ("event identity","detector identity","strain and event products","public release and license")),
    source("ICECUBE-PUBLIC-DATA-001", "IceCube Collaboration", "IceCube public data releases", "https://icecube.wisc.edu/science/data-releases/", ("compact_high_energy_multimessenger",), ("event and sample identity","time direction and energy proxy","selection and livetime","release documentation")),
    source("NASA-HEASARC-001", "NASA High Energy Astrophysics Science Archive Research Center", "HEASARC data archive", "https://heasarc.gsfc.nasa.gov/docs/archive.html", ("compact_high_energy_multimessenger","stellar_systems","galaxies_populations"), ("mission observation and object catalogs","high-energy data products","calibration and documentation","public-access status")),
    source("NASA-LAMBDA-001", "NASA Goddard Space Flight Center", "Legacy Archive for Microwave Background Data Analysis", "https://lambda.gsfc.nasa.gov/", ("large_scale_expansion","early_background_abundance","dark_horizon_unobserved"), ("CMB archive identity","mission data","dataset identifiers","maps spectra likelihood and documentation")),
    source("DESI-DR1-001", "Dark Energy Spectroscopic Instrument Collaboration", "DESI public Data Release 1", "https://data.desi.lbl.gov/doc/", ("galaxies_populations","large_scale_expansion","dark_horizon_unobserved"), ("spectroscopic target identity","redshift","selection","release and data model","public files")),
    source("SDSS-DATA-001", "Sloan Digital Sky Survey", "SDSS public data", "https://www.sdss.org/dr19/data_access/", ("object_identity_classification","radiation_motion_time","galaxies_populations","large_scale_expansion"), ("imaging and spectra","catalogues","data release","selection and quality fields")),
    source("NASA-IRSA-001", "NASA Infrared Science Archive", "IRSA archives", "https://irsa.ipac.caltech.edu/frontpage/", ("stellar_systems","planetary_small_body","interstellar_enrichment_formation","galaxies_populations"), ("mission and survey identity","images spectra catalogues","infrared bands","provenance and access")),
    source("NASA-JPL-HORIZONS-001", "NASA Jet Propulsion Laboratory", "JPL Horizons system", "https://ssd.jpl.nasa.gov/horizons/", ("planetary_small_body",), ("target and center identity","ephemeris epoch","state and orbit","uncertainty and solution boundary")),
    source("NASA-ADS-001", "NASA Astrophysics Data System", "NASA ADS literature and data links", "https://ui.adsabs.harvard.edu/", ("inference_prediction_handoffs",), ("bibliographic identity","versioned record","data links","citation provenance")),
)

FAMILY = {
 "observation_geometry": ("ESA-GAIA-ARCHIVE-001","STSCI-MAST-001","CDS-SIMBAD-001"),
 "object_identity_classification": ("CDS-SIMBAD-001","ESA-GAIA-ARCHIVE-001","SDSS-DATA-001"),
 "radiation_motion_time": ("ESA-GAIA-ARCHIVE-001","STSCI-MAST-001","SDSS-DATA-001"),
 "stellar_systems": ("ESA-GAIA-ARCHIVE-001","STSCI-MAST-001","NASA-HEASARC-001"),
 "planetary_small_body": ("NASA-EXOPLANET-ARCHIVE-001","MPC-DATA-SERVICES-001","NASA-JPL-HORIZONS-001"),
 "interstellar_enrichment_formation": ("STSCI-MAST-001","NASA-IRSA-001","NASA-HEASARC-001"),
 "galaxies_populations": ("DESI-DR1-001","SDSS-DATA-001","NASA-IRSA-001"),
 "compact_high_energy_multimessenger": ("GWOSC-PUBLIC-001","ICECUBE-PUBLIC-DATA-001","NASA-HEASARC-001"),
 "large_scale_expansion": ("DESI-DR1-001","NASA-LAMBDA-001","SDSS-DATA-001"),
 "early_background_abundance": ("NASA-LAMBDA-001","NASA-HEASARC-001"),
 "dark_horizon_unobserved": ("NASA-LAMBDA-001","DESI-DR1-001","GWOSC-PUBLIC-001"),
 "inference_prediction_handoffs": ("NASA-ADS-001","NASA-LAMBDA-001","STSCI-MAST-001"),
}

def main():
    inv = json.loads((ROOT/"publications/inventories/astronomy_cosmology.json").read_text()); seal = json.loads((ROOT/"experiments/sealed_predictions/astronomy_cosmology_foundation_complete_pre_source.json").read_text())
    if seal["external_source_identities_selected"] is not False or seal["external_outcomes_opened"] is not False: raise ValueError("pre-source boundary violated")
    registry = {"schema":"sft-v3-astronomy-cosmology-source-registry/1","registration_date":"2026-07-28","complete_pre_source_seal":seal["complete_branch_pre_source_seal_hash"],"selection_policy":"Primary custodian selected by sealed purpose; source outcome cannot change grammar or survivor.","transport_policy":"Capture once and retain success, failure, denial, partial, moved, absent and adverse outcomes.","source_count":len(SOURCES),"sources":list(SOURCES),"outcome_values_opened_during_registration":False}; registry["registry_hash"] = digest(registry); REG.parent.mkdir(parents=True, exist_ok=True); REG.write_text(json.dumps(registry,indent=2,sort_keys=True)+"\n")
    claims=[]
    for x in inv["obligations"]:
        ids=("SPARC-BTFR-001",) if x["claim_id"]=="SFT-ASTRO-TULLY-FISHER-001" else FAMILY[x["family"]]
        claims.append({"claim_id":x["claim_id"],"family":x["family"],"source_ids":list(ids),"sealed_predicted_observation_label":x["predicted_observation_label"],"comparison_target_identity":x["claim_id"].lower()+"-external-astronomy-evidence","required_features":["carrier or state represented","source instrument epoch or release provenance retained","evidence class identifiable","quality uncertainty missingness or access boundary retained"],"exact_numeric_test":"presealed_rank_four_against_complete_btfr_rows" if x["claim_id"]=="SFT-ASTRO-TULLY-FISHER-001" else None,"measurement_cannot_select_survivor":True})
    bindings={"schema":"sft-v3-astronomy-cosmology-claim-source-bindings/1","registry_hash":registry["registry_hash"],"claim_count":len(claims),"claims":claims}; bindings["bindings_hash"]=digest(bindings); BIND.write_text(json.dumps(bindings,indent=2,sort_keys=True)+"\n")
    target={"schema":"sft-v3-astronomy-cosmology-external-target-seal/1","seal_date":"2026-07-28","complete_pre_source_seal":seal["complete_branch_pre_source_seal_hash"],"source_registry_hash":registry["registry_hash"],"targets":[{"target_id":"SFT-ASTRO-TULLY-FISHER-001-rank-four","claim_id":"SFT-ASTRO-TULLY-FISHER-001","source_id":"SPARC-BTFR-001","quantity":"slope of log10 baryonic mass on log10 flat rotation velocity","prediction":"exact integer rank four","rows":"all machine-readable rows with source-supplied finite mass and velocity","method":"unweighted exact-rational ordinary least squares on decimal source values; preserve result and all residuals; report incompatibility if the measured interval excludes four","outcome_opened":False}],"measurement_values_present":False}; target["target_seal_hash"]=digest(target); TARGET.write_text(json.dumps(target,indent=2,sort_keys=True)+"\n")
    cp=ROOT/"census/astronomy_cosmology_continuation_checkpoint.json"; c=json.loads(cp.read_text()); c.update({"status":"sources_and_value_free_external_targets_preregistered_capture_not_yet_executed","source_registry_path":str(REG.relative_to(ROOT)),"source_registry_hash":registry["registry_hash"],"registered_source_count":len(SOURCES),"claim_source_bindings_hash":bindings["bindings_hash"],"external_target_seal_hash":target["target_seal_hash"],"next_exact_operation":"capture_registered_sources_and_compare_without_reclassification"}); cp.write_text(json.dumps(c,indent=2,sort_keys=True)+"\n")
    print(f"Astronomy sources registered: sources={len(SOURCES)} claims={len(claims)} target={target['target_seal_hash']}")

if __name__ == "__main__": main()
