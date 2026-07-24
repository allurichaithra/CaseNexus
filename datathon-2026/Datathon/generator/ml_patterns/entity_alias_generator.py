# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Repeat Accused & Entity Alias Synthetic Variation Generator
# File: generator/ml_patterns/entity_alias_generator.py
# ==============================================================================

import random
from typing import Dict, Any, List

class EntityAliasGenerator:
    """
    Generates synthetic alias variations for accused persons across multiple FIRs
    to simulate real-world data entry noise (e.g., typos, age drift, structural variants).
    """

    TYPO_MAP = {
        'a': ['e', 's'], 'i': ['e', 'y'], 'u': ['oo', 'v'],
        'sh': ['s'], 'k': ['ck', 'q'], 'th': ['t']
    }

    @classmethod
    def create_accused_aliases(cls, base_accused: Dict[str, Any], num_aliases: int = 3) -> List[Dict[str, Any]]:
        """
        Takes a ground-truth offender record and generates variant representations.
        
        Rule Enforcement:
        - Gender is preserved.
        - Age drifts within a realistic window (±1 to 3 years).
        - Religion/Caste are NEVER generated or passed to matching functions.
        """
        aliases = []
        base_name = base_accused["AccusedName"]
        base_age = base_accused.get("AgeYear", 28)
        
        name_parts = base_name.split()
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        for i in range(num_aliases):
            mutation_type = random.choice(["PHONETIC", "TYPO", "NAME_SWAP", "INITIALS", "EXACT"])
            
            if mutation_type == "PHONETIC":
                variant_first = first_name.replace("a", "e").replace("i", "ee")
                variant_name = f"{variant_first} {last_name}".strip()
            elif mutation_type == "TYPO":
                # Introduce a random letter typo
                variant_name = f"{first_name} {last_name}a".strip() if last_name else f"{first_name}h"
            elif mutation_type == "NAME_SWAP" and last_name:
                variant_name = f"{last_name} {first_name}"
            elif mutation_type == "INITIALS" and last_name:
                variant_name = f"{first_name[0]}. {last_name}"
            else:
                variant_name = base_name

            # Introduce realistic age drift across years
            age_drift = random.choice([-2, -1, 0, 1, 2, 3])
            
            alias_record = {
                "AccusedName": variant_name,
                "AgeYear": max(18, base_age + age_drift),
                "GenderID": base_accused["GenderID"], # Preserved
                "IsGroundTruthRepeat": True,
                "CanonicalPersonID": base_accused["PersonID"] # Ground truth key for validation
            }
            aliases.append(alias_record)

        return aliases