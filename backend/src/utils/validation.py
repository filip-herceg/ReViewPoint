import re
from re import Pattern
from typing import Final, Literal, TypedDict, overload

# Strict constant for the email regex pattern
EMAIL_REGEX_PATTERN: Final[str] = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
EMAIL_REGEX: Final[Pattern[str]] = re.compile(EMAIL_REGEX_PATTERN)


@overload
def validate_email(email: str) -> Literal[True]: ...
@overload
def validate_email(email: str) -> Literal[False]: ...
def validate_email(email: str) -> bool:
    """
    Simple email format validation.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email matches the pattern, False otherwise.
    """
    result: bool = bool(EMAIL_REGEX.match(email))
    return result


@overload
def validate_password(password: str, min_length: int = 8) -> Literal[True]: ...
@overload
def validate_password(password: str, min_length: int = 8) -> Literal[False]: ...
def validate_password(password: str, min_length: int = 8) -> bool:
    """
    Basic password validation: min length, at least one digit, one letter.

    Args:
        password (str): The password to validate.
        min_length (int, optional): Minimum length. Defaults to 8.

    Returns:
        bool: True if valid, False otherwise.
    """
    is_long_enough: bool = len(password) >= min_length
    has_letter: bool = bool(re.search(r"[A-Za-z]", password))
    has_digit: bool = bool(re.search(r"\d", password))
    result: bool = is_long_enough and has_letter and has_digit
    return result


class PasswordValidationError(TypedDict, total=False):
    error: Literal[
        "Password must be at least {min_length} characters.",
        "Password must contain at least one letter.",
        "Password must contain at least one digit.",
    ]
    min_length: int


def get_password_validation_error(password: str, min_length: int = 8) -> str | None:
    """
    Get the error message for password validation.

    Args:
        password (str): The password to validate.
        min_length (int, optional): Minimum length. Defaults to 8.

    Returns:
        Optional[str]: Error message if invalid, None if valid.

    Raises:
        ValueError: If min_length is less than 1.
    """
    if min_length < 1:
        raise ValueError("min_length must be at least 1")
    if len(password) < min_length:
        return f"Password must be at least {min_length} characters."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    return None
