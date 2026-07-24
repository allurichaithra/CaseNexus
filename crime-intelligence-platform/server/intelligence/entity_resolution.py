import re
from typing import Any, Dict, List

import pandas as pd


class EntityResolutionEngine:
    """Generate explainable accused-entity match candidates from the available FIR tables."""

    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.data = data

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]):
        lookup = {str(column).lower(): column for column in df.columns}
        for name in possible_names:
            if name.lower() in lookup:
                return lookup[name.lower()]
        return None

    def _normalize_name(self, name: Any) -> str:
        if pd.isna(name):
            return ''
        text = str(name).lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def find_candidate_matches(self, limit: int = 20) -> List[Dict[str, Any]]:
        accused_df = self.data.get('accused', pd.DataFrame())
        if accused_df.empty:
            return []
        case_col = self._find_column(accused_df, ['CaseMasterID', 'case_master_id'])
        name_col = self._find_column(accused_df, ['AccusedName', 'accused_name'])
        age_col = self._find_column(accused_df, ['AgeYear', 'age_year'])
        gender_col = self._find_column(accused_df, ['GenderID', 'gender_id'])

        results = []
        names = []
        for _, row in accused_df.iterrows():
            names.append({
                'accused_id': row.get('AccusedMasterID'),
                'case_id': row.get(case_col) if case_col else None,
                'name': row.get(name_col) if name_col else None,
                'age': row.get(age_col) if age_col else None,
                'gender': row.get(gender_col) if gender_col else None,
            })

        index = {}
        for item in names:
            normalized_name = self._normalize_name(item['name'])
            tokens = normalized_name.split()
            if not tokens:
                continue
            for key in [tokens[0], tokens[-1]]:
                if key:
                    index.setdefault(key, []).append(item)

        seen_pairs = set()
        for left in names:
            left_name = self._normalize_name(left['name'])
            left_tokens = left_name.split()
            candidate_keys = []
            if left_tokens:
                candidate_keys.append(left_tokens[0])
                if len(left_tokens) > 1:
                    candidate_keys.append(left_tokens[-1])
            for key in candidate_keys:
                for right in index.get(key, []):
                    if right['accused_id'] == left['accused_id']:
                        continue
                    if right['case_id'] == left['case_id']:
                        continue
                    pair = tuple(sorted((left['accused_id'], right['accused_id'])))
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)

                    right_name = self._normalize_name(right['name'])
                    token_overlap = len(set(left_name.split()) & set(right_name.split()))
                    same_age = False
                    if left['age'] is not None and right['age'] is not None:
                        same_age = abs(int(left['age']) - int(right['age'])) <= 3
                    same_gender = left['gender'] is not None and right['gender'] is not None and left['gender'] == right['gender']
                    score = 0.0
                    evidence = []
                    if left_name and right_name and token_overlap >= 1:
                        score += 0.55
                        evidence.append('name token overlap')
                    if same_age:
                        score += 0.25
                        evidence.append('compatible age window')
                    if same_gender:
                        score += 0.20
                        evidence.append('matching gender')
                    if score >= 0.55:
                        results.append({
                            'accused_a_id': left['accused_id'],
                            'accused_b_id': right['accused_id'],
                            'confidence': round(min(score, 1.0), 3),
                            'evidence': evidence,
                            'explanation': 'Likely same identity because the records show ' + ', '.join(evidence) + '.' if evidence else 'Possible duplicate identity based on available evidence.',
                        })
                        if len(results) >= limit:
                            return results
        results.sort(key=lambda item: item['confidence'], reverse=True)
        return results[:limit]
