# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Transactional Case Generator Module
# File: generator/generators/case_generator.py
# ==============================================================================

import random
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any
from generator.generators.base_generator import BaseGenerator

class CaseGenerator(BaseGenerator):
    """
    Generates core transactional FIR records (CaseMaster) and associated legal
    charge sections (ActSectionAssociation) strictly mapped to the ER schema.
    """

    def generate(self, parent_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        # Safe extraction of scale config with fallback defaults
        scale_cfg = self.config.get("scale", self.config)
        total_cases = scale_cfg.get("total_cases", 200)

        units_df = parent_data.get("Unit")
        employees_df = parent_data.get("Employee")
        courts_df = parent_data.get("Court")
        crime_heads_df = parent_data.get("CrimeHead")
        crime_subheads_df = parent_data.get("CrimeSubHead")
        acts_df = parent_data.get("Act")
        sections_df = parent_data.get("Section")

        if units_df is None or units_df.empty:
            raise ValueError("Unit hierarchy is required before generating CaseMaster records.")

        unit_ids = units_df["UnitID"].tolist()
        emp_ids = employees_df["EmployeeID"].tolist() if employees_df is not None and not employees_df.empty else [1]
        court_ids = courts_df["CourtID"].tolist() if courts_df is not None and not courts_df.empty else [101]

        # Pre-build lookup mappings for CrimeHead and CrimeSubHead
        head_ids = crime_heads_df["CrimeHeadID"].tolist() if crime_heads_df is not None else [10]
        subhead_map = {}
        if crime_subheads_df is not None and not crime_subheads_df.empty:
            for _, row in crime_subheads_df.iterrows():
                subhead_map.setdefault(row["CrimeHeadID"], []).append(row["CrimeSubHeadID"])

        act_codes = acts_df["ActCode"].tolist() if acts_df is not None and not acts_df.empty else ["IPC"]
        section_codes = sections_df["SectionCode"].tolist() if sections_df is not None and not sections_df.empty else ["302", "379", "395", "420"]

        cases = []
        act_sections = []

        start_date = datetime(2025, 1, 1)
        end_date = datetime(2026, 3, 31)
        date_span_days = (end_date - start_date).days

        # Sample narratives for BriefFacts narrative-similarity scoring in ML engine
        sample_narratives = [
            "Unknown miscreants broke open the lock of the house during late night hours and stole gold ornaments and cash.",
            "Two persons riding a black motorcycle snatched a gold chain from a pedestrian near the bus stand and fled.",
            "Accused intercepted a commercial vehicle on the highway, threatened the driver with sharp weapons, and looted goods.",
            "Complainant reported unauthorized debit transactions from bank account following a fake KYC verification call.",
            "A group of individuals assaulted the victim following a minor road rage incident causing grievous injuries."
        ]

        for case_id in range(1, total_cases + 1):
            ps_id = random.choice(unit_ids)
            district_id = units_df.loc[units_df["UnitID"] == ps_id, "DistrictID"].values[0] if "DistrictID" in units_df.columns else 101

            reg_date = start_date + timedelta(days=random.randint(0, date_span_days), hours=random.randint(0, 23))
            inc_from = reg_date - timedelta(hours=random.randint(2, 48))
            inc_to = inc_from + timedelta(hours=random.randint(1, 12))

            major_head = random.choice(head_ids)
            possible_subheads = subhead_map.get(major_head, [1001])
            minor_head = random.choice(possible_subheads)

            # Construct CrimeNo: 1-digit Category + 4-digit District + 4-digit Station + 4-digit Year + 5-digit Serial
            year_str = reg_date.strftime("%Y")
            crime_no = f"1{district_id:04d}{ps_id:04d}{year_str}{case_id:05d}"
            case_no = f"{year_str}{case_id:05d}"

            # Spatial jitter around Bangalore coordinates for geospatial testing
            lat = round(12.9716 + random.uniform(-0.15, 0.15), 6)
            lon = round(77.5946 + random.uniform(-0.15, 0.15), 6)

            cases.append({
                "CaseMasterID": case_id,
                "CrimeNo": crime_no,
                "CaseNo": case_no,
                "CrimeRegisteredDate": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
                "PolicePersonID": random.choice(emp_ids),
                "PoliceStationID": ps_id,
                "DistrictID": district_id,
                "CaseCategoryID": 1,         # 1: FIR
                "GravityOffenceID": random.choice([1, 2]), # 1: Heinous, 2: Non-Heinous
                "CrimeMajorHeadID": major_head,
                "CrimeMinorHeadID": minor_head,
                "CaseStatusID": random.choice([1, 2, 3]), # Under Investigation, Charge Sheeted, Closed
                "CourtID": random.choice(court_ids),
                "IncidentFromDate": inc_from.strftime("%Y-%m-%d %H:%M:%S"),
                "IncidentToDate": inc_to.strftime("%Y-%m-%d %H:%M:%S"),
                "InfoReceivedPSDate": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": lat,
                "longitude": lon,
                "BriefFacts": random.choice(sample_narratives)
            })

            # ActSectionAssociation entries (1 to 3 legal sections per FIR)
            num_sections = random.choice([1, 2, 3])
            for sec_idx in range(num_sections):
                act_sections.append({
                    "CaseMasterID": case_id,
                    "ActID": random.choice(act_codes),
                    "SectionID": random.choice(section_codes),
                    "ActOrderID": 1,
                    "SectionOrderID": sec_idx + 1
                })

        return {
            "CaseMaster": pd.DataFrame(cases),
            "ActSectionAssociation": pd.DataFrame(act_sections)
        }