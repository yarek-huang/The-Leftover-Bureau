from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_membership
from app.models import Fridge, FridgeEvent, StockItem, User
from app.routers.items import _log_event, _to_out
from app.schemas import ItemPatchIn, StockItemOut

router = APIRouter(prefix="/items", tags=["items"])


def _get_item_with_access(
    db: Session, user: User, item_id: int
) -> tuple[StockItem, Fridge]:
    item = db.get(StockItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="条目不存在")
    fridge = db.get(Fridge, item.fridge_id)
    if fridge is None or get_membership(db, user.id, item.fridge_id) is None:
        raise HTTPException(status_code=404, detail="条目不存在")
    if fridge.status != "active":
        raise HTTPException(status_code=403, detail="冰箱已归档")
    return item, fridge


@router.patch("/{item_id}", response_model=StockItemOut)
def patch_item(
    item_id: int,
    body: ItemPatchIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """行内编辑（02 权限矩阵：member 与 owner 同权）。只更新显式传入的字段。"""
    item, fridge = _get_item_with_access(db, user, item_id)
    changed = False
    for field in ("name", "quantity", "zone", "state", "expiry_date"):
        if field in body.model_fields_set:
            setattr(item, field, getattr(body, field))
            changed = True
    if changed:
        db.flush()
        _log_event(db, item.fridge_id, user.id, item, "updated")
        db.commit()
        db.refresh(item)
    return _to_out(item, fridge.name)


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    action: str = "deleted",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除/已用/丢弃：写 FridgeEvent 留痕（带 snapshot）后移出在库。

    action: consumed | discarded | deleted（默认 deleted）。
    """
    if action not in ("consumed", "discarded", "deleted"):
        raise HTTPException(status_code=400, detail="action 非法")
    item, _ = _get_item_with_access(db, user, item_id)
    _log_event(db, item.fridge_id, user.id, item, action)
    db.delete(item)
    db.commit()
    return {"ok": True}
