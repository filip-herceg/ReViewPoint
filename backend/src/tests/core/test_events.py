from typing import Any

import pytest
from fastapi import FastAPI


@pytest.mark.asyncio
async def test_startup_and_shutdown_events(app: FastAPI, caplog: Any) -> None:
    # ...existing code...
    assert "Startup complete." in caplog.text
    # ...existing code...
    assert "Application shutdown complete" in caplog.text
