from schemas.module_result import ModuleResult


def run_mock_module() -> ModuleResult:
    return ModuleResult(
        module_name="structure_validator",
        status="warning",
        score=76,
        feedback=["Introduction too short", "Conclusion missing"],
        version="1.0.0",
    )
