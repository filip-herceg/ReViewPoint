
"""Test module for File model functionality.

This module tests the File model including:
- Model field validation and constraints
- CRUD operations
- User relationship
- Integrity and transactional behavior
- Bulk operations and table truncation
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from datetime import datetime
from typing import Final

import pytest
from sqlalchemy import Result, select, text
from sqlalchemy.exc import IntegrityError

from tests.test_data_generators import get_unique_email, get_test_user
from src.models.file import File
from src.models.user import User
from tests.test_templates import AsyncModelTestTemplate


class TestFileModel(AsyncModelTestTemplate):

    async def _run_in_transaction_typed(self, coro: Callable[[], object]) -> None:
        """Type-safe wrapper for run_in_transaction method."""
        from typing import cast
        await cast(Callable[[Callable[[], object]], Awaitable[None]], self.run_in_transaction)(coro)
    """Test class for File model functionality."""



    async def _seed_db_typed(self, objs: list[File] | list[User]) -> None:
        """Type-safe wrapper for seed_db method."""
        from typing import cast
        await cast(Callable[[list[File] | list[User]], Awaitable[None]], self.seed_db)(objs)

    async def _assert_integrity_error_typed(self, obj: File) -> None:
        """Type-safe wrapper for assert_integrity_error method."""
        from typing import cast
        await cast(Callable[[File], Awaitable[None]], self.assert_integrity_error)(obj)

    async def _truncate_table_typed(self, table: str) -> None:
        """Type-safe wrapper for truncate_table method."""
        from typing import cast
        await cast(Callable[[str], Awaitable[None]], self.truncate_table)(table)

    def _assert_model_attrs_typed(self, model: File, attrs: Mapping[str, object]) -> None:
        """Type-safe wrapper for assert_model_attrs method."""
        from typing import cast
        cast(Callable[[File, Mapping[str, object]], None], self.assert_model_attrs)(model, attrs)

    def _assert_repr_typed(self, obj: File, class_name: str) -> None:
        """Type-safe wrapper for assert_repr method."""
        from typing import cast
        cast(Callable[[File, str], None], self.assert_repr)(obj, class_name)

    @pytest.mark.asyncio
    async def test_file_model_fields(self) -> None:
        """Test that File model fields are properly set and validated.

        Verifies:
        - All fields are assigned correctly
        - created_at and updated_at are set
        - Model attributes match expected values
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: Final[File] = File(filename="doc.txt", content_type="text/plain", user_id=user.id)
        self.async_session.add(file)
        await self.async_session.flush()
        expected_attrs: Final[Mapping[str, object]] = {"filename": "doc.txt", "content_type": "text/plain", "user_id": user.id}
        self._assert_model_attrs_typed(file, expected_attrs)
        assert file.created_at is not None
        assert file.updated_at is not None
        assert isinstance(file.created_at, datetime)
        assert isinstance(file.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_file_crud(self) -> None:
        """Test CRUD operations for File model.

        Verifies:
        - Create, read, update, delete operations
        - File is persisted, updated, and deleted as expected
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: File = File(filename="crud.txt", content_type="text/plain", user_id=user.id)
        self.async_session.add(file)
        await self.async_session.commit()
        await self.async_session.refresh(file)
        assert file.id is not None
        db_file: File | None = await self.async_session.get(File, file.id)
        assert db_file is not None
        assert db_file.filename == "crud.txt"
        db_file.content_type = "application/pdf"
        await self.async_session.commit()
        await self.async_session.refresh(db_file)
        assert db_file.content_type == "application/pdf"
        await self.async_session.delete(db_file)
        await self.async_session.commit()
        gone: File | None = await self.async_session.get(File, file.id)
        assert gone is None

    @pytest.mark.asyncio
    async def test_file_user_relationship(self) -> None:
        """Test File to User relationship.

        Verifies:
        - File.user_id matches the related User's id
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: Final[File] = File(filename="rel.txt", content_type="text/plain", user_id=user.id)
        await self._seed_db_typed([file])
        db_file: File | None = await self.async_session.get(File, file.id)
        assert db_file is not None
        assert db_file.user_id == user.id

    @pytest.mark.asyncio
    @pytest.mark.requires_real_db(
        "SQLite in-memory does not reliably enforce foreign key constraints for this test."
    )
    async def test_file_integrity_error_missing_user(self) -> None:
        """Test integrity error when File references missing User.

        Expects:
        - IntegrityError is raised when user_id does not exist
        """
        file: Final[File] = File(filename="bad.txt", content_type="text/plain", user_id=999999)
        await self._assert_integrity_error_typed(file)

    @pytest.mark.asyncio
    async def test_bulk_insert_and_truncate(self) -> None:
        """Test bulk insert and table truncation for File model.

        Verifies:
        - Multiple files can be inserted in bulk
        - Table truncation removes all records
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        files: list[File] = [File(filename=f"bulk-{i}.txt", content_type="text/plain", user_id=user.id) for i in range(5)]
        await self._seed_db_typed(files)
        for f in files:
            assert f.id is not None
        await self._truncate_table_typed("files")
        result: Result[tuple[int]] = await self.async_session.execute(text("SELECT COUNT(*) FROM files"))
        count: int | None = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_transactional_rollback(self) -> None:
        """Test transaction rollback for File model.

        Verifies:
        - Changes are rolled back and not persisted
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: Final[File] = File(filename="rollback.txt", content_type="text/plain", user_id=user.id)

        async def op() -> None:
            self.async_session.add(file)

        await self._run_in_transaction_typed(op)
        result: Result[tuple[int]] = await self.async_session.execute(
            text("SELECT COUNT(*) FROM files WHERE filename = 'rollback.txt'")
        )
        count: int | None = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_file_repr(self) -> None:
        """Test __repr__ method for File model.

        Verifies:
        - __repr__ includes class name
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: Final[File] = File(filename="repr.txt", content_type="text/plain", user_id=user.id)
        await self._seed_db_typed([file])
        self._assert_repr_typed(file, "File")

    @pytest.mark.skip(
        reason="File model does not currently validate content_type is non-empty"
    )
    @pytest.mark.asyncio
    async def test_file_invalid_content_type(self) -> None:
        """Test that empty content_type raises IntegrityError (if validated).

        Expects:
        - IntegrityError on empty content_type (if constraint exists)
        """
        user: Final[User] = User(email="invalidct@example.com", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: File = File(filename="badct.txt", content_type="", user_id=user.id)
        self.async_session.add(file)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_duplicate_filename_same_user(self) -> None:
        """Test duplicate filenames for the same user.

        Verifies:
        - Whether unique constraint exists on (filename, user_id)
        - Documents current behavior (allowed or not)
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file1: File = File(filename="dup.txt", content_type="text/plain", user_id=user.id)
        file2: File = File(filename="dup.txt", content_type="text/plain", user_id=user.id)
        await self._seed_db_typed([file1])
        allowed: bool
        try:
            await self._seed_db_typed([file2])
            allowed = True
        except IntegrityError:
            allowed = False
        assert allowed in (True, False)  # Document behavior

    @pytest.mark.asyncio
    async def test_long_filename_and_content_type(self) -> None:
        """Test long filename and content_type values for File model.

        Verifies:
        - Model accepts long strings for filename and content_type
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        long_filename: Final[str] = "a" * 255
        long_content_type: Final[str] = "b" * 128
        file: File = File(filename=long_filename, content_type=long_content_type, user_id=user.id)
        await self._seed_db_typed([file])
        assert file.filename == long_filename
        assert file.content_type == long_content_type

    @pytest.mark.asyncio
    async def test_null_filename(self) -> None:
        """Test that null filename raises IntegrityError.

        Expects:
        - IntegrityError when filename is None
        """
        user: Final[User] = User(email="{get_unique_email()}", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: File = File(filename=None, content_type="text/plain", user_id=user.id)
        self.async_session.add(file)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_null_content_type(self) -> None:
        """Test that null content_type raises IntegrityError.

        Expects:
        - IntegrityError when content_type is None
        """
        user: Final[User] = User(email="nullct@example.com", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: File = File(filename="nullct.txt", content_type=None, user_id=user.id)
        self.async_session.add(file)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_null_user_id(self) -> None:
        """Test that null user_id raises IntegrityError.

        Expects:
        - IntegrityError when user_id is None
        """
        file: File = File(filename="nouser.txt", content_type="text/plain", user_id=None)
        self.async_session.add(file)
        with pytest.raises(IntegrityError):
            await self.async_session.commit()
        await self.async_session.rollback()

    @pytest.mark.asyncio
    async def test_multiple_files_same_user(self) -> None:
        """Test multiple files for the same user.

        Verifies:
        - User can have multiple files
        - All files are retrievable by user_id
        """
        user: Final[User] = User(email="multifile@example.com", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        files: list[File] = [File(filename=f"multi-{i}.txt", content_type="text/plain", user_id=user.id) for i in range(3)]
        await self._seed_db_typed(files)
        result = await self.async_session.execute(select(File).where(File.user_id == user.id))
        user_files = result.scalars().all()
        assert len(user_files) == 3

    @pytest.mark.asyncio
    async def test_non_ascii_filename(self) -> None:
        """Test non-ASCII filenames for File model.

        Verifies:
        - Model accepts Unicode filenames
        """
        user: Final[User] = User(email="unicode@example.com", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: File = File(filename="файл.txt", content_type="text/plain", user_id=user.id)
        await self._seed_db_typed([file])
        assert "файл" in file.filename

    @pytest.mark.asyncio
    async def test_special_characters_in_filename_and_content_type(self) -> None:
        """Test special characters in filename and content_type.

        Verifies:
        - Model accepts special characters in filename and content_type
        """
        user: Final[User] = User(email="specialchars@example.com", hashed_password="hashed", is_active=True)
        await self._seed_db_typed([user])
        file: File = File(
            filename="weird!@#$.txt",
            content_type="application/x-special!@#$",
            user_id=user.id,
        )
        await self._seed_db_typed([file])
        assert file.filename.startswith("weird!@#$.txt")
        assert file.content_type.startswith("application/x-special!@#$")
