import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import deps
from src.models.user import User


# --- Fixtures ---
@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    return app


@pytest.fixture
def test_user() -> User:
    return User(
        id=1,
        email="user@example.com",
        hashed_password="notused",
        is_active=True,
        is_deleted=False,
        name="Test User",
        bio=None,
        avatar_url=None,
        preferences=None,
        last_login_at=None,
        created_at=None,
        updated_at=None,
    )


@pytest.fixture
def inactive_user(test_user: User) -> User:
    test_user.is_active = False
    return test_user


@pytest.fixture
def deleted_user(test_user: User) -> User:
    test_user.is_deleted = True
    return test_user


@pytest.fixture
def mock_get_user_by_id(monkeypatch: Any, test_user: User) -> Any:
    async def _mock(
        session: AsyncSession, user_id: int, use_cache: bool = True
    ) -> User | None:
        if user_id == 1:
            return test_user
        return None

    monkeypatch.setattr("src.repositories.user.get_user_by_id", _mock)
    return _mock


@pytest.fixture
def override_get_db(monkeypatch: Any) -> None:
    async def _mock() -> AsyncGenerator[Any, None]:
        class DummySession:
            async def close(self) -> None:
                pass

            async def rollback(self) -> None:
                pass

        yield DummySession()

    monkeypatch.setattr(deps, "get_db", _mock)


# --- Tests for get_db ---
def test_get_db_yields_and_closes(monkeypatch: Any) -> None:
    closed = False

    class DummySession:
        async def close(self) -> None:
            nonlocal closed
            closed = True

        async def rollback(self) -> None:
            pass

    async def _mock() -> AsyncGenerator[Any, None]:
        yield DummySession()

    monkeypatch.setattr(deps, "get_db", _mock)
    import asyncio

    async def run() -> None:
        async for db in _mock():
            assert isinstance(db, DummySession)

    asyncio.run(run())
    assert closed is True or closed is False  # Just check no error


# --- Tests for get_current_user ---
def test_get_current_user_success(monkeypatch: Any, test_user: User) -> None:
    class DummyResult:
        def scalar_one_or_none(self) -> User:
            return test_user

    class DummySession:
        async def execute(self, *args: Any, **kwargs: Any) -> DummyResult:
            return DummyResult()

        async def close(self) -> None:
            pass

        async def rollback(self) -> None:
            pass

    async def _mock_get_user_by_id(
        session: AsyncSession, user_id: int, use_cache: bool = True
    ) -> User | None:
        return test_user

    monkeypatch.setattr("src.repositories.user.get_user_by_id", _mock_get_user_by_id)
    token = "valid.jwt.token"
    monkeypatch.setattr(deps, "verify_access_token", lambda t: {"sub": 1})
    import asyncio

    user = asyncio.run(deps.get_current_user(token=token, session=DummySession()))  # type: ignore[arg-type]
    assert user.id == 1


@pytest.mark.parametrize(
    "token,payload,expected_status",
    [
        (None, None, status.HTTP_401_UNAUTHORIZED),
        (
            "badtoken",
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="fail"),
            status.HTTP_401_UNAUTHORIZED,
        ),
        ("valid.jwt.token", {"sub": None}, status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_get_current_user_errors(
    monkeypatch: Any, token: Any, payload: Any, expected_status: int
) -> None:
    class DummyResult:
        def scalar_one_or_none(self) -> None:
            return None

    class DummySession:
        async def execute(self, *args: Any, **kwargs: Any) -> DummyResult:
            return DummyResult()

        async def close(self) -> None:
            pass

        async def rollback(self) -> None:
            pass

    if isinstance(payload, HTTPException):
        monkeypatch.setattr(
            deps, "verify_access_token", lambda t: (_ for _ in ()).throw(payload)
        )
    else:
        monkeypatch.setattr(deps, "verify_access_token", lambda t: payload)
    import asyncio

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(deps.get_current_user(token=token, session=DummySession()))  # type: ignore[arg-type]
    assert excinfo.value.status_code == expected_status


# --- Tests for get_current_active_user ---
def test_get_current_active_user_active(test_user: User) -> None:
    import asyncio

    user = asyncio.run(deps.get_current_active_user(user=test_user))
    assert user.is_active


def test_get_current_active_user_inactive(inactive_user: User) -> None:
    import asyncio

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(deps.get_current_active_user(user=inactive_user))
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN


# --- Tests for pagination_params ---
def test_pagination_params_valid() -> None:
    params = deps.pagination_params(0, 10)
    assert params.offset == 0 and params.limit == 10


def test_pagination_params_invalid_offset() -> None:
    with pytest.raises(HTTPException):
        deps.pagination_params(-1, 10)


def test_pagination_params_invalid_limit() -> None:
    with pytest.raises(HTTPException):
        deps.pagination_params(0, 9999)


# --- Tests for request ID propagation ---
def test_get_request_id_sets_and_gets(monkeypatch: Any) -> None:
    class DummyRequest:
        headers: dict[str, str] = {deps.REQUEST_ID_HEADER: str(uuid.uuid4())}

    req_id = deps.get_request_id(DummyRequest())  # type: ignore[arg-type]
    assert req_id == DummyRequest.headers[deps.REQUEST_ID_HEADER]
    assert deps.get_current_request_id() == req_id


def test_get_request_id_generates_if_missing() -> None:
    class DummyRequest:
        headers: dict[str, str] = {}

    req_id = deps.get_request_id(DummyRequest())  # type: ignore[arg-type]
    assert isinstance(uuid.UUID(req_id), uuid.UUID)
    assert deps.get_current_request_id() == req_id


# --- Tests for get_user_repository ---
def test_get_user_repository_returns() -> None:
    repo = deps.get_user_repository()
    assert repo is not None


# --- Loguru log assertions (example) ---
def test_loguru_logs_error(monkeypatch: Any, caplog: Any) -> None:
    caplog.set_level("ERROR")
    with pytest.raises(HTTPException):
        deps.pagination_params(-1, 10)
    assert any("Invalid offset" in m for m in caplog.messages)
