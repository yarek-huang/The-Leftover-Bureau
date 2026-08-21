from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


# ---- auth ----


class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    # TODO(PASSWORD_STRENGTH_CHECK): 公网迁移后打开强度校验（长度/字符类别）
    password: str = Field(min_length=6, max_length=128)
    invite_code: str


class LoginIn(BaseModel):
    username: str
    password: str


class InviteCodeCreateIn(BaseModel):
    expires_in_days: int = Field(default=30, ge=1, le=365)


class RegisterOut(BaseModel):
    user_id: int
    username: str
    is_admin: bool
    token: str


class UserBrief(BaseModel):
    id: int
    username: str
    is_admin: bool


class LoginOut(BaseModel):
    token: str
    user: UserBrief


class InviteCodeOut(BaseModel):
    code: str
    expires_at: datetime | None


# ---- admin ----


class ResetPasswordIn(BaseModel):
    # TODO(PASSWORD_STRENGTH_CHECK): 同上
    new_password: str = Field(min_length=6, max_length=128)


class SetAdminIn(BaseModel):
    is_admin: bool


class OkOut(BaseModel):
    ok: bool = True


# ---- fridge ----


class FridgeCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)


class FridgeOut(BaseModel):
    fridge_id: int
    name: str
    role: str
    status: str


class JoinIn(BaseModel):
    invite_code: str


class JoinOut(BaseModel):
    fridge_id: int
    name: str
    role: str


class MemberOut(BaseModel):
    user_id: int
    username: str
    role: str
    joined_at: datetime


# ---- stock items ----


class StockItemIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    quantity: str = Field(default="", max_length=64)
    zone: Literal["freezer", "fridge", "pantry"] = "fridge"
    state: Literal["raw", "cooked", "leftover"] = "raw"
    expiry_date: date | None = None


class BatchItemsIn(BaseModel):
    items: list[StockItemIn] = Field(min_length=1)


class StockItemOut(BaseModel):
    id: int
    name: str
    quantity: str
    zone: str
    state: str
    expiry_date: date | None
    fridge_id: int
    fridge_name: str


class ItemPatchIn(BaseModel):
    # 只 apply model_fields_set 里出现的字段；expiry_date 显式传 null = 清空
    name: str | None = Field(default=None, min_length=1, max_length=128)
    quantity: str | None = Field(default=None, max_length=64)
    zone: Literal["freezer", "fridge", "pantry"] | None = None
    state: Literal["raw", "cooked", "leftover"] | None = None
    expiry_date: date | None = None


class ExpiryAlertOut(StockItemOut):
    days_left: int


# ---- recipes ----


class RecipeLineIn(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    quantity: str = Field(default="", max_length=64)
    role: Literal["main", "seasoning"] = "main"


class RecipeCreateIn(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    steps: str = Field(min_length=1)
    duration_min: int | None = Field(default=None, ge=1, le=1440)
    servings: int | None = Field(default=None, ge=1, le=99)
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    ingredient_lines: list[RecipeLineIn] = Field(min_length=1)
    submit_for_review: bool = False


class RecipeLineOut(RecipeLineIn):
    id: int


class RecipeOut(BaseModel):
    id: int
    title: str
    steps: str
    duration_min: int | None
    servings: int | None
    difficulty: str
    meat_type: str
    status: str
    rejection_reason: str | None
    author_id: int
    author_name: str
    ingredient_lines: list[RecipeLineOut]


class StatusOut(BaseModel):
    status: str


class ReviewIn(BaseModel):
    action: Literal["approve", "reject"]
    reason: str | None = Field(default=None, max_length=1000)
