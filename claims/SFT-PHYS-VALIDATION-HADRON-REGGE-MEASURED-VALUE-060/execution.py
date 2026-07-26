from sft.physics.hadron_regge_measured_value_successor_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-VALIDATION-HADRON-REGGE-MEASURED-VALUE-060/execution.py")


__all__ = ("build_execution",)
