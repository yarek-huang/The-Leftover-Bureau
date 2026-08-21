from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import IdMixin


class Fridge(IdMixin, Base):
    __tablename__ = "fridges"

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="active", server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="fridge", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint("status IN ('active','archived')", name="fridge_status_chk"),
    )


class Membership(IdMixin, Base):
    __tablename__ = "memberships"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    fridge_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("fridges.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="member", server_default="member"
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    fridge: Mapped["Fridge"] = relationship(back_populates="memberships")
    __table_args__ = (
        CheckConstraint("role IN ('owner','member')", name="membership_role_chk"),
    )


class InviteCode(IdMixin, Base):
    __tablename__ = "invite_codes"

    code: Mapped[str] = mapped_column(String(6), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), nullable=False)
    fridge_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("fridges.id"), nullable=True, index=True
    )
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    used_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    __table_args__ = (
        CheckConstraint("type IN ('registration','fridge')", name="invite_type_chk"),
    )
