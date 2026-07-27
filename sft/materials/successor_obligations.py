"""Target-blind successor obligations discovered by the Materials V1/V2 audit.

This surface extends, but never rewrites, the frozen 84-claim Materials
foundation.  It contains no external source identity, measurement value or
post-seal observation.
"""

from __future__ import annotations

from sft.materials.obligations import MaterialsObligation


def row(
    claim_id: str,
    title: str,
    subbranch: str,
    carrier: str,
    relation: str,
    organization: str,
    observation: str,
    statement: str,
) -> MaterialsObligation:
    return MaterialsObligation(
        claim_id, title, subbranch, carrier, relation, organization,
        observation, statement,
    )


MATERIALS_SUCCESSOR_OBLIGATIONS = (
    row(
        "SFT-MAT-CRYST-QUASICRYSTAL-INFLATION-002",
        "Exact quasicrystal substitution inflation",
        "crystal_quasicrystal",
        "two-labelled-aperiodic-word-carrier",
        "first-label-to-pair-second-label-to-first-substitution",
        "finite-word-provenance-and-nonperiodic-population-retained",
        "positive-successor-and-no-rational-fixed-scale",
        "The two-label substitution A to AB and B to A generates an exact positive finite successor chain whose population pair never admits a positive rational fixed scale satisfying the recurrence.",
    ),
    row(
        "SFT-MAT-CRYST-PHONON-THERMAL-LIMITS-002",
        "Acoustic, optical and thermal mode limits",
        "crystal_quasicrystal",
        "rank-three-labelled-displacement-carrier",
        "shared-and-opposed-basis-displacement-relation",
        "acoustic-optical-and-complete-mode-support-retained",
        "gapless-shared-mode-and-rank-three-cube-count",
        "Uniform shared displacement supplies a gapless acoustic class, a retained two-constituent basis supplies an opposed optical class, and positive rank-three support contains the exact cube count of low-support modes and three displacement modes per site at complete support.",
    ),
    row(
        "SFT-MAT-SEMI-RECTIFICATION-002",
        "Exact p-n junction rectification",
        "electronic_semiconductor",
        "junction-barrier-and-held-bias-carrier",
        "orientation-conditioned-barrier-transition",
        "forward-opening-and-reverse-strengthening-retained",
        "complete-two-orientation-transport-census",
        "The two held bias orientations of a retained p-n junction force distinct forward barrier-opening and reverse barrier-strengthening transition classes without signed proof quantities.",
    ),
    row(
        "SFT-MAT-SC-ISOTOPE-RESPONSE-002",
        "Superconducting isotope-response record",
        "superconducting_superfluid_topological",
        "paired-material-and-isotope-identity-carrier",
        "isotope-substitution-to-transition-response-relation",
        "pairing-law-independent-provenance-retained",
        "specimen-method-condition-bounded-response",
        "A superconducting isotope comparison is admissible only when isotope identity, constituent-mass distinction and transition response are retained together while the observation remains incapable of selecting the pairing law.",
    ),
    row(
        "SFT-MAT-MAG-FERRIMAGNETISM-002",
        "Ferrimagnetic sublattice order",
        "thermal_magnetic_optical",
        "two-distinguishable-magnetic-sublattice-carrier",
        "opposed-unequal-positive-moment-relation",
        "local-opposition-and-nonempty-bulk-gap-retained",
        "partial-net-moment-order-class",
        "Opposed distinguishable magnetic sublattices with unequal positive counted moment support force a nonempty partial bulk moment class distinct from aligned and equal-opposed order.",
    ),
    row(
        "SFT-MAT-HALL-QUANTIZATION-002",
        "Integer and primary fractional Hall classes",
        "superconducting_superfluid_topological",
        "gapped-oriented-two-generator-material-carrier",
        "whole-winding-and-reduced-odd-part-relation",
        "gap-preserving-transport-classes-retained",
        "integer-and-primary-odd-denominator-filling-census",
        "A gapped oriented two-generator material carrier retains whole winding classes and a separately bounded primary hierarchy of reduced positive odd-denominator parts, invariant under gap-preserving deformation.",
    ),
    row(
        "SFT-MAT-TOPO-EDGE-COUNT-002",
        "Exact topological boundary-mode count",
        "superconducting_superfluid_topological",
        "adjacent-bulk-winding-pair-carrier",
        "positive-whole-winding-gap-relation",
        "bulk-orientation-and-boundary-recurrence-retained",
        "exact-protected-edge-class-count",
        "For two distinct adjacent whole bulk winding classes, the exact protected boundary recurrence count is their positive whole gap with orientation retained as a label rather than a signed number.",
    ),
    row(
        "SFT-MAT-BULK-WATER-RESPONSE-002",
        "Hydrogen-bonded water bulk-response ledger",
        "material_classes_bulk",
        "molecular-network-and-bulk-specimen-carrier",
        "intermolecular-organization-to-bulk-response-relation",
        "phase-density-boiling-and-heat-capacity-records-retained",
        "identity-condition-method-and-uncertainty-bounded",
        "A water bulk-response claim must retain the molecular hydrogen-bond network, specimen and phase identity, boiling, solid/liquid density and heat-capacity observations with their conditions, methods and uncertainty boundaries.",
    ),
)


__all__ = ("MATERIALS_SUCCESSOR_OBLIGATIONS",)
