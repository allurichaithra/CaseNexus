import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_loader import load_dataset
from intelligence.case_fingerprinting import CaseFingerprintingEngine
from intelligence.related_fir_engine import RelatedFIREngine
from intelligence.entity_resolution import EntityResolutionEngine
from generate_outputs import write_outputs
import main


def test_dataset_loads_and_has_expected_tables():
    data = load_dataset()
    assert 'cases' in data
    assert 'accused' in data
    assert 'act_sections' in data
    assert not data['cases'].empty


def test_fingerprints_are_generated_for_all_cases():
    data = load_dataset()
    engine = CaseFingerprintingEngine(data)
    fingerprints = engine.build_fingerprints()
    assert len(fingerprints) == len(data['cases'])
    for fp in fingerprints:
        assert 'normalized_text' in fp
        assert fp['normalized_text'] != 'nan'
        assert fp['normalized_text'] != 'None'


def test_related_fir_scoring_bounds():
    data = load_dataset()
    engine = RelatedFIREngine(data)
    results = engine.find_related_cases(1, limit=5)
    assert len(results) <= 5
    for result in results:
        assert 0.0 <= result['overall_score'] <= 1.0
        assert result['explanation']


def test_entity_resolution_returns_candidates():
    data = load_dataset()
    engine = EntityResolutionEngine(data)
    matches = engine.find_candidate_matches(limit=5)
    assert len(matches) <= 5
    for match in matches:
        assert match['confidence'] >= 0.0
        assert match['confidence'] <= 1.0


def test_output_generation_writes_artifacts(tmp_path):
    summary = write_outputs(output_dir=tmp_path / 'processed', evaluation_dir=tmp_path / 'evaluation')
    assert summary['case_fingerprints_generated'] == len(load_dataset()['cases'])
    assert (tmp_path / 'processed' / 'CaseFingerprint.csv').exists()
    assert (tmp_path / 'processed' / 'CaseLinkResult.csv').exists()
    assert (tmp_path / 'processed' / 'EntityMatchResult.csv').exists()
    assert (tmp_path / 'evaluation' / 'summary.json').exists()


def test_trends_endpoint_returns_json_safe_series():
    main.DATA = load_dataset()
    payload = main.get_trends()
    assert isinstance(payload, dict)
    assert 'daily' in payload and 'monthly' in payload
    assert isinstance(payload['daily'], dict)
    assert isinstance(payload['monthly'], dict)
    assert payload['daily']
    assert payload['monthly']
