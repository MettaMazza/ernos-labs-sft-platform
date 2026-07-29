"""Post-registry exact execution validator for VALID-001 through VALID-012."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_valid_001_012_target_registry_v1.json"
REGISTRY_HASH = "sha256:99e02c49b16611b4c371f03785791601042ac45733231f721bb45dd6d3ba12db"
VECTOR = "experiments/external_sources/computation/valid_001_012_observation_vector_v1.json"
VECTOR_HASH = "sha256:b29ec3c17fddd064651a5fa80ba7d50617b120bc76f636f1a567d4c532eef142"
FALSIFICATION = "Reject if the value-free registry, frozen obligation, current receipt replay, candidate census, survivor, control, observation, independent certificate, root lineage or explicit theorem and handoff boundary is missing, stale, changed, duplicated, suppressed or opened out of order."


def ValidationObservationValidator(root, spec):
    return CompleteFieldObservationValidator(
        root,
        spec,
        "VALID",
        REGISTRY,
        REGISTRY_HASH,
        VECTOR,
        VECTOR_HASH,
        "classical-computation-valid-observer-v1",
        FALSIFICATION,
    )
