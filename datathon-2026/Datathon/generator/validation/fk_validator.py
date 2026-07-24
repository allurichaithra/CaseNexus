# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Relational Schema & Foreign Key Validation Suite
# File: generator/validation/fk_validator.py
# ==============================================================================

import pandas as pd
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger("DatathonDataGen.Validation.FK")


class ForeignKeyValidator:
    """
    Enforces relational integrity across generated tables based on the
    Karnataka Police FIR ER Diagram specification.
    """

    # Mapping format: (ChildTable, ChildColumn) -> (ParentTable, ParentColumn)
    FK_RELATIONS: List[Tuple[Tuple[str, str], Tuple[str, str]]] = [
        (("CaseMaster", "PoliceStationID"), ("Unit", "UnitID")),
        (("CaseMaster", "PolicePersonID"), ("Employee", "EmployeeID")),
        (("CaseMaster", "CaseCategoryID"), ("CaseCategory", "CaseCategoryID")),
        (("CaseMaster", "GravityOffenceID"), ("GravityOffence", "GravityOffenceID")),
        (("CaseMaster", "CrimeMajorHeadID"), ("CrimeHead", "CrimeHeadID")),
        (("CaseMaster", "CrimeMinorHeadID"), ("CrimeSubHead", "CrimeSubHeadID")),
        (("CaseMaster", "CaseStatusID"), ("CaseStatusMaster", "CaseStatusID")),
        (("CaseMaster", "CourtID"), ("Court", "CourtID")),
        (("ActSectionAssociation", "CaseMasterID"), ("CaseMaster", "CaseMasterID")),
        (("ComplainantDetails", "CaseMasterID"), ("CaseMaster", "CaseMasterID")),
        (("Victim", "CaseMasterID"), ("CaseMaster", "CaseMasterID")),
        (("Accused", "CaseMasterID"), ("CaseMaster", "CaseMasterID")),
        (("ArrestSurrender", "CaseMasterID"), ("CaseMaster", "CaseMasterID")),
        (("ArrestSurrender", "AccusedMasterID"), ("Accused", "AccusedMasterID")),
        (("ArrestSurrender", "IOID"), ("Employee", "EmployeeID")),
        (("ArrestSurrender", "PoliceStationID"), ("Unit", "UnitID")),
        (("ArrestSurrender", "CourtID"), ("Court", "CourtID")),
        (("Unit", "DistrictID"), ("District", "DistrictID")),
        (("Employee", "UnitID"), ("Unit", "UnitID")),
    ]

    @classmethod
    def validate_all(cls, tables: Dict[str, pd.DataFrame]) -> bool:
        """Validates that all foreign key values exist in parent tables."""
        all_passed = True
        logger.info("Executing Foreign Key Integrity Checks...")

        for (child_table, child_col), (parent_table, parent_col) in cls.FK_RELATIONS:
            if child_table not in tables or parent_table not in tables:
                logger.warning(f"Skipping check: {child_table} or {parent_table} missing from generated tables.")
                continue

            child_df = tables[child_table]
            parent_df = tables[parent_table]

            if child_col not in child_df.columns or parent_col not in parent_df.columns:
                continue

            # Drop NaNs for optional foreign keys
            child_keys = set(child_df[child_col].dropna().unique())
            parent_keys = set(parent_df[parent_col].unique())

            orphans = child_keys - parent_keys
            if orphans:
                logger.error(f"FK Violation! {child_table}.{child_col} has {len(orphans)} orphan key(s) not in {parent_table}.{parent_col}. Samples: {list(orphans)[:5]}")
                all_passed = False
            else:
                logger.debug(f"FK Check Passed: {child_table}.{child_col} -> {parent_table}.{parent_col}")

        if all_passed:
            logger.info("All Foreign Key integrity constraints passed successfully!")
        return all_passed