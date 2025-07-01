from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.schemas.file import FileSchema
from tests.test_templates import ModelUnitTestTemplate


class TestFileSchema(ModelUnitTestTemplate):
    def test_valid_schema(self):
        now = datetime.now(UTC)
        schema = FileSchema(
            id=1,
            filename="test.txt",
            content_type="text/plain",
            user_id=42,
            created_at=now,
        )
        self.assert_equal(schema.id, 1)
        self.assert_equal(schema.filename, "test.txt")
        self.assert_equal(schema.content_type, "text/plain")
        self.assert_equal(schema.user_id, 42)
        self.assert_equal(schema.created_at, now)
        # Test from dict (orm_mode)
        dummy = {
            "id": 2,
            "filename": "b.txt",
            "content_type": "text/csv",
            "user_id": 99,
            "created_at": now,
        }
        schema2 = FileSchema.model_validate(dummy)
        self.assert_equal(schema2.id, 2)
        self.assert_equal(schema2.filename, "b.txt")
        self.assert_equal(schema2.content_type, "text/csv")
        self.assert_equal(schema2.user_id, 99)
        self.assert_equal(schema2.created_at, now)

    @pytest.mark.parametrize(
        "id,filename,content_type,user_id,created_at,should_raise",
        [
            (None, "f.txt", "text/plain", 1, datetime.now(UTC), True),
            (1, None, "text/plain", 1, datetime.now(UTC), True),
            (1, "f.txt", None, 1, datetime.now(UTC), True),
            (1, "f.txt", "text/plain", None, datetime.now(UTC), True),
            (1, "f.txt", "text/plain", 1, None, True),
            (1, "f.txt", "text/plain", 1, datetime.now(UTC), False),
        ],
    )
    def test_schema_missing_fields(
        self, id, filename, content_type, user_id, created_at, should_raise
    ):
        if should_raise:
            self.assert_raises(
                ValidationError,
                FileSchema,
                id=id,
                filename=filename,
                content_type=content_type,
                user_id=user_id,
                created_at=created_at,
            )
        else:
            schema = FileSchema(
                id=id,
                filename=filename,
                content_type=content_type,
                user_id=user_id,
                created_at=created_at,
            )
            self.assert_equal(schema.id, id)
            self.assert_equal(schema.filename, filename)
            self.assert_equal(schema.content_type, content_type)
            self.assert_equal(schema.user_id, user_id)
            self.assert_equal(schema.created_at, created_at)

    @pytest.mark.parametrize(
        "id,filename,content_type,user_id,created_at",
        [
            ("notint", "f.txt", "text/plain", 1, datetime.now(UTC)),
            (1, 123, "text/plain", 1, datetime.now(UTC)),
            (1, "f.txt", 123, 1, datetime.now(UTC)),
            (1, "f.txt", "text/plain", "notint", datetime.now(UTC)),
            (1, "f.txt", "text/plain", 1, "notadate"),
        ],
    )
    def test_schema_invalid_types(
        self, id, filename, content_type, user_id, created_at
    ):
        self.assert_raises(
            ValidationError,
            FileSchema,
            id=id,
            filename=filename,
            content_type=content_type,
            user_id=user_id,
            created_at=created_at,
        )

    def test_schema_repr_and_to_dict(self):
        now = datetime.now(UTC)
        schema = FileSchema(
            id=1,
            filename="repr.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        self.assert_repr(schema, "FileSchema")
        d = schema.model_dump()
        self.assert_equal(d["filename"], "repr.txt")
        self.assert_equal(d["content_type"], "text/plain")
        self.assert_equal(d["user_id"], 1)
        self.assert_equal(d["created_at"], now)

    def test_schema_equality(self):
        now = datetime.now(UTC)
        s1 = FileSchema(
            id=1,
            filename="eq.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        s2 = FileSchema(
            id=1,
            filename="eq.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        self.assert_equal(s1, s2)
        s3 = FileSchema(
            id=2,
            filename="neq.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        self.assert_not_equal(s1, s3)

    def test_schema_copy_and_update(self):
        now = datetime.now(UTC)
        s1 = FileSchema(
            id=1,
            filename="copy.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        s2 = s1.model_copy(update={"filename": "copy2.txt"})
        self.assert_equal(s2.filename, "copy2.txt")
        self.assert_equal(s2.content_type, "text/plain")
        self.assert_equal(s2.user_id, 1)
        self.assert_equal(s2.created_at, now)

    def test_schema_json_serialization(self):
        now = datetime.now(UTC)
        s1 = FileSchema(
            id=1,
            filename="json.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        json_str = s1.model_dump_json()
        self.assert_in("json.txt", json_str)
        self.assert_in(str(now.year), json_str)

    def test_schema_from_orm(self):
        now = datetime.now(UTC)

        class Dummy:
            def __init__(self, id, filename, content_type, user_id, created_at):
                self.id = id
                self.filename = filename
                self.content_type = content_type
                self.user_id = user_id
                self.created_at = created_at

        dummy = Dummy(10, "orm.txt", "text/plain", 2, now)
        schema = FileSchema.model_validate(dummy, from_attributes=True)
        self.assert_equal(schema.id, 10)
        self.assert_equal(schema.filename, "orm.txt")
        self.assert_equal(schema.content_type, "text/plain")
        self.assert_equal(schema.user_id, 2)
        self.assert_equal(schema.created_at, now)

    def test_schema_str(self):
        now = datetime.now(UTC)
        s = FileSchema(
            id=1,
            filename="str.txt",
            content_type="text/plain",
            user_id=1,
            created_at=now,
        )
        s_str = str(s)
        self.assert_in("str.txt", s_str)
        self.assert_in("content_type", s_str)
        self.assert_in("created_at", s_str)
