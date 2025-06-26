def test_upload_service_placeholder() -> None:
    # The upload service is currently empty, so just check import
    from src.services import upload

    assert hasattr(upload, "__file__") or upload is not None
