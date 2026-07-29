"""Post-registry exact execution validator for SCIX-001 through SCIX-025."""
from sft.computation.complete_field_observation_v1 import CompleteFieldObservationValidator

REGISTRY = "census/computation_scix_001_025_target_registry_v1.json"
REGISTRY_HASH = "sha256:c55dfd4503f3523f44ceeca8d276e7de1dfe5708039ca9b95ce0589a209f395f"
VECTOR = "experiments/external_sources/computation/scix_001_025_observation_vector_v1.json"
VECTOR_HASH = "sha256:d48c0880ffc590b92699f6f38375da4efe2abddfcc0bf12aa8990e719175d1af"
FALSIFICATION = "Reject if the value-free registry, exact representation, enclosure, mesh, error or residual ledger, model, data or validation boundary, source identity, survivor, seal, custody record, control or independent reconstruction is missing, changed, duplicated or opened out of order."


def ScientificObservationValidator(root, spec):
    return CompleteFieldObservationValidator(
        root,
        spec,
        "SCIX",
        REGISTRY,
        REGISTRY_HASH,
        VECTOR,
        VECTOR_HASH,
        "classical-computation-scix-observer-v1",
        FALSIFICATION,
    )
