# ==============================================================================
# DATATHON 2026: Explainable Crime Intelligence & Case-Linking Platform
# Abstract Base Class for Table Generators
# File: generator/generators/base_generator.py
# ==============================================================================

from abc import ABC, abstractmethod
import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger("DatathonDataGen.Generators")

class BaseGenerator(ABC):
    """
    Abstract Base Class enforced across all domain table generators.
    Guarantees consistent configuration reading, DataFrame formatting, and schema safety.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data: pd.DataFrame = pd.DataFrame()

    @abstractmethod
    def generate(self, parent_data: Dict[str, pd.DataFrame] = None) -> pd.DataFrame:
        """
        Generates tabular data. 
        Accepts previously generated parent tables to maintain foreign key integrity.
        """
        pass

    def validate(self) -> bool:
        """Basic validation to verify non-empty DataFrame generation."""
        if self.data.empty:
            logger.warning(f"Validation Warning: Generator {self.__class__.__name__} produced an empty DataFrame!")
            return False
        return True