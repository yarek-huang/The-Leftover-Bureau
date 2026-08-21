from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import InviteCode, User
from app.schemas import (
    InviteCodeCreateIn,
    InviteCodeOut,
    LoginIn,
    LoginOut,
    RegisterIn,
    RegisterOut,
    UserBrief,
)
from app.security import create_token, gen_code, hash_password, now_utc, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _find_valid_code(db: Session, code: str, type_: str) -> InviteCode | None:
    inv = db.scalar(select(InviteCode).where(InviteCode.code == code, InviteCode.type == type_))
    if inv is None or inv.revoked:
        return None
    if inv.expires_at is not None and inv.expires_at < now_utc():
        return None
    return inv


def _gen_unique_code(
    db: Session,
    type_: str,
    created_by: int,
    expires_at,
    fridge_id: int | None = None,
) -> InviteCode:
    while True:
        code = gen_code(6)
        exists = db.scalar(select(InviteCode).where(InviteCode.code == code))
        if exists is None:
            inv = InviteCode(
                code=code,
                type=type_,
                created_by=created_by,
                expires_at=expires_at,
                fridge_id=fridge_id,
            )
            db.add(inv)
            db.commit()
            db.refresh(inv)
            return inv


# TODO(LOGIN_RATE_LIMIT): 公网迁移后按 IP+用户名限流
@router.post("/register", response_model=RegisterOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    user_count = db.scalar(select(func.count()).select_from(User))
    inv = None
    if user_count > 0:
        # 空库豁免：首个用户无人可发码（010 决议：首个注册自动 admin）
        inv = _find_valid_code(db, body.invite_code, "registration")
        if inv is None:
            raise HTTPException(status_code=403, detail="邀请码无效或已撤销")

    exists = db.scalar(select(User).where(User.username == body.username))
    if exists is not None:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        is_admin=user_count == 0,
    )
    db.add(user)
    if inv is not None:
        inv.used_count += 1
    db.commit()
    db.refresh(user)
    return RegisterOut(
        user_id=user.id,
        username=user.username,
        is_admin=user.is_admin,
        token=create_token(user.id),
    )


@router.post("/login", response_model=LoginOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == body.username))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return LoginOut(token=create_token(user.id), user=UserBrief(
        id=user.id, username=user.username, is_admin=user.is_admin
    ))


@router.post("/invite-codes", response_model=InviteCodeOut, status_code=201)
def create_registration_invite(
    body: InviteCodeCreateIn | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """任意已登录用户可生成注册邀请码（010 决议）。"""
    days = body.expires_in_days if body else 30
    expires_at = now_utc() + timedelta(days=days)
    inv = _gen_unique_code(db, "registration", user.id, expires_at)
    return InviteCodeOut(code=inv.code, expires_at=inv.expires_at)
