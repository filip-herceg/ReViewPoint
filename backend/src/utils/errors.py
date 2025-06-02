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


# Add more as needed for standardizing error handling
