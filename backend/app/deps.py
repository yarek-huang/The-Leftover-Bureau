from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Membership, User
from app.security import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status_code=401, detail="未登录")
    user_id = decode_token(creds.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="登录已过期或 token 无效")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return user


def get_membership(db: Session, user_id: int, fridge_id: int) -> Membership | None:
    return db.scalar(
        select(Membership).where(
            Membership.user_id == user_id, Membership.fridge_id == fridge_id
        )
    )
