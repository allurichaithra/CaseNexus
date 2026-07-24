# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Taxonomy, Legal Framework, and Lookup Table Generators
# File: generator/generators/lookup_generators.py
# ==============================================================================

import pandas as pd
from typing import Dict, Any
from generator.generators.base_generator import BaseGenerator

class LookupGenerators(BaseGenerator):
    """
    Generates all standard lookup and taxonomy tables matching the Karnataka Police FIR ER Diagram:
    - CaseCategory, GravityOffence, CaseStatusMaster
    - Act, Section, CrimeHead, CrimeSubHead, CrimeHeadActSection
    - ReligionMaster, CasteMaster, OccupationMaster
    """

    def generate(self, parent_data: Dict[str, pd.DataFrame] = None) -> Dict[str, pd.DataFrame]:
        lookups = {}

        # 1. CaseCategory (FIR, UDR, PAR, Zero FIR)
        lookups["CaseCategory"] = pd.DataFrame([
            {"CaseCategoryID": 1, "LookupValue": "FIR"},
            {"CaseCategoryID": 3, "LookupValue": "UDR"},
            {"CaseCategoryID": 4, "LookupValue": "PAR"},
            {"CaseCategoryID": 8, "LookupValue": "Zero FIR"}
        ])

        # 2. GravityOffence (Heinous, Non-Heinous)
        lookups["GravityOffence"] = pd.DataFrame([
            {"GravityOffenceID": 1, "LookupValue": "Heinous"},
            {"GravityOffenceID": 2, "LookupValue": "Non-Heinous"}
        ])

        # 3. CaseStatusMaster (Lifecycle stages)
        lookups["CaseStatusMaster"] = pd.DataFrame([
            {"CaseStatusID": 101, "CaseStatusName": "Under Investigation"},
            {"CaseStatusID": 102, "CaseStatusName": "Charge Sheeted"},
            {"CaseStatusID": 103, "CaseStatusName": "Closed / Untraced"},
            {"CaseStatusID": 104, "CaseStatusName": "Transferred"}
        ])

        # 4. Act (Legal Statutes)
        lookups["Act"] = pd.DataFrame([
            {"ActCode": "IPC", "ActDescription": "Indian Penal Code, 1860", "ShortName": "IPC", "Active": 1},
            {"ActCode": "NDPS", "ActDescription": "Narcotic Drugs and Psychotropic Substances Act, 1985", "ShortName": "NDPS", "Active": 1},
            {"ActCode": "IT_ACT", "ActDescription": "Information Technology Act, 2000", "ShortName": "IT Act", "Active": 1},
            {"ActCode": "POCSO", "ActDescription": "Protection of Children from Sexual Offences Act", "ShortName": "POCSO", "Active": 1}
        ])

        # 5. Section (Legal provisions per Act)
        lookups["Section"] = pd.DataFrame([
            # IPC Theft / Robbery / Housebreak
            {"ActCode": "IPC", "SectionCode": "379", "SectionDescription": "Punishment for Theft", "Active": 1},
            {"ActCode": "IPC", "SectionCode": "392", "SectionDescription": "Punishment for Robbery", "Active": 1},
            {"ActCode": "IPC", "SectionCode": "457", "SectionDescription": "Lurking house-trespass or house-breaking by night", "Active": 1},
            {"ActCode": "IPC", "SectionCode": "302", "SectionDescription": "Punishment for Murder", "Active": 1},
            # Cyber Crime
            {"ActCode": "IT_ACT", "SectionCode": "66C", "SectionDescription": "Punishment for identity theft", "Active": 1},
            {"ActCode": "IT_ACT", "SectionCode": "66D", "SectionDescription": "Punishment for cheating by personation using computer resource", "Active": 1},
            # NDPS
            {"ActCode": "NDPS", "SectionCode": "20", "SectionDescription": "Punishment for contravention in relation to cannabis plant and cannabis", "Active": 1}
        ])

        # 6. CrimeHead (Major crime classification)
        lookups["CrimeHead"] = pd.DataFrame([
            {"CrimeHeadID": 101, "CrimeGroupName": "House Break-In & Burglary", "Active": 1},
            {"CrimeHeadID": 102, "CrimeGroupName": "Robbery & Chain Snatching", "Active": 1},
            {"CrimeHeadID": 103, "CrimeGroupName": "Cyber & Financial Fraud", "Active": 1},
            {"CrimeHeadID": 104, "CrimeGroupName": "Crimes Against Person", "Active": 1}
        ])

        # 7. CrimeSubHead (Minor crime classification)
        lookups["CrimeSubHead"] = pd.DataFrame([
            {"CrimeSubHeadID": 1001, "CrimeHeadID": 101, "CrimeHeadName": "Night House Breaking", "SeqID": 1},
            {"CrimeSubHeadID": 1002, "CrimeHeadID": 101, "CrimeHeadName": "Day House Breaking", "SeqID": 2},
            {"CrimeSubHeadID": 1003, "CrimeHeadID": 102, "CrimeHeadName": "Chain Snatching on Road", "SeqID": 1},
            {"CrimeSubHeadID": 1004, "CrimeHeadID": 102, "CrimeHeadName": "Highway Robbery", "SeqID": 2},
            {"CrimeSubHeadID": 1005, "CrimeHeadID": 103, "CrimeHeadName": "Part-Time Job / Telegram Scam", "SeqID": 1},
            {"CrimeSubHeadID": 1006, "CrimeHeadID": 103, "CrimeHeadName": "UPI / SIM Swap Fraud", "SeqID": 2},
            {"CrimeSubHeadID": 1007, "CrimeHeadID": 104, "CrimeHeadName": "Grievous Hurt", "SeqID": 1}
        ])

        # 8. CrimeHeadActSection (Preset legal mappings)
        lookups["CrimeHeadActSection"] = pd.DataFrame([
            {"CrimeHeadID": 101, "ActCode": "IPC", "SectionCode": "457"},
            {"CrimeHeadID": 101, "ActCode": "IPC", "SectionCode": "379"},
            {"CrimeHeadID": 102, "ActCode": "IPC", "SectionCode": "392"},
            {"CrimeHeadID": 103, "ActCode": "IT_ACT", "SectionCode": "66D"}
        ])

        # 9. Non-ML Demographic Lookups (Strict Schema Compliance)
        lookups["ReligionMaster"] = pd.DataFrame([
            {"ReligionID": 1, "ReligionName": "Hindu"},
            {"ReligionID": 2, "ReligionName": "Muslim"},
            {"ReligionID": 3, "ReligionName": "Christian"},
            {"ReligionID": 4, "ReligionName": "Sikh"},
            {"ReligionID": 5, "ReligionName": "Jain"},
            {"ReligionID": 6, "ReligionName": "Others"}
        ])

        lookups["CasteMaster"] = pd.DataFrame([
            {"caste_master_id": 1, "caste_master_name": "General"},
            {"caste_master_id": 2, "caste_master_name": "OBC"},
            {"caste_master_id": 3, "caste_master_name": "Scheduled Caste (SC)"},
            {"caste_master_id": 4, "caste_master_name": "Scheduled Tribe (ST)"}
        ])

        lookups["OccupationMaster"] = pd.DataFrame([
            {"OccupationID": 1, "OccupationName": "Business / Self-Employed"},
            {"OccupationID": 2, "OccupationName": "Private Sector Employee"},
            {"OccupationID": 3, "OccupationName": "Government Employee"},
            {"OccupationID": 4, "OccupationName": "Agriculture / Farmer"},
            {"OccupationID": 5, "OccupationName": "Student"},
            {"OccupationID": 6, "OccupationName": "Homemaker"},
            {"OccupationID": 7, "OccupationName": "Unemployed"}
        ])

        return lookups