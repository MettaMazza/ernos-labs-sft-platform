"""Post-registry exact execution validator for HAND-001 through HAND-006."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_hand_001_006_target_registry_v1.json"
REGISTRY_HASH = "sha256:503e40b1ef0d25abf13fc2f420757fdbda9c05b90a95757cb5eafb2c8f2051e7"
VECTOR = "experiments/external_sources/computation/hand_001_006_observation_vector_v1.json"
VECTOR_HASH = "sha256:58e201c10f873c81d4447a07459a65a0fb070aed7aedc65294872246a0e20c5f"
FALSIFICATION = "Reject if the value-free registry, one-owner map, explicit interface, immutable prior receipt, formal-to-empirical custody chain, quantum or engineering boundary, open-extension rule, survivor, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def HandoffObservationValidator(root, spec):
    return CompleteFieldObservationValidator(
        root,
        spec,
        "HAND",
        REGISTRY,
        REGISTRY_HASH,
        VECTOR,
        VECTOR_HASH,
        "classical-computation-hand-observer-v1",
        FALSIFICATION,
    )
