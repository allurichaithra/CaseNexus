# verify_pipeline.py
import os
import pandas as pd

# Point directly to generator/output/ where the files reside
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generator", "output")

def test_file_existence():
    """Verify expected CSV output tables exist directly in generator/output/."""
    expected_tables = [
        "CaseMaster.csv",
        "ComplainantDetails.csv",
        "Victim.csv",
        "Accused.csv",
        "ArrestSurrender.csv",
        "ActSectionAssociation.csv",
        "Unit.csv",
        "Employee.csv",
        "GroundTruthCaseLinks.csv",
        "GroundTruthEntityMatches.csv"
    ]
    
    print("\n--- TEST 1: Checking Output File Generation ---")
    all_exist = True
    for table in expected_tables:
        file_path = os.path.join(OUTPUT_DIR, table)
        if os.path.exists(file_path):
            print(f"[PASS] {table} exists.")
        else:
            print(f"[FAIL] {table} IS MISSING!")
            all_exist = False
    return all_exist

def test_referential_integrity():
    """Verify Foreign Keys between CaseMaster, Accused, and Units."""
    print("\n--- TEST 2: Checking Referential Integrity (FKs) ---")
    
    cases_path = os.path.join(OUTPUT_DIR, "CaseMaster.csv")
    accused_path = os.path.join(OUTPUT_DIR, "Accused.csv")
    units_path = os.path.join(OUTPUT_DIR, "Unit.csv")

    if not (os.path.exists(cases_path) and os.path.exists(accused_path) and os.path.exists(units_path)):
        print("[SKIP] Skipping FK check because one or more core tables are missing.")
        return

    cases_df = pd.read_csv(cases_path)
    accused_df = pd.read_csv(accused_path)
    units_df = pd.read_csv(units_path)

    # 1. Check if all Accused.CaseMasterID exist in CaseMaster
    missing_case_ids = set(accused_df["CaseMasterID"]) - set(cases_df["CaseMasterID"])
    if not missing_case_ids:
        print("[PASS] Every Accused record maps to a valid CaseMasterID.")
    else:
        print(f"[FAIL] Found {len(missing_case_ids)} orphaned Accused records!")

    # 2. Check if all CaseMaster.PoliceStationID exist in Unit
    missing_units = set(cases_df["PoliceStationID"]) - set(units_df["UnitID"])
    if not missing_units:
        print("[PASS] Every CaseMaster record maps to a valid PoliceStationID (UnitID).")
    else:
        print(f"[FAIL] Found {len(missing_units)} invalid PoliceStationIDs!")

def test_ground_truth_injection():
    """Verify that pattern_injector embedded evaluation ground truth."""
    print("\n--- TEST 3: Checking Ground Truth Pattern Injection ---")
    gt_links_path = os.path.join(OUTPUT_DIR, "GroundTruthCaseLinks.csv")
    gt_entities_path = os.path.join(OUTPUT_DIR, "GroundTruthEntityMatches.csv")

    if os.path.exists(gt_links_path) and os.path.getsize(gt_links_path) > 10:
        df_links = pd.read_csv(gt_links_path)
        print(f"[PASS] Injected {len(df_links)} ground-truth cross-district case links for hackathon evaluation.")
    else:
        print("[WARN/FAIL] GroundTruthCaseLinks.csv is missing or empty. Ensure pattern_injector is producing ground truth tables.")

    if os.path.exists(gt_entities_path) and os.path.getsize(gt_entities_path) > 10:
        df_entities = pd.read_csv(gt_entities_path)
        print(f"[PASS] Injected {len(df_entities)} ground-truth duplicate accused entities.")
    else:
        print("[WARN/FAIL] GroundTruthEntityMatches.csv is missing or empty.")

if __name__ == "__main__":
    test_file_existence()
    test_referential_integrity()
    test_ground_truth_injection()