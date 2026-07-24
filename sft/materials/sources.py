"""Post-seal authoritative Materials source identities.

Nothing in this module is imported by the target-blind derivation.  It was
created only after ``materials_complete_branch_pre_source.json`` fixed every
prediction.  Each source is an exact local byte snapshot issued by BIPM or
NIST, a national/international measurement body.  Source text can test a
sealed consequence but cannot alter its grammar or survivor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sft.engine.source import hash_file


@dataclass(frozen=True)
class MaterialsAuthoritySource:
    source_id: str
    body: str
    source_uri: str
    snapshot_path: str
    snapshot_hash: str
    evidence_scope: str


def _nist(source_id: str, uri: str, filename: str, digest: str, scope: str) -> MaterialsAuthoritySource:
    return MaterialsAuthoritySource(
        source_id,
        "National Institute of Standards and Technology",
        uri,
        f"experiments/external_sources/materials/snapshots/{filename}",
        "sha256:" + digest,
        scope,
    )


MATERIALS_AUTHORITY_SOURCES = (
    MaterialsAuthoritySource(
        "BIPM-JCGM-VIM-TRACEABILITY-2026-07-24",
        "Joint Committee for Guides in Metrology / Bureau International des Poids et Mesures",
        "https://jcgm.bipm.org/vim/en/2.41.html",
        "experiments/external_sources/materials/snapshots/bipm-vim-traceability.html",
        "sha256:3c06dca2ea8ad71516b027b9979e7a8381edd1576606ad10a379591c4cb6dba4",
        "measurement result, reference chain, calibration and uncertainty",
    ),
    _nist("NIST-REFERENCE-MATERIALS-2026-07-24", "https://www.nist.gov/reference-materials", "nist-reference-materials.html", "2ff393988c4880068ca103e365b0f1e6aed5a02a493b33507f6684a2d9271db9", "material identity, property characterization, uncertainty and traceability"),
    _nist("NIST-MATERIALS-DIVISION-2026-07-24", "https://www.nist.gov/mml/materials-science-and-engineering-division", "nist-materials-division.html", "fac19ae0959946a8e73f970bf76c73325d93f4671ded97f8699dfcc5e1bf53e3", "materials measurement, composition, interfaces, processing, damage, classes and lifecycle"),
    _nist("NIST-WULFFMAN-CRYSTALLOGRAPHY-2026-07-24", "https://www.ctcms.nist.gov/wulffman/docs_1.2/", "nist-wulffman-crystallography.html", "52558a4ed54b8ecc464b0ba83d879a0cbbffcb7ed25385f7742d021e87b43cb6", "lattice generation, rotation, seven crystal systems and fourteen Bravais classes"),
    _nist("NIST-BRAVAIS-CLASSIFICATION-2026-07-24", "https://www.nist.gov/publications/semi-supervised-approach-automatic-crystal-structure-classification", "nist-bravais-classification.html", "82fc7e011a992352d5200131028339a83eca0938c7462131ada2dcc059f38c91", "diffraction classification across all fourteen Bravais lattices"),
    _nist("NIST-SHECHTMAN-QUASICRYSTALS-2026-07-24", "https://www.nist.gov/nist-and-nobel/dan-shechtman", "nist-shechtman-quasicrystals.html", "911c06e466a95d58749422c56cd4e33fa1fbece04ec06977af428d7dac23ae0e", "periodic rotation orders and fivefold quasicrystal observation"),
    _nist("NIST-QUASICRYSTAL-MEASUREMENT-2026-07-24", "https://www.nist.gov/news-events/news/2025/04/rare-crystal-shape-found-increase-strength-3d-printed-metal", "nist-quasicrystal-measurement.html", "a1b7cc0a5882502bb31b9706225b926c9ffb1e8d93ea5c0043249376c4d6ff18", "microscope confirmation, nonrepeating order and fivefold symmetry"),
    _nist("NIST-POINT-DEFECTS-2026-07-24", "https://www.nist.gov/programs-projects/measurements-point-defect-chemistry-complex-oxides", "nist-point-defects.html", "b885250bd645ed8eaefa55a29d99ea4436b691f77c17c74a457acb6acf88335a", "vacancies, interstitials, substitutions, diffusion, composition and defect metrology"),
    _nist("NIST-TEXTURE-PHASE-FRACTION-2026-07-24", "https://www.nist.gov/programs-projects/ncal-quantifying-crystallographic-texture-and-phase-fraction", "nist-texture-phase-fraction.html", "b5db09c98c668fbc3c4b7b8f1cf8b83c1b093fea6c42b7846316fb10004edabc", "grains, phase fractions, texture, deformation and uncertainty"),
    _nist("NIST-MULTISCALE-MATERIALS-2026-07-24", "https://www.nist.gov/programs-projects/multiscale-structure-and-dynamics-advanced-technological-materials", "nist-multiscale-materials.html", "2de46a8509f29f4ad9367652b9b4a4740b6cb0e1c7be1bf4cd3087b25e2eed2a", "multiscale microstructure, phase evolution, heat treatment, porous materials and in-situ processing"),
    _nist("NIST-SEMICONDUCTORS-2026-07-24", "https://www.nist.gov/mml/mmsd/primary-focus-areas/semiconductors", "nist-semiconductors.html", "ef9fac0f8cf33879c90fd5914dfd0ed1ac70c076972dbdb94b1ba3843be91325", "semiconductor structural, nanomechanical, thermal and spectroscopic measurement"),
    _nist("NIST-FUNCTIONAL-ELECTRONIC-MATERIALS-2026-07-24", "https://www.nist.gov/programs-projects/genomics-electronic-materials", "nist-functional-electronic-materials.html", "355b4893ea38080dd5bc36430beedf4631667ed50d465b08bb1c2aefd91e544e", "dopants, defects, piezoelectric, ferroelectric, magnetic, topological and superconducting materials"),
    _nist("NIST-SUPERCONDUCTING-GRAIN-BOUNDARIES-2026-07-24", "https://www.nist.gov/news-events/news/2009/06/nist-discovers-how-strain-grain-boundaries-suppresses-high-temperature", "nist-superconducting-grain-boundaries.html", "1309d6599f6894e517dac8f3adc0b6b8506842cdcccc680329007351cde6abf2", "grain boundaries, strain, dislocations, current flow and superconducting response"),
    _nist("NIST-SUPERCONDUCTING-FLUX-2026-07-24", "https://www.nist.gov/ncnr/flux-lattice-superconductors-and-melting", "nist-superconducting-flux.html", "47bbe8e690eb0c796876e0a0c808d131fd9f8fee98aee7ed4ab645b5b5de4cd6", "zero resistance, Meissner expulsion, quantized flux and vortices"),
    _nist("NIST-JOSEPHSON-STANDARD-2026-07-24", "https://www.nist.gov/news-events/events/josephson-volt-nists-first-quantum-electrical-standard", "nist-josephson.html", "371bb54f09d8e66d74cda08e66518b44ebf752445ee2a049b26a76fd669487e0", "superconductive tunnel junctions and quantized Josephson voltage"),
    _nist("NIST-SUPERFLUID-CIRCULATION-2026-07-24", "https://www.nist.gov/news-events/news/2012/11/first-controllable-atom-squid", "nist-superfluid-circulation.html", "49a5edb2dc307d0849d5fb5a245be46166dbffe2c50f2e9422a78f139aa5f8a0", "superfluid flow, vortices and discrete quantized circulation"),
    _nist("NIST-TOPOLOGICAL-INSULATORS-2026-07-24", "https://www.nist.gov/programs-projects/topological-insulators", "nist-topological-insulators.html", "4cbe823dffeabd728844a897aa1c5a222dfc3aef465263a06501974e194df449", "topological invariants, insulating bulk, band gap and metallic boundaries"),
    _nist("NIST-FATIGUE-FRACTURE-2026-07-24", "https://www.nist.gov/programs-projects/additive-manufacturing-fatigue-and-fracture", "nist-fatigue-fracture.html", "449a86d3ae74591957dd1a22cd314274c0a4b7acd05d9d6a9f9671af4ea06a11", "processing-structure-property-performance, defects, fatigue and fracture"),
    _nist("NIST-POLYMER-COMPOSITES-2026-07-24", "https://www.nist.gov/programs-projects/polymer-composites", "nist-polymer-composites.html", "0ca34811fdf8880ce744219b7ad7f9574bacfc01e5ed0b073f8c64a225f692c5", "polymer matrix composites, interfaces, strength, toughness, fatigue and recycling"),
    _nist("NIST-TRANSPORT-THERMOELECTRIC-2026-07-24", "https://www.nist.gov/programs-projects/transport-property-measurements-semiconductors-and-energy-materials", "nist-transport-thermoelectric.html", "4db74747d716cccfc34518d4885187f19dfdbb8b254eef29c92e6ed32f1f20a0", "thermal conductivity, heat capacity, electrical transport and thermoelectric conversion"),
    _nist("NIST-CERAMIC-ADDITIVE-2026-07-24", "https://www.nist.gov/programs-projects/additive-manufacturing-ceramics", "nist-ceramic-additive.html", "540ef912a827c1834a113352ac0305c7e8d25a76283dcc1bcbab48f0b826a3e9", "ceramic feedstock, defects, sintering, densification, phases and microstructure"),
    _nist("NIST-POLYMER-PROCESSING-2026-07-24", "https://www.nist.gov/programs-projects/polymer-advanced-manufacturing-and-rheology", "nist-polymer-processing.html", "11279429040fb5daff9108435f0c510fc12d89e09710e799b1a6182f63a63a18", "polymer processing, crystallization, rheology, kinetics and recycling"),
    _nist("NIST-SURFACE-DAMAGE-2026-07-24", "https://www.nist.gov/programs-projects/surface-damage-polymer-nanocomposites-project", "nist-surface-damage.html", "7f0a61e225462f1514a9b2b9e459f5a0727ef2dc291bbcf5e83626f52359169d", "surface/bulk distinction, degradation, radiation, moisture, cracking and nanofiller release"),
    _nist("NIST-NANO-PROTOCOLS-2026-07-24", "https://www.nist.gov/mml/nano-measurement-protocols", "nist-nano-protocols.html", "366ea750d8ed231893eae786234339a56067e86d14d8e282496d130680df5c51", "nanomaterial property measurement, reproducibility, preparation, lifecycle and biological/environmental matrices"),
    _nist("NIST-SOLIDIFICATION-2026-07-24", "https://www.nist.gov/publications/solidification-0", "nist-solidification.html", "d5e7cf15296ae0a6f1df3e022a8b4bb4c618a46d6b4f9b36ab2f49f7532a9d6c", "solidification transport, nucleation, growth, interfaces, segregation and processing"),
    _nist("NIST-METAL-ADDITIVE-CORROSION-2026-07-24", "https://www.nist.gov/programs-projects/additive-manufacturing-metals", "nist-metal-additive-corrosion.html", "a1bb9a6bc22eb85fb7a1b3c7d0ac4bc0837d68832b7b7c6f357a68ea6cde0322", "phase transformation, heat treatment, corrosion and environmental cracking"),
    _nist("NIST-NANOTRIBOLOGY-2026-07-24", "https://www.nist.gov/programs-projects/nanotribology-nanomanufacturing-archived", "nist-nanotribology.html", "3823f313343779c2a4a74a3e251a620319c89fef2142f2b1e58fa03250fec523", "interacting surfaces, relative motion, friction, adhesion, lubrication and wear"),
    _nist("NIST-OPTICAL-MATERIALS-2026-07-24", "https://www.nist.gov/programs-projects/theory-optical-properties-materials", "nist-optical-materials.html", "3cd2616a7d74445fda880027ee0d7659d112e27a48e9a86616e766b41f0c5f1b", "index of refraction, absorption, reflectance, dielectric response and photonic crystals"),
    _nist("NIST-SIX-NEIGHBOUR-MESH-2026-07-24", "https://math.nist.gov/oommf/doc/userguide20a0/userguide/Standard_Oxs_Ext_Child_Clas.html", "nist-six-neighbour-mesh.html", "505ca000d91c5ef134836cbc75307df1584750dfbfb2faf5c4e55756d054f5c2", "six nearest neighbours as forward/backward positions on three coordinate axes"),
    _nist("NIST-POLYMER-INTERFACE-CONSORTIUM-2026-07-24", "https://www.nist.gov/el/mssd/polymer-surfaceinterface-consortium", "nist-polymer-interface-consortium.html", "2d48772b1b901e657fa86e4ee28fad15e176dd675911ce8322b54cc718c32635", "surface damage, interfacial adhesion and interface-property measurement"),
    _nist("NIST-SEMICONDUCTOR-CARRIERS-2026-07-24", "https://www.nist.gov/news-events/news/2017/03/testing-performance-semiconductors-light", "nist-semiconductor-carriers.html", "05c774e4a30e6009f031b3064b16319d181ddac92e6d088a01bb6fe362172cc5", "electron and hole carrier signs, doping, transport and Hall measurement"),
    _nist("NIST-ANTIFERROMAGNETIC-COUPLING-2026-07-24", "https://www.nist.gov/ncnr/acns-2020-tutorial-ii-practical-approach-fitting-neutron-reflectometry-data/understanding", "nist-antiferromagnetic-coupling.html", "b8ce5105622c02b84bffe643693c05c199df57beae79bd9c5e29f26c4360e85e", "polarized-neutron measurement of magnetic structure and antiferromagnetic coupling"),
    _nist("NIST-GLASS-TRANSITION-2026-07-24", "https://www.nist.gov/publications/glass-transition-its-measurement-and-underlying-physics", "nist-glass-transition.html", "2d6b99e46aae9d3c6a503494eedd17db45d4b48a633bb254cd3a6a5195440777", "thermodynamic and kinetic glass-transition measurement in glass-forming materials"),
)


SOURCE_BY_ID = {row.source_id: row for row in MATERIALS_AUTHORITY_SOURCES}


def validate_sources(root: Path) -> None:
    if len(SOURCE_BY_ID) != len(MATERIALS_AUTHORITY_SOURCES):
        raise ValueError("Materials authority source identity repeats")
    if {row.body for row in MATERIALS_AUTHORITY_SOURCES} - {
        "National Institute of Standards and Technology",
        "Joint Committee for Guides in Metrology / Bureau International des Poids et Mesures",
    }:
        raise ValueError("Materials evidence contains an unregistered authority class")
    for source in MATERIALS_AUTHORITY_SOURCES:
        if hash_file(root / source.snapshot_path) != source.snapshot_hash:
            raise ValueError(f"Materials source snapshot changed: {source.source_id}")


__all__ = (
    "MATERIALS_AUTHORITY_SOURCES",
    "MaterialsAuthoritySource",
    "SOURCE_BY_ID",
    "validate_sources",
)
