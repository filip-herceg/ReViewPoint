import importlib.util
from pathlib import Path


def test_upload_service_module_exists():
    upload_path = Path(__file__).parent.parent.parent / "src" / "services" / "upload.py"
    assert upload_path.exists(), f"Upload service file does not exist: {upload_path}"
    spec = importlib.util.spec_from_file_location("upload", upload_path)
    assert spec is not None, "Could not load spec for upload.py"
    module = importlib.util.module_from_spec(spec)
    assert module is not None, "Could not import upload.py module"
