from services.module_runner import run_mock_module


def test_mock_result():
    result = run_mock_module()
    assert result.module_name == "structure_validator"
    assert result.status == "warning"
    assert isinstance(result.feedback, list)
