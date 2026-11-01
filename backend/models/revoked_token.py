from sqlalchemy import Column, DateTime, String

from core.database import Base


class RevokedToken(Base):
    """JWT revocados antes de su expiración natural."""

    __tablename__ = "revoked_tokens"

    jti = Column(String(64), primary_key=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
