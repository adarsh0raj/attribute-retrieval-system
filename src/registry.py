"""
Registry for managing attributes.
"""
from typing import Dict, Optional, Type, TypeVar, Generic, Any

from .attribute import Attribute
from .enums import Status

T = TypeVar('T')

class AttributeRegistry:
    """
    Registry for managing attributes in the system.
    
    This implements the Registry design pattern to provide
    global access to attribute instances.
    """
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AttributeRegistry, cls).__new__(cls)
            cls._instance._attributes = {}
        return cls._instance
    
    def register_attribute(self, attribute: Attribute) -> None:
        """
        Register an attribute in the registry.
        
        Args:
            attribute: The attribute to register
        """
        self._attributes[attribute.name] = attribute
        
    def get_attribute(self, name: str) -> Optional[Attribute]:
        """
        Get an attribute by name.
        
        Args:
            name: Name of the attribute
            
        Returns:
            Attribute: The attribute instance, or None if not found
        """
        return self._attributes.get(name)
        
    def list_attributes(self) -> Dict[str, Attribute]:
        """
        List all registered attributes.
        
        Returns:
            Dict[str, Attribute]: Dictionary of all registered attributes
        """
        return self._attributes.copy()
        
    def process_logfile(self, logfile_path: str) -> None:
        """
        Process a log file for all registered attributes.
        
        Args:
            logfile_path: Path to the log file
        """
        for attribute in self._attributes.values():
            attribute.process_logfile(logfile_path)
            
    def evaluate_all(self, previous_values: Dict[str, Any] = None) -> Dict[str, Status]:
        """
        Evaluate all registered attributes.
        
        Args:
            previous_values: Dictionary of previous values, keyed by attribute name
            
        Returns:
            Dict[str, Status]: Dictionary of evaluation results
        """
        results = {}
        for name, attribute in self._attributes.items():
            prev_value = None
            if previous_values and name in previous_values:
                prev_value = previous_values[name]
            results[name] = attribute.evaluate(prev_value)
        return results
        
    def to_dict(self) -> Dict[str, Dict]:
        """
        Convert all attributes to dictionaries for database storage.
        
        Returns:
            Dict[str, Dict]: Dictionary of attribute dictionaries
        """
        return {name: attr.to_dict() for name, attr in self._attributes.items()}
        

# Global registry instance for easy access
Registry = AttributeRegistry()
