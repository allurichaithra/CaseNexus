# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Synthetic Narrative & BriefFacts Generator
# File: generator/ml_patterns/narrative_templates.py
# ==============================================================================

import random
from typing import Dict, Any, List

class NarrativeTemplateEngine:
    """
    Generates realistic police FIR 'BriefFacts' narratives incorporating distinct 
    Modus Operandi (MO) patterns, weapon usage, vehicle details, and stolen property.
    """

    MO_PATTERNS = {
        "NIGHT_BURGLARY_CROWBAR": {
            "templates": [
                "On {date} between {time_from} and {time_to}, unknown culprit(s) gained entry into the closed house located at {location} by breaking open the main door lock using a {tool}. The culprit(s) ransacked the wooden almirah and committed theft of gold ornaments weighing approximately {weight} grams and cash amounting to Rs. {cash}.",
                "Complainant reported that on {date} night, unknown persons gained illegal entry into {location} by cutting the window grills using {tool}. Culprits stole gold coins and cash worth Rs. {cash} from the locker."
            ],
            "tools": ["iron crowbar", "heavy cutter", "iron rod"],
            "stolen_items": ["gold chain and bangles", "gold mangalsutra", "silver articles and cash"]
        },
        "CHAIN_SNATCHING_BIKE": {
            "templates": [
                "On {date} around {time_from}, while the victim was walking near {location}, two unknown male accused persons aged around 20-25 years came riding on a {vehicle} without registration plate. The pillion rider snatched a gold chain weighing {weight} grams from the victim's neck and sped away toward the main road.",
                "While complainant was returning home near {location} on {date} at {time_from}, two unidentified youths on a {vehicle} approached under the pretext of asking directions and forcibly snatched her gold mangalsutra."
            ],
            "vehicles": ["black Pulsar motorcycle", "stolen Yamaha FZ bike", "red Honda Activa scooter"],
            "tools": ["none"]
        },
        "CYBER_JOB_SCAM": {
            "templates": [
                "The complainant was approached via Telegram by unknown fraudsters offering part-time YouTube video liking jobs. After paying an initial registration fee, the victim was lured into depositing a total sum of Rs. {cash} across multiple bank accounts under the pretext of high-yield investment returns.",
                "Unidentified online fraudsters contacted the victim on WhatsApp offering work-from-home tasks. Victim was induced to transfer Rs. {cash} via UPI transfers before realizing the fraud."
            ],
            "tools": ["Telegram app", "WhatsApp / UPI handles"],
            "vehicles": ["N/A"]
        }
    }

    LOCATIONS = [
        "1st Main Road, Indiranagar", "Near Government School, Hebbal",
        "Opposite Bus Stand, Cross Road", "Near Sri Rama Temple Road",
        "Outer Ring Road, Near Petrol Bunk", "Residential Layout, 3rd Stage"
    ]

    @classmethod
    def generate_narrative(cls, mo_type: str, date_str: str, custom_params: Dict[str, Any] = None) -> str:
        """Generates a contextual BriefFacts narrative string based on an MO type."""
        pattern = cls.MO_PATTERNS.get(mo_type, cls.MO_PATTERNS["NIGHT_BURGLARY_CROWBAR"])
        template = random.choice(pattern["templates"])
        
        weight = random.choice([15, 25, 40, 60, 80])
        cash = random.choice([15000, 35000, 50000, 120000, 250000])
        tool = random.choice(pattern.get("tools", ["iron rod"]))
        vehicle = random.choice(pattern.get("vehicles", ["motorcycle"]))
        location = random.choice(cls.LOCATIONS)

        narrative = template.format(
            date=date_str,
            time_from=f"{random.randint(1, 5):02d}:00 AM" if "NIGHT" in mo_type else f"{random.randint(10, 19):02d}:30 PM",
            time_to=f"{random.randint(6, 8):02d}:00 AM",
            location=location,
            tool=tool,
            weight=weight,
            cash=cash,
            vehicle=vehicle
        )
        return narrative