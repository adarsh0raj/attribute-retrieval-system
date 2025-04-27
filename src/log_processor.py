"""
Utilities for log processing.
"""
from typing import List, Iterator
import re

def grep(pattern: str, logfile_path: str) -> List[str]:
    """
    Find all lines in log file that match a pattern.
    
    Args:
        pattern: Regular expression pattern to match
        logfile_path: Path to the log file
    
    Returns:
        List[str]: List of matching lines
    """
    matches = []
    with open(logfile_path, 'r') as file:
        for line in file:
            if re.search(pattern, line, re.IGNORECASE):
                matches.append(line.strip())
    return matches

class LogProcessor:
    """
    Class for efficiently processing log files.
    
    This class implements a cache to avoid re-reading a log file multiple times.
    """
    
    _file_cache = {}  # Class-level cache for log file contents
    
    @classmethod
    def process_log(cls, logfile_path: str, pattern: str = None) -> Iterator[str]:
        """
        Process a log file and yield matching lines.
        
        Args:
            logfile_path: Path to the log file
            pattern: Optional regular expression to filter lines
            
        Yields:
            str: Each matching line in the log file
        """
        # Cache the file content if not already cached
        if logfile_path not in cls._file_cache:
            with open(logfile_path, 'r') as file:
                cls._file_cache[logfile_path] = file.readlines()
                
        # Return lines matching the pattern (or all if no pattern)
        for line in cls._file_cache[logfile_path]:
            if pattern is None or re.search(pattern, line, re.IGNORECASE):
                yield line.strip()
    
    @classmethod
    def clear_cache(cls, logfile_path: str = None) -> None:
        """
        Clear the log file cache.
        
        Args:
            logfile_path: Path to specific log file to clear from cache,
                          or None to clear all cache
        """
        if logfile_path:
            if logfile_path in cls._file_cache:
                del cls._file_cache[logfile_path]
        else:
            cls._file_cache.clear()
