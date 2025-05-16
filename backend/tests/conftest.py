import sys
import os
import pytest

from main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)
