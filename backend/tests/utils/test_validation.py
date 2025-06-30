from src.utils.validation import (
    get_password_validation_error,
    validate_email,
    validate_password,
)
from tests.test_templates import UtilityUnitTestTemplate


class TestValidationUtils(UtilityUnitTestTemplate):
    def test_validate_email_and_password(self):
        self.assert_is_true(validate_email("test@example.com"))
        self.assert_is_false(validate_email("bademail"))
        self.assert_is_true(validate_password("Abc12345"))
        self.assert_is_false(validate_password("short"))
        self.assert_is_false(validate_password("nodigits"))  # fixed: no digit at all
        self.assert_is_false(validate_password("12345678"))
        self.assert_equal(
            get_password_validation_error("short"),
            "Password must be at least 8 characters.",
        )
        self.assert_equal(
            get_password_validation_error("abcdefgh"),
            "Password must contain at least one digit.",
        )
        self.assert_equal(
            get_password_validation_error("12345678"),
            "Password must contain at least one letter.",
        )
        self.assert_is_none(get_password_validation_error("Abc12345"))
