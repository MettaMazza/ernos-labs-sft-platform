import importlib.util,json
from pathlib import Path
import pytest
from sft.chemistry.electrophilic_substitution_batch_v1 import ELECTROPHILIC_SUBSTITUTION_SPEC,PRIMARY_PATH
from sft.chemistry.electrophilic_substitution_law_v1 import DIMENSIONS,OPERATIONAL_WITNESSES
from sft.chemistry.electrophilic_substitution_validation_v1 import _source_rows,exact_analysis
ROOT=Path(__file__).resolve().parents[1]
def test_native_witnesses():assert len(DIMENSIONS)==8 and len(OPERATIONAL_WITNESSES)==7 and all(x[2] for x in OPERATIONAL_WITNESSES)
def test_complete_external_surface():
 rows=_source_rows(ROOT);a,c=exact_analysis(ROOT,rows,json.loads((ROOT/PRIMARY_PATH).read_text()));assert all(c.values()) and a["complete_pdf_page_count"]==452 and a["complete_table_s1_row_count"]==25 and a["displayed_zero_yield_or_zero_star_row_count"]==14
def test_omission_halts():
 with pytest.raises(ValueError):exact_analysis(ROOT,_source_rows(ROOT)[:-1],{})
def test_execution_256_one_survivor():
 p=ROOT/"claims/SFT-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008/execution.py";s=importlib.util.spec_from_file_location("o8",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);e=m.build_execution(ROOT);c=e.program.generate_candidates();assert len(c.candidates)==256 and sum(e.program.decide_candidate(x).survives for x in c.candidates)==1 and all(x.passed for x in e.program.run_controls()) and ELECTROPHILIC_SUBSTITUTION_SPEC.exact_result in {x.candidate_id for x in c.candidates}
