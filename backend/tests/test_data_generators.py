"""
Test Data Generation Utilities

This module provides utilities for generating unique, non-conflicting test data
to ensure proper test isolation. All test data is generated with UUIDs to
guarantee uniqueness across test runs.
"""

import secrets
import string
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class TestUser:
    """Represents a test user with guaranteed unique data."""

    email: str
    password: str
    name: str
    uuid_suffix: str

    def to_register_dict(self) -> dict[str, str]:
        """Convert to registration request format."""
        return {"email": self.email, "password": self.password, "name": self.name}

    def to_login_dict(self) -> dict[str, str]:
        """Convert to login request format."""
        return {"email": self.email, "password": self.password}


class TestDataGenerator:
    """Generates unique test data for each test to prevent conflicts."""

    def __init__(self, test_prefix: str | None = None):
        """
        Initialize generator with optional test prefix.

        Args:
            test_prefix: Optional prefix to identify the test (e.g., test method name)
        """
        self.test_prefix = test_prefix or "test"
        self.unique_id = str(uuid.uuid4())[
            :8
        ]  # Short unique ID for this generator instance
        self._user_counter = 0

    def generate_unique_email(self, role: str | None = None) -> str:
        """
        Generate a unique email address.

        Args:
            role: Optional role identifier (e.g., 'admin', 'user', 'test')

        Returns:
            Unique email address guaranteed not to conflict
        """
        base = f"{self.test_prefix}-{self.unique_id}"
        if role:
            base += f"-{role}"

        # Add a counter for multiple emails in same test
        self._user_counter += 1
        if self._user_counter > 1:
            base += f"-{self._user_counter}"

        return f"{base}@example.com"

    def generate_test_user(
        self,
        role: str | None = None,
        password: str | None = None,
        name_prefix: str | None = None,
    ) -> TestUser:
        """
        Generate a complete test user with unique data.

        Args:
            role: Optional role identifier
            password: Optional custom password (default: secure random password)
            name_prefix: Optional prefix for the name

        Returns:
            TestUser with guaranteed unique data
        """
        uuid_suffix = str(uuid.uuid4())[:8]
        email = self.generate_unique_email(role)

        if password is None:
            # Generate secure password that meets requirements
            password = self._generate_secure_password()

        if name_prefix is None:
            name_prefix = "Test User"

        name = f"{name_prefix} {uuid_suffix}"

        return TestUser(
            email=email, password=password, name=name, uuid_suffix=uuid_suffix
        )

    def generate_multiple_users(
        self, count: int, role_prefix: str | None = None
    ) -> list[TestUser]:
        """
        Generate multiple unique test users.

        Args:
            count: Number of users to generate
            role_prefix: Optional prefix for role naming

        Returns:
            List of unique TestUser objects
        """
        users = []
        for i in range(count):
            role = f"{role_prefix}{i}" if role_prefix else f"user{i}"
            user = self.generate_test_user(role=role)
            users.append(user)
        return users

    def generate_unique_string(self, prefix: str = "test", length: int = 8) -> str:
        """
        Generate a unique string for general test data.

        Args:
            prefix: Prefix for the string
            length: Length of the random suffix

        Returns:
            Unique string
        """
        suffix = str(uuid.uuid4())[:length]
        return f"{prefix}-{suffix}"

    def generate_unique_nonce(self) -> str:
        """Generate a unique nonce for token tests."""
        return str(uuid.uuid4())

    def generate_file_data(self, filename_prefix: str = "test") -> dict[str, Any]:
        """
        Generate unique file test data.

        Args:
            filename_prefix: Prefix for the filename

        Returns:
            Dictionary with unique file data
        """
        unique_suffix = str(uuid.uuid4())[:8]
        return {
            "filename": f"{filename_prefix}-{unique_suffix}.txt",
            "content_type": "text/plain",
            "size": 1024,
            "content": f"Test file content {unique_suffix}",
        }

    def _generate_secure_password(self) -> str:
        """Generate a secure password that meets application requirements."""
        # Ensure password has: uppercase, lowercase, digit, special char, 8+ chars
        password_parts = [
            secrets.choice(string.ascii_uppercase),  # At least one uppercase
            secrets.choice(string.ascii_lowercase),  # At least one lowercase
            secrets.choice(string.digits),  # At least one digit
            secrets.choice("!@#$%^&*"),  # At least one special char
        ]

        # Fill the rest with random characters
        remaining_length = max(8, 12) - len(password_parts)
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password_parts.extend(
            secrets.choice(all_chars) for _ in range(remaining_length)
        )

        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password_parts)

        return "".join(password_parts)


# Convenience functions for common use cases
def get_unique_email(test_name: str | None = None, role: str | None = None) -> str:
    """Quick function to get a unique email."""
    generator = TestDataGenerator(test_name)
    return generator.generate_unique_email(role)


def get_test_user(test_name: str | None = None, role: str | None = None) -> TestUser:
    """Quick function to get a unique test user."""
    generator = TestDataGenerator(test_name)
    return generator.generate_test_user(role=role)


def get_unique_string(prefix: str = "test", test_name: str | None = None) -> str:
    """Quick function to get a unique string."""
    generator = TestDataGenerator(test_name)
    return generator.generate_unique_string(prefix)


# Pre-configured generators for specific test scenarios
class AuthTestDataGenerator(TestDataGenerator):
    """Specialized generator for authentication tests."""

    def __init__(self, test_method_name: str):
        super().__init__(f"auth-{test_method_name}")

    def get_registration_user(self) -> TestUser:
        """Get a user for registration tests."""
        return self.generate_test_user(role="register")

    def get_login_user(self) -> TestUser:
        """Get a user for login tests."""
        return self.generate_test_user(role="login")

    def get_duplicate_test_users(self) -> tuple[TestUser, TestUser]:
        """Get two users for duplicate email testing (different emails guaranteed)."""
        user1 = self.generate_test_user(role="original")
        user2 = self.generate_test_user(role="duplicate")
        return user1, user2

    def get_password_reset_user(self) -> TestUser:
        """Get a user for password reset tests."""
        return self.generate_test_user(role="pwreset")


class ModelTestDataGenerator(TestDataGenerator):
    """Specialized generator for model tests."""

    def __init__(self, model_name: str, test_method_name: str):
        super().__init__(f"{model_name}-{test_method_name}")
        self.model_name = model_name

    def get_crud_user(self) -> TestUser:
        """Get a user for CRUD operation tests."""
        return self.generate_test_user(role="crud")

    def get_bulk_users(self, count: int = 5) -> list[TestUser]:
        """Get multiple users for bulk operation tests."""
        return self.generate_multiple_users(count, role_prefix="bulk")
