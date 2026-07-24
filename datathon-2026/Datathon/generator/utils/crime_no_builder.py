# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Structured CrimeNo Parser and Builder Utility
# File: generator/utils/crime_no_builder.py
# ==============================================================================

from typing import Dict, Any

class CrimeNoBuilder:
    """
    Parses and builds 18-digit CrimeNo according to Karnataka Police ER specification:
    Format: [1-digit Category][4-digit District][4-digit Unit][4-digit Year][5-digit Serial]
    Example: '104430006202600001'
    """

    @staticmethod
    def build(case_category_id: int, district_id: int, unit_id: int, year: int, serial: int) -> str:
        return f"{case_category_id:01d}{district_id:04d}{unit_id:04d}{year:04d}{serial:05d}"

    @staticmethod
    def parse(crime_no: str) -> Dict[str, Any]:
        if len(crime_no) != 18 or not crime_no.isdigit():
            raise ValueError(f"Invalid CrimeNo length or format: {crime_no}")
            
        return {
            "CaseCategoryID": int(crime_no[0]),
            "DistrictID": int(crime_no[1:5]),
            "UnitID": int(crime_no[5:9]),
            "Year": int(crime_no[9:13]),
            "RunningSerial": int(crime_no[13:18]),
            "CaseNo": crime_no[9:]  # Last 9 digits (YYYY + 5-digit serial)
        }