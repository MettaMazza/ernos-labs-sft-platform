from sft.physics.criticality_measured_value_successor_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-VALIDATION-CRITICALITY-MEASURED-VALUE-056/execution.py")


__all__ = ("build_execution",)
