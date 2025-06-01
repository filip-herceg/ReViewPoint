from typing import Any

class JWTError(Exception): ...

def encode(
    claims: dict[str, Any],
    key: str | bytes,
    algorithm: str = ...,
    headers: dict[str, Any] | None = ...,
    json_encoder: Any = ...,
) -> str: ...
def decode(
    token: str,
    key: str | bytes,
    algorithms: list[str],
    options: dict[str, Any] | None = ...,
    audience: str | None = ...,
    issuer: str | None = ...,
    subject: str | None = ...,
    access_token: str | None = ...,
    leeway: int = ...,
) -> dict[str, Any]: ...
