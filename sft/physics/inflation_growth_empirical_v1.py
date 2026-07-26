"""Post-seal empirical test of the inflation-growth terminal law."""

from __future__ import annotations

from dataclasses import replace

from sft.engine import ProvenanceClass
from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    GeneratedEmpiricalPhysicsProgram,
    empirical_dimensions,
)
from sft.physics.inflation_growth_terminal_law_v1 import theorem_certificate


CLAIM_ID = "SFT-PHYS-VALIDATION-INFLATION-GROWTH-040"
EXPERIMENT_ID = "SFT-EXP-PHYS-VALIDATION-INFLATION-GROWTH-040"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/inflation-growth-postseal-source-record.json"
SOURCE_HASH = "sha256:b04ac2ae7426e91117f0f7594019354fd4921629b22e42dbc38d3acce93ff45b"
SOURCE_FILES = (
    ("experiments/external_sources/physics/snapshots/arxiv-1807.06211-planck-inflation.pdf", "sha256:fa728dc0198ccfddd7132c0e0a29cca586a1431a045568a33d7a197a0427427d"),
    ("experiments/external_sources/physics/snapshots/arxiv-2112.07961-bicep-planck-tensor.pdf", "sha256:5a1add11c98a8e5c4d70fd438eacd5242aa10631ffea0c72358f49e59eda07f2"),
)
SOURCE_IDS = ("PLANCK-2018-INFLATION", "BICEP-PLANCK-2022-TENSOR")
OBSERVATION_LABEL = (
    "sealed-inflation-growth-law__complete-scalar-index-and-tensor-bound-record__"
    "exact-31-of-32-partition-tested-without-fit"
)


class ObservationalEmpiricalPhysicsProgram(GeneratedEmpiricalPhysicsProgram):
    @property
    def registration(self):
        return replace(super().registration, provenance=(ProvenanceClass.OBSERVATIONAL_DERIVATION,))


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal scalar-support and tensor-support measurement test",
    statement=(
        "After formal Claim 039 is admitted, Planck's complete scalar spectral-index estimate and the improved "
        "BICEP/Keck-Planck tensor-to-scalar upper bound are opened. Exact scalar support 31/32 lies inside the "
        "registered Planck one-standard interval. Exact least tensor support 1/32 lies strictly below the registered "
        "95 percent upper bound 4/125. Neither row selects or modifies the exact formal partition."
    ),
    dependencies=(
        "SFT-PHYS-INFLATION-GROWTH-TERMINAL-039",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of sealed inflation relation, complete external target, source "
        "provenance, capability-closed isolation, proof/measurement separation, complete rows, successor closure and extension."
    ),
    grammar_boundary=(
        "The admitted scalar support 31/32 and tensor support 1/32; both endpoints of the Planck one-standard scalar "
        "interval; the strict BICEP/Planck tensor upper bound; every bound source and custody row; and explicit "
        "separation of exact Fold doubling depth from conventional model-dependent e-fold language."
    ),
    dimensions=empirical_dimensions(
        "sealed-inflation-growth-law-versus-complete-scalar-index-and-tensor-bound-record",
        "The formal receipt was fixed before the primary snapshots and target record were opened.",
    ),
    exact_result=(
        "Planck ns=0.9649+/-0.0042 gives exact interval [9607/10000,9691/10000]; the independently forced 31/32 "
        "equals 0.96875 and lies inside that interval. BICEP/Keck plus Planck reports r<0.032=4/125 at 95 percent; "
        "the independently forced 1/32=0.03125 lies strictly below the bound by 3/4000=0.00075. The complete exact "
        "31/32+1/32 partition therefore passes both external rows without fitting. Five Fold doublings is not "
        "relabelled as a conventional natural-log e-fold count, for which this claim asserts no measured equality."
    ),
    induction_base=(
        "The formal receipt fixes volume 27, cover support 32 and the complete 31/32 plus 1/32 partition before target release."
    ),
    induction_step=(
        "Each additional uncertainty endpoint or stricter positive upper bound is retained once and cannot rewrite the sealed survivor."
    ),
    exclusions=(
        "no external scalar index or tensor limit readable by the formal generator or formal validator",
        "no fitted spectral index, tensor amplitude, inflaton potential, transfer function or exit scale",
        "no historical-blindness claim because V1/V2 named these observables",
        "no claim that five exact Fold doublings equal a conventional logarithmic e-fold count",
        "no omission or rounding of the narrow tensor-bound margin",
        "no numerical-zero, negative, irrational, imaginary or floating Fold proof magnitude",
    ),
    operational_witnesses=(
        ("cover", "The formal cover is depth five and support thirty-two.", theorem_certificate()["depth"] == 5 and theorem_certificate()["support"] == 32),
        ("partition", "The formal scalar/tensor partition closes exactly to One.", theorem_certificate()["scalar"] + theorem_certificate()["tensor"] == 1),
        ("growth", "The formal two-step growth and component transfer are exact.", theorem_certificate()["strict_growth"] and theorem_certificate()["transfer"]),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("PLANCK-SCALAR-INDEX", SOURCE_IDS[0], "Scalar index central value and complete standard interval", OBSERVATION_LABEL),
        ExternalTargetRow("BICEP-PLANCK-TENSOR-BOUND", SOURCE_IDS[1], "Strict 95 percent tensor-to-scalar upper bound", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if any source identity or registered row changes; if 31/32 leaves the complete scalar interval; if "
        "1/32 is not strictly below the tensor bound; if the narrow margin is omitted; if conventional e-fold language "
        "is asserted as exact equality; or if a target changes the formal survivor."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID", "EXPERIMENT_ID", "OBSERVATION_LABEL", "ObservationalEmpiricalPhysicsProgram", "SOURCE_FILES",
    "SOURCE_HASH", "SOURCE_IDS", "SOURCE_PATH", "SPEC",
)
