"""Physics laws at the explicit Astronomy/Cosmology handoff boundary."""

from __future__ import annotations

from sft.physics.generated_empirical_law import EmpiricalPhysicsSpec, ExternalTargetRow, empirical_dimensions


SOURCES = {
    "nasa": ("NASA-LAMBDA-2026-07-23", "experiments/external_sources/physics/snapshots/nasa-lambda-home.html", "sha256:805ea293cbcf660499be996e0d80175b61ba2a68bdddedffe94e50b2d4275915"),
    "firas": ("NASA-LAMBDA-COBE-FIRAS-2026-07-23", "experiments/external_sources/physics/snapshots/nasa-lambda-cobe-firas.html", "sha256:5eae175f5ea06f7a5cb863866eeee9d87a38d870937d9a93ebf28629af0d6ef9"),
    "gw": ("GWOSC-GW231123-135430-V3-2026-07-23", "experiments/external_sources/physics/snapshots/gwosc-gw231123-135430-v3.json", "sha256:67266a5406cbee1dc98a9853beb42d771595fa474f5ddd33ab4b368d5b71c45d"),
}
BASE = "SFT-PHYS-GRAVITY-HORIZON-001"


def cosmo_law(claim_id, title, statement, relation, reason, result, label, prior, source_key, *locators):
    source_id, source_path, source_hash = SOURCES[source_key]
    slug = claim_id.removeprefix("SFT-PHYS-COSMO-").removesuffix("-001")
    dependencies = (
        "SFT-PHYS-SPACETIME-CAUSAL-ORDER-001", "SFT-PHYS-SPACETIME-CLOCK-RATE-001",
        "SFT-PHYS-GRAVITY-CURVATURE-001", "SFT-PHYS-GRAVITY-WAVE-001", BASE,
    ) + (() if prior == BASE else (prior,))
    return EmpiricalPhysicsSpec(
        claim_id, title, statement, dependencies,
        "Generate the complete emission, propagation, observation-time, source/response, provenance, target-access, successor and extra-rule product.",
        "All finite cosmological-boundary forms generated from exact source-bound propagation, recurrence ratios, causal paths and observation records; astronomical census and historical initial conditions remain outside this Physics closure.",
        empirical_dimensions(relation, reason), result,
        "One source event emits one recurrence carrier along one generated causal path to one observation event.",
        "Adding one source, path cell or observation preserves every prior emission, recurrence, causal and detector record and appends exactly its generated relations.",
        ("ungenerated cosmic continuum, completed infinity or whole-universe census", "floating, irrational, imaginary or signed proof magnitude", "imported cosmological fit, historical initial condition or target-selected parameter", "target access, selected favorable observation or unrecorded source/path"),
        (("source-observer-trace", "Every observation retains source, path and observation-time provenance.", True), ("finite-boundary", "Every claim states its finite observation and disciplinary boundary.", True)),
        f"SFT-EXP-PHYS-COSMO-{slug}-001", label,
        tuple(ExternalTargetRow(f"{slug.lower()}-{n}", source_id, locator, label) for n, locator in enumerate(locators, 1)),
        source_path, source_hash,
        "The cosmological-boundary law is falsified if a committed external row lacks the sealed propagation/observation relation, a row is omitted, or the tampered row is accepted.",
    )


REDSHIFT = cosmo_law("SFT-PHYS-COSMO-REDSHIFT-001", "Propagation redshift relation",
    "Redshift is the exact ratio change between emitted and observed recurrence carriers after source, propagation and observer clock relations are retained.",
    "emission-observation-recurrence-ratio", "Paired recurrence counting uniquely separates physical frequency change from source identity or detector relabeling.",
    "Cosmological redshift is an exact source-to-observer Fold recurrence ratio with complete path provenance.", "cosmological-redshift-relation", BASE, "gw", "GW231123 source-frame redshift posterior", "GW231123 detector/source parameter records")

EXPANSION = cosmo_law("SFT-PHYS-COSMO-EXPANSION-001", "Relational expansion observation",
    "Relational expansion is coherent change of source-separation support relative to observation-clock recurrence across multiple source-bound paths; it is not motion into external space.",
    "coherent-source-separation-clock-change", "Common orientation of independent exact separation changes distinguishes expansion from local peculiar propagation without assuming an absolute scale.",
    "Expansion is coherent Fold change of relational source support per observation recurrence over a declared finite census.", "relational-expansion-observation", REDSHIFT.claim_id, "nasa", "NASA LAMBDA expansion-observation datasets", "NASA LAMBDA large-scale-structure and background holdings")

BACKGROUND = cosmo_law("SFT-PHYS-COSMO-BACKGROUND-001", "Background-radiation field relation",
    "Background radiation is a near-omnidirectional recurrence field whose thermodynamic observation class is invariant across registered frequency support after local foreground records are separated.",
    "omnidirectional-frequency-invariant-thermal-recurrence", "Complete direction/frequency support and retained foreground provenance uniquely distinguish a background field from selected sources.",
    "Cosmic background radiation is a source-history-bound, frequency-consistent thermal Fold recurrence field.", "background-radiation-relation", EXPANSION.claim_id, "firas", "COBE FIRAS absolute spectrum and temperature", "COBE FIRAS full-sky frequency support")

LENSING = cosmo_law("SFT-PHYS-COSMO-LENSING-001", "Gravitational lensing relation",
    "Lensing occurs when source-curved event support generates multiple causal propagation paths between one emitter and observer, changing direction, arrival recurrence and observed support while preserving source labels.",
    "multiple-curved-source-observer-paths", "Complete curved-path enumeration forces magnification, delay and image multiplicity as observation projections without adding a new interaction.",
    "Gravitational lensing is multiple source-bound causal Fold paths through relational curvature to one observation support.", "gravitational-lensing-relation", BACKGROUND.claim_id, "nasa", "NASA LAMBDA lensing and CMB products", "NASA LAMBDA source-map and reconstruction datasets")

DISTANCE = cosmo_law("SFT-PHYS-COSMO-DISTANCE-001", "Causal distance and observation-time relation",
    "Cosmological distance is the exact equivalence class of source-to-observer causal path support conditioned on emission and observation recurrence records; different distance notions are distinct retained projections.",
    "causal-path-support-conditioned-on-clock-records", "Complete path and clock provenance prevents luminosity, propagation and simultaneous-separation observations from being conflated.",
    "Cosmological distance is a declared Fold projection of exact causal support and observation-time relations.", "cosmological-causal-distance", LENSING.claim_id, "gw", "GW231123 luminosity-distance posterior", "GW231123 redshift and source-frame records")

STRUCTURE_GROWTH = cosmo_law("SFT-PHYS-COSMO-STRUCTURE-GROWTH-001", "Finite structure-growth relation",
    "Structure growth is deterministic evolution of a finite source-density distinction network under locally forced interaction and expansion relations; weights describe unresolved initial/history fibres rather than ontic randomness.",
    "finite-density-network-dynamical-growth", "Complete finite evolution retains initial, interaction and observation traces and prevents an ungenerated continuum history from selecting the law.",
    "Cosmic structure growth is finite deterministic Fold network evolution under registered gravitational and expansion relations.", "finite-cosmic-structure-growth", DISTANCE.claim_id, "nasa", "NASA LAMBDA large-scale-structure datasets", "NASA LAMBDA CMB anisotropy and matter-map products")

BRANCH_BOUNDARY = cosmo_law("SFT-PHYS-COSMO-BRANCH-BOUNDARY-001", "Physics-to-astronomy/cosmology handoff boundary",
    "Physics closes the universal source, propagation, observation and interaction relations; object census, historical initial state and inferred cosmic chronology pass as explicit measured inputs to the later Astronomy/Cosmology branch.",
    "law-versus-historical-state-boundary", "Separating forced transformation law from contingent measured state prevents observations or fitted histories from becoming axioms or free proof parameters.",
    "The branch handoff preserves closed Physics laws and exports only source-bound finite observations for later astronomical reconstruction.", "physics-cosmology-handoff", STRUCTURE_GROWTH.claim_id, "nasa", "NASA LAMBDA public observational data archive", "NASA LAMBDA dataset identity and provenance system")


COSMOLOGICAL_BOUNDARY_SPECS = (REDSHIFT, EXPANSION, BACKGROUND, LENSING, DISTANCE, STRUCTURE_GROWTH, BRANCH_BOUNDARY)
for _law in COSMOLOGICAL_BOUNDARY_SPECS: _law.validate()
__all__ = ("COSMOLOGICAL_BOUNDARY_SPECS",)
