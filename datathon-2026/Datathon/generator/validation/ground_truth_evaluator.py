# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Ground Truth Benchmark Generator & Evaluator
# File: generator/validation/ground_truth_evaluator.py
# ==============================================================================

import pandas as pd
from typing import Dict, Any


class GroundTruthEvaluator:
    """
    Extracts ground-truth series and repeat offender links injected by PatternInjector
    to export evaluation matrices for hackathon benchmarking.
    """

    @classmethod
    def generate_ground_truth_tables(cls, tables: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        gt_data = {}

        # 1. Ground Truth Case Links
        if "GroundTruthSeries" in tables:
            gt_series = tables["GroundTruthSeries"]
            
            # Perform self-join on GroundTruthSeries to create pairwise ground truth FIR links
            paired_links = pd.merge(gt_series, gt_series, on="SeriesID", suffixes=("_1", "_2"))
            paired_links = paired_links[paired_links["CaseMasterID_1"] < paired_links["CaseMasterID_2"]]
            
            gt_data["GroundTruthCaseLinks"] = paired_links[[
                "SeriesID", "CaseMasterID_1", "CaseMasterID_2", "MO_Type_1"
            ]].rename(columns={
                "CaseMasterID_1": "QueryCaseMasterID",
                "CaseMasterID_2": "LinkedCaseMasterID",
                "MO_Type_1": "GroundTruthMO"
            })

        # 2. Ground Truth Repeat Accused
        accused_df = tables.get("Accused")
        if accused_df is not None and "PersonID" in accused_df.columns:
            repeat_accused = accused_df[accused_df["PersonID"].str.startswith("PER_REPEAT_", na=False)]
            
            paired_accused = pd.merge(repeat_accused, repeat_accused, on="PersonID", suffixes=("_1", "_2"))
            paired_accused = paired_accused[paired_accused["AccusedMasterID_1"] < paired_accused["AccusedMasterID_2"]]
            
            gt_data["GroundTruthEntityMatches"] = paired_accused[[
                "PersonID", "AccusedMasterID_1", "AccusedName_1", "AccusedMasterID_2", "AccusedName_2"
            ]].rename(columns={
                "AccusedMasterID_1": "AccusedMasterID_A",
                "AccusedName_1": "AccusedName_A",
                "AccusedMasterID_2": "AccusedMasterID_B",
                "AccusedName_2": "AccusedName_B"
            })

        return gt_data