# Python OOPs: Attributes Storage and Retrieval System

A log parsing and metrics storage/retrieval system for high-frequency trading (HFT) environments using advanced Python OOP principles.

## Project Overview

This project implements a robust system for log parsing and metrics storage/retrieval designed for monitoring high-frequency trading environments but applicable to any log-based metrics collection scenario. It showcases modern Python OOP principles including abstract classes, inheritance, generics, and design patterns.

## Project Structure

```
python-attr-storage/
│
├── src/
│   ├── __init__.py       # Package exports
│   ├── enums.py          # Status and CriticalityLevel enums
│   ├── attribute.py      # Base Attribute abstract class
│   ├── attribute_types.py # Concrete attribute implementations
│   ├── log_processor.py  # Utility for efficient log processing
│   ├── registry.py       # Registry for managing attributes
│   └── database.py       # Database abstraction layer
│
├── main.py               # Interactive demo with CLI
├── external_sample.log   # Sample log file for testing
└── README.md             # This file
```

## Dependencies

This project only uses standard Python libraries, so no additional packages are required. Just make sure you have Python 3.6+ installed.

## Key Components

### 1. Attribute System
- Abstract base class `Attribute[T]` with generic type parameter
- Concrete implementations:
  - `NumericAttribute`: For numeric values (PnL, RAM usage)
  - `CountAttribute`: For counting occurrences (warnings, errors)
  - `AccumulatorAttribute`: For accumulating values (sleep time)
  - `ComplexAttribute`: For complex metrics (latency quartiles)

### 2. Log Processing
- Efficient log processing with caching
- Pattern matching and value extraction
- Support for different types of log formats

### 3. Evaluation System
- Customizable evaluator functions for each attribute
- Support for criticality levels (CRITICAL, RELAXED)
- Status results (OK, WARNING, ERROR)

### 4. Storage System
- Database abstraction layer
- Support for metadata persistence
- Data retrieval capabilities

### 5. User Interface
- Interactive CLI demo application
- Command-line argument support
- Comprehensive error handling

## OOP Design Features

### Abstract Classes and Inheritance
- `Attribute` abstract base class
- Concrete attribute type hierarchies

### Generics
- Type variables for type-safe attributes (`T` in `Attribute[T]`)
- Generic method implementations

### Encapsulation
- Protected attributes with property access
- Clear separation of concerns

### Design Patterns
- **Registry Pattern**: Global access to attribute instances
- **Strategy Pattern**: Customizable evaluator functions
- **Singleton Pattern**: Registry implementation
- **Factory Methods**: Creating attributes from database records

## Running the Demo

### Interactive CLI
```bash
python main.py
```
Provides a command-line interface for interactive processing and database operations with the following commands:
- `process <logfile>` - Process a log file and extract metrics
- `save <db_name>` - Save current metrics to database
- `help` - Show help information
- `exit` - Exit the program

### Direct Log Processing
```bash
python main.py --logfile external_sample.log
```
Processes the specified log file and shows extracted metrics and evaluation results.

## Example Use Case

The system successfully processes a sample log file, extracts metrics, stores them in a database, and evaluates them against previous values. It demonstrates how monitoring systems can use this framework to detect anomalous conditions in trading systems.

For example, when processing the included `external_sample.log` file:
1. It extracts error counts, warning counts, and response times
2. It evaluates these metrics against defined thresholds
3. It detects when error counts exceed critical thresholds
4. It provides status indicators (✅, ⚠️, 🚨) for quick assessment

## Extending the System

To add a new attribute type:

1. Create a new class extending `Attribute[T]`
2. Implement the required abstract methods
3. Register instances in the registry
4. Use in your application

For example:

```python
class BooleanAttribute(Attribute[bool]):
    # Implement abstract methods...
    pass
```

## Conclusion

This project successfully demonstrates how Python's OOP features can be leveraged to create a modular, extensible system for log processing and metrics extraction. The design emphasizes reusability, type safety, and clear separation of concerns.
