# Filter Utilities Documentation

## Purpose

The `filters.py` module provides generic filtering and data processing utilities for the ReViewPoint application. This module implements type-safe filtering operations, field selection, and parameter processing commonly used in API endpoints and data transformation layers. It focuses on maintaining data integrity while providing flexible filtering capabilities for user data and API responses.

## Architecture

The filter utilities system follows a functional design pattern:

- **Type Safety**: Comprehensive type annotations and TypedDict structures
- **Generic Functions**: Reusable filtering functions for different data types
- **API Integration**: Specialized parameter processing for JSON:API compliance
- **Field Control**: Secure field filtering with required field protection
- **Date Processing**: Flexible date range filtering with parser integration
- **Immutability**: Non-destructive filtering operations that return new objects

## Type System

### Data Structure Types

**User Data Type Definition:**

```python
from typing_extensions import TypedDict

class UserDict(TypedDict, total=False):
    id: str
    email: str
    # Add other possible user fields here as needed
    # For strict typing, you should enumerate all expected fields
    # If unknown, you may use: ...
```

**Design Characteristics:**

- **Type Safety**: Structured typing for user data representation
- **Extensibility**: Easy to add new fields while maintaining type safety
- **Partial Fields**: `total=False` allows optional fields for flexible usage
- **Documentation**: Clear indication of expected vs. actual data structure

**Required Field Type:**

```python
from typing import Literal

RequiredField = Literal["id", "email"]
```

**Security Purpose:**

- **Field Protection**: Ensures critical fields are always included
- **Type Validation**: Compile-time validation of required field names
- **Security Baseline**: Prevents accidental omission of essential data
- **API Consistency**: Guarantees minimum data in all filtered responses

### Generic Type Variables

**Date Type Variable:**

```python
from typing import TypeVar

TDate = TypeVar("TDate")
```

**Usage Benefits:**

- **Parser Flexibility**: Works with any date parsing function return type
- **Type Preservation**: Maintains type information through function calls
- **Integration**: Compatible with different datetime libraries
- **Reusability**: Single function works with multiple date representations

## Core Functions

### Field Filtering

**filter_fields Function:**

```python
from collections.abc import Mapping, Sequence

def filter_fields(
    obj: Mapping[str, object],
    fields: Sequence[str]
) -> dict[str, object]:
    """
    Filter a mapping to only include specified fields and required fields.

    Args:
        obj: The mapping to filter.
        fields: The fields to include.

    Returns:
        A new dict with only the specified and required fields.
    """
```

**Implementation Details:**

1. **Input Validation:**

   ```python
   if fields is None:
       raise TypeError("fields parameter cannot be None")
   ```

2. **Empty Fields Handling:**

   ```python
   if not fields:
       return dict(obj)
   ```

3. **Required Fields Protection:**

   ```python
   required_fields: Final[list[RequiredField]] = ["id", "email"]
   fields_to_include: list[str] = list(set(fields) | set(required_fields))
   ```

4. **Filtering Operation:**
   ```python
   return {k: v for k, v in obj.items() if k in fields_to_include}
   ```

**Security Features:**

- **Required Field Enforcement**: Always includes `id` and `email` fields
- **Input Validation**: Validates parameters before processing
- **Safe Defaults**: Returns complete object when fields list is empty
- **Type Safety**: Maintains type information throughout operation

### User Filter Processing

**process_user_filters Function:**

```python
from collections.abc import Callable
from typing import Literal

def process_user_filters(
    sort_jsonapi: str,
    created_after: str,
    created_before: str,
    parse_flexible_datetime: Callable[[str], TDate],
) -> tuple[str, Literal["asc", "desc"], TDate, TDate]:
    """
    Process user filter parameters for sorting and date filtering.

    Args:
        sort_jsonapi: The sort field, possibly prefixed with '-'.
        created_after: The lower bound for creation date (string).
        created_before: The upper bound for creation date (string).
        parse_flexible_datetime: Callable to parse date strings.

    Returns:
        sort: The field to sort by.
        order: 'asc' or 'desc'.
        created_after_dt: Parsed lower bound date.
        created_before_dt: Parsed upper bound date.

    Raises:
        ValueError: If date parsing fails.
    """
```

**Processing Logic:**

1. **Sort Parameter Processing:**

   ```python
   sort: str
   order: Literal["asc", "desc"]
   if sort_jsonapi.startswith("-"):
       sort = sort_jsonapi[1:]
       order = "desc"
   else:
       sort = sort_jsonapi
       order = "asc"
   ```

2. **Date Range Processing:**

   ```python
   try:
       created_after_dt: TDate = parse_flexible_datetime(created_after)
   except ValueError as e:
       raise ValueError(f"Invalid created_after: {e}") from e

   try:
       created_before_dt: TDate = parse_flexible_datetime(created_before)
   except ValueError as e:
       raise ValueError(f"Invalid created_before: {e}") from e
   ```

3. **Return Processing:**
   ```python
   return sort, order, created_after_dt, created_before_dt
   ```

**Features:**

- **JSON:API Compliance**: Supports standard JSON:API sorting syntax
- **Error Handling**: Comprehensive error handling with context preservation
- **Type Safety**: Maintains type information for parsed dates
- **Flexible Integration**: Works with any datetime parsing function

## Usage Patterns

### API Endpoint Field Filtering

**User API with Field Selection:**

```python
from src.utils.filters import filter_fields
from fastapi import Query
from typing import Optional, List

@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    fields: Optional[List[str]] = Query(None, description="Fields to include in response"),
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get user with optional field filtering."""

    # Get user data
    user = await user_repository.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert to dictionary
    user_dict = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "is_active": user.is_active,
        "profile_image": user.profile_image
    }

    # Apply field filtering if requested
    if fields:
        filtered_data = filter_fields(user_dict, fields)

        logger.info(f"Applied field filtering for user {user_id}", extra={
            "requested_fields": fields,
            "returned_fields": list(filtered_data.keys()),
            "user_id": current_user.id
        })

        return filtered_data

    return user_dict

@app.get("/users")
async def list_users(
    fields: Optional[List[str]] = Query(None, description="Fields to include in response"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
) -> dict:
    """List users with optional field filtering."""

    # Get users
    users = await user_repository.get_users(limit=limit, offset=offset)
    total_count = await user_repository.count_users()

    # Convert to dictionaries
    user_dicts = []
    for user in users:
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active
        }

        # Apply field filtering if requested
        if fields:
            user_dict = filter_fields(user_dict, fields)

        user_dicts.append(user_dict)

    return {
        "users": user_dicts,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }
```

### Advanced Filter Processing

**User Search with Comprehensive Filtering:**

```python
from src.utils.filters import process_user_filters
from src.utils.datetime import parse_flexible_datetime
from fastapi import Query
from typing import Optional

@app.get("/users/search")
async def search_users(
    # Search parameters
    q: Optional[str] = Query(None, description="Search query"),

    # Sorting parameters (JSON:API style)
    sort: str = Query("created_at", description="Sort field (prefix with - for desc)"),

    # Date filtering
    created_after: Optional[str] = Query(None, description="Created after date"),
    created_before: Optional[str] = Query(None, description="Created before date"),

    # Field selection
    fields: Optional[List[str]] = Query(None, description="Fields to include"),

    # Pagination
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),

    current_user: User = Depends(get_current_user)
) -> dict:
    """Advanced user search with filtering, sorting, and field selection."""

    try:
        # Process filter parameters
        if created_after and created_before:
            sort_field, sort_order, start_date, end_date = process_user_filters(
                sort_jsonapi=sort,
                created_after=created_after,
                created_before=created_before,
                parse_flexible_datetime=parse_flexible_datetime
            )
        else:
            # Handle sorting only
            if sort.startswith("-"):
                sort_field = sort[1:]
                sort_order = "desc"
            else:
                sort_field = sort
                sort_order = "asc"
            start_date = end_date = None

        # Build search criteria
        search_criteria = {
            "query": q,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "created_after": start_date,
            "created_before": end_date,
            "limit": limit,
            "offset": offset
        }

        # Execute search
        users, total_count = await user_repository.search_users(**search_criteria)

        # Convert to dictionaries and apply field filtering
        user_dicts = []
        for user in users:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "is_active": user.is_active,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }

            # Apply field filtering
            if fields:
                user_dict = filter_fields(user_dict, fields)

            user_dicts.append(user_dict)

        # Log search operation
        logger.info("User search executed", extra={
            "search_query": q,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "result_count": len(user_dicts),
            "total_count": total_count,
            "requester_id": current_user.id
        })

        return {
            "users": user_dicts,
            "total": total_count,
            "search_criteria": {
                "query": q,
                "sort": sort,
                "created_after": created_after,
                "created_before": created_before
            },
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }

    except ValueError as e:
        logger.warning(f"Invalid filter parameters: {e}", extra={
            "sort": sort,
            "created_after": created_after,
            "created_before": created_before,
            "requester_id": current_user.id
        })

        raise HTTPException(
            status_code=400,
            detail=f"Invalid filter parameters: {e}"
        )
```

### Service Layer Data Processing

**User Service with Advanced Filtering:**

```python
from src.utils.filters import filter_fields, process_user_filters
from typing import Dict, List, Optional, Any

class UserService:
    """User service with advanced filtering capabilities."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_filtered_users(
        self,
        filters: Dict[str, Any],
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get users with comprehensive filtering."""

        # Extract filter parameters
        search_query = filters.get("query")
        sort_param = filters.get("sort", "created_at")
        created_after = filters.get("created_after")
        created_before = filters.get("created_before")
        limit = filters.get("limit", 10)
        offset = filters.get("offset", 0)

        # Process date filters if provided
        if created_after and created_before:
            try:
                sort_field, sort_order, start_date, end_date = process_user_filters(
                    sort_jsonapi=sort_param,
                    created_after=created_after,
                    created_before=created_before,
                    parse_flexible_datetime=parse_flexible_datetime
                )
            except ValueError as e:
                raise ValueError(f"Invalid date filters: {e}")
        else:
            # Handle sorting only
            sort_field = sort_param.lstrip("-")
            sort_order = "desc" if sort_param.startswith("-") else "asc"
            start_date = end_date = None

        # Build repository query
        query_params = {
            "search_query": search_query,
            "sort_field": sort_field,
            "sort_order": sort_order,
            "created_after": start_date,
            "created_before": end_date,
            "limit": limit,
            "offset": offset
        }

        # Execute query
        users = await self.user_repository.get_users_filtered(**query_params)

        # Convert to dictionaries
        user_dicts = []
        for user in users:
            user_dict = self._user_to_dict(user)

            # Apply field filtering if specified
            if fields:
                user_dict = filter_fields(user_dict, fields)

            user_dicts.append(user_dict)

        return user_dicts

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user model to dictionary."""
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "profile_image": user.profile_image,
            "role": user.role,
            "email_verified": user.email_verified
        }

    async def export_user_data(
        self,
        user_ids: List[str],
        export_fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Export user data with field filtering for GDPR compliance."""

        users = await self.user_repository.get_users_by_ids(user_ids)

        exported_data = []
        for user in users:
            user_dict = self._user_to_dict(user)

            # Apply field filtering for export
            if export_fields:
                user_dict = filter_fields(user_dict, export_fields)

            exported_data.append(user_dict)

        logger.info(f"User data exported", extra={
            "user_count": len(exported_data),
            "export_fields": export_fields,
            "user_ids": user_ids
        })

        return exported_data
```

### Data Transformation Pipeline

**Advanced Data Processing Pipeline:**

```python
from typing import Protocol, Callable, Any, Dict, List

class DataProcessor(Protocol):
    """Protocol for data processing functions."""

    def __call__(self, data: Dict[str, Any]) -> Dict[str, Any]:
        ...

def create_filter_pipeline(
    filters: List[str],
    processors: List[DataProcessor] = None
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Create a data processing pipeline with filtering."""

    def pipeline(data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through the pipeline."""

        # Apply field filtering first
        if filters:
            filtered_data = filter_fields(data, filters)
        else:
            filtered_data = data.copy()

        # Apply additional processors
        if processors:
            for processor in processors:
                filtered_data = processor(filtered_data)

        return filtered_data

    return pipeline

# Example processors
def anonymize_email(data: Dict[str, Any]) -> Dict[str, Any]:
    """Anonymize email addresses for privacy."""
    if "email" in data:
        email = data["email"]
        if "@" in email:
            local, domain = email.split("@", 1)
            anonymized = f"{local[:2]}***@{domain}"
            data["email"] = anonymized
    return data

def format_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format timestamp fields for display."""
    timestamp_fields = ["created_at", "updated_at", "last_login"]

    for field in timestamp_fields:
        if field in data and data[field]:
            try:
                # Assume ISO format input
                from datetime import datetime
                dt = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                data[field] = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except (ValueError, AttributeError):
                # Keep original value if parsing fails
                pass

    return data

# Usage example
def create_user_export_pipeline(include_sensitive: bool = False) -> Callable:
    """Create pipeline for user data export."""

    base_fields = ["id", "username", "first_name", "last_name", "created_at"]

    if include_sensitive:
        fields = base_fields + ["email", "last_login", "is_active"]
        processors = [format_timestamps]
    else:
        fields = base_fields
        processors = [anonymize_email, format_timestamps]

    return create_filter_pipeline(fields, processors)

# Pipeline usage
async def export_users_for_analytics(user_ids: List[str]) -> List[Dict[str, Any]]:
    """Export user data for analytics with privacy protection."""

    # Create processing pipeline
    pipeline = create_user_export_pipeline(include_sensitive=False)

    # Get user data
    users = await user_repository.get_users_by_ids(user_ids)

    # Process through pipeline
    processed_users = []
    for user in users:
        user_dict = user_to_dict(user)
        processed_data = pipeline(user_dict)
        processed_users.append(processed_data)

    return processed_users
```

## Advanced Filter Patterns

### Dynamic Field Selection

**Dynamic API Response Filtering:**

```python
from typing import Set, Dict, Any, Optional

class DynamicFieldFilter:
    """Dynamic field filtering with relationship support."""

    def __init__(self, required_fields: Set[str] = None):
        self.required_fields = required_fields or {"id"}

    def filter_with_relations(
        self,
        data: Dict[str, Any],
        fields: Optional[List[str]] = None,
        include_relations: bool = False
    ) -> Dict[str, Any]:
        """Filter fields with optional relationship inclusion."""

        if not fields:
            return data

        # Add required fields
        all_fields = set(fields) | self.required_fields

        # Filter main fields
        filtered = {k: v for k, v in data.items() if k in all_fields}

        # Handle relationships if requested
        if include_relations:
            for key, value in data.items():
                if key.endswith("_id") and isinstance(value, str):
                    # Include related IDs
                    filtered[key] = value
                elif isinstance(value, dict) and key not in filtered:
                    # Include nested objects if any field matches
                    if any(field.startswith(f"{key}.") for field in fields):
                        nested_fields = [
                            field[len(key)+1:] for field in fields
                            if field.startswith(f"{key}.")
                        ]
                        filtered[key] = self.filter_with_relations(
                            value, nested_fields, include_relations
                        )

        return filtered

# Usage with complex data structures
field_filter = DynamicFieldFilter(required_fields={"id", "email"})

@app.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    fields: Optional[List[str]] = Query(None),
    include_relations: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    """Get user profile with dynamic field filtering."""

    # Get user with relationships
    user_data = await user_repository.get_user_with_relations(user_id)

    # Convert to nested dictionary
    profile_data = {
        "id": user_data.id,
        "email": user_data.email,
        "username": user_data.username,
        "profile": {
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "bio": user_data.bio,
            "avatar": user_data.avatar
        },
        "settings": {
            "theme": user_data.settings.theme if user_data.settings else "light",
            "notifications": user_data.settings.notifications if user_data.settings else True
        },
        "created_at": user_data.created_at.isoformat(),
        "last_login": user_data.last_login.isoformat() if user_data.last_login else None
    }

    # Apply dynamic filtering
    if fields:
        profile_data = field_filter.filter_with_relations(
            profile_data, fields, include_relations
        )

    return profile_data
```

### Performance-Optimized Filtering

**Cached Filter Operations:**

```python
from functools import lru_cache
from typing import FrozenSet, Tuple

@lru_cache(maxsize=1000)
def get_filtered_fields(
    available_fields: FrozenSet[str],
    requested_fields: Tuple[str, ...],
    required_fields: FrozenSet[str]
) -> FrozenSet[str]:
    """Cache field filtering decisions for performance."""

    if not requested_fields:
        return available_fields

    requested_set = set(requested_fields)
    return frozenset((requested_set | required_fields) & available_fields)

def optimized_filter_fields(
    obj: Dict[str, Any],
    fields: Optional[List[str]] = None,
    available_fields: Optional[Set[str]] = None,
    required_fields: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Optimized field filtering with caching."""

    if not fields:
        return obj

    # Use available fields or derive from object
    available = frozenset(available_fields or obj.keys())
    required = frozenset(required_fields or {"id"})
    requested = tuple(fields)  # Tuple for hashing

    # Get cached field selection
    selected_fields = get_filtered_fields(available, requested, required)

    # Filter object
    return {k: v for k, v in obj.items() if k in selected_fields}

# High-performance user listing
@app.get("/users/bulk")
async def list_users_bulk(
    fields: Optional[List[str]] = Query(None),
    limit: int = Query(100, le=1000)
):
    """High-performance user listing with optimized filtering."""

    # Pre-define available fields for caching
    available_user_fields = {
        "id", "email", "username", "first_name", "last_name",
        "created_at", "updated_at", "is_active", "last_login"
    }

    # Get users
    users = await user_repository.get_users(limit=limit)

    # Apply optimized filtering
    filtered_users = []
    for user in users:
        user_dict = user_to_dict(user)

        if fields:
            filtered_dict = optimized_filter_fields(
                user_dict,
                fields,
                available_user_fields,
                {"id", "email"}
            )
        else:
            filtered_dict = user_dict

        filtered_users.append(filtered_dict)

    return {"users": filtered_users}
```

## Testing Strategies

### Filter Function Testing

**Comprehensive Filter Testing:**

```python
import pytest
from src.utils.filters import filter_fields, process_user_filters
from datetime import datetime

class TestFilterUtilities:
    """Test suite for filter utilities."""

    def test_filter_fields_basic(self):
        """Test basic field filtering functionality."""

        data = {
            "id": "123",
            "email": "test@example.com",
            "username": "testuser",
            "password": "secret",
            "created_at": "2023-01-01T00:00:00Z"
        }

        # Test field selection
        filtered = filter_fields(data, ["username", "created_at"])

        # Should include requested fields plus required fields
        assert "id" in filtered  # Required field
        assert "email" in filtered  # Required field
        assert "username" in filtered  # Requested field
        assert "created_at" in filtered  # Requested field
        assert "password" not in filtered  # Not requested, not required

    def test_filter_fields_empty_list(self):
        """Test filtering with empty field list."""

        data = {"id": "123", "email": "test@example.com", "name": "Test"}

        # Empty fields should return all data
        filtered = filter_fields(data, [])
        assert filtered == data

    def test_filter_fields_none_parameter(self):
        """Test filtering with None parameter."""

        data = {"id": "123", "email": "test@example.com"}

        # None fields should raise TypeError
        with pytest.raises(TypeError):
            filter_fields(data, None)

    def test_filter_fields_required_only(self):
        """Test that required fields are always included."""

        data = {
            "id": "123",
            "email": "test@example.com",
            "username": "testuser",
            "optional": "value"
        }

        # Request only non-required field
        filtered = filter_fields(data, ["optional"])

        # Should include required fields plus requested
        assert "id" in filtered
        assert "email" in filtered
        assert "optional" in filtered
        assert "username" not in filtered

    def test_process_user_filters_ascending(self):
        """Test user filter processing with ascending sort."""

        def mock_parse_date(date_str):
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

        sort_field, order, start_date, end_date = process_user_filters(
            sort_jsonapi="created_at",
            created_after="2023-01-01T00:00:00Z",
            created_before="2023-12-31T23:59:59Z",
            parse_flexible_datetime=mock_parse_date
        )

        assert sort_field == "created_at"
        assert order == "asc"
        assert start_date.year == 2023
        assert end_date.year == 2023

    def test_process_user_filters_descending(self):
        """Test user filter processing with descending sort."""

        def mock_parse_date(date_str):
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

        sort_field, order, start_date, end_date = process_user_filters(
            sort_jsonapi="-created_at",
            created_after="2023-01-01T00:00:00Z",
            created_before="2023-12-31T23:59:59Z",
            parse_flexible_datetime=mock_parse_date
        )

        assert sort_field == "created_at"
        assert order == "desc"

    def test_process_user_filters_invalid_date(self):
        """Test user filter processing with invalid dates."""

        def mock_parse_date(date_str):
            if date_str == "invalid":
                raise ValueError("Invalid date format")
            return datetime.now()

        # Should raise ValueError with context
        with pytest.raises(ValueError) as exc_info:
            process_user_filters(
                sort_jsonapi="created_at",
                created_after="invalid",
                created_before="2023-12-31T23:59:59Z",
                parse_flexible_datetime=mock_parse_date
            )

        assert "Invalid created_after" in str(exc_info.value)

    def test_filter_integration(self):
        """Test integration of filtering functions."""

        # Sample user data
        users_data = [
            {
                "id": "1",
                "email": "user1@example.com",
                "username": "user1",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2023-06-01T10:00:00Z",
                "sensitive_data": "secret"
            },
            {
                "id": "2",
                "email": "user2@example.com",
                "username": "user2",
                "first_name": "Jane",
                "last_name": "Smith",
                "created_at": "2023-06-15T14:30:00Z",
                "sensitive_data": "classified"
            }
        ]

        # Filter fields for all users
        requested_fields = ["username", "first_name", "last_name"]

        filtered_users = [
            filter_fields(user, requested_fields)
            for user in users_data
        ]

        # Verify filtering
        for filtered_user in filtered_users:
            # Should have required fields
            assert "id" in filtered_user
            assert "email" in filtered_user

            # Should have requested fields
            assert "username" in filtered_user
            assert "first_name" in filtered_user
            assert "last_name" in filtered_user

            # Should not have unrequested fields
            assert "created_at" not in filtered_user
            assert "sensitive_data" not in filtered_user
```

### Performance Testing

**Filter Performance Benchmarks:**

```python
import time
import pytest
from src.utils.filters import filter_fields

class TestFilterPerformance:
    """Performance tests for filter operations."""

    def test_filter_fields_performance(self):
        """Test field filtering performance with large datasets."""

        # Create large dataset
        large_data = {
            f"field_{i}": f"value_{i}"
            for i in range(1000)
        }
        large_data["id"] = "test_id"
        large_data["email"] = "test@example.com"

        # Test filtering performance
        requested_fields = [f"field_{i}" for i in range(0, 100, 10)]

        start_time = time.time()

        for _ in range(100):
            filter_fields(large_data, requested_fields)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process 100 operations quickly
        assert processing_time < 1.0

        # Calculate throughput
        throughput = 100 / processing_time
        assert throughput > 100  # More than 100 operations per second

    def test_filter_many_objects_performance(self):
        """Test filtering many objects."""

        # Create many objects
        objects = [
            {
                "id": f"id_{i}",
                "email": f"user{i}@example.com",
                "name": f"User {i}",
                "data": f"data_{i}",
                "extra": f"extra_{i}"
            }
            for i in range(1000)
        ]

        fields = ["name", "data"]

        start_time = time.time()

        filtered_objects = [
            filter_fields(obj, fields)
            for obj in objects
        ]

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process 1000 objects quickly
        assert processing_time < 1.0
        assert len(filtered_objects) == 1000

        # Verify filtering correctness
        for filtered_obj in filtered_objects:
            assert "id" in filtered_obj  # Required
            assert "email" in filtered_obj  # Required
            assert "name" in filtered_obj  # Requested
            assert "data" in filtered_obj  # Requested
            assert "extra" not in filtered_obj  # Not requested
```

## Best Practices

### Field Filtering Guidelines

- **Required Fields**: Always enforce required fields for security and consistency
- **Input Validation**: Validate filter parameters before processing
- **Performance**: Use caching for repeated filter operations
- **Type Safety**: Maintain type information throughout filtering operations

### API Design Patterns

- **JSON:API Compliance**: Follow JSON:API conventions for sorting and field selection
- **Error Handling**: Provide clear error messages for invalid filter parameters
- **Documentation**: Document available fields and filtering options in API documentation
- **Backward Compatibility**: Maintain compatibility when adding new filtering features

### Security Considerations

- **Sensitive Data**: Never expose sensitive fields through filtering
- **Required Fields**: Ensure critical fields are always included in responses
- **Input Sanitization**: Validate and sanitize all filter inputs
- **Access Control**: Apply proper access control before filtering operations

## Related Files

### Dependencies

- `collections.abc.Mapping` - Abstract base class for mapping types
- `collections.abc.Sequence` - Abstract base class for sequence types
- `typing.Final` - Immutable constant declarations
- `typing.TypeVar` - Generic type variable definitions
- `typing_extensions.TypedDict` - Structured type definitions

### Integration Points

- `src.utils.datetime` - Date parsing for filter processing
- `src.api.v1.users` - API endpoints using filter utilities
- `src.services.user` - Service layer data processing
- `src.repositories.user` - Repository layer query building

### Related Utilities

- Input validation modules for parameter checking
- Caching utilities for performance optimization
- Serialization modules for data transformation

## Configuration

### Filter Configuration

```python
# Filter system configuration
FILTER_CONFIG = {
    "required_fields": ["id", "email"],        # Always included fields
    "max_field_count": 50,                     # Maximum fields per request
    "enable_field_caching": True,              # Enable filter result caching
    "cache_size": 1000,                        # LRU cache size
    "allow_nested_filters": True,              # Enable nested field filtering
}

# API filter settings
API_FILTER_SETTINGS = {
    "default_sort": "created_at",              # Default sort field
    "max_date_range_days": 365,               # Maximum date range
    "enable_field_validation": True,           # Validate requested fields
    "log_filter_usage": True,                 # Log filter operations
}
```

This filter utilities module provides comprehensive data filtering capabilities for the ReViewPoint application, enabling flexible API responses while maintaining security and performance standards.
