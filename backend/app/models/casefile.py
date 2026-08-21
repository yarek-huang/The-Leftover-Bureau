from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import IdMixin


class CaseFile(IdMixin, Base):
    __tablename__ = "case_files"

    fridge_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("fridges.id"), nullable=False, index=True
    )
    author_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    cooked_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    entries: Mapped[list["CaseFileEntry"]] = relationship(
        back_populates="case_file", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint("rating IS NULL OR (rating BETWEEN 1 AND 5)", name="casefile_rating_chk"),
    )


class CaseFileEntry(IdMixin, Base):
    __tablename__ = "case_file_entries"

    casefile_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("case_files.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    stockitem_name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity_used: Mapped[str] = mapped_column(
        String(64), nullable=False, default="", server_default=""
    )

    case_file: Mapped["CaseFile"] = relationship(back_populates="entries")
