class UserRepositoryError(Exception):
    """Base exception for user repository errors."""


class UserNotFoundError(UserRepositoryError):
    pass


class UserAlreadyExistsError(UserRepositoryError):
    pass


class ValidationError(UserRepositoryError):
    pass


class RateLimitExceededError(UserRepositoryError):
    pass


class InvalidDataError(UserRepositoryError):
    """Raised when user input data is invalid but not a validation error."""

    pass


# Add more as needed for standardizing error handling
