from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import IdMixin, TimestampMixin


class Recipe(IdMixin, TimestampMixin, Base):
    __tablename__ = "recipes"

    author_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    steps: Mapped[str] = mapped_column(Text, nullable=False)
    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[str] = mapped_column(
        String(16), nullable=False, default="easy", server_default="easy"
    )
    meat_type: Mapped[str] = mapped_column(
        String(16), nullable=False, default="mixed", server_default="mixed"
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="private", server_default="private"
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    ingredient_lines: Mapped[list["RecipeIngredientLine"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint("difficulty IN ('easy','medium','hard')", name="recipe_difficulty_chk"),
        CheckConstraint("meat_type IN ('meat','veg','mixed')", name="recipe_meat_type_chk"),
        CheckConstraint(
            "status IN ('private','pending','approved','rejected')",
            name="recipe_status_chk",
        ),
    )


class RecipeIngredientLine(IdMixin, Base):
    __tablename__ = "recipe_ingredient_lines"

    recipe_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    quantity: Mapped[str] = mapped_column(
        String(64), nullable=False, default="", server_default=""
    )
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default="main", server_default="main"
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="ingredient_lines")
    __table_args__ = (
        CheckConstraint("role IN ('main','seasoning')", name="recipe_line_role_chk"),
    )
