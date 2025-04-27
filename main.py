"""
Main Demo script with CLI for the attributes storage and retrieval system.
"""
import os
import argparse
import datetime
from typing import Dict, Any, List, Optional

from src.enums import Status, CriticalityLevel
from src.attribute_types import NumericAttribute, CountAttribute, AccumulatorAttribute, ComplexAttribute
from src.registry import Registry
from src.database import DatabaseManager
from src.log_processor import LogProcessor


# Define evaluator functions
def evaluate_status_code(last_val: Optional[int], current_val: Optional[int]) -> Status:
    """Evaluate HTTP status code."""
    if current_val is None:
        return Status.OK
    
    if current_val >= 500:
        return Status.ERROR
    elif current_val >= 400:
        return Status.WARNING
    return Status.OK


def evaluate_latency(last_val: Optional[float], current_val: Optional[float]) -> Status:
    """Evaluate latency."""
    if current_val is None:
        return Status.OK
    
    # Thresholds in ms
    if current_val > 1000:  # 1s
        return Status.ERROR
    elif current_val > 300:  # 300ms
        return Status.WARNING
    return Status.OK


def evaluate_error_count(last_val: Optional[int], current_val: Optional[int]) -> Status:
    """Evaluate error count."""
    if current_val is None:
        return Status.OK
    
    if current_val > 5:
        return Status.ERROR
    elif current_val > 2:
        return Status.WARNING
    return Status.OK


def evaluate_memory(last_val: Optional[float], current_val: Optional[float]) -> Status:
    """Evaluate memory usage (in MB)."""
    if current_val is None:
        return Status.OK
    
    if current_val > 1024:  # 1GB
        return Status.ERROR
    elif current_val > 512:  # 512MB
        return Status.WARNING
    return Status.OK


def evaluate_accumulated_time(last_val: Optional[float], current_val: Optional[float]) -> Status:
    """Evaluate accumulated time (in seconds)."""
    if current_val is None:
        return Status.OK
    
    if current_val > 20.0:  # More than 20 seconds total
        return Status.ERROR
    elif current_val > 10.0:  # More than 10 seconds total
        return Status.WARNING
    return Status.OK


def calculate_percentiles(lines: List[str]) -> Dict[str, float]:
    """Calculate percentiles from log lines."""
    values = []
    for line in lines:
        try:
            value = float(line.split(":")[-1].strip())
            values.append(value)
        except (ValueError, IndexError):
            continue
            
    values.sort()
    n = len(values)
    
    if n == 0:
        return {'min': 0, 'p50': 0, 'p90': 0, 'p99': 0, 'max': 0}
        
    return {
        'min': values[0],
        'p50': values[int(n * 0.5)] if n > 0 else 0,
        'p90': values[int(n * 0.9)] if n > 1 else values[0],
        'p99': values[int(n * 0.99)] if n > 2 else values[0],
        'max': values[-1],
        'count': n,
        'avg': sum(values) / n
    }


def create_registry(config: Dict[str, Any]) -> None:
    """Create and configure the attribute registry."""
    # Clear existing registry
    Registry._attributes = {}
    
    # HTTP status codes
    status_attr = NumericAttribute(
        name="STATUS",
        criticality=CriticalityLevel.CRITICAL,
        evaluator=evaluate_status_code
    )
    Registry.register_attribute(status_attr)
    
    # Latency 
    latency_attr = NumericAttribute(
        name="LATENCY",
        criticality=CriticalityLevel.RELAXED,
        evaluator=evaluate_latency
    )
    Registry.register_attribute(latency_attr)
    
    # Memory usage
    memory_attr = NumericAttribute(
        name="MEMORY",
        criticality=CriticalityLevel.RELAXED,
        evaluator=evaluate_memory
    )
    Registry.register_attribute(memory_attr)
    
    # Error and warning counts
    error_attr = CountAttribute(
        name="ERROR",
        criticality=CriticalityLevel.CRITICAL,
        evaluator=evaluate_error_count
    )
    Registry.register_attribute(error_attr)
    
    warning_attr = CountAttribute(
        name="WARNING",
        criticality=CriticalityLevel.RELAXED,
        evaluator=lambda last, current: Status.OK
    )
    Registry.register_attribute(warning_attr)
    
    # Accumulator attribute for processing time
    process_time_attr = AccumulatorAttribute(
        name="PROCESS_TIME",
        criticality=CriticalityLevel.RELAXED,
        evaluator=evaluate_accumulated_time,
        extractor=lambda line: float(line.split(":")[-1].strip())
    )
    Registry.register_attribute(process_time_attr)
    
    # Complex attribute for response time percentiles
    resp_time_attr = ComplexAttribute(
        name="RESPONSE_TIME",
        criticality=CriticalityLevel.CRITICAL,
        evaluator=lambda last, current: Status.OK if current is None else (
            Status.ERROR if current.get('p99', 0) > 1000 else 
            Status.WARNING if current.get('p95', 0) > 500 else
            Status.OK
        ),
        processor=calculate_percentiles
    )
    Registry.register_attribute(resp_time_attr)
    
    print(f"Registered {len(Registry._attributes)} attributes")


def process_logfile(logfile: str) -> None:
    """Process a log file and print results."""
    if not os.path.exists(logfile):
        print(f"Error: Log file {logfile} not found")
        return
        
    print(f"Processing log file: {logfile}")
    LogProcessor.clear_cache()  # Clear cache to ensure fresh processing
    
    try:
        Registry.process_logfile(logfile)
        print("\nExtracted Metrics:")
        for name, attr in Registry._attributes.items():
            print(f"  {name}: {attr.value}")
            
        print("\nEvaluation Results:")
        results = Registry.evaluate_all()
        for name, status in results.items():
            status_symbol = "✅" if status == Status.OK else "⚠️" if status == Status.WARNING else "🚨"
            print(f"  {status_symbol} {name}: {status}")
            
    except Exception as e:
        print(f"Error processing log file: {e}")


# Placeholder Code For Saving To Database
def save_to_database(db_name: str) -> None:
    """Save extracted metrics to database."""
    try:
        db = DatabaseManager(f"sqlite:///{db_name}")
        
        # Store metadata
        db.store_attribute_metadata(Registry.to_dict())
        
        # Store values
        general_id = db.insert_into_general_table(
            timestamp=datetime.datetime.now().isoformat()
        )
        
        # Build dynamic kwargs from attributes
        kwargs = {}
        for name, attr in Registry._attributes.items():
            if isinstance(attr, ComplexAttribute) and attr.value:
                # For complex attributes, store p50 (median) value 
                kwargs[attr.column_name] = attr.value.get('p50', None)
            else:
                kwargs[attr.column_name] = attr.value
        
        # Insert into logs table
        db.insert_into_log_table(fk=general_id, **kwargs)
        print(f"Metrics stored in database: {db_name}")
        
    except Exception as e:
        print(f"Error saving to database: {e}")


def print_help() -> None:
    """Print help information."""
    print("\nAttributes Storage and Retrieval Demo")
    print("====================================")
    print("Commands:")
    print("  process <logfile>     - Process a log file and extract metrics")
    print("  save <db_name>        - Save current metrics to database")
    print("  help                  - Show this help information")
    print("  exit                  - Exit the program")


def main() -> None:
    """Main function for CLI demo."""
    parser = argparse.ArgumentParser(description="Attributes Storage and Retrieval Demo")
    parser.add_argument("--config", help="Configuration file path", default=None)
    parser.add_argument("--logfile", help="Log file to process", default=None)
    args = parser.parse_args()
    
    print("Attributes Storage and Retrieval Demo")
    print("====================================")
    
    # Create and configure the registry
    create_registry(config={})
    
    # If log file provided as argument, process it
    if args.logfile:
        process_logfile(args.logfile)
    else:
        # Interactive mode
        print_help()
        while True:
            try:
                command = input("\nCommand> ").strip()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "exit":
                    break
                elif cmd == "help":
                    print_help()
                elif cmd == "process":
                    if len(parts) < 2:
                        print("Error: Missing log file path")
                        continue
                    process_logfile(parts[1])
                elif cmd == "save":
                    if len(parts) < 2:
                        print("Error: Missing database name")
                        continue
                    save_to_database(parts[1])
                else:
                    print(f"Unknown command: {cmd}")
                    print_help()
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    print("Demo completed")


if __name__ == "__main__":
    main()
