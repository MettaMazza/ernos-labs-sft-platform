"""Post-registry exact execution validator for DISTX-001 through DISTX-026."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_distx_001_026_target_registry_v1.json"
REGISTRY_HASH = "sha256:181c4add52a53cd9946842e0a1e98c6e4209e85857ea604a7cb37c3237fc7e03"
VECTOR = "experiments/external_sources/computation/distx_001_026_observation_vector_v1.json"
VECTOR_HASH = "sha256:b173acff8b751b2e7272a39374fde8532e2bcd15846d58d740d64e178cad0b12"
FALSIFICATION = "Reject if the value-free registry, event identity, local order, message or synchronization ledger, fault, timing or topology boundary, exact trace, source identity, survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def DistributedObservationValidator(root, spec):
    return CompleteFieldObservationValidator(root, spec, "DISTX", REGISTRY, REGISTRY_HASH, VECTOR, VECTOR_HASH, "classical-computation-distx-observer-v1", FALSIFICATION)
