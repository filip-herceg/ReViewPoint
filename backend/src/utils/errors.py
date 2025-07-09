from typing import Final


class UserRepositoryError(Exception):
    """Base exception for user repository errors."""


class UserNotFoundError(UserRepositoryError):
    """Raised when a user is not found in the repository."""

    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message)


class UserAlreadyExistsError(UserRepositoryError):
    """Raised when attempting to create a user that already exists."""

    def __init__(self, message: str = "User already exists") -> None:
        super().__init__(message)


class ValidationError(UserRepositoryError):
    """Raised when user input fails validation checks."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)


class RateLimitExceededError(UserRepositoryError):
    """Raised when a user exceeds the allowed rate limit."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)


class InvalidDataError(UserRepositoryError):
    """Raised when user input data is invalid but not a validation error."""

    def __init__(self, message: str = "Invalid data") -> None:
        super().__init__(message)


# Add more as needed for standardizing error handling

# Example of a module-level constant for error codes (if needed in future):
USER_NOT_FOUND_CODE: Final[int] = 404
USER_ALREADY_EXISTS_CODE: Final[int] = 409
VALIDATION_ERROR_CODE: Final[int] = 422
RATE_LIMIT_EXCEEDED_CODE: Final[int] = 429
INVALID_DATA_ERROR_CODE: Final[int] = 400
