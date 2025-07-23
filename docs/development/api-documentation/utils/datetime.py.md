# DateTime Utilities Documentation

## Purpose

The `datetime.py` module provides flexible datetime parsing utilities for the ReViewPoint application. This module handles the complexity of parsing various ISO datetime string formats that may come from different sources (frontend, external APIs, database exports) and normalizes them to UTC timezone-aware datetime objects. The utility is essential for consistent datetime handling across the application's data processing pipeline.

## Architecture

The datetime utilities follow a defensive parsing strategy:

- **Flexible Input Handling**: Accepts multiple ISO datetime formats with various timezone representations
- **UTC Normalization**: All parsed datetimes are converted to UTC for consistency
- **Timezone Safety**: Handles both naive and timezone-aware input strings
- **Error Resilience**: Provides clear error messages for invalid formats
- **Type Safety**: Full type annotations for reliable datetime operations
- **Standard Compliance**: Uses Python's built-in `datetime.fromisoformat()` for parsing

## Core Function

### `parse_flexible_datetime(dt: str) -> datetime | None`

Parses ISO format datetime strings with flexible timezone handling and UTC normalization.

```python
from src.utils.datetime import parse_flexible_datetime

# Various input formats supported
formats = [
    "2024-01-15T14:30:00Z",              # ISO with Z suffix
    "2024-01-15T14:30:00+00:00",         # ISO with +00:00 offset
    "2024-01-15T14:30:00 00:00",         # Space-separated offset
    "2024-01-15T14:30:00",               # Naive datetime (assumes UTC)
    "2024-01-15 14:30:00",               # Space-separated naive
]

for dt_string in formats:
    parsed_dt = parse_flexible_datetime(dt_string)
    print(f"Input: {dt_string} -> UTC: {parsed_dt}")
```

**Return Value:**
- `datetime | None` - UTC timezone-aware datetime object or None for empty input
- All returned datetimes are guaranteed to have UTC timezone
- None is returned only for empty/falsy input strings

## Input Format Support

### Supported Formats

**UTC Timezone Indicators:**

1. **Z Suffix Format**: `"2024-01-15T14:30:00Z"`
   - Standard ISO format with Zulu time indicator
   - Automatically converted to `+00:00` format for parsing
   - Most common format from frontend JavaScript Date.toISOString()

2. **Offset Format**: `"2024-01-15T14:30:00+00:00"`
   - Standard ISO format with explicit UTC offset
   - Directly parseable by Python's fromisoformat()
   - Common format from REST APIs and databases

3. **Space-Separated Offset**: `"2024-01-15T14:30:00 00:00"`
   - Non-standard format with space before offset
   - Converted to `+00:00` format during preprocessing
   - Handles edge cases from certain data sources

4. **Naive DateTime**: `"2024-01-15T14:30:00"`
   - ISO format without timezone information
   - Assumed to be UTC for consistent handling
   - Common from databases without timezone storage

### Format Normalization Process

**Step-by-Step Processing:**

```python
def format_normalization_example(input_dt: str) -> str:
    """Demonstrate the format normalization process."""
    
    original = input_dt
    
    # Step 1: Replace Z with +00:00
    if input_dt.endswith("Z"):
        input_dt = input_dt.replace("Z", "+00:00")
        print(f"Z replacement: {original} -> {input_dt}")
    
    # Step 2: Handle space-separated offset
    if " " in input_dt and (input_dt.endswith(" 00:00") or input_dt.endswith(" 00:00:00")):
        input_dt = input_dt.replace(" ", "+", 1)  # Replace first space only
        print(f"Space normalization: {original} -> {input_dt}")
    
    return input_dt

# Examples
print(format_normalization_example("2024-01-15T14:30:00Z"))
# Output: Z replacement: 2024-01-15T14:30:00Z -> 2024-01-15T14:30:00+00:00

print(format_normalization_example("2024-01-15T14:30:00 00:00"))
# Output: Space normalization: 2024-01-15T14:30:00 00:00 -> 2024-01-15T14:30:00+00:00
```

## Timezone Handling

### UTC Conversion Strategy

**Automatic UTC Normalization:**

```python
def timezone_handling_examples():
    """Demonstrate timezone handling for different input types."""
    
    # Naive datetime - assumed UTC
    naive_dt = parse_flexible_datetime("2024-01-15T14:30:00")
    print(f"Naive -> UTC: {naive_dt}")  # 2024-01-15 14:30:00+00:00
    
    # Z suffix - converted to UTC
    z_dt = parse_flexible_datetime("2024-01-15T14:30:00Z")
    print(f"Z suffix -> UTC: {z_dt}")  # 2024-01-15 14:30:00+00:00
    
    # Explicit UTC offset - preserved
    utc_dt = parse_flexible_datetime("2024-01-15T14:30:00+00:00")
    print(f"UTC offset -> UTC: {utc_dt}")  # 2024-01-15 14:30:00+00:00
    
    # Non-UTC timezone - converted to UTC
    pst_dt = parse_flexible_datetime("2024-01-15T14:30:00-08:00")
    print(f"PST -> UTC: {pst_dt}")  # 2024-01-15 22:30:00+00:00
```

**Timezone Awareness Logic:**

1. **Naive DateTime Detection**: Check if `parsed.tzinfo is None`
2. **UTC Assignment**: Use `parsed.replace(tzinfo=UTC)` for naive datetimes
3. **Timezone Conversion**: Use `parsed.astimezone(UTC)` for timezone-aware datetimes
4. **Consistency Guarantee**: All outputs have UTC timezone information

### Edge Cases and Special Handling

**Space-Separated Offset Processing:**

```python
def handle_space_offset(dt_str: str) -> str:
    """Handle space-separated timezone offsets."""
    
    # Check for space-separated offset patterns
    space_patterns = [
        " 00:00",      # Standard format
        " 00:00:00",   # Extended format with seconds
        " +00:00",     # Already has plus sign
        " -00:00",     # Negative offset
    ]
    
    for pattern in space_patterns:
        if dt_str.endswith(pattern):
            # Replace first space with + for positive offset
            if not pattern.startswith(" +") and not pattern.startswith(" -"):
                return dt_str.replace(" ", "+", 1)
            else:
                # Already has sign, just remove space
                return dt_str.replace(" ", "", 1)
    
    return dt_str
```

## Error Handling

### Exception Management

**ValueError Handling with Context:**

```python
def safe_datetime_parsing(dt_str: str) -> datetime | None:
    """Safe datetime parsing with comprehensive error handling."""
    
    try:
        return parse_flexible_datetime(dt_str)
        
    except ValueError as e:
        # Log the specific error for debugging
        logger.error(f"DateTime parsing failed for input '{dt_str}': {e}")
        
        # Return None for invalid input
        return None
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error parsing datetime '{dt_str}': {e}")
        return None

# Usage examples
def process_datetime_input(user_input: str) -> str:
    """Process user datetime input with error handling."""
    
    parsed_dt = safe_datetime_parsing(user_input)
    
    if parsed_dt is None:
        return "Invalid datetime format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)."
    
    return f"Parsed datetime: {parsed_dt.isoformat()}"
```

**Error Message Enhancement:**

```python
# Original error: ValueError: Invalid datetime format: 2024-13-45T25:99:99
# Enhanced error provides context about what formats are expected

def validate_datetime_format(dt_str: str) -> tuple[bool, str]:
    """Validate datetime format and provide helpful error messages."""
    
    if not dt_str:
        return False, "DateTime string cannot be empty"
    
    try:
        parse_flexible_datetime(dt_str)
        return True, "Valid datetime format"
        
    except ValueError as e:
        supported_formats = [
            "2024-01-15T14:30:00Z",
            "2024-01-15T14:30:00+00:00",
            "2024-01-15T14:30:00",
            "2024-01-15 14:30:00"
        ]
        
        error_msg = (
            f"Invalid datetime format: {dt_str}\n"
            f"Original error: {e}\n"
            f"Supported formats: {', '.join(supported_formats)}"
        )
        
        return False, error_msg
```

## Usage Patterns

### API Request Processing

**Frontend to Backend DateTime Handling:**

```python
from src.utils.datetime import parse_flexible_datetime

async def process_api_request(request_data: dict) -> dict:
    """Process API request with flexible datetime parsing."""
    
    datetime_fields = ['created_at', 'updated_at', 'deadline', 'scheduled_time']
    
    for field in datetime_fields:
        if field in request_data and request_data[field]:
            try:
                # Parse flexible datetime from frontend
                parsed_dt = parse_flexible_datetime(request_data[field])
                
                if parsed_dt:
                    # Store as UTC datetime for database
                    request_data[field] = parsed_dt
                else:
                    # Remove empty datetime fields
                    request_data.pop(field, None)
                    
            except ValueError as e:
                raise ValidationError(f"Invalid {field} format: {e}")
    
    return request_data

# Example usage
frontend_data = {
    "title": "Important Task",
    "created_at": "2024-01-15T14:30:00Z",  # JavaScript Date.toISOString()
    "deadline": "2024-01-20T23:59:59+00:00",  # Explicit UTC
    "updated_at": ""  # Empty string - will be removed
}

processed_data = await process_api_request(frontend_data)
```

### Database Integration

**Model Field Processing:**

```python
from sqlalchemy import DateTime
from src.utils.datetime import parse_flexible_datetime

class BaseModel:
    """Base model with flexible datetime handling."""
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create model instance with datetime parsing."""
        
        # Parse datetime fields
        datetime_fields = ['created_at', 'updated_at', 'expires_at']
        
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = parse_flexible_datetime(data[field])
                except ValueError:
                    # Log warning and use None for invalid dates
                    logger.warning(f"Invalid datetime in field {field}: {data[field]}")
                    data[field] = None
        
        return cls(**data)

# Usage in repository layer
async def create_user_from_api(user_data: dict) -> User:
    """Create user with datetime field processing."""
    
    # Parse flexible datetime fields
    if 'last_login' in user_data:
        user_data['last_login'] = parse_flexible_datetime(user_data['last_login'])
    
    if 'account_expires' in user_data:
        user_data['account_expires'] = parse_flexible_datetime(user_data['account_expires'])
    
    return User(**user_data)
```

### Data Migration and Import

**CSV/JSON Import Processing:**

```python
import csv
from typing import Iterator

def import_datetime_data(csv_file: str) -> Iterator[dict]:
    """Import data with flexible datetime parsing."""
    
    datetime_columns = ['created_date', 'modified_date', 'publish_date']
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Process datetime columns
            for col in datetime_columns:
                if col in row and row[col]:
                    try:
                        # Handle various CSV datetime formats
                        parsed_dt = parse_flexible_datetime(row[col])
                        row[col] = parsed_dt.isoformat() if parsed_dt else None
                        
                    except ValueError:
                        # Log invalid datetime but continue processing
                        logger.warning(f"Invalid datetime in row {reader.line_num}, column {col}: {row[col]}")
                        row[col] = None
            
            yield row

# Usage
for record in import_datetime_data('export.csv'):
    await create_record(record)
```

### Testing and Validation

**Comprehensive Format Testing:**

```python
import pytest
from src.utils.datetime import parse_flexible_datetime

class TestFlexibleDateTimeParsing:
    """Test suite for flexible datetime parsing."""
    
    def test_iso_z_format(self):
        """Test ISO format with Z suffix."""
        
        dt_str = "2024-01-15T14:30:00Z"
        result = parse_flexible_datetime(dt_str)
        
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(None).total_seconds() == 0
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
    
    def test_utc_offset_format(self):
        """Test ISO format with UTC offset."""
        
        dt_str = "2024-01-15T14:30:00+00:00"
        result = parse_flexible_datetime(dt_str)
        
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(None).total_seconds() == 0
    
    def test_space_separated_offset(self):
        """Test space-separated offset format."""
        
        dt_str = "2024-01-15T14:30:00 00:00"
        result = parse_flexible_datetime(dt_str)
        
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(None).total_seconds() == 0
    
    def test_naive_datetime(self):
        """Test naive datetime (assumes UTC)."""
        
        dt_str = "2024-01-15T14:30:00"
        result = parse_flexible_datetime(dt_str)
        
        assert result is not None
        assert result.tzinfo is not None
        assert result.tzinfo.utcoffset(None).total_seconds() == 0
    
    def test_timezone_conversion(self):
        """Test conversion from non-UTC timezone."""
        
        # PST (UTC-8)
        dt_str = "2024-01-15T14:30:00-08:00"
        result = parse_flexible_datetime(dt_str)
        
        assert result is not None
        assert result.hour == 22  # 14 + 8 = 22 UTC
        assert result.tzinfo.utcoffset(None).total_seconds() == 0
    
    def test_empty_input(self):
        """Test empty input handling."""
        
        assert parse_flexible_datetime("") is None
        assert parse_flexible_datetime(None) is None
    
    def test_invalid_format(self):
        """Test invalid format error handling."""
        
        with pytest.raises(ValueError):
            parse_flexible_datetime("not-a-datetime")
        
        with pytest.raises(ValueError):
            parse_flexible_datetime("2024-13-45T25:99:99")
    
    @pytest.mark.parametrize("dt_str,expected_utc_hour", [
        ("2024-01-15T14:30:00Z", 14),
        ("2024-01-15T14:30:00+00:00", 14),
        ("2024-01-15T14:30:00-05:00", 19),  # EST to UTC
        ("2024-01-15T14:30:00+09:00", 5),   # JST to UTC
    ])
    def test_timezone_conversions(self, dt_str: str, expected_utc_hour: int):
        """Test various timezone conversions to UTC."""
        
        result = parse_flexible_datetime(dt_str)
        assert result.hour == expected_utc_hour
        assert result.tzinfo.utcoffset(None).total_seconds() == 0
```

## Performance Considerations

### Optimization Strategies

**Efficient String Processing:**

```python
def optimized_datetime_parsing(dt_str: str) -> datetime | None:
    """Optimized version with minimal string operations."""
    
    if not dt_str:
        return None
    
    # Single pass for format detection and normalization
    normalized_str = dt_str
    
    # Handle Z suffix (most common case first)
    if dt_str.endswith("Z"):
        normalized_str = dt_str[:-1] + "+00:00"
    
    # Handle space-separated offset (less common)
    elif " 00:00" in dt_str:
        if dt_str.endswith(" 00:00") or dt_str.endswith(" 00:00:00"):
            normalized_str = dt_str.replace(" ", "+", 1)
    
    try:
        parsed = datetime.fromisoformat(normalized_str)
        
        # Single timezone check and conversion
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        else:
            return parsed.astimezone(UTC) if parsed.tzinfo != UTC else parsed
            
    except ValueError as e:
        raise ValueError(f"Invalid datetime format: {dt_str}") from e
```

**Batch Processing:**

```python
def parse_datetime_batch(dt_strings: list[str]) -> list[datetime | None]:
    """Parse multiple datetime strings efficiently."""
    
    results = []
    
    for dt_str in dt_strings:
        try:
            parsed_dt = parse_flexible_datetime(dt_str)
            results.append(parsed_dt)
        except ValueError:
            # Log error but continue processing batch
            logger.warning(f"Failed to parse datetime in batch: {dt_str}")
            results.append(None)
    
    return results

# Usage for bulk data processing
datetime_strings = [
    "2024-01-15T14:30:00Z",
    "2024-01-16T15:45:00+00:00",
    "invalid-datetime",
    "2024-01-17T16:30:00"
]

parsed_datetimes = parse_datetime_batch(datetime_strings)
valid_datetimes = [dt for dt in parsed_datetimes if dt is not None]
```

## Best Practices

### Function Design

- **Single Responsibility**: Focus solely on datetime parsing and UTC conversion
- **Type Safety**: Clear type annotations for input and output
- **Error Transparency**: Let ValueError bubble up with enhanced context
- **Null Handling**: Explicit handling of empty/None input values

### Integration Guidelines

- **API Layer**: Use for processing all datetime inputs from external sources
- **Database Layer**: Apply before storing datetime values
- **Serialization**: Use for parsing datetime strings from JSON/CSV
- **Validation**: Integrate with form validation and schema validation

### Error Handling Strategy

- **Fail Fast**: Raise ValueError immediately for invalid formats
- **Context Preservation**: Include original input in error messages
- **Logging**: Log parsing failures for monitoring and debugging
- **Graceful Degradation**: Handle errors appropriately in higher-level functions

## Related Files

### Dependencies

- `datetime.UTC` - UTC timezone constant for timezone-aware operations
- `datetime.datetime` - Core datetime functionality and ISO parsing

### Integration Points

- `src.schemas.auth` - DateTime validation in authentication schemas
- `src.schemas.user` - User profile datetime fields
- `src.models.base` - BaseModel datetime field processing
- `src.api.v1` - API endpoint datetime parameter parsing

### Usage Context

- Request/response processing in API endpoints
- Database model field parsing and validation
- Data import/export datetime normalization
- Frontend-backend datetime synchronization

## Configuration

### Parsing Settings

```python
# DateTime parsing configuration
DATETIME_CONFIG = {
    "assume_utc_for_naive": True,  # Treat naive datetime as UTC
    "strict_iso_only": False,      # Allow flexible format variations
    "log_parsing_errors": True,    # Log all parsing failures
    "default_timezone": "UTC",     # Default timezone for naive datetimes
}

# Supported format patterns
SUPPORTED_PATTERNS = [
    "YYYY-MM-DDTHH:MM:SSZ",           # ISO with Z suffix
    "YYYY-MM-DDTHH:MM:SS+00:00",      # ISO with UTC offset
    "YYYY-MM-DDTHH:MM:SS 00:00",      # Space-separated offset
    "YYYY-MM-DDTHH:MM:SS",            # Naive (assumes UTC)
]
```

This datetime utility provides robust, flexible datetime parsing that handles the diverse datetime formats commonly encountered in web applications, ensuring consistent UTC timezone handling throughout the ReViewPoint application.
