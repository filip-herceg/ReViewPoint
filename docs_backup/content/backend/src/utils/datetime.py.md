# `utils/datetime.py`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | Utilities                                                          |
| **Responsibility** | Date and time handling utilities with timezone awareness           |
| **Status**         | 🟢 Done                                                            |

## 1. Purpose

Provides comprehensive date and time utilities for the ReViewPoint platform, ensuring consistent timezone handling, formatting, and date arithmetic across the application.

## 2. Public API

| Symbol       | Type     | Description            |
| ------------ | -------- | ---------------------- |
| `utc_now` | Function | Get current UTC timestamp |
| `format_datetime` | Function | Format datetime for display |
| `parse_datetime` | Function | Parse string to datetime object |
| `timezone_aware` | Function | Convert naive datetime to timezone-aware |
| `days_ago` | Function | Calculate date N days in the past |
| `date_range` | Function | Generate date range iterator |
| `business_days` | Function | Calculate business days between dates |

## 3. Core Functions

### UTC Timestamp Management
```python
def utc_now() -> datetime:
    """Get current UTC timestamp with timezone info"""
    return datetime.now(timezone.utc)

def to_utc(dt: datetime) -> datetime:
    """Convert any datetime to UTC"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
```

### Formatting and Display
```python
def format_datetime(
    dt: datetime, 
    format_type: str = "iso",
    timezone: Optional[str] = None
) -> str:
    """Format datetime for various display needs"""
    # Supports: iso, human, short, long formats
    
def relative_time(dt: datetime) -> str:
    """Human-readable relative time (e.g., '2 hours ago')"""
```

### Parsing and Validation
```python
def parse_datetime(
    date_string: str,
    formats: Optional[List[str]] = None
) -> datetime:
    """Parse string to datetime with multiple format support"""
    
def validate_date_range(start: datetime, end: datetime) -> bool:
    """Validate that date range is logical"""
```

## 4. Usage Examples

### Basic Operations
```python
from backend.utils.datetime import utc_now, format_datetime

# Get current time
now = utc_now()

# Format for API response
formatted = format_datetime(now, "iso")  # "2025-01-15T10:30:00Z"

# Format for display
display = format_datetime(now, "human")  # "January 15, 2025 at 10:30 AM"
```

### Date Arithmetic
```python
from backend.utils.datetime import days_ago, business_days

# Get date 7 days ago
week_ago = days_ago(7)

# Calculate business days between dates
work_days = business_days(start_date, end_date)
```

### Timezone Handling
```python
from backend.utils.datetime import timezone_aware, to_user_timezone

# Convert naive datetime to UTC
utc_dt = timezone_aware(naive_datetime, "UTC")

# Convert to user's timezone
user_dt = to_user_timezone(utc_dt, "America/New_York")
```

## 5. Timezone Support

### Default Behavior
- All internal operations use UTC
- Database stores all timestamps in UTC
- API responses include timezone information
- User preferences control display timezone

### Supported Timezones
- Full pytz timezone database support
- Common timezone aliases
- Automatic DST handling
- Validation of timezone names

## 6. Date Range Operations

### Range Generation
```python
def date_range(
    start: datetime,
    end: datetime,
    step: timedelta = timedelta(days=1)
) -> Iterator[datetime]:
    """Generate datetime range with custom step"""
    
def month_range(start: datetime, months: int) -> List[datetime]:
    """Generate monthly date points"""
```

### Business Logic
```python
def is_business_day(dt: datetime) -> bool:
    """Check if date is a business day"""
    
def next_business_day(dt: datetime) -> datetime:
    """Get next business day"""
    
def business_hours_between(
    start: datetime, 
    end: datetime,
    business_start: time = time(9, 0),
    business_end: time = time(17, 0)
) -> float:
    """Calculate business hours between two datetimes"""
```

## 7. Performance Optimizations

### Caching
- Timezone object caching
- Parsed format caching
- Common calculation memoization

### Efficient Operations
- Bulk date operations
- Vectorized calculations for large datasets
- Lazy evaluation for expensive operations

## 8. Validation and Error Handling

### Input Validation
```python
def validate_datetime_input(value: Any) -> datetime:
    """Validate and convert various input types to datetime"""
    
def safe_parse_datetime(value: str) -> Optional[datetime]:
    """Parse datetime with graceful error handling"""
```

### Error Types
- `InvalidDateFormatError`: Unparseable date strings
- `TimezoneNotFoundError`: Invalid timezone names
- `DateRangeError`: Invalid date ranges

## 9. Integration Points

### Database Layer
- Automatic UTC conversion for storage
- Query helpers for date range filtering
- Migration support for datetime fields

### API Layer
- Request/response datetime serialization
- Query parameter parsing
- Response formatting based on Accept-Language

### User Interface
- Localized date formatting
- Timezone preference handling
- Calendar integration support

## 10. Configuration

### Settings
```python
# Default datetime formats
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TIMEZONE = "UTC"

# Business day configuration
BUSINESS_DAYS = [0, 1, 2, 3, 4]  # Monday-Friday
BUSINESS_START_HOUR = 9
BUSINESS_END_HOUR = 17
```

### Environment Variables
- `DEFAULT_TIMEZONE`: System default timezone
- `DATE_FORMAT_PREFERENCE`: Default formatting preference
- `BUSINESS_HOURS_START`: Business day start time
- `BUSINESS_HOURS_END`: Business day end time
