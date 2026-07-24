# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Export Utility Module (CSV & Parquet)
# File: generator/export/csv_parquet_exporter.py
# ==============================================================================

import os
import pandas as pd
from typing import Dict

class FileExporter:
    """Exports generated dataframes to target CSV directory."""

    @staticmethod
    def export_all(tables: Dict[str, pd.DataFrame], output_base_dir: str):
        csv_dir = os.path.join(output_base_dir, "csv")
        os.makedirs(csv_dir, exist_ok=True)

        for name, df in tables.items():
            if df is not None and isinstance(df, pd.DataFrame):
                file_path = os.path.join(csv_dir, f"{name}.csv")
                df.to_csv(file_path, index=False)