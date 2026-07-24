from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SERVER_DIR = BASE_DIR
WORKSPACE_ROOT = BASE_DIR.parent.parent

DATASET_DIRS = [
    WORKSPACE_ROOT / "datathon-2026" / "Datathon" / "generator" / "output",
    WORKSPACE_ROOT / "datathon-2026" / "data" / "synthetic",
    WORKSPACE_ROOT / "datathon-2026" / "data" / "ground_truth",
]

DATASET_DIR = next((path for path in DATASET_DIRS if path.exists()), DATASET_DIRS[0])
GROUND_TRUTH_DIR = next((path for path in [WORKSPACE_ROOT / "datathon-2026" / "Datathon" / "generator" / "output"] if path.exists()), DATASET_DIR)


def discover_dataset_dir() -> Path:
    """Locate the real CSV export directory from the workspace structure."""
    for candidate in DATASET_DIRS:
        if candidate.exists():
            return candidate
    return DATASET_DIRS[0]


DATASET_DIR = discover_dataset_dir()
GROUND_TRUTH_DIR = DATASET_DIR


def find_csv(possible_names: List[str]) -> Path | None:
    """Find a CSV file while tolerating minor filename/case differences."""
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {DATASET_DIR}")

    files = {file.name.lower(): file for file in DATASET_DIR.glob("*.csv")}
    for name in possible_names:
        if name.lower() in files:
            return files[name.lower()]
    return None


def read_optional_csv(possible_names: List[str]) -> pd.DataFrame:
    """Load a CSV if it exists. Returns an empty DataFrame if it is not present."""
    path = find_csv(possible_names)
    if path is None:
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def load_dataset() -> Dict[str, pd.DataFrame]:
    print(f"Loading dataset from: {DATASET_DIR}")

    case_master = read_optional_csv(["CaseMaster.csv", "case_master.csv", "casemaster.csv"])
    if case_master.empty:
        raise FileNotFoundError(f"Could not find CaseMaster CSV in {DATASET_DIR}")

    accused = read_optional_csv(["Accused.csv", "accused.csv"])
    victims = read_optional_csv(["Victim.csv", "victim.csv"])
    complainants = read_optional_csv(["ComplainantDetails.csv", "complainant_details.csv"])
    act_sections = read_optional_csv(["ActSectionAssociation.csv", "act_section_association.csv"])
    units = read_optional_csv(["Unit.csv", "unit.csv"])
    districts = read_optional_csv(["District.csv", "district.csv"])
    crime_heads = read_optional_csv(["CrimeHead.csv", "crime_head.csv"])
    crime_sub_heads = read_optional_csv(["CrimeSubHead.csv", "crime_sub_head.csv"])
    ground_truth_case_links = read_optional_csv(["GroundTruthCaseLinks.csv", "ground_truth_case_links.csv"])
    ground_truth_entity_matches = read_optional_csv(["GroundTruthEntityMatches.csv", "ground_truth_entity_matches.csv"])

    return {
        "cases": case_master,
        "accused": accused,
        "victims": victims,
        "complainants": complainants,
        "act_sections": act_sections,
        "units": units,
        "districts": districts,
        "crime_heads": crime_heads,
        "crime_sub_heads": crime_sub_heads,
        "ground_truth_case_links": ground_truth_case_links,
        "ground_truth_entity_matches": ground_truth_entity_matches,
    }


def dataframe_summary(data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, object]]:
    summary = {}
    for name, df in data.items():
        summary[name] = {
            "rows": len(df),
            "columns": list(df.columns),
        }
    return summary