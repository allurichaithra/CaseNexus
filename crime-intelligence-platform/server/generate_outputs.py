import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from data_loader import load_dataset
from intelligence.case_fingerprinting import CaseFingerprintingEngine
from intelligence.related_fir_engine import RelatedFIREngine
from intelligence.entity_resolution import EntityResolutionEngine


def build_case_fingerprint_output(data: dict) -> pd.DataFrame:
    engine = CaseFingerprintingEngine(data)
    fingerprints = engine.build_fingerprints()
    out = pd.DataFrame(fingerprints)
    if 'case_master_id' in out.columns:
        out = out.sort_values('case_master_id').reset_index(drop=True)
    return out


def build_case_link_output(data: dict, limit_per_case: int = 50, source_case_ids: list[int] | None = None) -> pd.DataFrame:
    engine = RelatedFIREngine(data)
    cases = data.get('cases', pd.DataFrame())
    case_id_col = None
    for name in ['CaseMasterID', 'case_master_id']:
        if name in cases.columns:
            case_id_col = name
            break
    if case_id_col is None:
        return pd.DataFrame(columns=['LinkID', 'QueryCaseMasterID', 'CandidateCaseMasterID', 'OverallConfidence', 'NarrativeScore', 'SpatialScore', 'TemporalScore', 'SectionScore', 'OfficerDecision', 'ReviewedByOfficerID', 'Timestamp'])

    if source_case_ids is None:
        ground_truth = data.get('ground_truth_case_links', pd.DataFrame())
        if not ground_truth.empty and 'SourceCaseMasterID' in ground_truth.columns:
            source_case_ids = [int(item) for item in ground_truth['SourceCaseMasterID'].dropna().astype(int).unique().tolist()]
        else:
            source_case_ids = [int(item) for item in cases[case_id_col].dropna().astype(int).tolist()[:20]]

    rows = []
    link_id = 1
    for case_id in source_case_ids:
        results = engine.find_related_cases(int(case_id), limit=limit_per_case)
        for result in results:
            if result['overall_score'] < 0.05:
                continue
            rows.append({
                'LinkID': link_id,
                'QueryCaseMasterID': int(case_id),
                'CandidateCaseMasterID': int(result['related_case_id']),
                'OverallConfidence': float(result['overall_score']),
                'NarrativeScore': float(result['narrative_score']),
                'SpatialScore': float(result['geographic_score']),
                'TemporalScore': float(result['temporal_score']),
                'SectionScore': float(result['legal_section_score']),
                'OfficerDecision': 'Pending',
                'ReviewedByOfficerID': None,
                'Timestamp': None,
            })
            link_id += 1
    return pd.DataFrame(rows)


def build_entity_match_output(data: dict, limit: int = 200) -> pd.DataFrame:
    engine = EntityResolutionEngine(data)
    matches = engine.find_candidate_matches(limit=limit)
    rows = []
    for index, match in enumerate(matches, start=1):
        rows.append({
            'MatchID': index,
            'AccusedMasterID_A': match.get('accused_a_id'),
            'AccusedMasterID_B': match.get('accused_b_id'),
            'MatchConfidence': match.get('confidence'),
            'PhoneticScore': None,
            'AgeDelta': None,
            'SharedCaseContext': None,
            'OfficerDecision': 'Possible',
            'ReviewedByOfficerID': None,
            'Timestamp': None,
        })
    return pd.DataFrame(rows)


def evaluate_case_links(data: dict):
    gt = data.get('ground_truth_case_links', pd.DataFrame())
    if gt.empty:
        return []
    engine = RelatedFIREngine(data)
    results = []
    source_col = 'SourceCaseMasterID'
    target_col = 'TargetCaseMasterID'
    for _, row in gt.iterrows():
        source_id = int(row[source_col])
        target_id = int(row[target_col])
        ranked_results = engine.find_related_cases(source_id, limit=500)
        ranked_ids = [int(item['related_case_id']) for item in ranked_results]
        found = target_id in ranked_ids
        rank = ranked_ids.index(target_id) + 1 if found else None
        match = next((item for item in ranked_results if int(item['related_case_id']) == target_id), None)
        results.append({
            'SourceCaseID': source_id,
            'ExpectedLinkedCaseID': target_id,
            'Found': bool(found),
            'Rank': rank,
            'OverallScore': float(match['overall_score']) if match else None,
            'NarrativeScore': float(match['narrative_score']) if match else None,
            'CrimePatternScore': float(match['crime_pattern_score']) if match else None,
            'LegalScore': float(match['legal_section_score']) if match else None,
            'GeographicScore': float(match['geographic_score']) if match else None,
            'TemporalScore': float(match['temporal_score']) if match else None,
            'EntityScore': float(match['entity_score']) if match else None,
            'Explanation': match['explanation'] if match else None,
        })
    return results


def evaluate_entity_matches(data: dict):
    gt = data.get('ground_truth_entity_matches', pd.DataFrame())
    if gt.empty:
        return []
    engine = EntityResolutionEngine(data)
    results = []
    for _, row in gt.iterrows():
        a = int(row['AccusedMasterID_A'])
        b = int(row['AccusedMasterID_B'])
        match = engine.find_match(a, b)
        results.append({
            'ExpectedAccusedA': a,
            'ExpectedAccusedB': b,
            'Found': bool(match),
            'Confidence': float(match['confidence']) if match else None,
            'Evidence': match.get('evidence') if match else None,
        })
    return results


def write_outputs(output_dir: Path | None = None, evaluation_dir: Path | None = None):
    data = load_dataset()
    out_dir = output_dir or (ROOT / 'data' / 'processed')
    out_dir.mkdir(parents=True, exist_ok=True)

    fingerprints = build_case_fingerprint_output(data)
    fingerprints.to_csv(out_dir / 'CaseFingerprint.csv', index=False)

    case_links = build_case_link_output(data)
    case_links.to_csv(out_dir / 'CaseLinkResult.csv', index=False)

    entity_matches = build_entity_match_output(data)
    entity_matches.to_csv(out_dir / 'EntityMatchResult.csv', index=False)

    evaluation_dir = evaluation_dir or (ROOT / 'evaluation')
    evaluation_dir.mkdir(parents=True, exist_ok=True)

    case_eval = evaluate_case_links(data)
    with open(evaluation_dir / 'case_link_evaluation.json', 'w', encoding='utf-8') as handle:
        json.dump(case_eval, handle, indent=2)

    entity_eval = evaluate_entity_matches(data)
    with open(evaluation_dir / 'entity_match_evaluation.json', 'w', encoding='utf-8') as handle:
        json.dump(entity_eval, handle, indent=2)

    summary = {
        'case_fingerprints_generated': int(len(fingerprints)),
        'case_links_generated': int(len(case_links)),
        'entity_matches_generated': int(len(entity_matches)),
        'ground_truth_case_links': int(len(data.get('ground_truth_case_links', pd.DataFrame()))),
        'ground_truth_entity_matches': int(len(data.get('ground_truth_entity_matches', pd.DataFrame()))),
    }
    with open(evaluation_dir / 'summary.json', 'w', encoding='utf-8') as handle:
        json.dump(summary, handle, indent=2)

    print(json.dumps(summary, indent=2))
    return summary


if __name__ == '__main__':
    write_outputs()
