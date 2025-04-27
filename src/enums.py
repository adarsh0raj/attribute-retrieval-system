"""
Enumerations for the attribute storage and retrieval system.
"""
from enum import Enum, auto

class Status(Enum):
    """Status returned by evaluator functions."""
    OK = auto()
    WARNING = auto()
    ERROR = auto()

class CriticalityLevel(Enum):
    """Criticality level of an attribute."""
    CRITICAL = auto()  # Evaluation Failure will return ERROR
    RELAXED = auto()   # Evaluation Failure will return WARNING
