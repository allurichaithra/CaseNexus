# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Data Quality Audit & Anomaly Detection Module
# File: generator/validation/data_quality_checks.py
# ==============================================================================

import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger("DatathonDataGen.Validation.Quality")


class DataQualityAuditor:
    """
    Audits generated data against real-world police system quality constraints:
    - Temporal logic sequence checks
    - CrimeNo parsing validation
    - Duplicate GPS coordinate anomaly flag (Police Station Geocoding Bias)
    - Empty narrative detection
    """

    @classmethod
    def audit_dataset(cls, tables: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        report = {"errors": [], "warnings": [], "stats": {}}
        case_df = tables.get("CaseMaster")

        if case_df is None or case_df.empty:
            report["errors"].append("CaseMaster table is missing or empty.")
            return report

        # 1. Temporal Logic Sequence Check
        incident_from = pd.to_datetime(case_df["IncidentFromDate"])
        incident_to = pd.to_datetime(case_df["IncidentToDate"])
        reg_date = pd.to_datetime(case_df["CrimeRegisteredDate"])

        invalid_incident_window = case_df[incident_from > incident_to]
        if not invalid_incident_window.empty:
            report["errors"].append(f"Found {len(invalid_incident_window)} cases where IncidentFromDate > IncidentToDate.")

        invalid_reg_window = case_df[incident_to > reg_date]
        if not invalid_reg_window.empty:
            report["warnings"].append(f"Found {len(invalid_reg_window)} cases registered prior to IncidentToDate.")

        # 2. CrimeNo Structure Verification
        # Format: 1-digit Cat + 4-digit Dist + 4-digit Unit + 4-digit Year + 5-digit Serial
        invalid_crime_nos = case_df[case_df["CrimeNo"].str.len() != 18]
        if not invalid_crime_nos.empty:
            report["errors"].append(f"Found {len(invalid_crime_nos)} invalid CrimeNo strings that do not match the 18-character ER spec.")

        # 3. Geocoding Anomaly Detection (Station-centric clustering)
        coord_counts = case_df.groupby(["latitude", "longitude"]).size()
        station_bias_clusters = coord_counts[coord_counts > 3]
        report["stats"]["station_geocoding_clusters"] = len(station_bias_clusters)
        if len(station_bias_clusters) > 0:
            logger.info(f"Data Quality Flag: Identified {len(station_bias_clusters)} coordinate clusters (simulated station-level geocoding bias).")

        # 4. Empty Narrative Audit
        empty_facts = case_df[case_df["BriefFacts"].isna() | (case_df["BriefFacts"] == "")]
        if not empty_facts.empty:
            report["warnings"].append(f"Found {len(empty_facts)} cases with missing BriefFacts narratives.")

        logger.info(f"Data Quality Audit finished. Errors: {len(report['errors'])}, Warnings: {len(report['warnings'])}")
        return report