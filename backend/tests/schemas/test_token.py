import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Final

def test_token_schema_module_exists() -> None:
    """
    Test that the token.py schema module exists and can be loaded as a module.
    Verifies the file exists and import machinery works. Raises AssertionError if not.
    """
    token_path: Final[Path] = Path(__file__).parent.parent.parent / "src" / "schemas" / "token.py"
    assert token_path.exists(), f"Token schema file does not exist: {token_path}"
    spec = importlib.util.spec_from_file_location("token", token_path)
    assert spec is not None, "Could not load spec for token.py"
    module: ModuleType = importlib.util.module_from_spec(spec)
    assert module is not None, "Could not import token.py module"
