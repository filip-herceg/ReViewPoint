import importlib.util
from pathlib import Path


def test_token_schema_module_exists():
    token_path = Path(__file__).parent.parent.parent / "src" / "schemas" / "token.py"
    assert token_path.exists(), f"Token schema file does not exist: {token_path}"
    spec = importlib.util.spec_from_file_location("token", token_path)
    assert spec is not None, "Could not load spec for token.py"
    module = importlib.util.module_from_spec(spec)
    assert module is not None, "Could not import token.py module"
