from pathlib import Path
from types import SimpleNamespace
import unittest
from sft.chemistry.state_energy_order_law_v1 import ExactFiniteStateOrder,OrderedMolecularState,build_exact_state_order,precedes
from sft.chemistry.state_energy_order_validation_v1 import StateEnergyOrderValidator,prediction_program_document
from sft.claim_evidence import CapabilityClosedFoldInterpreter,FoldTable,fold_program_from_mapping
from sft.claim_evidence.fold_language import EMPTY_ONE
from sft.engine.exact import HeldLabel,InadmissibleExactValue,PositiveCount
ROOT=Path(__file__).resolve().parents[1]
class StateOrderTests(unittest.TestCase):
 def test_unique_ground_and_successors(self):
  o=build_exact_state_order("m",("X","A","B"));self.assertEqual(o.ground_state.order_position,EMPTY_ONE);self.assertEqual(o.states[1].order_position,PositiveCount(1));self.assertTrue(precedes(o.states[1],o.states[2]))
 def test_duplicate_ground_halts(self):
  c=HeldLabel("molecular-carrier","m")
  with self.assertRaises(InadmissibleExactValue): ExactFiniteStateOrder(c,(OrderedMolecularState(c,HeldLabel("molecular-electronic-state","a"),EMPTY_ONE,HeldLabel("molecular-support","a")),OrderedMolecularState(c,HeldLabel("molecular-electronic-state","b"),EMPTY_ONE,HeldLabel("molecular-support","b"))))
 def test_missing_successor_halts(self):
  c=HeldLabel("molecular-carrier","m")
  with self.assertRaises(InadmissibleExactValue): ExactFiniteStateOrder(c,(OrderedMolecularState(c,HeldLabel("molecular-electronic-state","a"),EMPTY_ONE,HeldLabel("molecular-support","a")),OrderedMolecularState(c,HeldLabel("molecular-electronic-state","b"),PositiveCount(2),HeldLabel("molecular-support","b"))))
 def test_cross_carrier_comparison_halts(self):
  a=build_exact_state_order("a",("X","A"));b=build_exact_state_order("b",("X","A"))
  with self.assertRaises(InadmissibleExactValue): precedes(a.states[0],b.states[1])
 def test_capability_closed_prediction(self):
  e=CapabilityClosedFoldInterpreter().execute(fold_program_from_mapping(prediction_program_document(ROOT)),{"registered-premise":HeldLabel("sealed-derivation","unit")});self.assertIsInstance(e.output,FoldTable);self.assertEqual(len(e.output.entries),22)
 def test_complete_NIST_energy_vector(self):
  r=StateEnergyOrderValidator(ROOT).validate(SimpleNamespace(seal_hash="sha256:"+"e"*64));self.assertTrue(r.passed);self.assertEqual(len(r.measurements),313)
if __name__=="__main__":unittest.main()
