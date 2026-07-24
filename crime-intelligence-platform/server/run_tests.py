import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))

from tests.test_intelligence import (
    test_dataset_loads_and_has_expected_tables,
    test_fingerprints_are_generated_for_all_cases,
    test_related_fir_scoring_bounds,
    test_entity_resolution_returns_candidates,
)


test_dataset_loads_and_has_expected_tables()
test_fingerprints_are_generated_for_all_cases()
test_related_fir_scoring_bounds()
test_entity_resolution_returns_candidates()
print('all intelligence tests passed')
