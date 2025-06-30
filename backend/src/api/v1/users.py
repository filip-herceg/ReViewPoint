# --- This file is now split into modules under users/ ---
# All user-related endpoints have been moved to:
#   users/core.py         (CRUD)
#   users/exports.py      (exports)
#   users/advanced.py     (deprecated/advanced)
#   users/test_utils.py   (test-only)
#   users/__init__.py     (router aggregation)
#
# To use these endpoints, import routers from users/ in your FastAPI app:
#
#   from src.api.v1.users import all_routers
#   for router in all_routers:
#       app.include_router(router, prefix="/api/v1")
