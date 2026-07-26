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

    def find_match(self, accused_a_id: int, accused_b_id: int) -> dict | None:
        """Score a specific pair of accused directly."""
        accused_df = self.data.get('accused', pd.DataFrame())
        if accused_df.empty:
            return None
        name_col = self._find_column(accused_df, ['AccusedName', 'accused_name'])
        age_col = self._find_column(accused_df, ['AgeYear', 'age_year'])
        gender_col = self._find_column(accused_df, ['GenderID', 'gender_id'])
        case_col = self._find_column(accused_df, ['CaseMasterID', 'case_master_id'])

        row_a = accused_df[accused_df['AccusedMasterID'] == accused_a_id]
        row_b = accused_df[accused_df['AccusedMasterID'] == accused_b_id]
        if row_a.empty or row_b.empty:
            return None
        a, b = row_a.iloc[0], row_b.iloc[0]

        if case_col and a.get(case_col) == b.get(case_col):
            return None

        a_name = self._normalize_name(a.get(name_col))
        b_name = self._normalize_name(b.get(name_col))
        a_tokens = a_name.split()
        b_tokens = b_name.split()
        if not a_tokens or not b_tokens:
            return None

        a_last = a_tokens[-1]
        b_last = b_tokens[-1]
        a_first = a_tokens[0]
        b_first = b_tokens[0]

        score = 0.0
        evidence = []
        surname_match = a_last and b_last and a_last == b_last
        firstname_match = a_first and b_first and a_first == b_first
        if surname_match and firstname_match:
            score += 0.65
            evidence.append('full name match')
        elif surname_match:
            score += 0.45
            evidence.append('surname match')
        elif a_first and b_first and a_first == b_first:
            score += 0.40
            evidence.append('first name match')
        elif len(set(a_tokens) & set(b_tokens)) >= 1:
            score += 0.35
            evidence.append('name token overlap')

        same_age = False
        if age_col:
            try:
                same_age = abs(int(a.get(age_col)) - int(b.get(age_col))) <= 10
            except (ValueError, TypeError):
                pass
        if same_age:
            score += 0.25
            evidence.append('compatible age window')

        same_gender = gender_col and a.get(gender_col) is not None and b.get(gender_col) is not None and a.get(gender_col) == b.get(gender_col)
        if same_gender:
            score += 0.10
            evidence.append('matching gender')

        if score < 0.40:
            return None

        return {
            'accused_a_id': accused_a_id,
            'accused_b_id': accused_b_id,
            'confidence': round(min(score, 1.0), 3),
            'evidence': evidence,
            'explanation': 'Likely same identity because the records show ' + ', '.join(evidence) + '.' if evidence else 'Possible duplicate identity based on available evidence.',
        }

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
                    left_tokens = left_name.split()
                    right_tokens = right_name.split()
                    token_overlap = len(set(left_tokens) & set(right_tokens))
                    left_last = left_tokens[-1] if left_tokens else ''
                    right_last = right_tokens[-1] if right_tokens else ''
                    left_first = left_tokens[0] if left_tokens else ''
                    right_first = right_tokens[0] if right_tokens else ''
                    same_age = False
                    if left['age'] is not None and right['age'] is not None:
                        try:
                            same_age = abs(int(left['age']) - int(right['age'])) <= 10
                        except (ValueError, TypeError):
                            pass
                    same_gender = left['gender'] is not None and right['gender'] is not None and left['gender'] == right['gender']
                    score = 0.0
                    evidence = []
                    surname_match = left_last and right_last and left_last == right_last
                    firstname_match = left_first and right_first and left_first == right_first
                    if surname_match and firstname_match:
                        score += 0.65
                        evidence.append('full name match')
                    elif surname_match:
                        score += 0.45
                        evidence.append('surname match')
                    elif left_first and right_first and left_first == right_first:
                        score += 0.40
                        evidence.append('first name match')
                    elif token_overlap >= 1:
                        score += 0.35
                        evidence.append('name token overlap')
                    if same_age:
                        score += 0.25
                        evidence.append('compatible age window')
                    if same_gender:
                        score += 0.10
                        evidence.append('matching gender')
                    if score >= 0.40:
                        results.append({
                            'accused_a_id': left['accused_id'],
                            'accused_b_id': right['accused_id'],
                            'confidence': round(min(score, 1.0), 3),
                            'evidence': evidence,
                            'explanation': 'Likely same identity because the records show ' + ', '.join(evidence) + '.' if evidence else 'Possible duplicate identity based on available evidence.',
                        })
        results.sort(key=lambda item: (item['confidence'], min(item['accused_a_id'], item['accused_b_id'])), reverse=True)
        return results[:limit]
