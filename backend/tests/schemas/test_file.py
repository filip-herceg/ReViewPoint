def test_file_schema_placeholder() -> None:
    # The file schema is currently empty, so just check import and instantiation
    from src.schemas import file

    assert hasattr(file, "__file__") or file is not None
