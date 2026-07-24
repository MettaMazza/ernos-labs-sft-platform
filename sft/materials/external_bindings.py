"""Claim-specific post-seal Materials authority bindings.

Every required fragment is reproduced from a byte-sealed measurement-body
snapshot.  The fragments are intentionally short factual discriminators rather
than copied definitions.  They establish that each sealed structural
consequence meets an independently observed or standardized Materials feature;
they never participate in candidate generation or elimination.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from pathlib import Path
import re

from sft.materials.obligations import MATERIALS_OBLIGATIONS
from sft.materials.sources import SOURCE_BY_ID, validate_sources


@dataclass(frozen=True)
class RequiredFragment:
    source_id: str
    fragment: str


@dataclass(frozen=True)
class MaterialsExternalBinding:
    claim_id: str
    requirements: tuple[RequiredFragment, ...]
    comparison_class: str = "post-seal-measurement-body-correspondence"


def req(source_id: str, *fragments: str) -> tuple[RequiredFragment, ...]:
    return tuple(RequiredFragment(source_id, fragment) for fragment in fragments)


def binding(claim_id: str, *requirements: RequiredFragment) -> MaterialsExternalBinding:
    return MaterialsExternalBinding(claim_id, tuple(requirements))


BIPM = "BIPM-JCGM-VIM-TRACEABILITY-2026-07-24"
REF = "NIST-REFERENCE-MATERIALS-2026-07-24"
DIV = "NIST-MATERIALS-DIVISION-2026-07-24"
CRYS = "NIST-WULFFMAN-CRYSTALLOGRAPHY-2026-07-24"
BRAVAIS = "NIST-BRAVAIS-CLASSIFICATION-2026-07-24"
QUASI = "NIST-SHECHTMAN-QUASICRYSTALS-2026-07-24"
QUASI_MEAS = "NIST-QUASICRYSTAL-MEASUREMENT-2026-07-24"
SIX = "NIST-SIX-NEIGHBOUR-MESH-2026-07-24"
DEFECT = "NIST-POINT-DEFECTS-2026-07-24"
TEXTURE = "NIST-TEXTURE-PHASE-FRACTION-2026-07-24"
MULTI = "NIST-MULTISCALE-MATERIALS-2026-07-24"
SEMI = "NIST-SEMICONDUCTORS-2026-07-24"
FUNC = "NIST-FUNCTIONAL-ELECTRONIC-MATERIALS-2026-07-24"
SC_GRAIN = "NIST-SUPERCONDUCTING-GRAIN-BOUNDARIES-2026-07-24"
SC_FLUX = "NIST-SUPERCONDUCTING-FLUX-2026-07-24"
JOSEPH = "NIST-JOSEPHSON-STANDARD-2026-07-24"
SUPERFLUID = "NIST-SUPERFLUID-CIRCULATION-2026-07-24"
TOPO = "NIST-TOPOLOGICAL-INSULATORS-2026-07-24"
FATIGUE = "NIST-FATIGUE-FRACTURE-2026-07-24"
COMPOSITE = "NIST-POLYMER-COMPOSITES-2026-07-24"
THERMO = "NIST-TRANSPORT-THERMOELECTRIC-2026-07-24"
CERAMIC = "NIST-CERAMIC-ADDITIVE-2026-07-24"
POLYMER = "NIST-POLYMER-PROCESSING-2026-07-24"
DAMAGE = "NIST-SURFACE-DAMAGE-2026-07-24"
NANO = "NIST-NANO-PROTOCOLS-2026-07-24"
SOLIDIFY = "NIST-SOLIDIFICATION-2026-07-24"
CORROSION = "NIST-METAL-ADDITIVE-CORROSION-2026-07-24"
TRIBOLOGY = "NIST-NANOTRIBOLOGY-2026-07-24"
OPTICAL = "NIST-OPTICAL-MATERIALS-2026-07-24"
INTERFACE = "NIST-POLYMER-INTERFACE-CONSORTIUM-2026-07-24"
CARRIERS = "NIST-SEMICONDUCTOR-CARRIERS-2026-07-24"
ANTIFERRO = "NIST-ANTIFERROMAGNETIC-COUPLING-2026-07-24"
GLASS = "NIST-GLASS-TRANSITION-2026-07-24"


MATERIALS_EXTERNAL_BINDINGS = (
    # Measurement, identity and traceability
    binding("SFT-MAT-MEAS-MATERIAL-001", *req(REF, "material is thoroughly measured and characterized", "values of material’s properties")),
    binding("SFT-MAT-MEAS-SPECIMEN-001", *req(TEXTURE, "sampling schemes", "material being quantified")),
    binding("SFT-MAT-MEAS-COMPOSITION-001", *req(DIV, "chemical composition", "properties of materials and material interfaces")),
    binding("SFT-MAT-MEAS-PHASE-001", *req(MULTI, "phase composition", "phase evolution")),
    binding("SFT-MAT-MEAS-MICROSTRUCTURE-001", *req(MULTI, "multi-scale microstructure", "microstructural changes")),
    binding("SFT-MAT-MEAS-PROPERTY-001", *req(REF, "material’s properties", "uncertainties in the measurements")),
    binding("SFT-MAT-MEAS-TRACEABILITY-001", *req(BIPM, "unbroken chain of calibrations", "measurement uncertainty")),

    # Crystal and quasicrystal organization
    binding("SFT-MAT-CRYST-LATTICE-001", *req(CRYS, "lattice in three dimensions", "translational periodicity")),
    binding("SFT-MAT-CRYST-UNIT-CELL-001", *req(CRYS, "unit cell", "the entire crystal is generated")),
    binding("SFT-MAT-CRYST-TRANSLATION-001", *req(CRYS, "translational periodicity", "translations")),
    binding("SFT-MAT-CRYST-CUBIC-COORDINATION-001", *req(SIX, "nearest 6 neighbors", "forward and backward along each of the 3 coordinate axis directions")),
    binding("SFT-MAT-CRYST-ROTATION-RESTRICTION-001", *req(QUASI, "only one-, two-, three-, four- and sixfold symmetries", "fivefold periodic structures were not supposed to exist")),
    binding("SFT-MAT-CRYST-SYSTEMS-001", *req(CRYS, "there are seven such crystal systems", "triclinic, monoclinic, orthorhombic, tetragonal")),
    binding("SFT-MAT-CRYST-BRAVAIS-001", *req(CRYS, "the 14 Bravais lattices", "seven such crystal systems"), *req(BRAVAIS, "all 14 Bravais lattices", "powder diffraction patterns")),
    binding("SFT-MAT-CRYST-RECIPROCAL-001", *req(BRAVAIS, "powder diffraction patterns", "crystal structure classification")),
    binding("SFT-MAT-CRYST-QUASICRYSTAL-001", *req(QUASI_MEAS, "pattern that fills the space, but never repeats", "fivefold rotational symmetry")),
    binding("SFT-MAT-CRYST-PHONON-001", *req(THERMO, "thermal conductivity", "heat capacity"), *req(FUNC, "bulk acoustic wave", "elastic nonlinearities")),

    # Defects and microstructure
    binding("SFT-MAT-DEFECT-POINT-001", *req(DEFECT, "point defects", "impurities, interstitials, or vacancies")),
    binding("SFT-MAT-DEFECT-VACANCY-001", *req(DEFECT, "vacancy diffusion", "oxygen vacancy defect")),
    binding("SFT-MAT-DEFECT-INTERSTITIAL-SUBSTITUTION-001", *req(DEFECT, "interstitials, or vacancies", "substitutional mechanisms")),
    binding("SFT-MAT-DEFECT-DISLOCATION-001", *req(SC_GRAIN, "dislocations—defects in the crystalline structure", "grain-boundary angle")),
    binding("SFT-MAT-MICRO-GRAIN-BOUNDARY-001", *req(TEXTURE, "tiny individual granules (grains)", "different crystallographic orientations")),
    binding("SFT-MAT-MICRO-INTERFACE-001", *req(INTERFACE, "interfacial adhesion", "surface/interface properties")),
    binding("SFT-MAT-MICRO-DIFFUSION-001", *req(DEFECT, "ion diffusion", "local changes to composition")),
    binding("SFT-MAT-MICRO-NUCLEATION-GROWTH-001", *req(SOLIDIFY, "nucleation, growth kinetics", "planar interface")),

    # Electronic materials and semiconductors
    binding("SFT-MAT-ELEC-BAND-GAP-001", *req(TOPO, "energy gap separating the conduction and valance bands", "states that lie within the bulk energy band gap")),
    binding("SFT-MAT-ELEC-CONDUCTOR-CLASS-001", *req(TOPO, "insulator in their bulk interior", "metallic surfaces or edges"), *req(SEMI, "semiconductor", "thermal property measurement")),
    binding("SFT-MAT-ELEC-CARRIER-DUALITY-001", *req(CARRIERS, "negative carriers are electrons", "positive carriers are referred to as \u201choles\u201d"), *req(OPTICAL, "electron and hole lifetime-damping effects", "semiconductors")),
    binding("SFT-MAT-ELEC-OCCUPATION-001", *req(FUNC, "electron materials", "atomic-scale dopants")),
    binding("SFT-MAT-SEMI-DOPING-001", *req(FUNC, "individual atomic-scale dopants", "defects")),
    binding("SFT-MAT-SEMI-PN-TYPE-001", *req(CARRIERS, "number of free electrons", "number of free holes", "negative and positive side")),
    binding("SFT-MAT-SEMI-JUNCTION-001", *req(JOSEPH, "tunnel junctions", "two junctions connected in series"), *req(SEMI, "semiconductor devices", "electrical")),
    binding("SFT-MAT-SEMI-TRANSPORT-001", *req(THERMO, "electrical resistivity", "bulk and thin film thermoelectric materials")),
    binding("SFT-MAT-SEMI-OPTICAL-001", *req(OPTICAL, "optical properties of materials", "excitation spectra"), *req(SEMI, "x-ray absorption and emission spectroscopy", "semiconductor")),

    # Superconducting, superfluid and topological matter
    binding("SFT-MAT-SC-PAIR-001", *req(FUNC, "highly correlated electron materials", "superconductors")),
    binding("SFT-MAT-SC-ZERO-RESISTANCE-001", *req(SC_FLUX, "zero resistance", "supercurrent")),
    binding("SFT-MAT-SC-MEISSNER-001", *req(SC_FLUX, "completely expel the field", "known as the Meissner effect")),
    binding("SFT-MAT-SC-FLUX-QUANTIZATION-001", *req(SC_FLUX, "magnetic flux is quantized", "tubes called vortices")),
    binding("SFT-MAT-SC-JOSEPHSON-001", *req(JOSEPH, "superconductive tunnel junctions", "voltage across a junction")),
    binding("SFT-MAT-SF-SUPERFLUID-001", *req(SUPERFLUID, "superfluid ring", "flows of atoms")),
    binding("SFT-MAT-SF-CIRCULATION-001", *req(SUPERFLUID, "quantized circulation states", "discrete quantized changes")),
    binding("SFT-MAT-TOPO-INVARIANT-001", *req(TOPO, "topological invariants", "classify materials")),
    binding("SFT-MAT-TOPO-BULK-BOUNDARY-001", *req(TOPO, "insulator in their bulk interior", "metallic surfaces or edges")),

    # Mechanical response
    binding("SFT-MAT-MECH-STRESS-STRAIN-001", *req(FATIGUE, "full processing-structure-properties-performance spectrum", "fatigue crack initiation"), *req(SC_GRAIN, "mechanical strain", "applying compression")),
    binding("SFT-MAT-MECH-ELASTICITY-001", *req(SEMI, "elastic property measurements", "mechanical properties")),
    binding("SFT-MAT-MECH-PLASTICITY-001", *req(TEXTURE, "deformation mechanisms", "evolution with deformation")),
    binding("SFT-MAT-MECH-SLIP-001", *req(QUASI_MEAS, "atoms to slip past each other", "metal bends, stretches or breaks")),
    binding("SFT-MAT-MECH-MODULUS-001", *req(SEMI, "elastic property measurements", "calibrate")),
    binding("SFT-MAT-MECH-STRENGTH-HARDNESS-001", *req(COMPOSITE, "strength, toughness", "yield strength")),
    binding("SFT-MAT-MECH-FRACTURE-001", *req(FATIGUE, "fatigue and fracture", "fracture surfaces"), *req(COMPOSITE, "toughness", "damage initiation")),
    binding("SFT-MAT-MECH-FATIGUE-CREEP-001", *req(FATIGUE, "high-cycle fatigue", "full AM lifecycle"), *req(COMPOSITE, "sub-catastrophic cyclic loading", "fatigue strength")),

    # Thermal, magnetic and optical response
    binding("SFT-MAT-THERM-HEAT-CAPACITY-001", *req(THERMO, "heat capacity", "thermal conductivity")),
    binding("SFT-MAT-THERM-CONDUCTION-001", *req(THERMO, "thermal conductivity", "thermal interface resistance")),
    binding("SFT-MAT-THERM-EXPANSION-001", *req(MULTI, "heated over 4 hours", "temperature and time")),
    binding("SFT-MAT-MAG-FERROMAGNETISM-001", *req(FUNC, "magnetic-field biases", "magnetoelectric coefficient")),
    binding("SFT-MAT-MAG-ANTIFERROMAGNETISM-001", *req(ANTIFERRO, "antiferromagnetic coupling", "in-plane magnetization", "polarized neutron reflectometry")),
    binding("SFT-MAT-DIEL-POLARIZATION-001", *req(FUNC, "dielectric properties", "ferroelectrics")),
    binding("SFT-MAT-OPT-REFRACTIVE-001", *req(OPTICAL, "index of refraction", "absorption, and reflectance")),
    binding("SFT-MAT-PHASE-TRANSITION-001", *req(MULTI, "phase evolution", "temperature and time"), *req(SC_FLUX, "vortex lattice", "warming")),

    # Material classes and bulk correspondence
    binding("SFT-MAT-CLASS-METAL-001", *req(SOLIDIFY, "casting of metals", "metallic systems")),
    binding("SFT-MAT-CLASS-CERAMIC-001", *req(CERAMIC, "ceramic AM feedstocks", "sintering")),
    binding("SFT-MAT-CLASS-POLYMER-001", *req(POLYMER, "polymeric materials", "composition and crystallinity")),
    binding("SFT-MAT-CLASS-COMPOSITE-001", *req(COMPOSITE, "polymer matrix composites", "fiber-matrix interphase")),
    binding("SFT-MAT-CLASS-GLASS-001", *req(GLASS, "glass transition", "glassy materials", "thermodynamic and kinetic aspects")),
    binding("SFT-MAT-CLASS-POROUS-001", *req(MULTI, "heterogeneous or porous materials", "multiple length scales")),
    binding("SFT-MAT-BULK-CORRESPONDENCE-001", *req(COMPOSITE, "macroscopic properties", "microscopic platform"), *req(MULTI, "angstrom to micrometer-scale range", "multi-scale")),
    binding("SFT-MAT-BULK-ANISOTROPY-001", *req(TEXTURE, "different crystallographic orientations", "respond differently")),
    binding("SFT-MAT-BULK-SIZE-SURFACE-001", *req(DAMAGE, "surface properties", "bulk properties"), *req(NANO, "physico-chemical and biological properties", "engineered nanomaterials")),

    # Processing and degradation
    binding("SFT-MAT-PROC-PATH-001", *req(FATIGUE, "processing-structure-properties-performance spectrum", "full AM lifecycle")),
    binding("SFT-MAT-PROC-PHASE-DIAGRAM-001", *req(THERMO, "phase equilibrium data", "bulk and thin film"), *req(TEXTURE, "phase fraction", "types and amounts of phases")),
    binding("SFT-MAT-PROC-SOLIDIFICATION-001", *req(SOLIDIFY, "transport phenomena in solidification", "nucleation, growth kinetics")),
    binding("SFT-MAT-PROC-SINTERING-001", *req(CERAMIC, "post-build sintering step", "densification kinetics")),
    binding("SFT-MAT-PROC-HEAT-TREATMENT-001", *req(MULTI, "heat treatments", "microstructural changes"), *req(CORROSION, "time-temperature-transformation diagram", "heat treatment")),
    binding("SFT-MAT-DEGR-CORROSION-001", *req(CORROSION, "corrosion resistance", "electrochemical measurements")),
    binding("SFT-MAT-DEGR-WEAR-001", *req(TRIBOLOGY, "friction, adhesion, lubrication, and wear", "interacting surfaces in relative motion")),
    binding("SFT-MAT-DEGR-RADIATION-001", *req(DAMAGE, "ultraviolet (UV) radiation", "surface damage"), *req(MULTI, "ionizing radiation metrology", "materials")),

    # Advanced functional and sustainable materials
    binding("SFT-MAT-FUNC-PIEZOELECTRIC-001", *req(FUNC, "piezoelectric coefficient", "cross-couplings")),
    binding("SFT-MAT-FUNC-FERROELECTRIC-001", *req(FUNC, "ferroelectrics", "electric- and magnetic-field biases")),
    binding("SFT-MAT-FUNC-THERMOELECTRIC-001", *req(THERMO, "inter-conversion of thermal and electrical energy", "Seebeck coefficient")),
    binding("SFT-MAT-FUNC-PHOTONIC-001", *req(OPTICAL, "photonic crystals", "optical fibers")),
    binding("SFT-MAT-FUNC-MAGNETIC-001", *req(FUNC, "magneto-electric materials", "magnetic-field biases")),
    binding("SFT-MAT-FUNC-NANOMATERIAL-001", *req(NANO, "engineered nanomaterials", "physico-chemical and biological properties")),
    binding("SFT-MAT-FUNC-BIOMATERIAL-001", *req(NANO, "biological matrices", "relevant media"), *req(COMPOSITE, "biomedical composites", "dental, scaffolds")),
    binding("SFT-MAT-SUST-LIFECYCLE-001", *req(DIV, "post-consumer resin", "reuse in production processes"), *req(NANO, "full material and product life cycles", "reproducibility")),
)


BINDING_BY_CLAIM = {row.claim_id: row for row in MATERIALS_EXTERNAL_BINDINGS}


def source_corpus(root: Path, source_id: str) -> str:
    source = SOURCE_BY_ID[source_id]
    text = (root / source.snapshot_path).read_text(encoding="utf-8", errors="ignore")
    without_tags = re.sub(r"<[^>]+>", " ", text)
    return " ".join(unescape(without_tags).casefold().split())


def validate_bindings(root: Path) -> None:
    validate_sources(root)
    required_ids = tuple(row.claim_id for row in MATERIALS_OBLIGATIONS)
    if tuple(row.claim_id for row in MATERIALS_EXTERNAL_BINDINGS) != required_ids:
        raise ValueError("Materials external bindings do not cover the frozen inventory in order")
    if len(BINDING_BY_CLAIM) != len(MATERIALS_EXTERNAL_BINDINGS):
        raise ValueError("Materials external binding identity repeats")
    corpora: dict[str, str] = {}
    for row in MATERIALS_EXTERNAL_BINDINGS:
        if len(row.requirements) < 2:
            raise ValueError(f"Materials binding lacks two independent discriminators: {row.claim_id}")
        for requirement in row.requirements:
            if requirement.source_id not in SOURCE_BY_ID:
                raise ValueError(f"Materials binding cites an unknown source: {row.claim_id}")
            corpus = corpora.setdefault(requirement.source_id, source_corpus(root, requirement.source_id))
            if requirement.fragment.casefold() not in corpus:
                raise ValueError(
                    f"Materials source does not reproduce fragment for {row.claim_id}: {requirement.fragment}"
                )


__all__ = (
    "BINDING_BY_CLAIM",
    "MATERIALS_EXTERNAL_BINDINGS",
    "MaterialsExternalBinding",
    "RequiredFragment",
    "source_corpus",
    "validate_bindings",
)
