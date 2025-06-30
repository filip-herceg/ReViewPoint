"""
Aggregate all user-related routers for easy import in the FastAPI app.
"""

from .core import router as core_router
from .exports import router as exports_router
from .test_only_router import router as test_only_router

all_routers = [
    core_router,
    exports_router,
    test_only_router,
]
