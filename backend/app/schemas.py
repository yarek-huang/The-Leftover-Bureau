from datetime import datetime

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
