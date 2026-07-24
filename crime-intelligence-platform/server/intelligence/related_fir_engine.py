import math
import re
from typing import Any, Dict, List

import pandas as pd


class RelatedFIREngine:
    """Generate explainable related-FIR candidates using deterministic scoring."""

    def __init__(self, data: Dict[str, pd.DataFrame], weights: Dict[str, float] | None = None):
        self.data = data
        self.weights = weights or {
            'narrative': 0.40,
            'crime': 0.25,
            'legal': 0.10,
            'geographic': 0.15,
            'temporal': 0.05,
            'entity': 0.05,
        }

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]):
        lookup = {str(column).lower(): column for column in df.columns}
        for name in possible_names:
            if name.lower() in lookup:
                return lookup[name.lower()]
        return None

    def _normalize_text(self, text: str) -> str:
        text = (text or '').lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _token_overlap(self, left: str, right: str) -> float:
        if not left or not right:
            return 0.0
        left_tokens = set(left.split())
        right_tokens = set(right.split())
        if not left_tokens or not right_tokens:
            return 0.0
        overlap = len(left_tokens & right_tokens)
        return overlap / max(1, min(len(left_tokens), len(right_tokens)))

    def _section_overlap(self, left_sections: List[str], right_sections: List[str]) -> float:
        if not left_sections or not right_sections:
            return 0.0
        left_set = {s.strip().lower() for s in left_sections if str(s).strip()}
        right_set = {s.strip().lower() for s in right_sections if str(s).strip()}
        if not left_set or not right_set:
            return 0.0
        overlap = len(left_set & right_set)
        return overlap / max(1, min(len(left_set), len(right_set)))

    def _temporal_score(self, left: Any, right: Any) -> float:
        if pd.isna(left) or pd.isna(right):
            return 0.0
        try:
            left_dt = pd.to_datetime(left, errors='coerce')
            right_dt = pd.to_datetime(right, errors='coerce')
            if pd.isna(left_dt) or pd.isna(right_dt):
                return 0.0
            delta_days = abs((left_dt - right_dt).days)
            if delta_days <= 3:
                return 1.0
            if delta_days <= 14:
                return 0.6
            if delta_days <= 30:
                return 0.3
            return 0.0
        except Exception:
            return 0.0

    def _geographic_score(self, left_lat: Any, left_lon: Any, right_lat: Any, right_lon: Any) -> float:
        if pd.isna(left_lat) or pd.isna(left_lon) or pd.isna(right_lat) or pd.isna(right_lon):
            return 0.0
        try:
            lat1, lon1 = float(left_lat), float(left_lon)
            lat2, lon2 = float(right_lat), float(right_lon)
            distance_km = self._distance_km(lat1, lon1, lat2, lon2)
            if distance_km <= 2:
                return 1.0
            if distance_km <= 8:
                return 0.7
            if distance_km <= 20:
                return 0.35
            return 0.0
        except Exception:
            return 0.0

    def _distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 6371.0 * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def _entity_score(self, left_case_id: Any, right_case_id: Any) -> float:
        accused_df = self.data.get('accused', pd.DataFrame())
        if accused_df.empty:
            return 0.0
        case_col = self._find_column(accused_df, ['CaseMasterID', 'case_master_id'])
        if not case_col:
            return 0.0
        left_names = {str(row.get('AccusedName') or '').strip().lower() for _, row in accused_df[accused_df[case_col] == left_case_id].iterrows() if str(row.get('AccusedName') or '').strip()}
        right_names = {str(row.get('AccusedName') or '').strip().lower() for _, row in accused_df[accused_df[case_col] == right_case_id].iterrows() if str(row.get('AccusedName') or '').strip()}
        overlap = len(left_names & right_names)
        return 1.0 if overlap > 0 else 0.0

    def find_related_cases(self, case_id: Any, limit: int = 10) -> List[Dict[str, Any]]:
        cases = self.data.get('cases', pd.DataFrame())
        if cases.empty:
            return []
        case_id_col = self._find_column(cases, ['CaseMasterID', 'case_master_id'])
        if not case_id_col:
            return []
        source_case = cases[cases[case_id_col] == case_id]
        if source_case.empty:
            return []
        source = source_case.iloc[0]

        act_section_df = self.data.get('act_sections', pd.DataFrame())
        act_section_case_col = self._find_column(act_section_df, ['CaseMasterID', 'case_master_id'])
        source_sections = []
        if not act_section_df.empty and act_section_case_col:
            source_sections = [
                f"{row.get('ActID')}:{row.get('SectionID')}"
                for _, row in act_section_df[act_section_df[act_section_case_col] == case_id].iterrows()
                if not pd.isna(row.get('ActID')) or not pd.isna(row.get('SectionID'))
            ]

        source_text = self._normalize_text(str(source.get('BriefFacts') or ''))
        source_major = source.get('CrimeMajorHeadID')
        source_minor = source.get('CrimeMinorHeadID')

        candidate_ids = set()
        major_col = self._find_column(cases, ['CrimeMajorHeadID', 'crime_major_head_id'])
        minor_col = self._find_column(cases, ['CrimeMinorHeadID', 'crime_minor_head_id'])
        if major_col and source_major is not None:
            candidate_ids.update(
                int(item)
                for item in cases[cases[major_col] == source_major][case_id_col].dropna().astype(int).tolist()
                if int(item) != int(case_id)
            )
        if minor_col and source_minor is not None:
            candidate_ids.update(
                int(item)
                for item in cases[cases[minor_col] == source_minor][case_id_col].dropna().astype(int).tolist()
                if int(item) != int(case_id)
            )

        source_tokens = {token for token in self._normalize_text(str(source.get('BriefFacts') or '')).split() if len(token) >= 3}
        if source_tokens:
            for _, candidate in cases.iterrows():
                candidate_id = candidate.get(case_id_col)
                if pd.isna(candidate_id) or int(candidate_id) == int(case_id):
                    continue
                candidate_tokens = {token for token in self._normalize_text(str(candidate.get('BriefFacts') or '')).split() if len(token) >= 3}
                if source_tokens & candidate_tokens:
                    candidate_ids.add(int(candidate_id))

        if not candidate_ids:
            candidate_ids.update(int(item) for item in cases[case_id_col].dropna().astype(int).tolist() if int(item) != int(case_id))

        candidate_ids = list(candidate_ids)[: max(limit * 4, 120)]

        results = []
        for candidate_id in candidate_ids:
            candidate = cases[cases[case_id_col] == candidate_id]
            if candidate.empty:
                continue
            candidate = candidate.iloc[0]
            candidate_text = self._normalize_text(str(candidate.get('BriefFacts') or ''))
            narrative_score = self._token_overlap(source_text, candidate_text)
            crime_score = 1.0 if source_major == candidate.get('CrimeMajorHeadID') else 0.0
            legal_score = self._section_overlap(source_sections, self._candidate_sections(candidate_id, act_section_df, act_section_case_col))
            geographic_score = self._geographic_score(source.get('latitude'), source.get('longitude'), candidate.get('latitude'), candidate.get('longitude'))
            temporal_score = self._temporal_score(source.get('IncidentFromDate'), candidate.get('IncidentFromDate'))
            entity_score = self._entity_score(case_id, candidate_id)

            overall = (
                self.weights['narrative'] * narrative_score
                + self.weights['crime'] * crime_score
                + self.weights['legal'] * legal_score
                + self.weights['geographic'] * geographic_score
                + self.weights['temporal'] * temporal_score
                + self.weights['entity'] * entity_score
            )

            if overall <= 0.0:
                continue

            explanation = self._build_explanation(
                narrative_score,
                crime_score,
                legal_score,
                geographic_score,
                temporal_score,
                entity_score,
                source,
                candidate,
                source_sections,
            )
            results.append({
                'source_case_id': int(case_id) if case_id is not None else None,
                'related_case_id': int(candidate_id) if candidate_id is not None else None,
                'overall_score': round(overall, 3),
                'narrative_score': round(narrative_score, 3),
                'crime_pattern_score': round(crime_score, 3),
                'legal_section_score': round(legal_score, 3),
                'geographic_score': round(geographic_score, 3),
                'temporal_score': round(temporal_score, 3),
                'entity_score': round(entity_score, 3),
                'explanation': explanation,
            })

        results.sort(key=lambda item: item['overall_score'], reverse=True)
        return results[:limit]

    def _candidate_sections(self, case_id: Any, act_section_df: pd.DataFrame, case_col: str | None) -> List[str]:
        if act_section_df.empty or not case_col:
            return []
        related = act_section_df[act_section_df[case_col] == case_id]
        return [
            f"{row.get('ActID')}:{row.get('SectionID')}"
            for _, row in related.iterrows()
            if not pd.isna(row.get('ActID')) or not pd.isna(row.get('SectionID'))
        ]

    def _build_explanation(self, narrative_score: float, crime_score: float, legal_score: float, geographic_score: float, temporal_score: float, entity_score: float, source: pd.Series, candidate: pd.Series, source_sections: List[str]) -> str:
        reasons = []
        if narrative_score > 0.0:
            reasons.append('shared narrative terms')
        if crime_score > 0.0:
            reasons.append('matching crime major head')
        if legal_score > 0.0:
            reasons.append('overlapping legal sections')
        if geographic_score > 0.0:
            reasons.append('nearby geography')
        if temporal_score > 0.0:
            reasons.append('close incident timing')
        if entity_score > 0.0:
            reasons.append('shared accused identity')
        if not reasons:
            return 'The case shares limited measurable evidence with this candidate.'
        return 'Likely related because it shows ' + ', '.join(reasons) + '.'
