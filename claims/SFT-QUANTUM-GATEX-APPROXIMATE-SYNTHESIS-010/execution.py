from pathlib import Path
from sft.quantum_computation.gatex_001_022_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-GATEX-APPROXIMATE-SYNTHESIS-010", Path(__file__).resolve())
