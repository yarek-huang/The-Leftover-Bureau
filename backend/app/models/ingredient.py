from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import IdMixin, TimestampMixin


class StockItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "stock_items"

    fridge_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("fridges.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[str] = mapped_column(
        String(64), nullable=False, default="", server_default=""
    )
    zone: Mapped[str] = mapped_column(
        String(16), nullable=False, default="fridge", server_default="fridge"
    )
    state: Mapped[str] = mapped_column(
        String(16), nullable=False, default="raw", server_default="raw"
    )
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    __table_args__ = (
        CheckConstraint("zone IN ('freezer','fridge','pantry')", name="stock_zone_chk"),
        CheckConstraint("state IN ('raw','cooked','leftover')", name="stock_state_chk"),
    )


class FridgeEvent(IdMixin, Base):
    __tablename__ = "fridge_events"

    fridge_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("fridges.id"), nullable=False, index=True
    )
    actor_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    stockitem_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("stock_items.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    __table_args__ = (
        CheckConstraint(
            "action IN ('created','updated','deleted','consumed','discarded')",
            name="fridge_event_action_chk",
        ),
    )
