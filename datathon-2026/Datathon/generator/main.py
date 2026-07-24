# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Master Synthetic Data Generation Framework Entrypoint
# File: generator/main.py
# ==============================================================================

import os
import yaml
import random
import logging
import pandas as pd
from datetime import datetime, timedelta

from generator.generators.lookup_generators import LookupGenerators
from generator.generators.hierarchy_generators import HierarchyGenerators
from generator.generators.case_generator import CaseGenerator
from generator.generators.entity_generators import EntityGenerators
from generator.generators.app_generators import ApplicationGenerators
from generator.ml_patterns.pattern_injector import PatternInjector
from generator.validation.fk_validator import ForeignKeyValidator
from generator.validation.data_quality_checks import DataQualityAuditor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("DatathonDataGen")

def generate_chargesheet_details(case_master_df, employee_df, chargesheet_ratio=0.45):
    """
    Generates ChargesheetDetails table adhering to the Police FIR ER Diagram.
    Schema: CSID (PK), CaseMasterID (FK), csdate, cstype, PolicePersonID (FK)
    cstype values: 'A' -> Chargesheet, 'B' -> False Case, 'C' -> Undetected
    """
    logger.info("Generating ChargesheetDetails Table...")
    cs_records = []
    cs_id_counter = 1

    if case_master_df is None or case_master_df.empty:
        return pd.DataFrame(columns=["CSID", "CaseMasterID", "csdate", "cstype", "PolicePersonID"])

    # Collect valid employee IDs for assigned IOs
    employee_ids = employee_df["EmployeeID"].tolist() if (employee_df is not None and not employee_df.empty) else [1]

    for _, case in case_master_df.iterrows():
        # Generate chargesheet based on configured ratio (default ~45%)
        if random.random() < chargesheet_ratio:
            reg_date_val = case["CrimeRegisteredDate"]
            
            # Robust datetime conversion
            if isinstance(reg_date_val, str):
                reg_date_str = reg_date_val.split()[0]
                reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d")
            elif isinstance(reg_date_val, (datetime, pd.Timestamp)):
                reg_date = reg_date_val
            else:
                reg_date = datetime(2025, 1, 1)
            
            # csdate occurs between 15 to 90 days after registration date
            cs_date = reg_date + timedelta(days=random.randint(15, 90))
            
            # Final Report Type Distribution: Mostly 'A' (Chargesheet)
            cs_type = random.choices(["A", "B", "C"], weights=[0.75, 0.15, 0.10])[0]
            
            # Assigned Officer
            officer_id = case.get("PolicePersonID")
            if pd.isna(officer_id) or officer_id not in employee_ids:
                officer_id = random.choice(employee_ids)

            cs_records.append({
                "CSID": cs_id_counter,
                "CaseMasterID": case["CaseMasterID"],
                "csdate": cs_date.strftime("%Y-%m-%d %H:%M:%S"),
                "cstype": cs_type,
                "PolicePersonID": int(officer_id)
            })
            cs_id_counter += 1

    cs_df = pd.DataFrame(cs_records)
    logger.info(f" - Generated {len(cs_df)} ChargesheetDetails records.")
    return cs_df

def main():
    logger.info("Initializing Datathon 2026 Data Generator Pipeline...")

    # 1. Load Configurations
    config_path = os.path.join(os.path.dirname(__file__), "config", "dataset.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded config file from {config_path}")
    else:
        logger.warning(f"Config file not found at {config_path}. Falling back to default 3000-4000 cases config.")
        config = {
            "meta": {"state_id": 29, "state_name": "KARNATAKA"},
            "scale": {
                "districts_count": 5,
                "units_per_district": 8,
                "employees_per_unit": 10,
                "courts_per_district": 3,
                "min_total_cases": 3000,
                "max_total_cases": 4000,
                "avg_victims_per_case": 1.2,
                "avg_complainants_per_case": 1.0,
                "avg_accused_per_case": 1.8,
                "arrest_ratio_per_case": 0.65,
                "chargesheet_ratio": 0.45
            },
            "temporal_bounds": {
                "start_date": "2024-01-01",
                "end_date": "2026-07-21"
            },
            "ml_patterns": {
                "crime_series": {"enabled": True, "total_series_clusters": 25},
                "repeat_accused": {"enabled": True, "total_repeat_entities": 45}
            }
        }

    # Extract target volume from scale settings (random between min/max)
    scale = config.get("scale", {})
    min_cases = scale.get("min_total_cases", 3000)
    max_cases = scale.get("max_total_cases", 4000)
    target_cases = random.randint(min_cases, max_cases)
    # Inject resolved total into config for generators to read
    config["scale"]["total_cases"] = target_cases
    logger.info(f"Target dataset scale: {target_cases} CaseMaster records (random between {min_cases}-{max_cases}).")

    # 2. Execute Table Generators in Sequential Dependency Order
    tables = {}

    logger.info("Generating Lookup and Taxonomy Tables...")
    tables.update(LookupGenerators(config).generate())

    logger.info("Generating Geographic & Police Personnel Hierarchy...")
    tables.update(HierarchyGenerators(config).generate(tables))

    logger.info("Generating Transactional FIR Case Records...")
    tables.update(CaseGenerator(config).generate(tables))

    logger.info("Generating Entity Records (ComplainantDetails, Victim, Accused, ArrestSurrender)...")
    tables.update(EntityGenerators(config).generate(tables))

    # Generate ChargesheetDetails table using configured chargesheet_ratio
    cs_ratio = config.get("scale", {}).get("chargesheet_ratio", 0.45)
    if "CaseMaster" in tables and "Employee" in tables:
        tables["ChargesheetDetails"] = generate_chargesheet_details(
            tables["CaseMaster"], 
            tables["Employee"], 
            chargesheet_ratio=cs_ratio
        )

    logger.info("Initializing Application Persistence Tables...")
    tables.update(ApplicationGenerators(config).generate(tables))

    # 3. Inject ML Crime Patterns & Benchmark Ground Truth
    logger.info("Injecting Cross-District Crime Series & Entity Resolution Ground Truth...")
    injector = PatternInjector(config)
    tables = injector.inject_series_patterns(tables)

    # 4. Validation & Quality Audits
    logger.info("Executing Referential Integrity & Quality Validation...")
    fk_ok = ForeignKeyValidator.validate_all(tables)
    audit_report = DataQualityAuditor.audit_dataset(tables)

    if not fk_ok:
        logger.warning("Foreign key validation reported issues. Review log details above.")
    else:
        logger.info("Foreign Key Validation Passed Successfully!")

    # 5. Direct Export to generator/output/
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    logger.info(f"Writing all {len(tables)} tables to {output_dir}...")
    for table_name, df in tables.items():
        if isinstance(df, pd.DataFrame):
            out_path = os.path.join(output_dir, f"{table_name}.csv")
            df.to_csv(out_path, index=False)
            logger.info(f" - Exported {table_name}.csv ({len(df)} rows)")

    logger.info(f"Synthetic Data Engine Pipeline Completed Successfully! ({target_cases} cases generated)")

if __name__ == "__main__":
    main()