#!/usr/bin/env python3
"""Preregister Earth evidence custodians after the complete pre-source seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "publications/inventories/earth_environment.json"
SEAL_PATH = ROOT / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json"
REGISTRY_PATH = ROOT / "experiments/earth_environment/source_registry.json"
BINDINGS_PATH = ROOT / "experiments/earth_environment/claim_source_bindings.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source(source_id: str, custodian: str, title: str, locator: str, kind: str, families: tuple[str, ...], features: tuple[str, ...], *, access: str = "public_https") -> dict[str, object]:
    row = {
        "source_id": source_id,
        "custodian": custodian,
        "title": title,
        "locator": locator,
        "source_kind": kind,
        "families": list(families),
        "registered_features": list(features),
        "access_class": access,
        "outcome_values_registered": False,
        "selected_by": "purpose-matched Earth question and authoritative custody, after the complete derivation seal",
    }
    row["source_identity"] = digest(row)
    return row


SOURCES = (
    source("NASA-EARTHDATA-SEARCH-001", "NASA Earth Science Data and Information System", "Earthdata Search data discovery and access", "https://www.earthdata.nasa.gov/data/tools/earthdata-search", "authoritative_data_catalog", ("earth_system_observation", "evidence_hazard_handoffs"), ("dataset identity", "spatial and temporal coverage", "instrument or platform provenance", "download or service access")),
    source("USGS-LANDSAT-ACCESS-001", "U.S. Geological Survey Landsat Missions", "Landsat Data Access", "https://www.usgs.gov/landsat-missions/landsat-data-access", "authoritative_remote_sensing_archive", ("earth_system_observation", "evidence_hazard_handoffs", "environmental_transport_quality"), ("sensor and mission identity", "Earth surface observation", "archive access", "product and processing distinction")),
    source("USGS-NGMDB-001", "U.S. Geological Survey National Cooperative Geologic Mapping Program", "National Geologic Map Database", "https://ngmdb.usgs.gov/", "authoritative_geoscience_archive", ("geological_material_history", "interior_geodynamics"), ("spatially referenced geology", "map and report provenance", "stratigraphic information", "geochemistry geophysics palaeontology and geochronology coverage")),
    source("USGS-SOIL-GEOCHEM-001", "U.S. Geological Survey", "Soil geochemistry and mineralogy data portal", "https://mrdata.usgs.gov/soilgeochemistry/", "authoritative_soil_observation_archive", ("geological_material_history", "environmental_transport_quality"), ("soil specimen location", "geochemical composition", "mineralogical composition", "spatial coverage")),
    source("EARTHSCOPE-SAGE-SERVICES-001", "NSF SAGE Facility operated by EarthScope Consortium", "Seismological and geophysical web services", "https://service.iris.edu/", "authoritative_geophysical_data_service", ("interior_geodynamics", "seismic_volcanic", "evidence_hazard_handoffs"), ("station and channel identity", "waveform and event access", "instrument response", "observed and derived product distinction")),
    source("USGS-GEOMAG-OBSERVATORIES-001", "U.S. Geological Survey Geomagnetism Program", "USGS geomagnetic observatory operations", "https://geomag.usgs.gov/operations/observatory?mode=read", "authoritative_geomagnetic_observation_network", ("interior_geodynamics",), ("observatory identity", "time-bounded geomagnetic observation", "station status", "read-only access")),
    source("USGS-EARTHQUAKE-FDSN-001", "U.S. Geological Survey Earthquake Hazards Program", "FDSN Earthquake Catalog web service", "https://earthquake.usgs.gov/fdsnws/event/1/", "authoritative_event_catalog_api", ("seismic_volcanic", "evidence_hazard_handoffs"), ("event identity", "origin time and location", "magnitude and magnitude type", "catalog query boundary", "service version")),
    source("SMITHSONIAN-GVP-VOTW-001", "Smithsonian Institution Global Volcanism Program", "Volcanoes of the World web services", "https://volcano.si.edu/database/webservices.cfm", "authoritative_volcano_eruption_database", ("seismic_volcanic", "geological_material_history"), ("volcano identity", "eruption identity and time", "location and morphology", "database version and citation")),
    source("USGS-NWIS-001", "U.S. Geological Survey Water Resources", "National Water Information System", "https://waterdata.usgs.gov/nwis/", "authoritative_hydrological_observation_network", ("hydrosphere_cryosphere", "planetary_budgets"), ("site identity", "surface water and groundwater observations", "time series", "parameter units and methods")),
    source("WQP-WEB-SERVICES-001", "U.S. Geological Survey, U.S. Environmental Protection Agency and National Water Quality Monitoring Council", "Water Quality Portal web services", "https://www.waterqualitydata.us/webservices_documentation/", "authoritative_water_quality_federation", ("hydrosphere_cryosphere", "biogeochemical_ecological", "environmental_transport_quality"), ("station and organization identity", "sample and result identity", "characteristic and unit", "quality and metadata fields")),
    source("NSIDC-SEA-ICE-INDEX-001", "National Snow and Ice Data Center", "Sea Ice Index data and image archive", "https://nsidc.org/data/seaice_index/data-and-image-archive", "authoritative_cryosphere_data_product", ("hydrosphere_cryosphere", "ocean_coast", "climate_system"), ("hemisphere and date identity", "extent and area distinction", "daily and monthly data", "missing-data and product-version documentation")),
    source("NOAA-GHCND-001", "NOAA National Centers for Environmental Information", "Global Historical Climatology Network Daily", "https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily", "authoritative_station_climate_archive", ("atmosphere_weather", "climate_system", "evidence_hazard_handoffs"), ("station identity and metadata", "daily weather observations", "quality flags", "record length and variable coverage", "archive version")),
    source("NASA-CERES-EBAF-001", "NASA Langley Research Center CERES", "CERES Energy Balanced and Filled data products", "https://ceres.larc.nasa.gov/Data/", "authoritative_radiative_budget_data_product", ("planetary_budgets", "atmosphere_weather", "climate_system"), ("top-of-atmosphere and surface boundary", "shortwave and longwave flux distinction", "cloud and clear-sky distinction", "spatial and temporal resolution", "data-quality documentation")),
    source("NOAA-GML-CO2-001", "NOAA Global Monitoring Laboratory", "Carbon-cycle greenhouse-gas measurements", "https://gml.noaa.gov/ccgg/data/getdata.php?gas=co2", "authoritative_atmospheric_composition_archive", ("atmosphere_weather", "climate_system", "biogeochemical_ecological", "planetary_budgets"), ("gas and measurement programme identity", "site and altitude", "time and frequency", "calibration and data-use policy", "source and sink interpretation separated from measurement")),
    source("NOAA-WOD-001", "NOAA National Centers for Environmental Information", "World Ocean Database", "https://www.ncei.noaa.gov/products/world-ocean-database", "authoritative_ocean_profile_archive", ("ocean_coast", "planetary_budgets", "biogeochemical_ecological"), ("cast cruise and accession identity", "depth location and time", "temperature salinity nutrients and plankton", "quality flags", "original-source provenance")),
    source("ARGO-DATA-001", "Argo Data Management Team", "Argo profile and trajectory data access", "https://argo.ucsd.edu/data/", "authoritative_ocean_observing_program", ("ocean_coast", "climate_system"), ("float and profile identity", "depth temperature salinity and trajectory", "real-time and delayed-mode quality distinction", "quality-control flags")),
    source("NOAA-PALEO-001", "NOAA National Centers for Environmental Information World Data Service for Paleoclimatology", "Paleoclimatology data archive", "https://www.ncei.noaa.gov/products/paleoclimatology", "authoritative_proxy_archive", ("geological_material_history", "climate_system", "evidence_hazard_handoffs"), ("archive and study identity", "proxy and reconstructed-variable distinction", "dating and temporal coverage", "location and investigator provenance")),
    source("EPA-AIRDATA-001", "U.S. Environmental Protection Agency", "AirData pre-generated monitoring files", "https://aqs.epa.gov/aqsweb/airdata/download_files.html", "authoritative_air_quality_archive", ("environmental_transport_quality", "atmosphere_weather"), ("site and monitor identity", "pollutant parameter and units", "hourly daily and annual distinction", "method and quality metadata", "blank and missing records")),
    source("NEON-OPEN-DATA-001", "U.S. National Science Foundation National Ecological Observatory Network", "NEON open ecosystem data", "https://www.neonscience.org/data", "authoritative_ecosystem_observation_program", ("biogeochemical_ecological", "environmental_transport_quality"), ("site and data-product identity", "organismal and abiotic observations", "collection method", "availability and latency")),
    source("GBIF-OCCURRENCE-API-001", "Global Biodiversity Information Facility", "GBIF Occurrence API", "https://techdocs.gbif.org/en/openapi/v1/occurrence", "authoritative_biodiversity_data_federation", ("biogeochemical_ecological",), ("occurrence and dataset identity", "taxon location date and basis of record", "publishing organization", "paging limits and download distinction")),
    source("SCHUMANN-MAGNETOMETER-2018-001", "Virgo and KAGRA magnetometer measurement collaboration", "Measurement and subtraction of Schumann resonances at gravitational-wave interferometers", "https://arxiv.org/abs/1802.00885", "primary_measurement_study", ("atmosphere_weather",), ("independent site identity", "magnetometer spectrum", "correlated Earth-scale resonance", "frequency-resolved measured peaks", "instrumental subtraction boundary")),
)


FAMILY_SOURCE_IDS = {
    "earth_system_observation": ("NASA-EARTHDATA-SEARCH-001", "USGS-LANDSAT-ACCESS-001", "NOAA-GHCND-001"),
    "planetary_budgets": ("NASA-CERES-EBAF-001", "NOAA-GML-CO2-001", "NOAA-WOD-001", "USGS-NWIS-001"),
    "geological_material_history": ("USGS-NGMDB-001", "USGS-SOIL-GEOCHEM-001", "NOAA-PALEO-001", "SMITHSONIAN-GVP-VOTW-001"),
    "interior_geodynamics": ("EARTHSCOPE-SAGE-SERVICES-001", "USGS-GEOMAG-OBSERVATORIES-001", "USGS-NGMDB-001"),
    "seismic_volcanic": ("USGS-EARTHQUAKE-FDSN-001", "EARTHSCOPE-SAGE-SERVICES-001", "SMITHSONIAN-GVP-VOTW-001"),
    "hydrosphere_cryosphere": ("USGS-NWIS-001", "WQP-WEB-SERVICES-001", "NSIDC-SEA-ICE-INDEX-001"),
    "atmosphere_weather": ("NOAA-GHCND-001", "NASA-CERES-EBAF-001", "NOAA-GML-CO2-001", "EPA-AIRDATA-001"),
    "ocean_coast": ("NOAA-WOD-001", "ARGO-DATA-001", "NSIDC-SEA-ICE-INDEX-001"),
    "climate_system": ("NOAA-GHCND-001", "NASA-CERES-EBAF-001", "NOAA-GML-CO2-001", "NSIDC-SEA-ICE-INDEX-001", "NOAA-PALEO-001"),
    "biogeochemical_ecological": ("NOAA-GML-CO2-001", "NOAA-WOD-001", "WQP-WEB-SERVICES-001", "NEON-OPEN-DATA-001", "GBIF-OCCURRENCE-API-001"),
    "environmental_transport_quality": ("EPA-AIRDATA-001", "WQP-WEB-SERVICES-001", "USGS-LANDSAT-ACCESS-001", "NEON-OPEN-DATA-001"),
    "evidence_hazard_handoffs": ("NASA-EARTHDATA-SEARCH-001", "USGS-LANDSAT-ACCESS-001", "NOAA-GHCND-001", "NOAA-PALEO-001", "EARTHSCOPE-SAGE-SERVICES-001"),
}


CLAIM_OVERRIDES = {
    "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001": ("USGS-EARTHQUAKE-FDSN-001",),
    "SFT-EARTH-EARTH-IONOSPHERE-RESONANCE-001": ("SCHUMANN-MAGNETOMETER-2018-001", "EARTHSCOPE-SAGE-SERVICES-001"),
    "SFT-EARTH-EARTH-SYSTEM-TIPPING-001": ("NOAA-PALEO-001", "NOAA-GHCND-001", "NSIDC-SEA-ICE-INDEX-001"),
}


def main() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    seal = json.loads(SEAL_PATH.read_text(encoding="utf-8"))
    if seal["external_source_identities_selected"] is not False or seal["external_outcomes_opened"] is not False:
        raise ValueError("Earth derivations were not sealed before source registration")
    if seal["inventory_hash"] != inventory["inventory_hash"]:
        raise ValueError("Earth pre-source seal binds another inventory")

    registry = {
        "schema": "sft-v3-earth-environment-source-registry/1",
        "registration_date": "2026-07-28",
        "complete_pre_source_seal": seal["complete_branch_pre_source_seal_hash"],
        "selection_policy": "Authoritative primary data custodian or primary measurement study selected by the sealed Earth question; no source outcome may change the derivation, candidate grammar or survivor.",
        "transport_policy": "Capture each registered locator once per declared attempt; preserve successful, failed, denied, moved, absent and partial transports.",
        "source_count": len(SOURCES),
        "sources": list(SOURCES),
        "outcome_values_opened_during_registration": False,
    }
    registry["registry_hash"] = digest(registry)
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    source_ids = {row["source_id"] for row in SOURCES}
    bindings = []
    for obligation in inventory["obligations"]:
        selected = CLAIM_OVERRIDES.get(obligation["claim_id"], FAMILY_SOURCE_IDS[obligation["family"]])
        if not set(selected) <= source_ids:
            raise ValueError(f"unregistered Earth source binding: {obligation['claim_id']}")
        bindings.append({
            "claim_id": obligation["claim_id"],
            "family": obligation["family"],
            "source_ids": list(selected),
            "sealed_predicted_observation_label": obligation["predicted_observation_label"],
            "comparison_target_identity": obligation["claim_id"].lower() + "-external-earth-evidence",
            "required_evidence_features": [
                "claim-specific carrier or state is represented",
                "source, place, time or sample provenance is retained",
                "measurement, retrieval, reconstruction or model evidence class is identifiable",
                "quality, uncertainty, missingness or access boundary is retained where supplied",
            ],
            "exact_numeric_test": "presealed_unit_exponent_against_complete_catalog" if obligation["claim_id"] == "SFT-EARTH-QUAKE-MAGNITUDE-FREQUENCY-001" else None,
            "measurement_cannot_select_survivor": True,
        })
    binding_doc = {
        "schema": "sft-v3-earth-environment-claim-source-bindings/1",
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "registry_hash": registry["registry_hash"],
        "claim_count": len(bindings),
        "claims": bindings,
    }
    binding_doc["bindings_hash"] = digest(binding_doc)
    BINDINGS_PATH.write_text(json.dumps(binding_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "external_source_identities_preregistered_capture_not_yet_executed",
        "source_registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "source_registry_hash": registry["registry_hash"],
        "registered_source_count": len(SOURCES),
        "claim_source_bindings_path": str(BINDINGS_PATH.relative_to(ROOT)),
        "claim_source_bindings_hash": binding_doc["bindings_hash"],
        "next_exact_operation": "capture_all_registered_source_transports_and_preserve_every_outcome",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered Earth external sources: sources={len(SOURCES)} claims={len(bindings)} registry={registry['registry_hash']}")


if __name__ == "__main__":
    main()
