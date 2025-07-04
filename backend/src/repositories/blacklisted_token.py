from datetime import UTC, datetime
from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.blacklisted_token import BlacklistedToken


async def blacklist_token(
    session: AsyncSession, jti: str, expires_at: datetime
) -> None:
    """
    Blacklist a token by storing its JTI and expiration.

    Args:
        session (AsyncSession): The SQLAlchemy async session.
        jti (str): The JWT ID to blacklist.
        expires_at (datetime): The expiration datetime of the token.
    """
    token: Final[BlacklistedToken] = BlacklistedToken(jti=jti, expires_at=expires_at)
    session.add(token)
    await session.commit()


async def is_token_blacklisted(session: AsyncSession, jti: str) -> bool:
    """
    Check if a token is blacklisted and not yet expired.

    Args:
        session (AsyncSession): The SQLAlchemy async session.
        jti (str): The JWT ID to check.

    Returns:
        bool: True if the token is blacklisted and not expired, False otherwise.
    """
    result: Final = await session.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    token: BlacklistedToken | None = result.scalar_one_or_none()
    now: Final[datetime] = datetime.now(UTC)
    if token is not None:
        expires_at: datetime = token.expires_at
        # If naive, treat as UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at > now:
            return True
    return False
