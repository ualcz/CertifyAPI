from sqlalchemy import Column, Boolean, DateTime
from sqlalchemy.sql import func


class TimestampMixin:
    """Mixin para adicionar campos de timestamp automáticos."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin:
    """Mixin para soft delete."""
    is_active = Column(Boolean, default=True, nullable=False)
