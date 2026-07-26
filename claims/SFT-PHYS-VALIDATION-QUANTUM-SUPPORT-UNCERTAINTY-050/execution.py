from sft.physics.quantum_support_uncertainty_empirical_execution_v1 import build_execution as _build_execution


def build_execution(root):
    return _build_execution(root, root / "claims/SFT-PHYS-VALIDATION-QUANTUM-SUPPORT-UNCERTAINTY-050/execution.py")


__all__ = ("build_execution",)
