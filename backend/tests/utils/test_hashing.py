from src.utils.hashing import hash_password, verify_password


def test_hash_password_and_verify():
    password = "s3cr3t!"
    hashed = hash_password(password)
    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_hash_uniqueness():
    password = "repeatable"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2  # bcrypt uses random salt
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)
