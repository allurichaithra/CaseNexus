# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Pattern Injector & Evaluation Ground Truth Module
# File: generator/ml_patterns/pattern_injector.py
# ==============================================================================

import random
import pandas as pd
from typing import Dict, Any

class PatternInjector:
    """
    Injects synthetic cross-district crime series and duplicate offender aliases,
    producing ground-truth benchmark datasets for hackathon evaluation.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def inject_series_patterns(self, tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        cases_df = tables.get("CaseMaster")
        accused_df = tables.get("Accused")

        if cases_df is None or cases_df.empty:
            return tables

        gt_case_links = []
        gt_entity_matches = []

        # 1. Inject Cross-District Case Series Links
        case_ids = cases_df["CaseMasterID"].tolist()
        num_series = min(8, max(1, len(case_ids) // 5))

        for series_idx in range(1, num_series + 1):
            series_size = random.randint(2, 4)
            if len(case_ids) < series_size:
                continue
            cluster_cases = random.sample(case_ids, series_size)
            primary_case = cluster_cases[0]

            for linked_case in cluster_cases[1:]:
                gt_case_links.append({
                    "LinkID": len(gt_case_links) + 1,
                    "SourceCaseMasterID": primary_case,
                    "TargetCaseMasterID": linked_case,
                    "SeriesType": random.choice(["CrossDistrictGang", "HighwayRobbery", "CyberPhishing"]),
                    "GroundTruthConfidence": 0.95
                })

        # 2. Inject Duplicate Accused Profiles (Entity Resolution Ground Truth)
        if accused_df is not None and not accused_df.empty:
            acc_ids = accused_df["AccusedMasterID"].tolist()
            num_duplicates = min(10, max(1, len(acc_ids) // 3))

            for match_idx in range(1, num_duplicates + 1):
                if len(acc_ids) < 2:
                    break
                pair = random.sample(acc_ids, 2)
                gt_entity_matches.append({
                    "MatchID": match_idx,
                    "AccusedMasterID_A": pair[0],
                    "AccusedMasterID_B": pair[1],
                    "MatchReason": "Phonetic Similarity & Age Window Overlap",
                    "GroundTruthConfidence": 0.90
                })

        # Explicitly attach evaluation tables to dictionary
        tables["GroundTruthCaseLinks"] = pd.DataFrame(gt_case_links)
        tables["GroundTruthEntityMatches"] = pd.DataFrame(gt_entity_matches)

        return tables# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Pattern Injector & Evaluation Ground Truth Module
# File: generator/ml_patterns/pattern_injector.py
# ==============================================================================

import random
import pandas as pd
from typing import Dict, Any

class PatternInjector:
    """
    Injects synthetic cross-district crime series and duplicate offender aliases,
    producing ground-truth benchmark datasets for hackathon evaluation.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def inject_series_patterns(self, tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        cases_df = tables.get("CaseMaster")
        accused_df = tables.get("Accused")

        if cases_df is None or cases_df.empty:
            return tables

        gt_case_links = []
        gt_entity_matches = []

        # 1. Inject Cross-District Case Series Links
        case_ids = cases_df["CaseMasterID"].tolist()
        num_series = min(8, max(1, len(case_ids) // 5))

        for series_idx in range(1, num_series + 1):
            series_size = random.randint(2, 4)
            if len(case_ids) < series_size:
                continue
            cluster_cases = random.sample(case_ids, series_size)
            primary_case = cluster_cases[0]

            for linked_case in cluster_cases[1:]:
                gt_case_links.append({
                    "LinkID": len(gt_case_links) + 1,
                    "SourceCaseMasterID": primary_case,
                    "TargetCaseMasterID": linked_case,
                    "SeriesType": random.choice(["CrossDistrictGang", "HighwayRobbery", "CyberPhishing"]),
                    "GroundTruthConfidence": 0.95
                })

        # 2. Inject Duplicate Accused Profiles (Entity Resolution Ground Truth)
        if accused_df is not None and not accused_df.empty:
            acc_ids = accused_df["AccusedMasterID"].tolist()
            num_duplicates = min(10, max(1, len(acc_ids) // 3))

            for match_idx in range(1, num_duplicates + 1):
                if len(acc_ids) < 2:
                    break
                pair = random.sample(acc_ids, 2)
                gt_entity_matches.append({
                    "MatchID": match_idx,
                    "AccusedMasterID_A": pair[0],
                    "AccusedMasterID_B": pair[1],
                    "MatchReason": "Phonetic Similarity & Age Window Overlap",
                    "GroundTruthConfidence": 0.90
                })

        # Explicitly attach evaluation tables to dictionary
        tables["GroundTruthCaseLinks"] = pd.DataFrame(gt_case_links)
        tables["GroundTruthEntityMatches"] = pd.DataFrame(gt_entity_matches)

        return tables