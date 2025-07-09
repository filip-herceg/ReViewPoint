from typing import Final

from tests.test_templates import UtilityUnitTestTemplate


class TestHashingUtils(UtilityUnitTestTemplate):
    """Test utility functions for password hashing and verification in src.utils.hashing."""

    def test_hash_password_and_verify(self) -> None:
        """
        Test that hashing a password produces a different string, and that verification works for correct and incorrect passwords.
        Verifies that the hash uses bcrypt and that the verify function returns the correct boolean.
        """
        from src.utils.hashing import hash_password, verify_password

        password: Final[str] = "s3cr3t!"
        hashed: str = hash_password(password)
        self.assert_not_equal(hashed, password)
        self.assert_true(hashed.startswith("$2b$") or hashed.startswith("$2a$"))
        self.assert_is_true(verify_password(password, hashed))
        self.assert_is_false(verify_password("wrong", hashed))
        self.assert_predicate_true(verify_password, password, hashed)
        self.assert_predicate_false(verify_password, "wrong", hashed)

    def test_hash_uniqueness(self) -> None:
        """
        Test that hashing the same password twice produces different hashes (due to random salt),
        and that both hashes can be used to verify the original password.
        """
        from src.utils.hashing import hash_password, verify_password

        password: Final[str] = "repeatable"
        hash1: str = hash_password(password)
        hash2: str = hash_password(password)
        self.assert_not_equal(hash1, hash2)  # bcrypt uses random salt
        self.assert_is_true(verify_password(password, hash1))
        self.assert_is_true(verify_password(password, hash2))
        self.assert_predicate_true(verify_password, password, hash1)
        self.assert_predicate_true(verify_password, password, hash2)
