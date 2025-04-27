"""
Abstract base class for attributes in the system.
"""
from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar, Optional

from .enums import Status, CriticalityLevel

T = TypeVar('T')

EvaluatorFunc = Callable[[Optional[T], T], Status]

class Attribute(Generic[T], ABC):
    """
    Abstract base class for attributes in the system.
    
    An attribute represents a metric which can be:
    - Extracted from logs
    - Stored in a database
    - Evaluated for monitoring
    """
    
    def __init__(
        self, 
        name: str, 
        criticality: CriticalityLevel, 
        evaluator: EvaluatorFunc
    ):
        self.name = name
        self.criticality = criticality
        self._evaluator = evaluator
        self._value: Optional[T] = None
        
    @property
    def value(self) -> Optional[T]:
        """Get the current value of the attribute."""
        return self._value
        
    @property
    def column_name(self) -> str:
        """Get the SQL column name for this attribute."""
        return self.name.lower().replace(' ', '_')
    
    def fill_value(self, value: T) -> None:
        """Set the value of the attribute."""
        self._value = value
    
    def evaluate(self, previous_value: Optional[T] = None) -> Status:
        """
        Evaluate the attribute against its previous value.
        
        Returns:
            Status: Result of evaluation (OK, WARNING, ERROR)
        """
        result = self._evaluator(previous_value, self._value)
        
        # If evaluation failed and criticality is CRITICAL, return ERROR
        if result != Status.OK:
            if self.criticality == CriticalityLevel.CRITICAL:
                return Status.ERROR
            else:
                return Status.WARNING
                
        return Status.OK
    
    @abstractmethod
    def process_logfile(self, logfile_path: str) -> None:
        """
        Process a log file to extract the attribute value.
        
        Args:
            logfile_path: Path to the log file
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert the attribute to a dictionary for database storage.
        
        Returns:
            dict: Dictionary representation of the attribute
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'Attribute[T]':
        """
        Create an attribute from a dictionary (loaded from database).
        
        Args:
            data: Dictionary with attribute data
            
        Returns:
            Attribute: Reconstructed attribute instance
        """
        pass
