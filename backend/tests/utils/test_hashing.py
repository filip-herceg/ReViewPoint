from tests.test_templates import UtilityUnitTestTemplate


class TestHashingUtils(UtilityUnitTestTemplate):
    def test_hash_password_and_verify(self):
        from src.utils.hashing import hash_password, verify_password

        password = "s3cr3t!"
        hashed = hash_password(password)
        self.assert_not_equal(hashed, password)
        self.assert_true(hashed.startswith("$2b$") or hashed.startswith("$2a$"))
        self.assert_is_true(verify_password(password, hashed))
        self.assert_is_false(verify_password("wrong", hashed))
        self.assert_predicate_true(verify_password, password, hashed)
        self.assert_predicate_false(verify_password, "wrong", hashed)

    def test_hash_uniqueness(self):
        from src.utils.hashing import hash_password, verify_password

        password = "repeatable"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assert_not_equal(hash1, hash2)  # bcrypt uses random salt
        self.assert_is_true(verify_password(password, hash1))
        self.assert_is_true(verify_password(password, hash2))
        self.assert_predicate_true(verify_password, password, hash1)
        self.assert_predicate_true(verify_password, password, hash2)
