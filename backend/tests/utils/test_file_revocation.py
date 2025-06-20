import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils import file_revocation
from src.utils.file_revocation import FileRevocationError


def setup_module(module: object) -> None:
    # Use temp files for blacklist paths
    file_revocation._LOCAL_BLACKLIST_PATH = Path(tempfile.mktemp(suffix="_local.json"))
    file_revocation._S3_BLACKLIST_PATH = Path(tempfile.mktemp(suffix="_s3.json"))


def teardown_module(module: object) -> None:
    # Clean up temp files
    if file_revocation._LOCAL_BLACKLIST_PATH.exists():
        file_revocation._LOCAL_BLACKLIST_PATH.unlink()
    if file_revocation._S3_BLACKLIST_PATH.exists():
        file_revocation._S3_BLACKLIST_PATH.unlink()


def test_revoke_and_check_local_token() -> None:
    token = "token123"
    assert not file_revocation.is_local_token_revoked(token)
    file_revocation.revoke_local_token(token)
    assert file_revocation.is_local_token_revoked(token)


def test_revoke_and_check_s3_file() -> None:
    file_id = "fileid123"
    assert not file_revocation.is_s3_file_revoked(file_id)
    file_revocation.revoke_s3_file(file_id)
    assert file_revocation.is_s3_file_revoked(file_id)


def test_revoke_local_token_error() -> None:
    # Simulate error by making write_text fail at the class level
    with patch("pathlib.Path.write_text", side_effect=OSError("fail")):
        with pytest.raises(FileRevocationError):
            file_revocation.revoke_local_token("badtoken")


def test_is_local_token_revoked_error() -> None:
    # Simulate error by making read_text fail at the class level
    file_revocation._LOCAL_BLACKLIST_PATH.write_text(json.dumps(["tok"]))
    with patch("pathlib.Path.read_text", side_effect=OSError("fail")):
        with pytest.raises(FileRevocationError):
            file_revocation.is_local_token_revoked("tok")


def test_revoke_s3_file_error() -> None:
    # Simulate error by making write_text fail at the class level
    with patch("pathlib.Path.write_text", side_effect=OSError("fail")):
        with pytest.raises(FileRevocationError):
            file_revocation.revoke_s3_file("badfileid")


def test_is_s3_file_revoked_error() -> None:
    # Simulate error by making read_text fail at the class level
    file_revocation._S3_BLACKLIST_PATH.write_text(json.dumps(["fid"]))
    with patch("pathlib.Path.read_text", side_effect=OSError("fail")):
        with pytest.raises(FileRevocationError):
            file_revocation.is_s3_file_revoked("fid")
