from typing import Any, Dict, List, Optional, Union

class JWTError(Exception): ...

def encode(
    claims: Dict[str, Any],
    key: Union[str, bytes],
    algorithm: str = ...,
    headers: Optional[Dict[str, Any]] = ...,
    json_encoder: Any = ...,
) -> str: ...

def decode(
    token: str,
    key: Union[str, bytes],
    algorithms: List[str],
    options: Optional[Dict[str, Any]] = ...,
    audience: Optional[str] = ...,
    issuer: Optional[str] = ...,
    subject: Optional[str] = ...,
    access_token: Optional[str] = ...,
    leeway: int = ...,
) -> Dict[str, Any]: ...
