# Application Metadata (__about__.py)

This file contains metadata and version information for the ReViewPoint backend application.

## Overview

The `__about__.py` file is a Python convention for storing package metadata in a centralized location. It provides version information and other package details that can be imported and used throughout the application.

## Current Contents

```python
# SPDX-FileCopyrightText: 2025-present filip-herceg <pvt.filip.herceg@gmail.com>
#
# SPDX-License-Identifier: MIT
__version__ = "0.0.1"
```

## Version Information

### Current Version: 0.0.1
The application is currently in early development phase (pre-release version 0.0.1).

### Version Format
The project follows [Semantic Versioning (SemVer)](https://semver.org/) format:
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

## License Information

### SPDX License Identifier
The file includes SPDX (Software Package Data Exchange) license identifiers:
- **SPDX-FileCopyrightText**: Copyright ownership information
- **SPDX-License-Identifier**: MIT License specification

### MIT License
The project is licensed under the MIT License, which allows:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability (no warranty)
- ❌ Warranty (no warranty)

## Usage

### Importing Version Information
```python
from src.__about__ import __version__

print(f"ReViewPoint Backend v{__version__}")
```

### In Setup/Build Scripts
```python
from src.__about__ import __version__

setup(
    name="reviewpoint-backend",
    version=__version__,
    # ... other setup parameters
)
```

### API Version Endpoints
```python
from fastapi import FastAPI
from src.__about__ import __version__

app = FastAPI(title="ReViewPoint API", version=__version__)

@app.get("/version")
async def get_version():
    return {"version": __version__}
```

## Potential Additional Metadata

As the project evolves, this file may be expanded to include:

```python
# SPDX-FileCopyrightText: 2025-present filip-herceg <pvt.filip.herceg@gmail.com>
#
# SPDX-License-Identifier: MIT

__version__ = "0.0.1"
__title__ = "ReViewPoint Backend"
__description__ = "Backend API for ReViewPoint application"
__url__ = "https://github.com/username/reviewpoint"
__author__ = "filip-herceg"
__author_email__ = "pvt.filip.herceg@gmail.com"
__license__ = "MIT"
__copyright__ = "2025-present filip-herceg"
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.0.1 | 2025-07-11 | Initial development version |

## Development Workflow

### Version Bumping
When releasing new versions:

1. **Patch Release** (0.0.1 → 0.0.2): Bug fixes
2. **Minor Release** (0.0.1 → 0.1.0): New features, backwards compatible
3. **Major Release** (0.0.1 → 1.0.0): Breaking changes

### Automated Version Management
Consider using tools like:
- **bump2version**: Automated version bumping
- **setuptools_scm**: Version from Git tags
- **hatch**: Modern Python project management

### CI/CD Integration
The version information can be used in:
- Docker image tags
- API documentation
- Release notes generation
- Deployment scripts

## File Location and Purpose

### Why __about__.py?
This pattern provides:
- **Single Source of Truth**: One place for version information
- **Easy Imports**: Simple import statements throughout codebase
- **Build Tool Integration**: Standard location for build scripts
- **Metadata Centralization**: All package info in one place

### Alternative Patterns
Other common approaches include:
- `_version.py`: Version-only file
- `__init__.py`: Version in main package init
- `pyproject.toml`: Modern Python packaging (dynamic versions)
- `setup.py`: Traditional setuptools approach

## Best Practices

1. **Keep it Simple**: Only essential metadata
2. **Follow Conventions**: Use standard variable names
3. **Version Consistency**: Ensure version matches package metadata
4. **License Clarity**: Include clear license information
5. **Documentation**: Document version history and procedures

## Related Files

### pyproject.toml
The package configuration should reference this version:
```toml
[project]
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "src.__about__.__version__"}
```

### Docker Configuration
Use version for container tagging:
```dockerfile
LABEL version="${VERSION}"
LABEL description="ReViewPoint Backend API"
```

### API Documentation
FastAPI automatically uses version in OpenAPI schema:
```python
app = FastAPI(
    title="ReViewPoint API",
    version=__version__,
    description="Backend API for document review and collaboration"
)
```

This file serves as the authoritative source for application metadata and version information throughout the ReViewPoint backend system.