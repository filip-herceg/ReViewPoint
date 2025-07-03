from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.blacklisted_token import BlacklistedToken


async def blacklist_token(
    session: AsyncSession, jti: str, expires_at: datetime
) -> None:
    token = BlacklistedToken(jti=jti, expires_at=expires_at)
    session.add(token)
    await session.commit()


async def is_token_blacklisted(session: AsyncSession, jti: str) -> bool:
    result = await session.execute(
        select(BlacklistedToken).where(BlacklistedToken.jti == jti)
    )
    token = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if token:
        expires_at = token.expires_at
        # If naive, treat as UTC
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at > now:
            return True
    return False
