# verify_er_schema.py
import os
import pandas as pd

# Target output directory where main.py dumps CSVs
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generator", "output")

# 1. Complete ER Diagram Schema Definition (22 Core ER Tables + 3 App Tables)
REQUIRED_SCHEMA = {
    # Core Transactions
    "CaseMaster": ["CaseMasterID", "CrimeNo", "CaseNo", "CrimeRegisteredDate", "PolicePersonID", 
                   "PoliceStationID", "CaseCategoryID", "GravityOffenceID", "CrimeMajorHeadID", 
                   "CrimeMinorHeadID", "CaseStatusID", "CourtID", "IncidentFromDate", "IncidentToDate", 
                   "latitude", "longitude", "BriefFacts"],
    "ComplainantDetails": ["ComplainantID", "CaseMasterID", "ComplainantName", "AgeYear", 
                          "OccupationID", "ReligionID", "CasteID", "GenderID"],
    "Victim": ["VictimMasterID", "CaseMasterID", "VictimName", "AgeYear", "GenderID", "VictimPolice"],
    "Accused": ["AccusedMasterID", "CaseMasterID", "AccusedName", "AgeYear", "GenderID", "PersonID"],
    "ArrestSurrender": ["ArrestSurrenderID", "CaseMasterID", "ArrestSurrenderTypeID", "ArrestSurrenderDate", 
                       "ArrestSurrenderStateId", "ArrestSurrenderDistrictId", "PoliceStationID", "IOID", 
                       "CourtID", "AccusedMasterID", "IsAccused", "IsComplainantAccused"],
    "ActSectionAssociation": ["CaseMasterID", "ActID", "SectionID", "ActOrderID", "SectionOrderID"],
    "ChargesheetDetails": ["CSID", "CaseMasterID", "csdate", "cstype", "PolicePersonID"],

    # Taxonomies & Legal Framework
    "Act": ["ActCode", "ActDescription", "ShortName", "Active"],
    "Section": ["ActCode", "SectionCode", "SectionDescription", "Active"],
    "CrimeHead": ["CrimeHeadID", "CrimeGroupName", "Active"],
    "CrimeSubHead": ["CrimeSubHeadID", "CrimeHeadID", "CrimeHeadName", "SeqID"],
    "CrimeHeadActSection": ["CrimeHeadID", "ActCode", "SectionCode"],
    "CaseCategory": ["CaseCategoryID", "LookupValue"],
    "GravityOffence": ["GravityOffenceID", "LookupValue"],
    "CaseStatusMaster": ["CaseStatusID", "CaseStatusName"],
    "CasteMaster": ["caste_master_id", "caste_master_name"],
    "ReligionMaster": ["ReligionID", "ReligionName"],
    "OccupationMaster": ["OccupationID", "OccupationName"],

    # Administrative & Personnel Hierarchy
    "State": ["StateID", "StateName"],
    "District": ["DistrictID", "DistrictName", "StateID"],
    "Unit": ["UnitID", "UnitName", "TypeID", "StateID", "DistrictID"],
    "UnitType": ["UnitTypeID", "UnitTypeName", "Hierarchy"],
    "Rank": ["RankID", "RankName", "Hierarchy"],
    "Designation": ["DesignationID", "DesignationName"],
    "Employee": ["EmployeeID", "DistrictID", "UnitID", "RankID", "DesignationID", "KGID", "FirstName"],
    "Court": ["CourtID", "CourtName", "DistrictID", "StateID"],

    # Application Persistence & Evaluation (Platform Layer)
    "GroundTruthCaseLinks": ["LinkID", "SourceCaseMasterID", "TargetCaseMasterID", "SeriesType"],
    "GroundTruthEntityMatches": ["MatchID", "AccusedMasterID_A", "AccusedMasterID_B"]
}

# 2. Key Foreign Key Mappings from ER Relationship Matrix
FK_RELATIONSHIPS = [
    ("ComplainantDetails", "CaseMasterID", "CaseMaster", "CaseMasterID"),
    ("Victim", "CaseMasterID", "CaseMaster", "CaseMasterID"),
    ("Accused", "CaseMasterID", "CaseMaster", "CaseMasterID"),
    ("ActSectionAssociation", "CaseMasterID", "CaseMaster", "CaseMasterID"),
    ("ArrestSurrender", "CaseMasterID", "CaseMaster", "CaseMasterID"),
    ("ArrestSurrender", "AccusedMasterID", "Accused", "AccusedMasterID"),
    ("CaseMaster", "PoliceStationID", "Unit", "UnitID"),
    ("CaseMaster", "PolicePersonID", "Employee", "EmployeeID"),
    ("Employee", "UnitID", "Unit", "UnitID"),
    ("Unit", "DistrictID", "District", "DistrictID")
]

def check_er_coverage():
    print("==================================================================")
    print("   DATATHON 2026: ER DIAGRAM & SCHEMA COMPLIANCE AUDIT          ")
    print("==================================================================\n")

    missing_tables = []
    schema_errors = []

    # Test 1: Check File & Column Existence
    print("--- 1. Checking Table & Column Existence ---")
    for table_name, expected_cols in REQUIRED_SCHEMA.items():
        file_path = os.path.join(OUTPUT_DIR, f"{table_name}.csv")
        if not os.path.exists(file_path):
            print(f"[FAIL] Missing Table: {table_name}.csv")
            missing_tables.append(table_name)
            continue

        df = pd.read_csv(file_path)
        missing_cols = [col for col in expected_cols if col not in df.columns]
        
        if missing_cols:
            print(f"[FAIL] {table_name}.csv is missing columns: {missing_cols}")
            schema_errors.append((table_name, missing_cols))
        else:
            print(f"[PASS] {table_name}.csv is valid ({len(df)} records generated).")

    # Test 2: Verify Foreign Key Referential Integrity
    print("\n--- 2. Checking Foreign Key Referential Integrity ---")
    fk_errors = 0
    for child_table, child_fk, parent_table, parent_pk in FK_RELATIONSHIPS:
        child_path = os.path.join(OUTPUT_DIR, f"{child_table}.csv")
        parent_path = os.path.join(OUTPUT_DIR, f"{parent_table}.csv")

        if not os.path.exists(child_path) or not os.path.exists(parent_path):
            continue

        child_df = pd.read_csv(child_path)
        parent_df = pd.read_csv(parent_path)

        # Find orphaned IDs
        child_keys = set(child_df[child_fk].dropna().astype(int))
        parent_keys = set(parent_df[parent_pk].dropna().astype(int))
        orphans = child_keys - parent_keys

        if orphans:
            print(f"[FAIL] FK Violation: {child_table}.{child_fk} -> {parent_table}.{parent_pk}. Found {len(orphans)} orphaned keys!")
            fk_errors += 1
        else:
            print(f"[PASS] FK Match: {child_table}.{child_fk} properly maps to {parent_table}.{parent_pk}.")

    # Summary
    print("\n==================================================================")
    if not missing_tables and not schema_errors and fk_errors == 0:
        print(" SUCCESS: Generator 100% compliant with Police FIR ER Diagram! ")
    else:
        print(" ATTENTION: Compliance issues detected. Review details above. ")
    print("==================================================================")

if __name__ == "__main__":
    check_er_coverage()