import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Final

def test_upload_service_module_exists() -> None:
    """
    Test that the upload.py service module exists and can be loaded as a module.
    Verifies the file exists and import machinery works. Raises AssertionError if not.
    """
    upload_path: Final[Path] = Path(__file__).parent.parent.parent / "src" / "services" / "upload.py"
    assert upload_path.exists(), f"Upload service file does not exist: {upload_path}"
    spec = importlib.util.spec_from_file_location("upload", upload_path)
    assert spec is not None, "Could not load spec for upload.py"
    module: ModuleType = importlib.util.module_from_spec(spec)
    assert module is not None, "Could not import upload.py module"
