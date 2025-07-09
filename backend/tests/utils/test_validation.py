from typing import Final

from src.utils.validation import (
    get_password_validation_error,
    validate_email,
    validate_password,
)
from tests.test_templates import UtilityUnitTestTemplate


class TestValidationUtils(UtilityUnitTestTemplate):
    """Test utility functions for email and password validation in src.utils.validation."""

    def test_validate_email_and_password(self) -> None:
        """
        Test that email and password validation functions return correct results for valid and invalid inputs.
        Also tests that get_password_validation_error returns the correct error message or None.
        """
        valid_email: Final[str] = "test@example.com"
        invalid_email: Final[str] = "bademail"
        valid_password: Final[str] = "Abc12345"
        short_password: Final[str] = "short"
        no_digit_password: Final[str] = "nodigits"
        no_letter_password: Final[str] = "12345678"

        self.assert_is_true(validate_email(valid_email))
        self.assert_is_false(validate_email(invalid_email))
        self.assert_is_true(validate_password(valid_password))
        self.assert_is_false(validate_password(short_password))
        self.assert_is_false(validate_password(no_digit_password))
        self.assert_is_false(validate_password(no_letter_password))

        self.assert_equal(
            get_password_validation_error(short_password),
            "Password must be at least 8 characters.",
        )
        self.assert_equal(
            get_password_validation_error("abcdefgh"),
            "Password must contain at least one digit.",
        )
        self.assert_equal(
            get_password_validation_error(no_letter_password),
            "Password must contain at least one letter.",
        )
        self.assert_is_none(get_password_validation_error(valid_password))
