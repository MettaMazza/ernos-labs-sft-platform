#!/usr/bin/env python3
"""Build the categorical, atomic V1/V2-to-V3 Physics audit.

This is a read-only audit of scientific ownership and existing receipts.  It
does not call, alter, or relax the admission engine.  A historical mapping
review is retained only after independently reclassifying a source atom as
Physics and verifying that its referenced claim remains model-admitted; its
former blanket Physics ownership is rejected here.  Current registration,
receipt hashes, source hashes, categorical exceptions, and same-strength
dispositions are emitted so that every conclusion can be inspected.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V1_PATH = ROOT / "audits/v1_theorem_manifest_observation_census.json"
V2_PATH = ROOT / "audits/v2_407_step_observation_census.json"
CLAIMS_PATH = ROOT / "census/claims.json"
OUTPUT = ROOT / "audits/physics_v1_v2_atomic_ownership.json"
REPORT = ROOT / "audits/physics_v1_v2_atomic_ownership.md"

# This ancestor contains candidate V1/V2-to-V3 links produced before the
# ownership correction.  Those links are hypotheses only.  No ownership or
# admission conclusion is inherited from it.
MAPPING_SNAPSHOT = "9a41f6d:census/physics_prior_obligations.json"


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def legacy_candidates() -> dict[tuple[str, str], dict]:
    raw = subprocess.run(
        ["git", "show", MAPPING_SNAPSHOT],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    data = json.loads(raw)
    return {
        (str(row["source"]), str(row["source_entry"])): row
        for row in data["source_entries"]
    }


# Rows that the former relevance sweep wrongly treated as Physics-owned.
# Their atomic content is owned by the named branch; a downstream physical
# application does not transfer ownership.
V1_EXCLUSIONS = {
    "E1": "Mathematics",
    "E2": "Mathematics",
    "E5": "Mathematics",
    "PH1": "Mathematics",
    "PH1b": "Mathematics",
    "D1b": "Mathematics",
    "D8": "Mathematics",
    "G9": "Consciousness",
    "G14": "Mathematics",
    "U3": "corpus-level cross-reference, not an atomic physical law",
    "III-7": "Chemistry",
    "XVIII-8": "branch-level completeness audit, not an atomic physical law",
    "XVIII-9": "Astronomy/Cosmology and Chemistry",
    **{f"II-{n}": "Materials" for n in range(1, 12)},
}

V2_EXCLUSIONS = {
    21: "Information Science and Foundation",
    33: "Mathematics",
    49: "Materials",
    52: "Materials",
    53: "Foundation",
    54: "Materials",
    57: "Mathematics",
    67: "Materials",
    72: "Materials",
    73: "Chemistry",
    74: "Materials",
    75: "Materials",
    86: "Mathematics",
    89: "Mathematics",
    93: "Mathematics",
    112: "Chemistry",
    115: "Foundation",
    120: "Astronomy/Cosmology and Chemistry",
    121: "Mathematics",
    126: "Foundation",
    133: "Materials",
    137: "Materials",
    143: "Materials",
    144: "Chemistry and Biology",
    145: "Learning and Consciousness",
    148: "Consciousness",
    164: "Mathematics and Quantum Computation",
    191: "Mathematics and Foundation",
    209: "Mathematics",
    257: "Consciousness",
    261: "Mathematics",
    265: "Mathematics and Quantum Computation",
    274: "branch-level constant census, not an atomic physical law",
    291: "Materials and Astronomy/Cosmology",
    306: "Scientific Computation and Engineering",
    308: "Learning/Unison application experiment",
}

# Source rows missed by the former Physics relevance sweep but containing a
# separately owned universal-Physics atom.
V1_ADDITIONS = {
    "IX-1", "IX-2", "IX-3", "IX-4", "IX-5", "IX-6", "IX-7", "IX-8",
    "XII-5", "XIII-2", "XIII-4", "XIII-5", "XIII-6", "XIV-6",
}
V2_ADDITIONS = {42, 118, 203, 258, 259}

# Mixed rows retain a Physics atom and explicitly leave the rest with the
# other owner.  The text states the categorical cut; it is not a claim of
# same-strength closure.
MIXED_BOUNDARIES = {
    ("v1", "VIII-1"): "Physics owns temperature/scale transport; Astronomy/Cosmology owns the dated cosmic epoch history.",
    ("v1", "VIII-2"): "Physics owns freeze-out and nuclear-reaction transport; Astronomy/Cosmology owns primordial abundance history.",
    ("v1", "VIII-3"): "Physics owns atomic/plasma/acoustic relations; Astronomy/Cosmology owns recombination history and the observed CMB spectrum.",
    ("v1", "VIII-4"): "Physics owns baryon-number, CP and nonequilibrium process laws; Astronomy/Cosmology owns cosmic baryogenesis history.",
    ("v1", "VIII-5"): "Physics owns the universal perturbation-growth relation; Astronomy/Cosmology owns structure history and the observed population spectrum.",
    ("v1", "VIII-6"): "Physics owns expansion and primordial-spectrum relations; Astronomy/Cosmology owns inflationary history and CMB inference.",
    ("v1", "IX-1"): "Physics owns hydrostatic, transport and reaction relations; Astronomy owns stellar populations, the main sequence and calibrated mass-luminosity data.",
    ("v1", "IX-2"): "Physics owns nuclear fusion and binding progression; Astronomy owns the stellar burning history and object structure.",
    ("v1", "IX-3"): "Physics owns exclusion-pressure and collapse relations; Astronomy owns white-dwarf/neutron-star populations and measured mass limits.",
    ("v1", "IX-4"): "Physics owns nuclear capture, reaction and collapse relations; Astronomy owns supernova histories, populations and abundance records.",
    ("v1", "IX-5"): "Physics owns horizon, temperature, area-support and information laws; Astronomy owns black-hole populations and event observations.",
    ("v1", "IX-6"): "Physics owns wave speed, quadrupole radiation and energy transport; Astronomy owns source histories and waveform catalogues.",
    ("v1", "IX-7"): "Physics owns gravity/dark-sector response and the modified-gravity discriminator; Astronomy owns galaxy and cluster observations.",
    ("v1", "IX-8"): "Physics owns resonance and dissipative locking; Astronomy owns planetary-system histories and population evidence.",
    ("v1", "XII-5"): "Physics owns the Yang-Mills confinement/mass-gap atom; Mathematics owns the Millennium-problem formulation and Navier-Stokes proof question.",
    ("v1", "XIV-6"): "Physics owns vacuum/inertia and work-accounting laws; Engineering owns any proposed device and UAP interpretation.",
    ("v2", "42"): "Physics owns the universal perturbation-growth relation; Astronomy/Cosmology owns galaxy-formation history.",
    ("v2", "58"): "Physics owns freeze-out and nuclear transport; Astronomy/Cosmology owns primordial abundance history.",
    ("v2", "107"): "Physics owns the orbital-response relation; Astronomy owns rotation-curve observations and halo inference.",
    ("v2", "139"): "Physics owns atomic/plasma decoupling relations; Astronomy/Cosmology owns recombination history and CMB observations.",
    ("v2", "140"): "Physics owns support-loss and collapse relations; Astronomy owns stellar endpoint history.",
    ("v2", "197"): "Physics owns expansion, thermodynamic ordering and component transport; Astronomy/Cosmology owns the ordered cosmic history.",
    ("v2", "255"): "Physics owns exclusion-pressure/collapse relations; Astronomy owns the compact-object endpoint census.",
    ("v2", "280"): "Physics owns the normalized criticality relation; Earth Science, Astronomy and other application branches own their separate observed signatures.",
    ("v2", "283"): "Physics owns the exact alpha/proton energy-share law and its post-seal dimensional correspondence; heliophysics owns the observed Parker Solar Probe event and its physical interpretation.",
    ("v2", "296"): "Physics owns particle couplings and interaction signatures; experimental search engineering owns detector strategy.",
}

ADDITIONAL_MAPS = {
    **{("v1", entry): ["SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069", "SFT-PHYS-VALIDATION-STELLAR-NUCLEAR-COLLAPSE-070", "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006"] for entry in ("IX-2", "IX-4")},
    **{("v2", entry): ["SFT-PHYS-STELLAR-NUCLEAR-COLLAPSE-TERMINAL-069", "SFT-PHYS-VALIDATION-STELLAR-NUCLEAR-COLLAPSE-070", "SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006"] for entry in ("140", "150")},
    ("v2", "128"): ["SFT-PHYS-NUCLEAR-FUSION-FISSION-YIELD-THRESHOLD-006"],
    **{("v1", entry): ["SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067", "SFT-PHYS-VALIDATION-STELLAR-GALACTIC-TIDAL-068"] for entry in ("IX-8", "IX-7", "IX-1")},
    **{("v2", entry): ["SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067", "SFT-PHYS-VALIDATION-STELLAR-GALACTIC-TIDAL-068"] for entry in ("152", "153")},
    ("v1", "D11d"): ["SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065", "SFT-PHYS-VALIDATION-HIGGS-SYMMETRY-TERMINAL-066"],
    ("v2", "287"): ["SFT-PHYS-HIGGS-SYMMETRY-TERMINAL-065", "SFT-PHYS-VALIDATION-HIGGS-SYMMETRY-TERMINAL-066"],
    ("v2", "107"): ["SFT-PHYS-ORBITAL-DIMENSION-STABILITY-TERMINAL-009"],
    ("v1", "XVIII-2"): ["SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063", "SFT-PHYS-VALIDATION-STRONG-CP-BARYON-STABILITY-064"],
    ("v1", "N5"): ["SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063", "SFT-PHYS-VALIDATION-STRONG-CP-BARYON-STABILITY-064"],
    ("v1", "N2"): ["SFT-PHYS-STRONG-CP-BARYON-STABILITY-TERMINAL-063", "SFT-PHYS-VALIDATION-STRONG-CP-BARYON-STABILITY-064"],
    ("v1", "B-9N"): ["SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"],
    ("v1", "N8"): ["SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"],
    ("v2", "271"): ["SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"],
    ("v2", "296"): ["SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"],
    ("v2", "297"): ["SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"],
    ("v2", "299"): ["SFT-PHYS-DARK-SMITHION-LFV-TERMINAL-061", "SFT-PHYS-VALIDATION-DARK-SMITHION-LFV-062"],
    ("v1", "G5"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v1", "M3"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v1", "M10"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v1", "M12"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v1", "M19"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "87"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "104"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "106"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "113"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "212"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "221"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "222"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "242"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "246"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v2", "250"): ["SFT-PHYS-PARTICLE-MODE-GENERATION-TERMINAL-051", "SFT-PHYS-VALIDATION-PARTICLE-MODE-GENERATION-052"],
    ("v1", "D6b"): ["SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049", "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"],
    ("v1", "D6"): ["SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049", "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"],
    ("v2", "76"): ["SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049", "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"],
    ("v2", "159"): ["SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049", "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"],
    ("v2", "260"): ["SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049", "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050"],
    ("v1", "I-9"): ["SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045", "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"],
    ("v1", "I-5"): ["SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045", "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"],
    ("v2", "23"): ["SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045", "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"],
    ("v2", "51"): ["SFT-PHYS-NUCLEAR-DEUTERON-DINUCLEON-TERMINAL-006", "SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045", "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"],
    ("v2", "100"): ["SFT-PHYS-SPIN-STATISTICS-CONDENSATION-TERMINAL-045", "SFT-PHYS-VALIDATION-SPIN-STATISTICS-CONDENSATION-046"],
    ("v1", "I-7"): ["SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043", "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"],
    ("v1", "I-3"): ["SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043", "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"],
    ("v1", "I-1"): ["SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043", "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"],
    ("v2", "88"): ["SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043", "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"],
    ("v2", "102"): ["SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043", "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"],
    ("v2", "155"): ["SFT-PHYS-THERMAL-EQUILIBRIUM-RESPONSE-TERMINAL-043", "SFT-PHYS-VALIDATION-THERMAL-EQUILIBRIUM-044"],
    ("v1", "VII-7"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v1", "VII-5"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v1", "VII-1"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v2", "48"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v2", "81"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v2", "111"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v2", "146"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v2", "170"): ["SFT-PHYS-COLLECTIVE-RADIATION-RESPONSE-TERMINAL-041", "SFT-PHYS-VALIDATION-COLLECTIVE-RADIATION-RESPONSE-042"],
    ("v1", "VIII-6"): [
        "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
    ],
    ("v1", "VIII-5"): [
        "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
    ],
    ("v1", "N7"): [
        "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
    ],
    ("v2", "31"): [
        "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
    ],
    ("v2", "42"): [
        "SFT-PHYS-COSMO-STRUCTURE-GROWTH-001",
        "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040",
    ],
    ("v1", "VIII-1"): [
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038",
    ],
    ("v1", "VIII-2"): [
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038",
    ],
    ("v1", "VIII-3"): [
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038",
    ],
    ("v2", "58"): [
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038",
    ],
    ("v2", "139"): [
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038",
    ],
    ("v2", "197"): [
        "SFT-PHYS-THERMAL-HISTORY-RECOMBINATION-TERMINAL-037",
        "SFT-PHYS-VALIDATION-THERMAL-HISTORY-RECOMBINATION-038",
    ],
    ("v1", "XVIII-3"): [
        "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
        "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
    ],
    ("v1", "N1c"): [
        "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
        "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
    ],
    ("v2", "35"): [
        "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032",
        "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
        "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
    ],
    ("v2", "40"): [
        "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
        "SFT-PHYS-VALIDATION-VACUUM-FLOOR-003",
        "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
        "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
    ],
    ("v1", "B-4N"): [
        "SFT-PHYS-FORCE-PRIME-SECTOR-LADDER-002",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    ],
    ("v1", "B1"): [
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    ],
    ("v1", "B13"): [
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    ],
    ("v1", "M1"): [
        "SFT-PHYS-MATTER-MASS-RATIO-FAMILY-003",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    ],
    ("v1", "G7"): [
        "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
        "SFT-PHYS-QUANTUM-NO-SIGNALLING-001",
        "SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024",
    ],
    ("v1", "G8"): [
        "SFT-PHYS-FIELD-LOCALITY-CAUSALITY-001",
        "SFT-PHYS-SPACETIME-CAUSAL-ORDER-001",
        "SFT-PHYS-FOLD-UNIVERSE-TRANSPORT-TERMINAL-024",
    ],
    ("v1", "G4"): [
        "SFT-PHYS-SYMMETRIC-SOURCE-CONSERVATION-TERMINAL-010",
        "SFT-PHYS-FIELD-FINITE-LOOP-CLOSURE-003",
        "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
        "SFT-PHYS-FINITE-QUANTUM-GRAVITY-TERMINAL-023",
    ],
    ("v1", "D1"): [
        "SFT-PHYS-WAVE-DISPERSION-001",
        "SFT-PHYS-DYNAMICS-FREE-PHASE-DISPERSION-003",
        "SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022",
    ],
    ("v1", "D1c"): [
        "SFT-PHYS-GRAVITY-LATTICE-CURVATURE-003",
        "SFT-PHYS-FIELD-MAXWELL-PLANAR-CLOSURE-003",
        "SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022",
    ],
    ("v1", "D1d"): [
        "SFT-PHYS-FIELD-MAXWELL-THREE-SPACE-CLOSURE-003",
        "SFT-PHYS-VALIDATION-ATOMIC-CUBIC-SUPPORT-004",
        "SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022",
    ],
    ("v1", "VIII-4"): [
        "SFT-PHYS-MATTER-CKM-TERMINAL-004",
        "SFT-PHYS-MATTER-BARYON-PHOTON-TERMINAL-004",
        "SFT-PHYS-BARYOGENESIS-DEPENDENCY-TERMINAL-021",
    ],
    ("v1", "D11a"): ["SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020"],
    ("v1", "D11c"): [
        "SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003",
        "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003",
        "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020",
    ],
    ("v1", "D11f"): [
        "SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005",
        "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020",
    ],
    ("v1", "IX-1"): ["SFT-PHYS-GRAVITY-FIELD-SOURCE-001", "SFT-PHYS-FLUID-PRESSURE-STRESS-001", "SFT-PHYS-NUCLEAR-FUSION-001"],
    ("v1", "IX-2"): ["SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005", "SFT-PHYS-NUCLEAR-FUSION-FISSION-TERMINAL-005"],
    ("v1", "IX-3"): [
        "SFT-PHYS-QUANTUM-EXCLUSION-001",
        "SFT-PHYS-FLUID-PRESSURE-STRESS-001",
        "SFT-PHYS-GRAVITY-HORIZON-001",
        "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071",
        "SFT-PHYS-VALIDATION-COMPACT-HORIZON-THERMODYNAMICS-072",
    ],
    ("v1", "IX-4"): ["SFT-PHYS-NUCLEAR-REACTIONS-001", "SFT-PHYS-NUCLEAR-BINDING-CURVE-TERMINAL-005"],
    ("v1", "IX-5"): [
        "SFT-PHYS-GRAVITY-STRONG-FIELD-HORIZON-003",
        "SFT-PHYS-GRAVITY-HORIZON-INFORMATION-003",
        "SFT-PHYS-VACUUM-ODD-RECURRENCE-003",
        "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071",
        "SFT-PHYS-VALIDATION-COMPACT-HORIZON-THERMODYNAMICS-072",
    ],
    ("v1", "IX-6"): [
        "SFT-PHYS-GRAVITY-WAVE-QUADRUPOLE-003",
        "SFT-PHYS-QUADRUPOLE-RADIATED-POWER-TERMINAL-012",
        "SFT-PHYS-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-TERMINAL-073",
        "SFT-PHYS-VALIDATION-GRAVITATIONAL-WAVE-CHIRP-RINGDOWN-074",
    ],
    ("v2", "255"): [
        "SFT-PHYS-COMPACT-HORIZON-THERMODYNAMICS-TERMINAL-071",
        "SFT-PHYS-VALIDATION-COMPACT-HORIZON-THERMODYNAMICS-072",
    ],
    ("v1", "IX-7"): ["SFT-PHYS-COSMO-STRUCTURE-GROWTH-001", "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001"],
    ("v1", "IX-8"): ["SFT-PHYS-WAVE-RESONANCE-001", "SFT-PHYS-MECH-ANGULAR-MOTION-001"],
    ("v1", "XII-5"): [
        "SFT-PHYS-STRONG-CARRIER-MASSLESS-CONFINED-TERMINAL-013",
        "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014",
        "SFT-PHYS-YANG-MILLS-SINGLET-GAP-TERMINAL-026",
        "SFT-PHYS-YANG-MILLS-SINGLET-GAP-EMPIRICAL-027",
    ],
    ("v1", "XIII-2"): [
        "SFT-PHYS-THERMO-PHASE-EQUILIBRIUM-001",
        "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008",
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
    ],
    ("v1", "I-6"): [
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
    ],
    ("v1", "XIII-4"): [
        "SFT-PHYS-MECH-CONSERVATION-001",
        "SFT-PHYS-FIELD-CONSERVED-SOURCE-001",
        "SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016",
    ],
    ("v1", "XIII-5"): ["SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016"],
    ("v1", "I-10"): [
        "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018",
        "SFT-PHYS-THERMO-LANDAUER-EMPIRICAL-019",
    ],
    ("v1", "XIII-6"): [
        "SFT-PHYS-MATTER-MASS-RATIO-FAMILY-003",
        "SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003",
        "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",
    ],
    ("v1", "XIV-6"): ["SFT-PHYS-VACUUM-INERTIA-UNITY-003", "SFT-PHYS-VACUUM-ASYMMETRIC-BEAT-EXTRACTION-003", "SFT-PHYS-VACUUM-COMPLETE-CYCLE-LEDGER-003"],
    ("v1", "B8"): ["SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006"],
    ("v1", "B3"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B4"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B5"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B7"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B11"): [
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",
    ],
    ("v1", "B12"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B15"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B17"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v1", "B-10N"): ["SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"],
    ("v1", "B-11N"): ["SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"],
    ("v1", "B-12N"): ["SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"],
    ("v1", "B-13N"): ["SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"],
    ("v1", "B-14N"): ["SFT-PHYS-COMPOSITE-CONFINING-SECTOR-TERMINAL-031"],
    ("v1", "VIII-11"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v1", "VIII-10"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v1", "VIII-9"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v1", "VIII-8"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v1", "N1d"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v1", "N1f"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v1", "B10"): ["SFT-PHYS-COUPLING-ACCUMULATED-SEPARATION-TERMINAL-015"],
    ("v2", "70"): ["SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020"],
    ("v2", "110"): ["SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022"],
    ("v2", "205"): ["SFT-PHYS-LATTICE-OPERATOR-TERMINAL-022"],
    ("v2", "183"): ["SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025"],
    ("v2", "243"): [
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025",
    ],
    ("v2", "91"): [
        "SFT-PHYS-MATTER-SCATTERING-001",
        "SFT-PHYS-SCATTERING-RUTHERFORD-COMPTON-TERMINAL-006",
        "SFT-PHYS-SCATTERING-PARTITION-PATH-TERMINAL-017",
    ],
    ("v2", "123"): [
        "SFT-PHYS-THERMO-IRREVERSIBILITY-001",
        "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018",
        "SFT-PHYS-THERMO-LANDAUER-EMPIRICAL-019",
    ],
    ("v2", "240"): [
        "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002",
        "SFT-PHYS-MEDIATOR-RANGE-CHANNEL-TERMINAL-020",
    ],
    ("v2", "118"): ["SFT-PHYS-CONTINUUM-COARSE-GRAIN-001"],
    ("v2", "119"): [
        "SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003",
        "SFT-PHYS-YANG-MILLS-SINGLET-GAP-TERMINAL-026",
        "SFT-PHYS-YANG-MILLS-SINGLET-GAP-EMPIRICAL-027",
    ],
    ("v2", "172"): ["SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006"],
    ("v2", "203"): ["SFT-PHYS-LYAPUNOV-KS-CORRESPONDENCE-TERMINAL-008"],
    ("v2", "108"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v2", "214"): [
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",
    ],
    ("v2", "254"): ["SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030"],
    ("v2", "46"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "61"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "85"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "109"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "114"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "188"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "202"): ["SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"],
    ("v2", "258"): ["SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006"],
    ("v2", "259"): [
        "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006",
        "SFT-PHYS-COUPLING-ACCUMULATED-SEPARATION-TERMINAL-015",
    ],
    ("v2", "271"): ["SFT-PHYS-FORCE-COMPLETE-SECTOR-INVENTORY-003", "SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001"],
    ("v2", "103"): [
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
    ],
    ("v2", "279"): [
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
    ],
    ("v2", "280"): [
        "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008",
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
    ],
    ("v2", "289"): [
        "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
        "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
    ],
    ("v2", "283"): ["SFT-PHYS-PARKER-PROTON-ENERGY-TERMINAL-028"],
    ("v2", "290"): ["SFT-PHYS-HADRON-REGGE-TERMINAL-005"],
    ("v1", "XVIII-1"): ["SFT-PHYS-PROTON-RADIUS-TERMINAL-029"],
    ("v2", "165"): ["SFT-PHYS-PROTON-RADIUS-TERMINAL-029"],
}

# Source summaries are not scientific atoms.  These rows contain several
# independently checkable Physics statements and therefore must never be
# excluded or represented by a single catch-all obligation.  Each component
# below is separately mapped, receipted and assigned a same-strength boundary.
# A component marked closed still fails this audit if any named receipt is
# absent or is not currently model-admitted.
COMPOSITE_PHYSICS_ATOMS = {
    ("v2", "53"): (
        {
            "suffix": "PAULI-EXCLUSION",
            "statement": "Fermionic exchange admits one occupied carrier per identical one-constituent observation cell and excludes a second indistinguishable occupation.",
            "claim_ids": ("SFT-PHYS-QUANTUM-EXCLUSION-001", "SFT-PHYS-QUANTUM-INDISTINGUISHABILITY-001"),
            "closed": True,
            "status": "closed_by_antisymmetric_exchange_and_indistinguishability_receipts",
        },
    ),
    ("v2", "73"): (
        {
            "suffix": "PARTICLE-CHIRALITY",
            "statement": "The complete two-preimage held fibre provides two distinguished particle hands, while a one-sided interaction channel is parity asymmetric.",
            "claim_ids": ("SFT-PHYS-WEAK-PARITY-FIBRE-002",),
            "closed": True,
            "status": "closed_by_complete_held_fibre_parity_receipt",
        },
    ),
    ("v2", "121"): (
        {
            "suffix": "LEAST-ACTION",
            "statement": "Finite Fold paths carry an exact positive action order whose surviving generated path is certified against every admissible alternative.",
            "claim_ids": ("SFT-PHYS-DYNAMICS-SYMMETRY-ACTION-TERMINAL-016",),
            "closed": True,
            "status": "closed_by_complete_generated_path_and_action_census",
        },
    ),
    ("v2", "126"): (
        {
            "suffix": "VELOCITY-COMPOSITION",
            "statement": "The exact composition of two same-direction sublimit velocities is closed within the positive causal domain, fixes the limiting speed and has the low-speed correspondence as a derived boundary.",
            "claim_ids": ("SFT-PHYS-SPACETIME-INERTIAL-TRANSFORMATION-001", "SFT-PHYS-SPACETIME-LIMIT-SPEED-001", "SFT-PHYS-SPACETIME-VELOCITY-COMPOSITION-TERMINAL-033", "SFT-PHYS-VALIDATION-VELOCITY-COMPOSITION-034"),
            "closed": True,
            "status": "closed_by_complete_bilinear_census_exact_pair_reconstruction_and_postseal_Fizeau_discriminator",
        },
    ),
    ("v2", "164"): (
        {
            "suffix": "JOINT-NONLOCAL-CORRELATION",
            "statement": "A complete coprime joint support has one held preparation trace, nonfactorable correlations when appropriate and no local signal under complete remote-fibre observation.",
            "claim_ids": (
                "SFT-PHYS-QUANTUM-ENTANGLEMENT-001",
                "SFT-PHYS-QUANTUM-NO-SIGNALLING-001",
                "SFT-PHYS-QUANTUM-SUPPORT-UNCERTAINTY-TERMINAL-049",
                "SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050",
            ),
            "closed": True,
            "status": "closed_by_complete_two_by_three_and_three_by_five_factorability_projection_censuses_and_postseal_Bell_factorization_test",
        },
    ),
    ("v2", "191"): (
        {
            "suffix": "PHYSICAL-UNIVERSALITY",
            "statement": "Physical critical systems are partitioned into exact generated universality classes with separately forced critical carriers and post-seal measured comparisons.",
            "claim_ids": (
                "SFT-PHYS-THERMO-PHASE-EQUILIBRIUM-001",
                "SFT-PHYS-COUPLED-MAP-CRITICALITY-TERMINAL-008",
                "SFT-PHYS-CRITICALITY-UNIVERSALITY-TURBULENCE-TERMINAL-047",
                "SFT-PHYS-VALIDATION-CRITICALITY-UNIVERSALITY-TURBULENCE-048",
            ),
            "closed": True,
            "status": "closed_by_two_generated_universality_classes_exact_exponent_carriers_complete_postseal_measurement_vector_and_retained_nonmatch",
        },
    ),
    ("v2", "291"): (
        {
            "suffix": "TULLY-FISHER",
            "statement": "The universal galactic luminosity/rotation carrier has a separately forced exact exponent and a post-seal astronomy comparison, independent of the row's Materials and planetary observations.",
            "claim_ids": (
                "SFT-PHYS-COSMO-STRUCTURE-GROWTH-001",
                "SFT-PHYS-STELLAR-GALACTIC-TIDAL-TERMINAL-067",
                "SFT-PHYS-VALIDATION-STELLAR-GALACTIC-TIDAL-068",
            ),
            "closed": True,
            "status": "closed_by_exact_fourth_power_rotation_carrier_complete_central_and_systematic_BTFR_comparison_and_retained_offset",
        },
    ),
    ("v1", "XVIII-8"): (
        {
            "suffix": "ALPHA",
            "statement": "The terminal inverse fine-structure ratio is structurally forced and independently compared after sealing.",
            "claim_ids": ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"),
            "closed": True,
            "status": "closed_by_terminal_exact_ratio_and_postseal_CODATA_receipt",
        },
        {
            "suffix": "STRONG",
            "statement": "The strong-sector coupling structure and its scale transport are structurally forced.",
            "claim_ids": ("SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001", "SFT-PHYS-COUPLING-RUNNING-CONVERGENCE-TERMINAL-006"),
            "closed": True,
            "status": "closed_by_colour_coupling_and_terminal_running_receipts",
        },
        {
            "suffix": "WEAK",
            "statement": "The electroweak mixing share and terminal on-shell transport are structurally forced and independently compared after sealing.",
            "claim_ids": ("SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002", "SFT-PHYS-ELECTROWEAK-TERMINAL-ON-SHELL-003", "SFT-PHYS-VALIDATION-ELECTROWEAK-TERMINAL-003"),
            "closed": True,
            "status": "closed_by_terminal_electroweak_receipts",
        },
        {
            "suffix": "LEPTONS",
            "statement": "The three charged-lepton mass ratios are fixed by one exact cubic and its terminal self-coupling successor.",
            "claim_ids": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001", "SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001", "SFT-PHYS-VALIDATION-CHARGED-LEPTON-KOIDE-001"),
            "closed": True,
            "status": "closed_by_terminal_charged_lepton_cubic_and_postseal_receipts",
        },
        {
            "suffix": "QUARKS",
            "statement": "The six quark mass carriers are fixed by the two channel cubics and terminal dressing law.",
            "claim_ids": ("SFT-PHYS-MATTER-QUARK-INVARIANTS-003", "SFT-PHYS-MATTER-QUARK-CUBICS-003", "SFT-PHYS-MATTER-QUARK-DRESSING-003", "SFT-PHYS-VALIDATION-QUARK-CKM-003"),
            "closed": True,
            "status": "closed_by_dual_quark_cubics_terminal_dressing_and_postseal_receipts",
        },
        {
            "suffix": "NEUTRINOS",
            "statement": "The neutrino mass ordering, splitting and positive absolute-mass carrier are fixed on the generated support.",
            "claim_ids": ("SFT-PHYS-NEUTRINO-POSITIVE-MASS-003", "SFT-PHYS-VALIDATION-NEUTRINO-MASS-MIXING-003"),
            "closed": True,
            "status": "closed_by_neutrino_mass_ordering_and_postseal_receipts",
        },
        {
            "suffix": "CKM",
            "statement": "The CKM magnitudes and CP carrier are fixed by the quark-mass and fibre-alignment construction.",
            "claim_ids": ("SFT-PHYS-MATTER-CKM-FIBRE-003", "SFT-PHYS-MATTER-CKM-PHYSICAL-003", "SFT-PHYS-MATTER-CKM-TERMINAL-004", "SFT-PHYS-VALIDATION-QUARK-CKM-003"),
            "closed": True,
            "status": "closed_by_terminal_CKM_and_postseal_receipts",
        },
        {
            "suffix": "PMNS",
            "statement": "The PMNS support angles and leptonic CP carrier are fixed by the lepton-sector construction.",
            "claim_ids": ("SFT-PHYS-NEUTRINO-PMNS-ANGLES-002", "SFT-PHYS-NEUTRINO-PMNS-CP-PHYSICAL-003", "SFT-PHYS-VALIDATION-NEUTRINO-MASS-MIXING-003"),
            "closed": True,
            "status": "closed_by_PMNS_CP_and_postseal_receipts",
        },
        {
            "suffix": "COSMIC-FRACTIONS",
            "statement": "The universal dark-to-baryon and complete cosmic-budget fractions are fixed on exact generated support.",
            "claim_ids": ("SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001", "SFT-PHYS-COSMO-COMPLETE-BUDGET-001", "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"),
            "closed": True,
            "status": "closed_by_exact_cosmic_budget_and_terminal_transport_receipts",
        },
        {
            "suffix": "ABSOLUTE-SCALE",
            "statement": "The physical hierarchy is carried by one exact dimensionless proton-to-Planck relation before dimensional units are named downstream.",
            "claim_ids": ("SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003", "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003"),
            "closed": True,
            "status": "closed_by_terminal_hierarchy_and_postseal_receipts",
        },
        {
            "suffix": "NO-OMISSION",
            "statement": "One enumerated certificate reconciles every claimed dimensionless Physics constant, mixing carrier and scale relation without omission or double ownership.",
            "claim_ids": ("SFT-PHYS-GRAND-LOCK-TERMINAL-075",),
            "closed": True,
            "status": "closed_by_complete_prelock_ownership_receipt_certificate_and_registration_hash_vector",
        },
        {
            "suffix": "EMPIRICAL-VECTOR",
            "statement": "Every member of the complete constant inventory is compared only after its structural value is sealed, with favorable and unfavorable outcomes retained in one vector.",
            "claim_ids": ("SFT-PHYS-GRAND-LOCK-TERMINAL-075", "SFT-PHYS-VALIDATION-GRAND-LOCK-076"),
            "closed": True,
            "status": "closed_by_complete_234_claim_147_source_empirical_vector_with_all_adverse_and_scope_boundaries_retained",
        },
    ),
    ("v1", "U3"): (
        {
            "suffix": "DEPENDENCY-DICTIONARY",
            "statement": "The complete Physics dictionary assigns every physical claim one categorical owner and one unbroken dependency trace to the One theorem.",
            "claim_ids": ("SFT-PHYS-GRAND-LOCK-TERMINAL-075",),
            "closed": True,
            "status": "closed_by_complete_534_node_acyclic_dependency_dictionary_with_every_Physics_claim_reaching_One",
        },
    ),
    ("v2", "274"): (
        {
            "suffix": "COUNTED-DEPTHS",
            "statement": "The down and up scale depths are counted from the generator-three support rather than selected from measured targets.",
            "claim_ids": ("SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030",),
            "closed": True,
            "status": "closed_by_unique_common_scale_axis_receipt",
        },
        {
            "suffix": "ALPHA",
            "statement": "The inverse fine-structure ratio is fixed at its exact terminal Fold value before comparison.",
            "claim_ids": ("SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001", "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"),
            "closed": True,
            "status": "closed_by_terminal_alpha_and_postseal_receipts",
        },
        {
            "suffix": "LEPTON",
            "statement": "The charged-lepton invariant and terminal mass carrier are fixed from the generated lepton cubic.",
            "claim_ids": ("SFT-PHYS-CONSTANT-CHARGED-LEPTON-TERMINAL-001",),
            "closed": True,
            "status": "closed_by_terminal_charged_lepton_receipt",
        },
        {
            "suffix": "QUARKS",
            "statement": "The two quark channel invariants and terminal dressing are fixed from the generated colour-hand supports.",
            "claim_ids": ("SFT-PHYS-MATTER-QUARK-CUBICS-003", "SFT-PHYS-MATTER-QUARK-DRESSING-003"),
            "closed": True,
            "status": "closed_by_dual_quark_cubic_and_dressing_receipts",
        },
        {
            "suffix": "DARK-FRACTIONS",
            "statement": "The dark-to-baryon and dark-matter shares are exact generated fractions on the common support.",
            "claim_ids": ("SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001", "SFT-PHYS-COSMO-COMPLETE-BUDGET-001", "SFT-PHYS-COSMO-COMPONENT-TRANSPORT-TERMINAL-032"),
            "closed": True,
            "status": "closed_by_dark_fraction_budget_and_transport_receipts",
        },
        {
            "suffix": "HUBBLE",
            "statement": "The early-to-late expansion calibration ratio is an exact generated relation.",
            "claim_ids": ("SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001",),
            "closed": True,
            "status": "closed_by_exact_Hubble_calibration_receipt",
        },
        {
            "suffix": "PLANCK",
            "statement": "The proton-to-Planck exponent and terminal hierarchy are fixed before dimensional comparison.",
            "claim_ids": ("SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003", "SFT-PHYS-VALIDATION-PROTON-PLANCK-TERMINAL-003"),
            "closed": True,
            "status": "closed_by_terminal_Planck_hierarchy_and_postseal_receipts",
        },
        {
            "suffix": "LAMBDA-FLOOR",
            "statement": "The previously asserted one-over-two-to-the-twentieth vacuum-density floor has a separately forced scale transport and physical correspondence.",
            "claim_ids": (
                "SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003",
                "SFT-PHYS-VACUUM-DENSITY-SCALE-TERMINAL-035",
                "SFT-PHYS-VALIDATION-VACUUM-DENSITY-SCALE-036",
            ),
            "closed": True,
            "status": "closed_by_exact_local_floor_finite_radiative_ledger_typed_scale_transport_and_postseal_Planck_CODATA_receipts",
        },
        {
            "suffix": "GENERATOR-PERTURBATION",
            "statement": "Changing the generated colour successor moves every and only colour-dependent constant through one enumerated covariant dependency web.",
            "claim_ids": ("SFT-PHYS-GRAND-LOCK-TERMINAL-075",),
            "closed": True,
            "status": "closed_by_complete_generator_three_to_four_adverse_census_with_all_21_declared_dependent_values_moving_and_independent_carriers_held",
        },
        {
            "suffix": "HALF-ONE-INVARIANCE",
            "statement": "The half-One coupling is independent of the colour generator and remains fixed under the generator perturbation.",
            "claim_ids": ("SFT-PHYS-VACUUM-HALF-ONE-FLOOR-003", "SFT-PHYS-INTERACTION-UNIFICATION-TERMINAL-025"),
            "closed": True,
            "status": "closed_by_half_One_and_interaction_unification_receipts",
        },
        {
            "suffix": "CROSS-DOMAIN-LOCKS",
            "statement": "The alpha, quark and dark-sector constructions reuse the same counted depth objects, and the complete identity graph is reconciled without duplicated premises.",
            "claim_ids": ("SFT-PHYS-SCALE-COMMON-AXIS-TERMINAL-030", "SFT-PHYS-GRAND-LOCK-TERMINAL-075"),
            "closed": True,
            "status": "closed_by_complete_cross_domain_identity_graph_and_all_value_reconciliation_certificate",
        },
    ),
}

SAME_STRENGTH_OVERRIDES = {
    **{
        ("v1", entry): (
            True,
            "closed_by_exact_exclusion_q4_q6_two_family_endpoint_inverse_mass_temperature_quarter_area_finite_floor_and_complete_postseal_compact_object_boundary",
        )
        for entry in ("IX-3", "IX-5")
    },
    ("v2", "255"): (
        True,
        "closed_by_exact_three_quarter_to_half_One_threshold_two_binary_fibre_endpoint_families_horizon_successor_and_complete_postseal_compact_object_boundary",
    ),
    **{("v1", entry): (True, "closed_by_depth_independent_stellar_stage_binding_terminal_collapse_thermonuclear_and_neutral_capture_law_with_complete_postseal_vector") for entry in ("IX-2", "IX-4")},
    **{("v2", entry): (True, "closed_by_exact_support_loss_endpoint_census_and_complete_stage_neutrino_gamma_and_neutron_capture_measurement_vector") for entry in ("140", "150")},
    ("v2", "128"): (True, "closed_by_complete_5832_form_fusion_fission_yield_threshold_census_2548_row_AME_comparison_and_complete_IAEA_energy_and_threshold_vector"),
    **{("v1", entry): (True, "closed_by_exact_stellar_galactic_tidal_terminal_law_complete_seven_source_vector_and_retained_piecewise_and_resonance_boundaries") for entry in ("IX-8", "IX-7", "IX-1")},
    **{("v2", entry): (True, "closed_by_exact_hydrostatic_radial_and_tidal_terminal_laws_with_complete_postseal_stellar_and_planetary_vector") for entry in ("152", "153")},
    ("v1", "D11d"): (True, "closed_by_unique_half_One_displaced_ground_complete_six_five_terminal_transport_exact_Higgs_ratio_and_complete_postseal_mass_and_self_coupling_vector"),
    ("v2", "287"): (True, "leading_half_quarter_eighth_hierarchy_retained_and_closed_by_exact_terminal_Higgs_ratio_native_self_coupling_and_complete_postseal_measurement_vector"),
    ("v2", "107"): (True, "closed_by_complete_all_dimension_positive_magnitude_effective_orbit_census_and_postseal_stability_comparison"),
    **{("v1", entry): (True, "closed_by_unique_vectorial_aligned_One_complete_cross_fibre_exclusion_baryon_One_invariant_and_postseal_EDM_proton_search_vector") for entry in ("XVIII-2", "N5", "N2")},
    **{("v1", entry): (True, "closed_by_terminal_dark_relic_Smithion_cubic_and_LFV_law_with_complete_postseal_density_galaxy_and_search_status_record") for entry in ("B-9N", "N8")},
    **{("v2", entry): (True, "closed_by_terminal_dark_relic_Smithion_cubic_and_LFV_law_with_complete_postseal_density_galaxy_and_search_status_record") for entry in ("271", "296", "297", "299")},
    **{("v1", entry): (True, "closed_by_terminal_particle_mode_generation_transport_and_complete_postseal_spectrum_mixing_lifetime_vector") for entry in ("G5", "M3", "M10", "M12", "M19")},
    **{("v2", entry): (True, "closed_by_terminal_particle_mode_generation_transport_and_complete_postseal_spectrum_mixing_lifetime_vector") for entry in ("87", "104", "106", "113", "212", "221", "222", "242", "246", "250")},
    ("v1", "I-9"): (True, "closed_by_complete_finite_boson_occupation_census_first_cold_lock_crossing_unique_shared_ground_word_and_postseal_BEC_measurement"),
    ("v1", "I-5"): (True, "closed_by_complete_preserving_alternating_occupation_census_exact_finite_weights_spin_return_and_postseal_Pauli_spinor_measurements"),
    ("v2", "23"): (True, "closed_by_typed_one_turn_two_turn_spin_return_alternating_pair_preservation_and_neutron_interferometry_interval"),
    ("v2", "51"): (True, "closed_by_complete_three_to_one_two_spin_census_terminal_deuteron_dinucleon_receipt_and_postseal_spinor_measurement"),
    ("v2", "100"): (True, "closed_by_positive_finite_fermion_cap_boson_no_ceiling_shared_ground_enumeration_and_postseal_BEC_Pauli_measurements"),
    ("v1", "I-7"): (True, "closed_by_exact_complementary_fluctuation_response_orbit_and_postseal_Johnson_noise_relation"),
    ("v1", "I-3"): (True, "closed_by_complete_fixed_count_throw_multinomial_census_and_explicit_measurement_boundary"),
    ("v1", "I-1"): (True, "closed_by_exact_finite_mean_total_identity_and_two_independent_postseal_thermometry_intervals"),
    ("v2", "88"): (True, "closed_by_exact_three_quarter_quarter_complementary_departure_and_noise_response_correspondence"),
    ("v2", "102"): (True, "closed_by_unique_half_One_binomial_maximum_and_detailed_balance_census"),
    ("v2", "155"): (True, "closed_by_exact_mean_throw_temperature_and_acoustic_kinetic_energy_correspondence"),
    ("v1", "VII-7"): (True, "closed_by_complete_finite_boson_census_fourth_power_relation_and_postseal_blackbody_vector"),
    ("v1", "VII-5"): (True, "closed_by_strict_inversion_gain_loss_threshold_positive_linewidth_and_postseal_laser_vector"),
    ("v1", "VII-1"): (True, "closed_by_exact_plasma_squared_carriers_and_postseal_direct_density_frequency_record"),
    ("v2", "48"): (True, "closed_by_stable_three_space_plus_energy_fourth_power_and_measured_exponent_four"),
    ("v2", "81"): (True, "closed_by_positive_whole_boundary_modes_and_postseal_cavity_resonance_record"),
    ("v2", "111"): (True, "closed_by_half_One_inversion_gain_loss_threshold_and_measured_feedback_narrowing"),
    ("v2", "146"): (True, "closed_by_exact_charge_stiffness_screening_carrier_and_two_flight_plasma_probe_record"),
    ("v2", "170"): (True, "closed_by_exact_magnetic_tension_over_inertia_squared_carrier_and_NASA_Alfven_record"),
    ("v1", "VIII-6"): (
        True,
        "closed_by_least_generator_volume_cover_exact_primordial_partition_and_complete_postseal_scalar_tensor_comparison",
    ),
    ("v1", "VIII-5"): (
        True,
        "closed_by_exact_quarter_half_One_growth_and_third_fourth_power_relative_transport",
    ),
    ("v1", "N7"): (
        True,
        "closed_by_five_exact_Fold_doublings_first_complete_exit_and_explicit_conventional_efold_type_boundary",
    ),
    ("v2", "31"): (
        True,
        "closed_by_exact_31_over_32_scalar_support_and_postseal_Planck_interval",
    ),
    ("v2", "42"): (
        True,
        "closed_by_exact_two_step_perturbation_growth_and_component_transport",
    ),
    ("v1", "VIII-1"): (
        True,
        "closed_by_exact_inverse_temperature_scale_transport_threshold_order_and_postseal_direct_thermometry",
    ),
    ("v1", "VIII-2"): (
        True,
        "closed_by_typed_freezeout_capture_transport_analytic_partition_and_complete_adverse_abundance_comparison",
    ),
    ("v1", "VIII-3"): (
        True,
        "closed_by_finite_visibility_internal_acoustic_parity_and_complete_Planck_projection_comparison",
    ),
    ("v2", "58"): (
        True,
        "closed_by_corrected_neutron_share_ratio_transport_and_postseal_abundance_record",
    ),
    ("v2", "139"): (
        True,
        "closed_by_half_One_midpoint_finite_visibility_and_recombination_measurement_receipt",
    ),
    ("v2", "197"): (
        True,
        "closed_by_single_exact_temperature_threshold_component_transport_composition",
    ),
    ("v1", "XVIII-3"): (
        True,
        "closed_by_exact_local_floor_global_share_normalized_Lambda_scale_transport_and_postseal_Planck_CODATA_receipts",
    ),
    ("v1", "N1c"): (
        True,
        "closed_by_positive_vacuum_floor_finite_mode_ledger_typed_density_transport_and_complete_measurement_vector",
    ),
    ("v2", "35"): (
        True,
        "closed_by_invariant_vacuum_transport_tension_orientation_terminal_density_and_postseal_measurement_receipts",
    ),
    ("v2", "40"): (
        True,
        "closed_by_complete_finite_zero_point_ledger_common_scale_typing_and_postseal_cosmological_comparison",
    ),
    ("v1", "B-4N"): (
        True,
        "closed_by_complete_odd_sector_standing_mode_census_and_unique_self_antipode",
    ),
    ("v1", "B1"): (
        True,
        "closed_by_single_m_indexed_coupling_mixing_mass_and_running_table",
    ),
    ("v1", "B13"): (
        True,
        "closed_by_depth_independent_positive_sector_gaps_and_finite_noncoincidence",
    ),
    ("v1", "M1"): (
        True,
        "closed_by_positive_unison_shortfall_rest_carrier_at_every_common_support",
    ),
    ("v1", "G7"): (
        True,
        "closed_by_exact_composite_orbit_bijection_LCM_correlation_and_no_signalling_boundary",
    ),
    ("v1", "G8"): (
        True,
        "closed_by_denominator_preservation_and_adverse_literal_physical_transport_resolution",
    ),
    ("v1", "G4"): (
        True,
        "closed_by_single_finite_lattice_rank_two_two_mode_loop_horizon_and_dimension_composition",
    ),
    ("v1", "D1"): (
        True,
        "closed_by_exact_conservative_stencil_phase_mode_family_and_inherited_dispersion_comparison",
    ),
    ("v1", "D1c"): (
        True,
        "closed_by_complete_planar_operator_point_source_ring_and_causal_diamond_census",
    ),
    ("v1", "D1d"): (
        True,
        "closed_by_complete_cubic_operator_point_source_ring_causal_octahedron_and_cubic_comparison",
    ),
    ("v1", "VIII-4"): (
        True,
        "closed_by_complete_baryon_change_CP_nonequilibrium_process_census_and_inherited_abundance_comparison",
    ),
    ("v1", "D11a"): (True, "closed_by_exact_conserved_forward_rest_transfer_and_inverse_mass_range"),
    ("v1", "D11c"): (True, "closed_by_complete_One_preservation_positive_shortfall_and_sealed_electroweak_comparison"),
    ("v1", "D11f"): (True, "closed_by_finite_native_range_boundary_and_positive_massless_finite_radius_transport"),
    ("v1", "XIV-6"): (True, "physical_atom_closed_device_and_UAP_interpretation_excluded"),
    ("v2", "118"): (True, "closed_by_finite_continuum_correspondence"),
    ("v2", "203"): (True, "closed_by_exact_expansion_information_rate_correspondence"),
    ("v2", "258"): (True, "closed_by_depth_independent_common_support_gap_formula"),
    ("v1", "B10"): (True, "closed_by_depth_independent_finite_accumulation_and_tolerance_witness"),
    ("v2", "259"): (True, "closed_by_depth_independent_finite_accumulation_and_tolerance_witness"),
    ("v1", "XIII-4"): (True, "closed_by_odd_core_invariance_and_complete_partition_symmetry_census"),
    ("v1", "XIII-5"): (True, "closed_by_depth_independent_dyadic_Fold_descent_and_positive_action_boundary"),
    ("v2", "91"): (True, "closed_by_two_fibre_partition_and_reciprocal_encounter_path_law"),
    ("v2", "290"): (
        True,
        "closed_by_normalized_affine_law_and_complete_postseal_PDG_trajectory_resolution",
    ),
    ("v1", "B8"): (
        True,
        "closed_by_common_binary_support_exact_pair_gap_finite_tolerance_and_complete_running_comparison",
    ),
    ("v2", "172"): (
        True,
        "closed_by_generator_indexed_running_functions_common_support_and_multiscale_comparison",
    ),
    ("v1", "B3"): (
        True,
        "closed_by_terminal_held_support_weak_curve_and_complete_postseal_weak_strong_electromagnetic_vector",
    ),
    ("v1", "B4"): (
        True,
        "closed_by_one_based_common_support_spacing_landmarks_and_exact_hierarchy_transport",
    ),
    ("v1", "B5"): (
        True,
        "closed_by_terminal_held_support_weak_curve_and_complete_postseal_weak_strong_electromagnetic_vector",
    ),
    ("v1", "B7"): (
        True,
        "closed_by_exact_terminal_complete_support_to_held_active_level_relation",
    ),
    ("v1", "B11"): (
        True,
        "closed_by_complete_multi_sector_running_vector_on_one_generated_support_axis",
    ),
    ("v1", "B12"): (
        True,
        "closed_by_exact_invariance_of_like_dimension_ratios_under_common_positive_rational_unit_rescaling",
    ),
    ("v1", "B15"): (
        True,
        "closed_by_unique_support_two_internal_source_power_and_later_odd_factor_exclusion",
    ),
    ("v1", "B17"): (
        True,
        "closed_by_one_based_common_support_spacing_landmarks_and_exact_hierarchy_transport",
    ),
    ("v1", "XIII-6"): (
        True,
        "closed_by_complete_named_common_scale_axis_landmarks_and_exact_proton_Planck_transport",
    ),
    ("v2", "108"): (
        True,
        "closed_by_one_based_common_support_spacing_landmarks_and_exact_hierarchy_transport",
    ),
    ("v2", "214"): (
        True,
        "closed_by_complete_multi_sector_running_vector_on_one_generated_support_axis",
    ),
    ("v2", "254"): (
        True,
        "closed_by_one_based_common_support_spacing_landmarks_and_exact_hierarchy_transport",
    ),
    ("v1", "B-10N"): (
        True,
        "closed_by_complete_denominator_seven_two_orbit_partition_antipodes_and_depth_independent_confinement",
    ),
    ("v1", "B-11N"): (
        True,
        "closed_by_complete_denominator_eleven_ten_mode_orbit_five_pair_inventory_and_holding_law",
    ),
    ("v1", "B-12N"): (
        True,
        "closed_by_complete_denominator_seventeen_two_eight_mode_orbit_partition_and_holding_law",
    ),
    ("v1", "B-13N"): (
        True,
        "closed_by_complete_denominator_twenty_three_two_eleven_mode_orbit_partition_and_holding_law",
    ),
    ("v1", "B-14N"): (
        True,
        "closed_by_complete_denominator_twenty_nine_twenty_eight_mode_orbit_fourteen_pair_inventory_and_holding_law",
    ),
    ("v1", "VIII-11"): (
        True,
        "closed_by_terminal_five_sixteenths_matter_fraction_curve_and_complete_32_row_expansion_vector",
    ),
    ("v1", "VIII-10"): (
        True,
        "closed_by_terminal_seventeen_thirty_seconds_typed_accelerating_magnitude_and_postseal_q_interval",
    ),
    ("v1", "VIII-9"): (
        True,
        "closed_by_exact_eleven_fifths_equality_and_twenty_two_fifths_acceleration_cube_thresholds",
    ),
    ("v1", "VIII-8"): (
        True,
        "closed_by_terminal_eleven_five_squared_expansion_law_and_complete_32_row_CCH_vector",
    ),
    ("v1", "N1d"): (
        True,
        "closed_by_Fold_invariant_vacuum_tension_One_and_complete_constant_state_interval_with_DESI_adverse_row_retained",
    ),
    ("v1", "N1f"): (
        True,
        "closed_by_generator_three_matter_volume_radiation_recurrence_and_vacuum_invariant_transport",
    ),
    ("v2", "46"): (
        True,
        "superseded_half_magnitude_resolved_by_terminal_seventeen_thirty_seconds_accelerating_carrier_and_postseal_q_interval",
    ),
    ("v2", "61"): (
        True,
        "closed_by_exact_third_power_fourth_power_and_invariant_One_component_transport",
    ),
    ("v2", "85"): (
        True,
        "closed_by_strict_four_three_invariant_transport_order_for_radiation_matter_and_vacuum",
    ),
    ("v2", "109"): (
        True,
        "superseded_quarter_scale_condition_resolved_by_terminal_twenty_two_fifths_onset_cube_and_postseal_transition_interval",
    ),
    ("v2", "114"): (
        True,
        "superseded_two_thirds_curve_resolved_by_terminal_eleven_five_curve_and_complete_32_row_CCH_vector",
    ),
    ("v2", "188"): (
        True,
        "closed_by_invariant_One_transport_and_typed_tension_One_correspondence_without_negative_proof_scalar",
    ),
    ("v2", "202"): (
        True,
        "superseded_one_third_endpoint_resolved_by_terminal_five_sixteenths_matter_fraction_curve",
    ),
    ("v2", "70"): (True, "closed_by_exact_positive_mass_range_order_and_massless_transport"),
    ("v2", "110"): (
        True,
        "closed_by_dimension_independent_conservative_nearest_neighbour_family",
    ),
    ("v2", "205"): (
        True,
        "closed_by_half_One_planar_partition_and_complete_causal_diamond_census",
    ),
    ("v2", "183"): (
        True,
        "closed_by_exact_one_two_three_period_dictionary_and_joint_six_recurrence",
    ),
    ("v2", "243"): (
        True,
        "closed_by_terminal_interaction_table_with_internally_inconsistent_prior_slope_bundle_resolved_adversely",
    ),
    ("v2", "240"): (True, "closed_by_preserved_broken_channel_mass_discriminator_and_inherited_WZ_comparison"),
    ("v1", "I-10"): (
        True,
        "closed_by_exact_reset_demon_ledger_and_sealed_primary_Landauer_comparison",
    ),
    ("v2", "123"): (
        True,
        "closed_by_exact_one_record_cost_and_sealed_primary_Landauer_comparison",
    ),
    ("v1", "XII-5"): (
        True,
        "closed_by_exact_positive_colour_singlet_gap_and_complete_postseal_lattice_spectrum_boundary",
    ),
    ("v2", "119"): (
        True,
        "closed_by_one_third_two_thirds_partition_with_local_massless_carrier_correction_and_postseal_lattice_boundary",
    ),
    ("v2", "283"): (
        True,
        "closed_by_exact_terminal_eight_alpha_squared_relation_complete_source_custody_range_level_correspondence_and_adverse_precision_resolution",
    ),
    ("v1", "XVIII-1"): (
        True,
        "closed_by_exact_probe_independent_radius_coefficient_complete_current_vector_and_retained_historical_conflict",
    ),
    ("v2", "165"): (
        True,
        "closed_by_exact_probe_independent_radius_coefficient_complete_current_vector_and_retained_historical_conflict",
    ),
    ("v1", "XIII-2"): (
        True,
        "closed_by_exact_binary_critical_exponents_distinct_cascade_class_and_complete_postseal_measurement_vector",
    ),
    ("v1", "I-6"): (
        True,
        "closed_by_exact_generator_three_two_thirds_structure_and_falling_five_thirds_spectrum_with_postseal_turbulence_records",
    ),
    ("v2", "103"): (
        True,
        "closed_by_exact_binary_critical_scaling_identities_and_complete_postseal_exponent_intervals",
    ),
    ("v2", "279"): (
        True,
        "closed_by_exact_generated_universality_keys_and_complete_matching_and_nonmatching_physical_vector",
    ),
    ("v2", "280"): (
        True,
        "closed_by_normalized_threshold_exact_class_key_and_retained_application_boundary",
    ),
    ("v2", "289"): (
        True,
        "closed_by_depth_independent_cube_square_fifth_power_cascade_and_complete_postseal_turbulence_comparison",
    ),
    ("v1", "D6b"): (
        True,
        "closed_by_depth_independent_unit_free_support_spread_and_complete_postseal_Bell_factorization_test",
    ),
    ("v1", "D6"): (
        True,
        "closed_by_complete_dyadic_Walsh_support_census_exact_orthogonality_and_depth_independent_induction",
    ),
    ("v2", "76"): (
        True,
        "closed_by_complete_two_by_three_joint_support_census_with_product_factorability_correction",
    ),
    ("v2", "159"): (
        True,
        "closed_by_preparation_derived_depth_three_and_exact_one_eighth_branch_unit",
    ),
    ("v2", "260"): (
        True,
        "closed_by_exact_depth_two_one_sixteenth_support_spread_floor_without_variance_relabelling",
    ),
    ("v1", "IX-6"): (
        True,
        "closed_by_depth_independent_rising_chirp_first_contact_merger_positive_finite_ringdown_and_complete_observational_postseal_vector",
    ),
}

GAP_OVERRIDES = {
    ("v1", "IX-1"): "Exact mass-luminosity exponent, lifetime law and post-seal stellar vector are not present at the same strength.",
    ("v1", "IX-2"): "The complete staged stellar fusion chain and its distinct dimensional thresholds are not present at the same strength.",
    ("v1", "IX-3"): "Zero-parameter Chandrasekhar/TOV magnitude carriers and authoritative comparisons are not present.",
    ("v1", "IX-4"): "Complete core-collapse, thermonuclear and r-process channel laws are not present at the same strength.",
    ("v1", "IX-5"): "Hawking temperature and explicit horizon area-support law remain absent at the stated strength.",
    ("v1", "IX-7"): "The gauge-inert relic and modified-gravity discriminator are not present at the same strength.",
    ("v1", "IX-8"): "General resonance is present; dissipative tidal evolution and population discriminator are not.",
    ("v1", "XIII-4"): "Conservation laws are present; the full symmetry-to-conserved-carrier equivalence is not separately admitted.",
    ("v1", "XIII-5"): "No same-strength least-action/extremal-path Physics receipt is registered.",
    ("v1", "I-10"): "The one-distinction reset, half-One native throw and complete demon/environment ledger are sealed. The target-inaccessible dimensional Landauer experiment remains.",
    ("v2", "123"): "The one-distinction reset, half-One native throw and complete demon/environment ledger are sealed. The target-inaccessible dimensional Landauer experiment remains.",
    ("v2", "42"): "A general structure-growth relation exists; the asserted two-step gravitational amplification is not same-strength.",
    ("v2", "290"): "Normalized affine Regge support exists; literal physical mass-squared spacing and the full measured trajectory remain post-seal work.",
}


def is_physics(source: str, entry: str, legacy: dict | None) -> tuple[bool, str]:
    if (source, entry) in COMPOSITE_PHYSICS_ATOMS:
        return True, "Physics (explicitly decomposed composite source)"
    if source == "v1" and entry in V1_EXCLUSIONS:
        return False, V1_EXCLUSIONS[entry]
    if source == "v2" and int(entry) in V2_EXCLUSIONS:
        return False, V2_EXCLUSIONS[int(entry)]
    if source == "v1" and entry in V1_ADDITIONS:
        return True, "Physics"
    if source == "v2" and int(entry) in V2_ADDITIONS:
        return True, "Physics"
    if legacy is not None:
        return True, "Physics"
    return False, "another categorical branch or corpus-level synthesis"


def make_atom(
    *,
    atom_id: str,
    statement: str,
    candidate_ids: list[str],
    claims: dict[str, dict],
    closed: bool,
    status: str,
    basis: str,
    gap: str | None,
    require_all_candidates: bool = False,
) -> dict:
    candidate_ids = list(dict.fromkeys(candidate_ids))
    physics_ids = [
        claim_id for claim_id in candidate_ids
        if claim_id in claims
        and claims[claim_id].get("branch") == "physics"
        and claims[claim_id].get("model_admitted") is True
    ]
    unavailable_ids = [claim_id for claim_id in candidate_ids if claim_id not in physics_ids]
    if closed and require_all_candidates and unavailable_ids:
        raise SystemExit(
            f"same-strength component {atom_id} names unavailable current "
            f"Physics receipts: {unavailable_ids}"
        )
    if not closed and not gap:
        gap = (
            "No current model-admitted Physics receipt is mapped to this atom."
            if not physics_ids else
            "Current Physics receipts are related, but same-strength reconstruction has not been demonstrated."
        )
    for claim_id in physics_ids:
        receipt_path = ROOT / claims[claim_id]["receipt_path"]
        if not receipt_path.is_file():
            raise SystemExit(f"missing current Physics receipt for {atom_id}: {receipt_path}")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (
            receipt.get("claim_id") != claim_id
            or receipt.get("model_admitted") is not True
            or receipt.get("receipt_hash") != claims[claim_id]["receipt_hash"]
        ):
            raise SystemExit(f"current Physics receipt mismatch for {atom_id}: {claim_id}")
    return {
        "atom_id": atom_id,
        "owner": "Physics",
        "atomic_statement": statement,
        "current_v3_claim_ids": physics_ids,
        "current_v3_receipts": [
            {
                "claim_id": claim_id,
                "receipt_path": claims[claim_id]["receipt_path"],
                "receipt_hash": claims[claim_id]["receipt_hash"],
            }
            for claim_id in physics_ids
        ],
        "candidate_ids_absent_or_not_currently_admitted_in_physics": unavailable_ids,
        "same_strength_closed": closed,
        "same_strength_status": status,
        "same_strength_basis": basis,
        "remaining_gap": None if closed else gap,
    }


def build() -> dict:
    v1 = json.loads(V1_PATH.read_text())
    v2 = json.loads(V2_PATH.read_text())
    claims_data = json.loads(CLAIMS_PATH.read_text())
    claims = {row["claim_id"]: row for row in claims_data["claims"]}
    legacy = legacy_candidates()
    source_rows = []

    raw_rows = []
    for row in v1["rows"]:
        raw_rows.append(("v1", str(row["v1_claim_id"]), row["prior_result_observation"], row["source_row_sha256"], row["explicit_v3_claim_ids"]))
    for row in v2["steps"]:
        raw_rows.append(("v2", str(row["step"]), row["prior_result_observation"], row["source_block_sha256"], row["explicit_v3_claim_ids"]))

    for source, entry, observation, source_hash, explicit_ids in raw_rows:
        legacy_row = legacy.get((source, entry))
        owned, owner = is_physics(source, entry, legacy_row)
        record = {
            "source": source,
            "source_entry": int(entry) if source == "v2" else entry,
            "source_hash": source_hash,
            "source_observation": observation,
            "categorical_owner": owner,
            "physics_owned": owned,
            "categorical_boundary": MIXED_BOUNDARIES.get((source, entry)),
        }
        if not owned:
            record["disposition"] = "excluded_from_physics_atomic_ownership"
            record["physics_atoms"] = []
            record["atomization_mode"] = "explicit_primary_owner_exclusion_or_nonphysics_source_disposition"
            source_rows.append(record)
            continue

        composite_components = COMPOSITE_PHYSICS_ATOMS.get((source, entry))
        if composite_components:
            atoms = []
            for component in composite_components:
                atoms.append(make_atom(
                    atom_id=f"SFT-PRIOR-{source.upper()}-{entry}-PHYS-{component['suffix']}",
                    statement=component["statement"],
                    candidate_ids=list(component["claim_ids"]),
                    claims=claims,
                    closed=bool(component["closed"]),
                    status=component["status"],
                    basis="explicit_composite_source_decomposition_and_current_receipt_check",
                    gap=component.get("gap"),
                    require_all_candidates=True,
                ))
            record["disposition"] = (
                "decomposed_composite_all_physics_atoms_same_strength_closed"
                if all(atom["same_strength_closed"] for atom in atoms)
                else "decomposed_composite_contains_open_physics_atoms"
            )
            record["physics_atoms"] = atoms
            record["decomposition_complete"] = True
            record["atomization_mode"] = "explicit_multi_atom_decomposition"
            source_rows.append(record)
            continue

        candidate_ids = list(explicit_ids)
        legacy_closed = False
        legacy_reason = None
        if legacy_row:
            for atom in legacy_row.get("atomic_obligations", []):
                candidate_ids.extend(atom.get("v3_claim_ids", []))
                legacy_closed = legacy_closed or bool(atom.get("same_strength_closed", False))
                legacy_reason = atom.get("remaining_work") or legacy_reason
        candidate_ids.extend(ADDITIONAL_MAPS.get((source, entry), []))
        mapped_current_physics_ids = [
            claim_id for claim_id in dict.fromkeys(candidate_ids)
            if claim_id in claims
            and claims[claim_id].get("branch") == "physics"
            and claims[claim_id].get("model_admitted") is True
        ]
        closed, status = SAME_STRENGTH_OVERRIDES.get(
            (source, entry),
            (
                legacy_closed and bool(mapped_current_physics_ids),
                "same_strength_closed_by_reviewed_current_receipts"
                if legacy_closed and mapped_current_physics_ids else "same_strength_open",
            ),
        )
        gap = GAP_OVERRIDES.get((source, entry))
        if not closed and not gap:
            gap = legacy_reason
        atom_id = f"SFT-PRIOR-{source.upper()}-{entry}-PHYS-001"
        boundary = MIXED_BOUNDARIES.get((source, entry))
        atomic_statement = observation
        if boundary:
            atomic_statement = boundary.split(";", 1)[0].removeprefix("Physics owns ")
        atom = make_atom(
            atom_id=atom_id,
            statement=atomic_statement,
            candidate_ids=candidate_ids,
            claims=claims,
            closed=closed,
            status=status,
            basis=(
                "explicit_current_atomic_override"
                if (source, entry) in SAME_STRENGTH_OVERRIDES
                else "retained_prior_same_strength_review_after_categorical_reclassification_and_current_receipt_check"
                if closed
                else "open_boundary_preserved_or_newly_identified_by_categorical_audit"
            ),
            gap=(gap if gap not in {None, "none"} else None),
        )
        record["disposition"] = "physics_atom_same_strength_closed" if closed else "physics_atom_open"
        record["physics_atoms"] = [atom]
        record["atomization_mode"] = "single_scientific_obligation_or_explicit_mixed_branch_boundary"
        source_rows.append(record)

    physics_atoms = [a for r in source_rows for a in r["physics_atoms"]]
    atom_ids = [atom["atom_id"] for atom in physics_atoms]
    if len(atom_ids) != len(set(atom_ids)):
        raise SystemExit("duplicate Physics atom identifier in ownership audit")
    source_keys = {(row["source"], str(row["source_entry"])) for row in source_rows}
    missing_composite_rows = sorted(set(COMPOSITE_PHYSICS_ATOMS) - source_keys)
    if missing_composite_rows:
        raise SystemExit(f"declared composite rows absent from source surface: {missing_composite_rows}")
    incomplete_composites = [
        f"{row['source']}:{row['source_entry']}"
        for row in source_rows
        if (row["source"], str(row["source_entry"])) in COMPOSITE_PHYSICS_ATOMS
        and not row.get("decomposition_complete")
    ]
    if incomplete_composites:
        raise SystemExit(f"composite source rows not decomposed: {incomplete_composites}")
    closed_atoms = [a for a in physics_atoms if a["same_strength_closed"]]
    open_atoms = [a for a in physics_atoms if not a["same_strength_closed"]]
    unmapped_open = [a for a in open_atoms if not a["current_v3_claim_ids"]]
    mapped_open = [a for a in open_atoms if a["current_v3_claim_ids"]]
    return {
        "schema": "sft.physics.v1-v2-atomic-ownership-audit.v2",
        "audit_status": "current_evidence_closed_extension_open" if not open_atoms else "open_blocking",
        "purpose": "Identify only categorically Physics-owned V1/V2 atoms and test whether current model-admitted V3 Physics receipts reconstruct them at the same strength.",
        "authority_boundary": {
            "engine_modified": False,
            "claims_admitted": False,
            "semantic_similarity_closes_claims": False,
            "mapping_snapshot_use": "candidate links and prior same-strength review are retained only after categorical reclassification and current model-admitted receipt verification; former blanket ownership is rejected",
            "one_owner_law": "Each scientific atom has exactly one primary categorical owner; mixed source prose is decomposed at the stated boundary.",
            "composite_row_law": "A branch summary, multi-domain row or multi-value row may not be excluded wholesale; every independently checkable Physics component is separately mapped and dispositioned.",
            "receipt_verification": "Every mapped current Physics receipt is opened and checked for claim identity, model-admitted status and the census receipt hash.",
        },
        "source_surface": {
            "v1_path": str(v1["source_path"]),
            "v1_sha256": v1["source_sha256"],
            "v1_row_count": v1["source_row_count"],
            "v2_source_id": v2["source_id"],
            "v2_sha256": v2["source_sha256"],
            "v2_step_count": v2["source_step_count"],
            "current_claim_census_path": str(CLAIMS_PATH.relative_to(ROOT)),
            "current_claim_census_sha256": "sha256:" + hashlib.sha256(CLAIMS_PATH.read_bytes()).hexdigest(),
            "total_source_rows_reviewed": len(source_rows),
            "explicitly_decomposed_composite_row_count": sum(bool(r.get("decomposition_complete")) for r in source_rows),
        },
        "summary": {
            "physics_owned_atom_count": len(physics_atoms),
            "same_strength_closed_atom_count": len(closed_atoms),
            "same_strength_open_atom_count": len(open_atoms),
            "open_with_related_v3_receipts": len(mapped_open),
            "open_without_mapped_v3_physics_receipt": len(unmapped_open),
            "non_physics_source_row_count": sum(not r["physics_owned"] for r in source_rows),
            "unique_atom_ids": len(atom_ids) == len(set(atom_ids)),
            "all_declared_composite_rows_decomposed": not missing_composite_rows and not incomplete_composites,
            "publication_blocked": bool(open_atoms),
        },
        "missing_physics_atoms": [
            {
                "atom_id": atom["atom_id"],
                "current_v3_claim_ids": atom["current_v3_claim_ids"],
                "remaining_gap": atom["remaining_gap"],
            }
            for atom in open_atoms
        ],
        "source_rows": source_rows,
    }


def main() -> None:
    result = build()
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    summary = result["summary"]
    lines = [
        "# Atomic V1/V2 Physics ownership and V3 coverage audit",
        "",
        "This is a categorical, one-owner audit of the complete 356-row V1 and 407-step V2 source surfaces. It does not assign every prior derivation to Physics. Mixed prose is split at an explicit scientific boundary; only universal physical laws, physical values, and physical correspondences are owned here. Astronomy/Cosmology retains histories and observed populations; Chemistry, Materials, Biology, Consciousness, Mathematics, computation, and applications retain their own atoms.",
        "",
        "The admission engine was not called or edited, and this audit admits no claim. A semantic resemblance never closes an obligation. `closed` below means a same-strength current model-admitted receipt was already established; `open` means the V3 Physics branch still lacks all or part of the prior atom at the stated strength.",
        "",
        "## Result",
        "",
        f"- Complete source rows reviewed: {result['source_surface']['total_source_rows_reviewed']}",
        f"- Composite source rows explicitly decomposed: {result['source_surface']['explicitly_decomposed_composite_row_count']}",
        f"- Categorically Physics-owned atoms: {summary['physics_owned_atom_count']}",
        f"- Same-strength closed in current V3: {summary['same_strength_closed_atom_count']}",
        f"- Open at the same-strength boundary: {summary['same_strength_open_atom_count']}",
        f"- Open with related but insufficient V3 receipts: {summary['open_with_related_v3_receipts']}",
        f"- Open without a mapped V3 Physics receipt: {summary['open_without_mapped_v3_physics_receipt']}",
        f"- Source rows excluded from Physics ownership: {summary['non_physics_source_row_count']}",
        f"- Unique Physics atom identifiers: {summary['unique_atom_ids']}",
        f"- Every declared composite source row decomposed: {summary['all_declared_composite_rows_decomposed']}",
        "",
        "The Physics publication remains blocked by the open atoms. Branch closure remains a dated current-knowledge boundary and is open to lawful extension even after these obligations are resolved.",
        "",
        "## Open Physics atoms",
        "",
        "| Source | Atom | Related current V3 receipts | Exact remaining boundary |",
        "|---|---|---|---|",
    ]
    for row in result["source_rows"]:
        for atom in row["physics_atoms"]:
            if atom["same_strength_closed"]:
                continue
            claims = ", ".join(atom["current_v3_claim_ids"]) or "none"
            gap = atom["remaining_gap"].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {row['source']} {row['source_entry']} | `{atom['atom_id']}` | {claims} | {gap} |")
    lines.extend([
        "",
        "## Machine-readable evidence",
        "",
        "The companion `physics_v1_v2_atomic_ownership.json` retains every source observation and hash, every categorical exclusion or mixed-row boundary, every current claim ID, receipt path and receipt hash, and the complete open-atom list.",
        "",
    ])
    REPORT.write_text("\n".join(lines))
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
