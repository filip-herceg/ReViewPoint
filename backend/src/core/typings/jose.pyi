from collections.abc import Callable, Mapping, Sequence
from typing import TypedDict, TypeVar

class JWTError(Exception):
    """Exception raised for JWT errors."""

    pass

# TypedDict for JWT headers if structure is known, else Mapping[str, object]
class JWTHeaders(TypedDict, total=False):
    alg: str
    typ: str
    kid: str

# TypedDict for JWT claims if structure is known, else Mapping[str, object]
class JWTClaims(TypedDict, total=False):
    iss: str
    sub: str
    aud: str
    exp: int
    nbf: int
    iat: int
    jti: str

_JsonEncoderT = TypeVar("_JsonEncoderT", bound=Callable[[object], str])

def encode(
    claims: Mapping[str, object],
    key: str | bytes,
    algorithm: str = ...,  # Could use Literal for known algorithms
    headers: Mapping[str, object] | None = ...,  # Use JWTHeaders if structure is fixed
    json_encoder: _JsonEncoderT | None = ...,
) -> str: ...
def decode(
    token: str,
    key: str | bytes,
    algorithms: Sequence[str],
    options: Mapping[str, object] | None = ...,
    audience: str | None = ...,
    issuer: str | None = ...,
    subject: str | None = ...,
    access_token: str | None = ...,
    leeway: int = ...,
) -> Mapping[str, object]: ...
