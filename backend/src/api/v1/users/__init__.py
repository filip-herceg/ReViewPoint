"""
Aggregate all user-related routers for easy import in the FastAPI app.
"""

from .core import router as core_router
from .exports import router as exports_router
from .test_only_router import router as test_only_router

all_routers = [
    exports_router,  # Put specific routes first
    core_router,  # Put parameterized routes last
    test_only_router,
]
