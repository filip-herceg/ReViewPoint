#!/usr/bin/env python3
"""Script to generate documentation for all missing source and test files
"""

import os
from typing import List, Set

# Template for Python file documentation
PYTHON_FILE_TEMPLATE = """# `{relative_path}`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | {layer}                                                           |
| **Responsibility** | {responsibility}                                                   |
| **Status**         | 🟡 WIP                                                            |

## 1. Purpose

{purpose}

## 2. Public API

| Symbol       | Type     | Description            |
| ------------ | -------- | ---------------------- |
| *TBD*        | *TBD*    | *To be documented*     |

## 3. Usage

```python
# Usage examples to be added
```

## 4. Dependencies

- List dependencies here

## 5. Notes

- Additional implementation notes
- TODO: Complete documentation based on actual file content
"""

# Template for TypeScript/JavaScript file documentation
TS_FILE_TEMPLATE = """# `{relative_path}`

| Item               | Value                                                              |
| ------------------ | ------------------------------------------------------------------ |
| **Layer**          | {layer}                                                           |
| **Responsibility** | {responsibility}                                                   |
| **Status**         | 🟡 WIP                                                            |

## 1. Purpose

{purpose}

## 2. Component/Module API

| Export       | Type     | Description            |
| ------------ | -------- | ---------------------- |
| *TBD*        | *TBD*    | *To be documented*     |

## 3. Usage

```typescript
// Usage examples to be added
```

## 4. Props/Parameters

*For components - document props here*

## 5. Dependencies

- List dependencies here

## 6. Notes

- Additional implementation notes
- TODO: Complete documentation based on actual file content
"""

def determine_layer(file_path: str) -> str:
    """Determine the layer/category based on file path"""
    if "/api/" in file_path:
        return "API Layer"
    if "/core/" in file_path:
        return "Core Infrastructure"
    if "/models/" in file_path:
        return "Data Models"
    if "/services/" in file_path:
        return "Business Logic"
    if "/repositories/" in file_path:
        return "Data Access"
    if "/schemas/" in file_path:
        return "Validation Schemas"
    if "/utils/" in file_path:
        return "Utilities"
    if "/middlewares/" in file_path:
        return "Middleware"
    if "/migrations/" in file_path or "/alembic/" in file_path:
        return "Database Migration"
    if "/tests/" in file_path:
        return "Tests"
    if "/components/" in file_path:
        return "UI Components"
    if "/pages/" in file_path:
        return "Page Components"
    if "/hooks/" in file_path:
        return "React Hooks"
    if "/store/" in file_path or "/stores/" in file_path:
        return "State Management"
    return "Application"

def generate_responsibility(file_path: str, file_name: str) -> str:
    """Generate a responsibility description based on file name and path"""
    name_without_ext = file_name.split(".")[0]

    if file_name.startswith("test_"):
        return f"Unit tests for {name_without_ext.replace('test_', '')} functionality"
    if "test" in file_path:
        return f"Test cases and validation for {name_without_ext}"
    if name_without_ext == "__init__":
        return "Module initialization and exports"
    if name_without_ext == "conftest":
        return "Pytest configuration and shared test fixtures"
    if "migration" in file_path.lower():
        return f"Database schema migration: {name_without_ext}"
    if name_without_ext == "main":
        return "Application entry point and initialization"
    if file_name.endswith(".tsx") or file_name.endswith(".jsx"):
        return f"React component: {name_without_ext}"
    if "component" in file_path.lower():
        return f"Reusable UI component: {name_without_ext}"
    if "page" in file_path.lower():
        return f"Page-level component: {name_without_ext}"
    if "hook" in file_path.lower():
        return f"Custom React hook: {name_without_ext}"
    if "store" in file_path.lower():
        return f"State management store: {name_without_ext}"
    return f"{name_without_ext.replace('_', ' ').title()} implementation and utilities"

def generate_purpose(file_path: str, file_name: str) -> str:
    """Generate a purpose description"""
    responsibility = generate_responsibility(file_path, file_name)

    if "/tests/" in file_path:
        return f"Provides comprehensive test coverage for the corresponding source module. {responsibility}"
    if "migration" in file_path.lower():
        return f"Database migration script that modifies the schema. {responsibility}"
    if file_name == "__init__.py":
        return f"Initializes the Python package and defines the public API. {responsibility}"
    return f"Core implementation module for the ReViewPoint platform. {responsibility}"

def get_all_source_files() -> List[str]:
    """Get all source files that need documentation"""
    source_files = []

    # Backend Python files
    for root, dirs, files in os.walk("backend/src"):
        for file in files:
            if file.endswith(".py"):
                source_files.append(os.path.join(root, file).replace("\\", "/"))

    for root, dirs, files in os.walk("backend/tests"):
        for file in files:
            if file.endswith(".py"):
                source_files.append(os.path.join(root, file).replace("\\", "/"))

    # Frontend TypeScript/JavaScript files
    for root, dirs, files in os.walk("frontend/src"):
        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                source_files.append(os.path.join(root, file).replace("\\", "/"))

    for root, dirs, files in os.walk("frontend/tests"):
        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                source_files.append(os.path.join(root, file).replace("\\", "/"))

    return source_files

def get_existing_docs() -> Set[str]:
    """Get all existing documentation files"""
    docs = set()

    for root, dirs, files in os.walk("docs/content"):
        for file in files:
            if file.endswith(".md"):
                # Convert doc path back to source path
                doc_path = os.path.join(root, file).replace("\\", "/")
                if "/backend/" in doc_path or "/frontend/" in doc_path:
                    # Extract the source file path from doc path
                    parts = doc_path.split("/")
                    if "backend" in parts:
                        idx = parts.index("backend")
                        source_path = "/".join(parts[idx:]).replace(".md", "")
                        docs.add(source_path)
                    elif "frontend" in parts:
                        idx = parts.index("frontend")
                        source_path = "/".join(parts[idx:]).replace(".md", "")
                        docs.add(source_path)

    return docs

def create_missing_documentation():
    """Create documentation for all missing files"""
    print("Scanning for missing documentation files...")

    source_files = get_all_source_files()
    existing_docs = get_existing_docs()

    missing_files = []
    for source_file in source_files:
        if source_file not in existing_docs:
            missing_files.append(source_file)

    print(f"Found {len(missing_files)} files missing documentation")

    created_count = 0

    for source_file in missing_files:
        # Generate documentation path
        doc_path = f"docs/content/{source_file}.md"

        # Create directory if it doesn't exist
        doc_dir = os.path.dirname(doc_path)
        os.makedirs(doc_dir, exist_ok=True)

        # Skip if doc already exists
        if os.path.exists(doc_path):
            continue

        # Generate documentation content
        file_name = os.path.basename(source_file)
        relative_path = source_file
        layer = determine_layer(source_file)
        responsibility = generate_responsibility(source_file, file_name)
        purpose = generate_purpose(source_file, file_name)

        if file_name.endswith((".ts", ".tsx", ".js", ".jsx")):
            template = TS_FILE_TEMPLATE
        else:
            template = PYTHON_FILE_TEMPLATE

        content = template.format(
            relative_path=relative_path,
            layer=layer,
            responsibility=responsibility,
            purpose=purpose,
        )

        # Write the documentation file
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(content)

        created_count += 1
        print(f"Created: {doc_path}")

    print("\nDocumentation generation complete!")
    print(f"Created {created_count} new documentation files")
    print(f"Total source files: {len(source_files)}")
    print(f"Existing docs: {len(existing_docs)}")
    print(f"Missing docs: {len(missing_files)}")

if __name__ == "__main__":
    create_missing_documentation()
