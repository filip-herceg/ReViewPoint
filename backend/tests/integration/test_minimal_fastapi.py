#!/usr/bin/env python3
"""Minimal FastAPI test to isolate the hanging issue."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

import uvicorn
from fastapi import FastAPI

if TYPE_CHECKING:
    from collections.abc import Mapping

# Server configuration constants
SERVER_HOST: Final[str] = "127.0.0.1"
SERVER_PORT: Final[int] = 8001
LOG_LEVEL: Final[str] = "info"

# Response messages
HELLO_MESSAGE: Final[str] = "Hello World"
TEST_STATUS: Final[str] = "working"
TEST_MESSAGE: Final[str] = "Minimal endpoint works"
STARTUP_MESSAGE: Final[str] = "Starting minimal FastAPI server on port 8001..."

app: FastAPI = FastAPI()


@app.get("/")
async def root() -> Mapping[str, str]:
    """Root endpoint returning a hello message.

    Returns:
        Mapping[str, str]: Dictionary containing hello message.

    """
    return {"message": HELLO_MESSAGE}


@app.get("/test")
async def test() -> Mapping[str, str]:
    """Test endpoint to verify server functionality.

    Returns:
        Mapping[str, str]: Dictionary containing status and test message.

    """
    return {"status": TEST_STATUS, "message": TEST_MESSAGE}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level=LOG_LEVEL,
    )
