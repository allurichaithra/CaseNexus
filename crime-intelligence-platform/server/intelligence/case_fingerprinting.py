import math
import re
from typing import Any, Dict, List

import pandas as pd


class CaseFingerprintingEngine:
    """Build lightweight, explainable fingerprints for FIR/case records."""

    def __init__(self, data: Dict[str, pd.DataFrame]):
        self.data = data

    def _find_column(self, df: pd.DataFrame, possible_names: List[str]):
        lookup = {str(column).lower(): column for column in df.columns}
        for name in possible_names:
            if name.lower() in lookup:
                return lookup[name.lower()]
        return None

    def get_case_fingerprint(self, case_row: pd.Series) -> Dict[str, Any]:
        case_id = case_row.get('CaseMasterID')
        if pd.isna(case_id):
            case_id = None

        crime_major_head = case_row.get('CrimeMajorHeadID')
        crime_minor_head = case_row.get('CrimeMinorHeadID')
        brief_facts = str(case_row.get('BriefFacts') or '').strip()
        act_sections = []

        act_section_df = self.data.get('act_sections', pd.DataFrame())
        case_id_col = self._find_column(act_section_df, ['CaseMasterID', 'case_master_id'])
        if not act_section_df.empty and case_id_col:
            related = act_section_df[act_section_df[case_id_col] == case_id]
            if not related.empty:
                act_sections = [
                    f"{row.get('ActID')}:{row.get('SectionID')}"
                    for _, row in related.iterrows()
                    if pd.notna(row.get('ActID')) and pd.notna(row.get('SectionID'))
                ]

        crime_head_df = self.data.get('crime_heads', pd.DataFrame())
        crime_sub_head_df = self.data.get('crime_sub_heads', pd.DataFrame())
        crime_head_col = self._find_column(crime_head_df, ['CrimeHeadID', 'crime_head_id'])
        crime_sub_col = self._find_column(crime_sub_head_df, ['CrimeSubHeadID', 'crime_sub_head_id'])

        crime_head_name = None
        crime_sub_name = None
        if crime_head_df is not None and not crime_head_df.empty and crime_head_col and crime_major_head is not None:
            match = crime_head_df[crime_head_df[crime_head_col] == crime_major_head]
            if not match.empty:
                crime_head_name = match.iloc[0].get('CrimeGroupName')
        if crime_sub_head_df is not None and not crime_sub_head_df.empty and crime_sub_col and crime_minor_head is not None:
            match = crime_sub_head_df[crime_sub_head_df[crime_sub_col] == crime_minor_head]
            if not match.empty:
                crime_sub_name = match.iloc[0].get('CrimeHeadName')

        accused_df = self.data.get('accused', pd.DataFrame())
        accused_case_col = self._find_column(accused_df, ['CaseMasterID', 'case_master_id'])
        accused_names = []
        if not accused_df.empty and accused_case_col:
            accused_names = [
                str(row.get('AccusedName') or '').strip()
                for _, row in accused_df[accused_df[accused_case_col] == case_id].iterrows()
                if str(row.get('AccusedName') or '').strip()
            ]

        normalized_text = ' '.join([brief_facts] + accused_names + act_sections).lower()
        normalized_text = re.sub(r'[^a-z0-9\s]', ' ', normalized_text)
        normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()

        return {
            'case_master_id': int(case_id) if case_id is not None else None,
            'crime_major_head_id': crime_major_head,
            'crime_minor_head_id': crime_minor_head,
            'crime_head_name': crime_head_name,
            'crime_sub_head_name': crime_sub_name,
            'act_sections': act_sections,
            'accused_names': accused_names,
            'brief_facts': brief_facts,
            'normalized_text': normalized_text,
            'temporal_bucket': self._bucket_date(case_row.get('IncidentFromDate')),
            'geo_bucket': self._bucket_geo(case_row.get('latitude'), case_row.get('longitude')),
        }

    def build_fingerprints(self) -> List[Dict[str, Any]]:
        cases = self.data.get('cases', pd.DataFrame())
        if cases.empty:
            return []
        return [self.get_case_fingerprint(row) for _, row in cases.iterrows()]

    def _bucket_date(self, value: Any) -> str | None:
        if pd.isna(value):
            return None
        try:
            if isinstance(value, str):
                value = value.split(' ')[0]
                return value[:7]
            return str(value)[:7]
        except Exception:
            return None

    def _bucket_geo(self, latitude: Any, longitude: Any) -> str | None:
        if pd.isna(latitude) or pd.isna(longitude):
            return None
        try:
            lat = float(latitude)
            lon = float(longitude)
            if not math.isfinite(lat) or not math.isfinite(lon):
                return None
            return f"{round(lat, 1)}:{round(lon, 1)}"
        except Exception:
            return None
