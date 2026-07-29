from pathlib import Path
from sft.quantum_computation.gatex_001_022_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-GATEX-COMPILATION-018", Path(__file__).resolve())
