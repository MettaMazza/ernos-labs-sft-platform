"""Post-seal physical comparison for the exact Fold erasure ledger."""

from __future__ import annotations

from sft.physics.generated_empirical_law import (
    EmpiricalPhysicsSpec,
    ExternalTargetRow,
    empirical_dimensions,
)
from sft.physics.landauer_demon_ledger_terminal_law_v1 import (
    demon_cycle_ledger,
    erased_distinction_count,
    minimum_throw,
)


CLAIM_ID = "SFT-PHYS-THERMO-LANDAUER-EMPIRICAL-019"
EXPERIMENT_ID = "SFT-EXP-PHYS-THERMO-LANDAUER-EMPIRICAL-019"
SOURCE_PATH = "experiments/external_sources/physics/snapshots/landauer-erasure-source-record.json"
SOURCE_HASH = "sha256:76a746eb8760816598724a2db17fb7cd1f3a07325e69193525d313fecea4d27f"
SOURCE_IDS = ("BERUT-NATURE-2012", "PIECHOCINSKA-PRA-2000")
OBSERVATION_LABEL = (
    "two-state-bit-reset-to-one__finite-positive-environmental-heat__"
    "long-cycle-mean-saturates-Landauer-bound__thermal-reservoir-and-"
    "ensemble-scope-retained__no-half-One-to-joule-identity"
)


SPEC = EmpiricalPhysicsSpec(
    claim_id=CLAIM_ID,
    title="Post-seal Landauer erasure and Maxwell-ledger comparison",
    statement=(
        "The independently admitted Fold reset closes one predecessor distinction "
        "and requires one environment reverse label.  Before any external target "
        "is opened, this predicts that a physical two-state memory reset to one "
        "state has finite positive environmental dissipation and that a reliable "
        "slow erasure approaches a nonvanishing thermal bound.  Post-seal primary "
        "theory and experiment match that structure: the conventional symmetric "
        "thermal-reservoir bound is average heat at least k_B T ln 2, and measured "
        "long-cycle mean heat saturates it.  The external logarithmic dimensional "
        "coefficient remains a measurement/theory inscription and is not equated "
        "numerically with the native half-One Fold separation."
    ),
    dependencies=(
        "SFT-PHYS-THERMO-LANDAUER-DEMON-TERMINAL-018",
        "SFT-FOUNDATION-MEASURED-VALUE-BOUNDARY-001",
        "SFT-PHYS-MEAS-TARGET-CUSTODY-001",
        "SFT-PHYS-MEAS-UNCERTAINTY-001",
        "SFT-PHYS-MEAS-DIMENSION-COMPOSITION-001",
    ),
    generation_rule=(
        "Generate the complete eight-axis product of physical carrier, erasure "
        "relation, provenance, prediction isolation, measurement separation, row "
        "retention, successor closure and extension forms."
    ),
    grammar_boundary=(
        "The admitted exact two-preimage Fold reset and every registered primary "
        "source row concerning a symmetric one-bit memory, thermal-reservoir "
        "erasure, environmental heat, ensemble averaging and long-cycle approach."
    ),
    dimensions=empirical_dimensions(
        "one-distinction-reset-with-environment-record",
        "The admitted Fold fibre closes one distinction and requires one external reverse record before any thermal source is opened.",
    ),
    exact_result=(
        "The exact Fold one-distinction reset predicts a nonfree environmental "
        "transfer for physical erasure.  Primary theory identifies the symmetric "
        "thermal-reservoir ensemble bound as k_B T ln 2 and primary experiment "
        "finds long-cycle mean heat saturating it; all distribution, reservoir, "
        "average and long-cycle scope rows are retained, while native half-One is "
        "not falsely identified with a dimensional energy number."
    ),
    induction_base=(
        "One physical two-state reset corresponds to one closed Fold distinction "
        "and one required environment record."
    ),
    induction_step=(
        "Appending one independently prepared reset appends one distinction and "
        "one environment-transfer obligation; ensemble averaging changes neither "
        "the record count nor the registered thermal scope."
    ),
    exclusions=(
        "no source text, k_B T ln 2 coefficient or experimental result in the formal predecessor law",
        "no numerical identification of native half-One with joules or with ln 2",
        "no omission of ensemble-average, reservoir, distribution or long-cycle limitations",
        "no numerical-zero, negative, irrational, imaginary or floating SFT proof value",
        "no target access before the prediction seal and no fitted correction",
    ),
    operational_witnesses=(
        ("one-distinction", "The admitted reset closes exactly one predecessor label.", erased_distinction_count() == 1),
        ("native-throw", "The native two-preimage separation is exact half-One.", str(minimum_throw()) == "1/2"),
        ("closed-ledger", "The demon cycle exports the distinction it gains.", demon_cycle_ledger()["complete"] is True),
    ),
    experiment_id=EXPERIMENT_ID,
    expected_observation_label=OBSERVATION_LABEL,
    target_rows=(
        ExternalTargetRow("LANDAUER-TWO-TO-ONE-RESET", "PIECHOCINSKA-PRA-2000", "page 1 reset from two possible bit states to one", OBSERVATION_LABEL),
        ExternalTargetRow("LANDAUER-THERMAL-BOUND", "PIECHOCINSKA-PRA-2000", "abstract and equations 19/52 average heat bound with reservoir scope", OBSERVATION_LABEL),
        ExternalTargetRow("LANDAUER-EXPERIMENTAL-SATURATION", "BERUT-NATURE-2012", "abstract and Figure 3 long-cycle mean-heat saturation", OBSERVATION_LABEL),
        ExternalTargetRow("LANDAUER-SCOPE-CONTROL", "BERUT-NATURE-2012", "one-bit bistable memory and long-cycle limiting mean", OBSERVATION_LABEL),
    ),
    source_snapshot_path=SOURCE_PATH,
    source_snapshot_hash=SOURCE_HASH,
    falsification_condition=(
        "Reject if the source snapshot changes; if a registered reset, heat, bound, "
        "experiment or scope row is omitted; if physical reliable erasure has no "
        "positive environment transfer; if long-cycle mean heat does not approach "
        "the registered bound; if the thermal coefficient enters the Fold proof; "
        "or if native half-One is misreported as a dimensional numerical equality."
    ),
)


SPEC.validate()


__all__ = (
    "CLAIM_ID",
    "EXPERIMENT_ID",
    "OBSERVATION_LABEL",
    "SOURCE_HASH",
    "SOURCE_IDS",
    "SOURCE_PATH",
    "SPEC",
)
