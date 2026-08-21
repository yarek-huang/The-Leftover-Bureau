from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_membership
from app.models import Fridge, InviteCode, Membership, User
from app.routers.auth import _find_valid_code, _gen_unique_code
from app.schemas import (
    FridgeCreateIn,
    FridgeOut,
    InviteCodeCreateIn,
    InviteCodeOut,
    JoinIn,
    JoinOut,
    MemberOut,
    OkOut,
)
from app.security import now_utc

router = APIRouter(prefix="/fridges", tags=["fridges"])

MEMBER_LIMIT = 10


def _require_owner(db: Session, user: User, fridge_id: int) -> Fridge:
    fridge = db.get(Fridge, fridge_id)
    if fridge is None:
        raise HTTPException(status_code=404, detail="冰箱不存在")
    if fridge.owner_id != user.id:
        raise HTTPException(status_code=403, detail="需要冰箱 owner 权限")
    return fridge


@router.post("", response_model=FridgeOut, status_code=201)
def create_fridge(body: FridgeCreateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fridge = Fridge(name=body.name, owner_id=user.id)
    db.add(fridge)
    db.flush()
    db.add(Membership(user_id=user.id, fridge_id=fridge.id, role="owner"))
    db.commit()
    db.refresh(fridge)
    return FridgeOut(fridge_id=fridge.id, name=fridge.name, role="owner", status=fridge.status)


@router.get("", response_model=list[FridgeOut])
def list_my_fridges(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Fridge, Membership.role)
        .join(Membership, Membership.fridge_id == Fridge.id)
        .where(Membership.user_id == user.id)
        .order_by(Fridge.id)
    ).all()
    return [
        FridgeOut(fridge_id=f.id, name=f.name, role=role, status=f.status)
        for f, role in rows
    ]


@router.get("/{fridge_id}/members", response_model=list[MemberOut])
def list_members(
    fridge_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if get_membership(db, user.id, fridge_id) is None:
        raise HTTPException(status_code=403, detail="不是该冰箱成员")
    rows = db.execute(
        select(Membership, User.username)
        .join(User, User.id == Membership.user_id)
        .where(Membership.fridge_id == fridge_id)
        .order_by(Membership.joined_at)
    ).all()
    return [
        MemberOut(user_id=m.user_id, username=name, role=m.role, joined_at=m.joined_at)
        for m, name in rows
    ]


@router.post("/{fridge_id}/invite-codes", response_model=InviteCodeOut, status_code=201)
def create_fridge_invite(
    fridge_id: int,
    body: InviteCodeCreateIn | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_owner(db, user, fridge_id)
    days = body.expires_in_days if body else 30
    expires_at = now_utc() + timedelta(days=days)
    inv = _gen_unique_code(db, "fridge", user.id, expires_at, fridge_id=fridge_id)
    return InviteCodeOut(code=inv.code, expires_at=inv.expires_at)


@router.post("/join", response_model=JoinOut)
def join_fridge(body: JoinIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    inv = _find_valid_code(db, body.invite_code, "fridge")
    if inv is None or inv.fridge_id is None:
        raise HTTPException(status_code=403, detail="邀请码无效或已撤销")
    fridge = db.get(Fridge, inv.fridge_id)
    if fridge is None or fridge.status != "active":
        raise HTTPException(status_code=403, detail="邀请码无效或已撤销")

    if get_membership(db, user.id, fridge.id) is not None:
        raise HTTPException(status_code=400, detail="已是该冰箱成员")

    member_count = len(
        db.scalars(select(Membership).where(Membership.fridge_id == fridge.id)).all()
    )
    if member_count >= MEMBER_LIMIT:
        raise HTTPException(status_code=403, detail=f"冰箱成员已满（上限 {MEMBER_LIMIT} 人）")

    db.add(Membership(user_id=user.id, fridge_id=fridge.id, role="member"))
    inv.used_count += 1
    db.commit()
    return JoinOut(fridge_id=fridge.id, name=fridge.name, role="member")


@router.delete("/{fridge_id}/members/{user_id}", response_model=OkOut)
def remove_member(
    fridge_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fridge = _require_owner(db, user, fridge_id)
    if user_id == fridge.owner_id:
        raise HTTPException(status_code=400, detail="不能移除 owner")
    m = get_membership(db, user_id, fridge_id)
    if m is None:
        raise HTTPException(status_code=404, detail="该用户不是冰箱成员")
    # 留痕：成员的 FridgeEvent.actor_id 由外键 SET NULL 保留署名（015）
    db.delete(m)
    db.commit()
    return OkOut()


@router.post("/{fridge_id}/archive", response_model=OkOut)
def archive_fridge(
    fridge_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    fridge = _require_owner(db, user, fridge_id)
    fridge.status = "archived"
    db.commit()
    return OkOut()


@router.post("/{fridge_id}/unarchive", response_model=OkOut)
def unarchive_fridge(
    fridge_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    fridge = _require_owner(db, user, fridge_id)
    fridge.status = "active"
    db.commit()
    return OkOut()


def accessible_fridge_ids(db: Session, user: User, fridge_id_param: str) -> list[int]:
    """聚合视图/推荐共用的范围解析：归档冰箱永远不在范围内。021 复用。"""
    if fridge_id_param == "all":
        return (
            db.scalars(
                select(Fridge.id)
                .join(Membership, Membership.fridge_id == Fridge.id)
                .where(Membership.user_id == user.id, Fridge.status == "active")
            ).all()
        )
    try:
        fid = int(fridge_id_param)
    except ValueError:
        raise HTTPException(status_code=400, detail="fridge_id 非法")
    fridge = db.get(Fridge, fid)
    if fridge is None or get_membership(db, user.id, fid) is None:
        raise HTTPException(status_code=404, detail="冰箱不存在")
    if fridge.status != "active":
        raise HTTPException(status_code=403, detail="冰箱已归档")
    return [fid]


@router.get("/items")
def list_items(
    fridge_id: str = "all",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """017 填充真实食材数据；此票打通路由与权限，返回空列表。"""
    accessible_fridge_ids(db, user, fridge_id)
    return []
