# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# SQL DDL and Insert Statements Exporter
# File: generator/export/sql_exporter.py
# ==============================================================================

import pandas as pd
import os
import logging
from typing import Dict

logger = logging.getLogger("DatathonDataGen.Export.SQL")


class SQLExporter:
    """Exports generated pandas DataFrames as standard SQL INSERT scripts."""

    @classmethod
    def export_to_sql(cls, tables: Dict[str, pd.DataFrame], output_path: str):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("-- ==============================================================================\n")
            f.write("-- DATATHON 2026: Karnataka Police Synthetic FIR Dataset\n")
            f.write("-- Generated Data Dump for PostgreSQL / Catalyst Data Store\n")
            f.write("-- ==============================================================================\n\n")

            for table_name, df in tables.items():
                if df.empty or table_name.startswith("GroundTruth"):
                    continue

                f.write(f"\n-- Data for Table: {table_name}\n")
                columns = ", ".join([f'"{col}"' for col in df.columns])

                for _, row in df.iterrows():
                    values = []
                    for val in row.values:
                        if pd.isna(val):
                            values.append("NULL")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            # Escape single quotes in text
                            clean_val = str(val).replace("'", "''")
                            values.append(f"'{clean_val}'")

                    val_str = ", ".join(values)
                    f.write(f"INSERT INTO \"{table_name}\" ({columns}) VALUES ({val_str});\n")

        logger.info(f"Successfully generated SQL Script: {output_path}")