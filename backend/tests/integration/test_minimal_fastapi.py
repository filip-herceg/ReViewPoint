#!/usr/bin/env python3
"""Minimal FastAPI test to isolate the hanging issue."""

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test")
async def test():
    return {"status": "working", "message": "Minimal endpoint works"}


if __name__ == "__main__":
    print("Starting minimal FastAPI server on port 8001...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
