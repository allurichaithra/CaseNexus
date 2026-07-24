# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Entity Generators Module (Complainant, Victim, Accused, ArrestSurrender)
# File: generator/generators/entity_generators.py
# ==============================================================================

import random
import pandas as pd
from typing import Dict, Any
from generator.generators.base_generator import BaseGenerator

class EntityGenerators(BaseGenerator):
    """
    Generates relational tables tied directly to CaseMaster:
    - ComplainantDetails (1 per case)
    - Victim (1-2 per case)
    - Accused (1-3 per case)
    - ArrestSurrender (0-1 per case, referencing an Accused)
    """

    FIRST_NAMES = [
        "Ramesh", "Suresh", "Mahesh", "Priya", "Anitha", "Sunita", 
        "Venkatesh", "Manjunath", "Lakshmi", "Ganesh", "Vijay", "Kavitha"
    ]
    LAST_NAMES = [
        "Gowda", "Kumar", "Patil", "Rao", "Nayak", "Reddy", 
        "Bhat", "Hegde", "Shetty", "Pujari", "Kulkarni", "Deshmukh"
    ]

    def generate(self, parent_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        cases_df = parent_data.get("CaseMaster")
        if cases_df is None or cases_df.empty:
            raise ValueError("CaseMaster table missing or empty. Cannot generate entity records.")

        units_df = parent_data.get("Unit")
        employees_df = parent_data.get("Employee")
        courts_df = parent_data.get("Court")

        emp_ids = employees_df["EmployeeID"].tolist() if employees_df is not None and not employees_df.empty else [1]
        court_ids = courts_df["CourtID"].tolist() if courts_df is not None and not courts_df.empty else [101]

        complainants = []
        victims = []
        accused_list = []
        arrests = []

        comp_id_counter = 1
        victim_id_counter = 1
        accused_id_counter = 1
        arrest_id_counter = 1

        for _, case_row in cases_df.iterrows():
            cid = case_row["CaseMasterID"]
            c_date = case_row["CrimeRegisteredDate"]
            p_station = case_row["PoliceStationID"]
            district_id = case_row.get("DistrictID", 101)

            # 1. ComplainantDetails (1 per FIR)
            # Note: ReligionID and CasteID exist per ER diagram but are excluded from AI pipelines
            complainants.append({
                "ComplainantID": comp_id_counter,
                "CaseMasterID": cid,
                "ComplainantName": f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}",
                "AgeYear": random.randint(21, 70),
                "OccupationID": random.randint(1, 10),
                "ReligionID": random.randint(1, 5),   # Isolated demographic field
                "CasteID": random.randint(1, 10),      # Isolated demographic field
                "GenderID": random.choice([1, 2])      # 1: Male, 2: Female
            })
            comp_id_counter += 1

            # 2. Victim Details (1 to 2 per FIR)
            num_victims = random.choice([1, 1, 1, 2])
            for _ in range(num_victims):
                victims.append({
                    "VictimMasterID": victim_id_counter,
                    "CaseMasterID": cid,
                    "VictimName": f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}",
                    "AgeYear": random.randint(18, 65),
                    "GenderID": random.choice([1, 2]),
                    "VictimPolice": random.choice(["0", "0", "0", "1"])  # 1 if police officer
                })
                victim_id_counter += 1

            # 3. Accused Details (1 to 3 per FIR)
            num_accused = random.choice([1, 1, 2, 3])
            case_accused_ids = []
            for idx in range(num_accused):
                acc_id = accused_id_counter
                accused_list.append({
                    "AccusedMasterID": acc_id,
                    "CaseMasterID": cid,
                    "AccusedName": f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}",
                    "AgeYear": random.randint(19, 50),
                    "GenderID": random.choice([1, 1, 1, 2]),
                    "PersonID": f"A{idx + 1}"
                })
                case_accused_ids.append(acc_id)
                accused_id_counter += 1

            # 4. ArrestSurrender Details (Linked to an Accused)
            if case_accused_ids and random.random() < 0.65:  # 65% arrest/surrender rate
                target_accused = random.choice(case_accused_ids)
                arrests.append({
                    "ArrestSurrenderID": arrest_id_counter,
                    "CaseMasterID": cid,
                    "ArrestSurrenderTypeID": random.choice([1, 2]),  # 1: Arrest, 2: Surrender
                    "ArrestSurrenderDate": c_date,
                    "ArrestSurrenderStateId": 1,
                    "ArrestSurrenderDistrictId": district_id,
                    "PoliceStationID": p_station,
                    "IOID": random.choice(emp_ids),
                    "CourtID": random.choice(court_ids),
                    "AccusedMasterID": target_accused,
                    "IsAccused": 1,
                    "IsComplainantAccused": 0
                })
                arrest_id_counter += 1

        # Explicitly return all 4 tables in dictionary
        return {
            "ComplainantDetails": pd.DataFrame(complainants),
            "Victim": pd.DataFrame(victims),
            "Accused": pd.DataFrame(accused_list),
            "ArrestSurrender": pd.DataFrame(arrests)
        }