"""Fix ground truth data: align signals for GT case link and entity match pairs."""
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / 'datathon-2026' / 'Datathon' / 'generator' / 'output'

# ── CaseMaster fixes: align CrimeMajorHeadID and CrimeMinorHeadID ──
# For each (source, target) pair, set source's IDs to match target's.

CASE_LINK_PAIRS = [
    (1792, 2927), (1792, 2669),
    (803, 1030),  (803, 509),
    (356, 80),
    (1524, 1704), (1524, 1465),
    (1267, 2643), (1267, 1463), (1267, 2149),
    (1294, 2148), (1294, 2357),
    (1884, 1971), (1884, 649),  (1884, 2691),
    (717, 473),
]

# Read GT to get target's actual values
gt_case = pd.read_csv(OUTPUT_DIR / 'GroundTruthCaseLinks.csv')
cases = pd.read_csv(OUTPUT_DIR / 'CaseMaster.csv')

# Build lookup: case_id → (CrimeMajorHeadID, CrimeMinorHeadID)
case_lookup = {}
for _, row in cases.iterrows():
    cid = int(row['CaseMasterID'])
    case_lookup[cid] = (row['CrimeMajorHeadID'], row['CrimeMinorHeadID'])

# For each pair, set source's major/minor head to match target's
for source_id, target_id in CASE_LINK_PAIRS:
    if target_id in case_lookup:
        target_major, target_minor = case_lookup[target_id]
        mask = cases['CaseMasterID'] == source_id
        cases.loc[mask, 'CrimeMajorHeadID'] = target_major
        cases.loc[mask, 'CrimeMinorHeadID'] = target_minor
        print(f'  Case {source_id} → major={target_major}, minor={target_minor} (from target {target_id})')

cases.to_csv(OUTPUT_DIR / 'CaseMaster.csv', index=False)
print(f'CaseMaster.csv updated ({len(cases)} rows)')

# ── Accused fixes: align names and ages for entity match pairs ──

ENTITY_PAIRS = [
    (2701, 1954, 'Vijay Patil',   'Mahesh Patil',   30, 33),
    (190,  3669, 'Anitha Gowda',  'Kavitha Gowda',  31, 29),
    (2325, 2388, 'Manjunath Bhat','Suresh Bhat',    30, 33),
    (3403, 1951, 'Ganesh Kulkarni','Kavitha Kulkarni',32, 29),
    (4965, 2972, 'Ramesh Kumar',  'Ramesh Kumar',   35, 33),
    (4786, 3981, 'Lakshmi Kumar', 'Venkatesh Kumar', 28, 30),
    (4446, 4343, 'Lakshmi Reddy', 'Venkatesh Reddy', 44, 42),
    (3714, 3857, 'Mahesh Kumar',  'Lakshmi Kumar',  35, 33),
    (1027, 2270, 'Priya Kumar',   'Suresh Kumar',   35, 37),
    (3135, 3153, 'Vijay Deshmukh','Mahesh Deshmukh',30, 27),
]

accused = pd.read_csv(OUTPUT_DIR / 'Accused.csv')

for a_id, b_id, a_name, b_name, a_age, b_age in ENTITY_PAIRS:
    mask_a = accused['AccusedMasterID'] == a_id
    mask_b = accused['AccusedMasterID'] == b_id
    accused.loc[mask_a, 'AccusedName'] = a_name
    accused.loc[mask_a, 'AgeYear'] = a_age
    accused.loc[mask_b, 'AccusedName'] = b_name
    accused.loc[mask_b, 'AgeYear'] = b_age
    print(f'  Entity {a_id}→"{a_name}" ({a_age}), {b_id}→"{b_name}" ({b_age})')

accused.to_csv(OUTPUT_DIR / 'Accused.csv', index=False)
print(f'Accused.csv updated ({len(accused)} rows)')
print('Done.')
