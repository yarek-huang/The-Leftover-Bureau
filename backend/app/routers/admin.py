from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import User
from app.schemas import OkOut, ResetPasswordIn, SetAdminIn
from app.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/users/{user_id}/reset-password", response_model=OkOut)
def reset_password(user_id: int, body: ResetPasswordIn, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return OkOut()


@router.post("/users/{user_id}/set-admin", response_model=OkOut)
def set_admin(user_id: int, body: SetAdminIn, db: Session = Depends(get_db)):
    """任命/转让 admin：设 true=任命，转让=给对方 true 后给自己 false。"""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_admin and not body.is_admin:
        admin_count = db.scalar(select(func.count()).select_from(User).where(User.is_admin))
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="至少保留一名管理员")
    user.is_admin = body.is_admin
    db.commit()
    return OkOut()
