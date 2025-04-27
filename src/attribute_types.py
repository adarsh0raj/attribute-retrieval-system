"""
Concrete implementations of attribute types.
"""
import json
from typing import Dict, Any, TypeVar, Callable, List

from .attribute import Attribute, EvaluatorFunc
from .enums import CriticalityLevel, Status
from .log_processor import LogProcessor

T = TypeVar('T')

class NumericAttribute(Attribute[float]):
    """Attribute for numeric values like PnL, RAM usage, etc."""
    
    def process_logfile(self, logfile_path: str) -> None:
        """
        Process a log file to extract the attribute value.
        
        Args:
            logfile_path: Path to the log file
        """
        # Default implementation using the last occurrence pattern
        matches = list(LogProcessor.process_log(logfile_path, self.name.upper()))
        if matches:
            last_match = matches[-1]
            try:
                value = float(last_match.split(":")[-1].strip())
                self.fill_value(value)
            except (ValueError, IndexError):
                pass
                
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        # For simplicity, storing the name and criticality type
        return {
            'name': self.name,
            'type': 'numeric',
            'criticality': self.criticality.name,
            'value': self.value
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'NumericAttribute':
        """Create from dictionary loaded from database."""
        criticality = CriticalityLevel[data['criticality']]
        
        # Simple defaault evaluator function
        def default_evaluator(last_val, current_val):
            return Status.OK
            
        instance = cls(
            name=data['name'],
            criticality=criticality,
            evaluator=default_evaluator
        )
        
        if 'value' in data and data['value'] is not None:
            instance.fill_value(float(data['value']))
            
        return instance


class CountAttribute(Attribute[int]):
    """Attribute for counting occurrences, like warning counts."""
    
    def process_logfile(self, logfile_path: str) -> None:
        """
        Process a log file to count occurrences of a pattern.
        
        Args:
            logfile_path: Path to the log file
        """
        count = len(list(LogProcessor.process_log(logfile_path, self.name.upper())))
        self.fill_value(count)
                
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'name': self.name,
            'type': 'count',
            'criticality': self.criticality.name,
            'value': self.value
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'CountAttribute':
        """Create from dictionary loaded from database."""
        criticality = CriticalityLevel[data['criticality']]
        
        # Default evaluator
        def default_evaluator(last_val, current_val):
            return Status.OK
        
        instance = cls(
            name=data['name'],
            criticality=criticality,
            evaluator=default_evaluator
        )
        
        if 'value' in data and data['value'] is not None:
            instance.fill_value(int(data['value']))
            
        return instance


class AccumulatorAttribute(Attribute[float]):
    """Attribute for accumulating values, like total sleep time."""
    
    def __init__(
        self, 
        name: str, 
        criticality: CriticalityLevel, 
        evaluator: EvaluatorFunc,
        extractor: Callable[[str], float] = lambda x: float(x.split(":")[-1].strip())
    ):
        super().__init__(name, criticality, evaluator)
        self._extractor = extractor
        
    def process_logfile(self, logfile_path: str) -> None:
        """
        Process a log file to accumulate values.
        
        Args:
            logfile_path: Path to the log file
        """
        total = 0.0
        for line in LogProcessor.process_log(logfile_path, self.name.upper()):
            try:
                value = self._extractor(line)
                total += value
            except (ValueError, IndexError):
                continue
                
        self.fill_value(total)
                
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        return {
            'name': self.name,
            'type': 'accumulator',
            'criticality': self.criticality.name,
            'value': self.value
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'AccumulatorAttribute':
        """Create from dictionary loaded from database."""
        criticality = CriticalityLevel[data['criticality']]
        
        # Default evaluator and extractor
        def default_evaluator(last_val, current_val):
            return Status.OK
            
        def default_extractor(line):
            return float(line.split(":")[-1].strip())
        
        instance = cls(
            name=data['name'],
            criticality=criticality,
            evaluator=default_evaluator,
            extractor=default_extractor
        )
        
        if 'value' in data and data['value'] is not None:
            instance.fill_value(float(data['value']))
            
        return instance


class ComplexAttribute(Attribute[Dict[str, Any]]):
    """Attribute for complex metrics that require detailed processing."""
    
    def __init__(
        self, 
        name: str, 
        criticality: CriticalityLevel, 
        evaluator: EvaluatorFunc,
        processor: Callable[[List[str]], Dict[str, Any]]
    ):
        super().__init__(name, criticality, evaluator)
        self._processor = processor
        
    def process_logfile(self, logfile_path: str) -> None:
        """
        Process a log file using complex processing logic.
        
        Args:
            logfile_path: Path to the log file
        """
        lines = list(LogProcessor.process_log(logfile_path, self.name.upper()))
        if lines:
            result = self._processor(lines)
            self.fill_value(result)
                
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage."""
        # Convert complex dictionary to JSON string for storage
        value_json = json.dumps(self.value) if self.value is not None else None
        
        return {
            'name': self.name,
            'type': 'complex',
            'criticality': self.criticality.name,
            'value': value_json
        }
        
    @classmethod
    def from_dict(cls, data: dict) -> 'ComplexAttribute':
        """Create from dictionary loaded from database."""
        criticality = CriticalityLevel[data['criticality']]
        
        # Default evaluator and processor
        def default_evaluator(last_val, current_val):
            return Status.OK
            
        def default_processor(lines):
            return {'value': len(lines)}
        
        instance = cls(
            name=data['name'],
            criticality=criticality,
            evaluator=default_evaluator,
            processor=default_processor
        )
        
        if 'value' in data and data['value'] is not None:
            instance.fill_value(json.loads(data['value']))
            
        return instance
