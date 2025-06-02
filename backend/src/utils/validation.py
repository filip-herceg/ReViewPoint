import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> bool:
    """Simple email format validation."""
    return bool(EMAIL_REGEX.match(email))


def validate_password(password: str, min_length: int = 8) -> bool:
    """Basic password validation: min length, at least one digit, one letter."""
    if len(password) < min_length:
        return False
    if not re.search(r"[A-Za-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def get_password_validation_error(password: str, min_length: int = 8) -> str | None:
    if len(password) < min_length:
        return f"Password must be at least {min_length} characters."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    return None
