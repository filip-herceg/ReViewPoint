import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    return TestClient(app)
