# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Administrative Hierarchy & Police Personnel Table Generators
# File: generator/generators/hierarchy_generators.py
# ==============================================================================

import random
import pandas as pd
from typing import Dict, Any
from generator.generators.base_generator import BaseGenerator

class HierarchyGenerators(BaseGenerator):
    """
    Generates geographic and organizational hierarchy tables:
    - State, District, UnitType, Unit (Police Station), Court
    - Rank, Designation, Employee (Investigating Officers & Registration Personnel)
    """

    def generate(self, parent_data: Dict[str, pd.DataFrame] = None) -> Dict[str, pd.DataFrame]:
        hierarchy = {}
        cfg_meta = self.config["meta"]
        cfg_geo = self.config["geospatial"]
        cfg_scale = self.config["scale"]

        # 1. State Table
        state_id = cfg_meta["state_id"]
        hierarchy["State"] = pd.DataFrame([{
            "StateID": state_id,
            "StateName": cfg_meta["state_name"],
            "NationalityID": 1,
            "Active": 1
        }])

        # 2. District Table
        districts_data = []
        for dist_id, details in cfg_geo["district_centers"].items():
            districts_data.append({
                "DistrictID": int(dist_id),
                "DistrictName": details["name"],
                "StateID": state_id,
                "Active": 1
            })
        hierarchy["District"] = pd.DataFrame(districts_data)

        # 3. UnitType Table
        hierarchy["UnitType"] = pd.DataFrame([
            {"UnitTypeID": 1, "UnitTypeName": "Police Station", "City_Dist_State": "District", "Hierarchy": 3, "Active": 1},
            {"UnitTypeID": 2, "UnitTypeName": "Circle Office", "City_Dist_State": "District", "Hierarchy": 2, "Active": 1},
            {"UnitTypeID": 3, "UnitTypeName": "District Headquarters", "City_Dist_State": "District", "Hierarchy": 1, "Active": 1}
        ])

        # 4. Unit (Police Station) Table
        units_data = []
        unit_id_counter = 3001
        for dist_id in hierarchy["District"]["DistrictID"]:
            dist_name = hierarchy["District"].loc[hierarchy["District"]["DistrictID"] == dist_id, "DistrictName"].values[0]
            clean_dist_name = dist_name.replace(" ", "_")
            
            for u_idx in range(1, cfg_scale["units_per_district"] + 1):
                units_data.append({
                    "UnitID": unit_id_counter,
                    "UnitName": f"{clean_dist_name}_PS_{u_idx:02d}",
                    "TypeID": 1,  # Police Station
                    "ParentUnit": None,
                    "NationalityID": 1,
                    "StateID": state_id,
                    "DistrictID": dist_id,
                    "Active": 1
                })
                unit_id_counter += 1
        hierarchy["Unit"] = pd.DataFrame(units_data)

        # 5. Court Table
        courts_data = []
        court_id_counter = 4001
        for dist_id in hierarchy["District"]["DistrictID"]:
            dist_name = hierarchy["District"].loc[hierarchy["District"]["DistrictID"] == dist_id, "DistrictName"].values[0]
            for c_idx in range(1, cfg_scale["courts_per_district"] + 1):
                courts_data.append({
                    "CourtID": court_id_counter,
                    "CourtName": f"{dist_name} {c_idx}nd Addl. Judicial Magistrate First Class (JMFC)",
                    "DistrictID": dist_id,
                    "StateID": state_id,
                    "Active": 1
                })
                court_id_counter += 1
        hierarchy["Court"] = pd.DataFrame(courts_data)

        # 6. Rank Lookup Table
        hierarchy["Rank"] = pd.DataFrame([
            {"RankID": 1, "RankName": "Police Constable (PC)", "Hierarchy": 5, "Active": 1},
            {"RankID": 2, "RankName": "Head Constable (HC)", "Hierarchy": 4, "Active": 1},
            {"RankID": 3, "RankName": "Assistant Sub-Inspector (ASI)", "Hierarchy": 3, "Active": 1},
            {"RankID": 4, "RankName": "Sub-Inspector (PSI)", "Hierarchy": 2, "Active": 1},
            {"RankID": 5, "RankName": "Police Inspector (PI)", "Hierarchy": 1, "Active": 1}
        ])

        # 7. Designation Lookup Table
        hierarchy["Designation"] = pd.DataFrame([
            {"DesignationID": 101, "DesignationName": "Investigating Officer (IO)", "Active": 1, "SortOrder": 1},
            {"DesignationID": 102, "DesignationName": "Station House Officer (SHO)", "Active": 1, "SortOrder": 2},
            {"DesignationID": 103, "DesignationName": "Station Writer / Crime Clerk", "Active": 1, "SortOrder": 3}
        ])

        # 8. Employee (Personnel) Table
        first_names = ["Ramesh", "Suresh", "Mahesh", "Basavaraj", "Shivakumar", "Vijay", "Anand", "Prakash", "Manjunatha", "Ganesh"]
        last_names = ["Patil", "Gowda", "Kulkarni", "Hiremath", "Nayak", "Rao", "Bhat", "Pujari", "Chavan"]

        employees_data = []
        emp_id_counter = 9001
        kgid_counter = 105001

        for _, unit_row in hierarchy["Unit"].iterrows():
            u_id = unit_row["UnitID"]
            d_id = unit_row["DistrictID"]

            # Generate employees per unit
            for e_idx in range(cfg_scale["employees_per_unit"]):
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                
                # Assign rank and designation balance
                if e_idx == 0:
                    rank_id = 5  # Police Inspector
                    desig_id = 102  # SHO
                elif e_idx <= 4:
                    rank_id = 4  # PSI
                    desig_id = 101  # IO
                else:
                    rank_id = random.choice([1, 2, 3])
                    desig_id = 103  # Clerk / Writer

                employees_data.append({
                    "EmployeeID": emp_id_counter,
                    "DistrictID": d_id,
                    "UnitID": u_id,
                    "RankID": rank_id,
                    "DesignationID": desig_id,
                    "KGID": f"KGID-{kgid_counter}",
                    "FirstName": f"{fname} {lname}",
                    "EmployeeDOB": f"{random.randint(1970, 1998)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                    "GenderID": 1,
                    "BloodGroupID": random.randint(1, 4),
                    "PhysicallyChallenged": 0,
                    "AppointmentDate": f"{random.randint(2005, 2022)}-06-01"
                })
                emp_id_counter += 1
                kgid_counter += 1

        hierarchy["Employee"] = pd.DataFrame(employees_data)

        return hierarchy