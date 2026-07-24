import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from generated.foundation_prior_independent_validator import validate
print(json.dumps(validate(sys.argv[1],"SFT-FOUNDATION-FOLD-DYNAMICS-001"),sort_keys=True))
