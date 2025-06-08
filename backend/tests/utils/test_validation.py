from src.utils.validation import (
    get_password_validation_error,
    validate_email,
    validate_password,
)


def test_validate_email_and_password() -> None:
    assert validate_email("test@example.com")
    assert not validate_email("bademail")
    assert validate_password("Abc12345")
    assert not validate_password("short")
    assert not validate_password("nodigits")  # fixed: no digit at all
    assert not validate_password("12345678")
    assert (
        get_password_validation_error("short")
        == "Password must be at least 8 characters."
    )
    assert (
        get_password_validation_error("abcdefgh")
        == "Password must contain at least one digit."
    )
    assert (
        get_password_validation_error("12345678")
        == "Password must contain at least one letter."
    )
    assert get_password_validation_error("Abc12345") is None
