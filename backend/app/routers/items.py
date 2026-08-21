from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_membership
from app.models import Fridge, FridgeEvent, StockItem, User
from app.schemas import BatchItemsIn, ExpiryAlertOut, StockItemOut
from app.routers.fridges import accessible_fridge_ids

router = APIRouter(prefix="/fridges", tags=["items"])


def _log_event(db: Session, fridge_id: int, actor_id: int, item: StockItem, action: str):
    db.add(
        FridgeEvent(
            fridge_id=fridge_id,
            actor_id=actor_id,
            stockitem_id=item.id,
            action=action,
            snapshot={
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "zone": item.zone,
                "state": item.state,
                "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
            },
        )
    )


def _require_active_member(db: Session, user: User, fridge_id: int) -> Fridge:
    fridge = db.get(Fridge, fridge_id)
    if fridge is None:
        raise HTTPException(status_code=404, detail="冰箱不存在")
    if get_membership(db, user.id, fridge_id) is None:
        raise HTTPException(status_code=403, detail="不是该冰箱成员")
    if fridge.status != "active":
        raise HTTPException(status_code=403, detail="冰箱已归档")
    return fridge


def _to_out(item: StockItem, fridge_name: str) -> StockItemOut:
    return StockItemOut(
        id=item.id,
        name=item.name,
        quantity=item.quantity,
        zone=item.zone,
        state=item.state,
        expiry_date=item.expiry_date,
        fridge_id=item.fridge_id,
        fridge_name=fridge_name,
    )


@router.post("/{fridge_id}/items", response_model=list[StockItemOut], status_code=201)
def batch_create_items(
    fridge_id: int,
    body: BatchItemsIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """批量文字录入（03 设计：多行表单一次提交）。拍照通道确认后的入库也走这里（020）。"""
    fridge = _require_active_member(db, user, fridge_id)
    created = []
    for row in body.items:
        item = StockItem(
            fridge_id=fridge_id,
            created_by=user.id,
            name=row.name,
            quantity=row.quantity,
            zone=row.zone,
            state=row.state,
            expiry_date=row.expiry_date,
        )
        db.add(item)
        db.flush()
        _log_event(db, fridge_id, user.id, item, "created")
        created.append(_to_out(item, fridge.name))
    db.commit()
    return created


@router.get("/items", response_model=list[StockItemOut])
def list_items(
    fridge_id: str = "all",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """聚合视图（默认全部活跃冰箱）/ 单冰箱。含 fridge_name 供前端分组显示。"""
    fids = accessible_fridge_ids(db, user, fridge_id)
    if not fids:
        return []
    rows = db.execute(
        select(StockItem, Fridge.name)
        .join(Fridge, Fridge.id == StockItem.fridge_id)
        .where(StockItem.fridge_id.in_(fids))
        .order_by(StockItem.expiry_date.nulls_last(), StockItem.id.desc())
    ).all()
    return [_to_out(item, name) for item, name in rows]


@router.get("/expiry-alerts", response_model=list[ExpiryAlertOut])
def expiry_alerts(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """红色通缉令：跨冰箱 3 天内到期（含已过期），按 days_left 升序。"""
    fids = accessible_fridge_ids(db, user, "all")
    if not fids:
        return []
    today = date.today()
    horizon = today + timedelta(days=3)
    rows = db.execute(
        select(StockItem, Fridge.name)
        .join(Fridge, Fridge.id == StockItem.fridge_id)
        .where(
            StockItem.fridge_id.in_(fids),
            StockItem.expiry_date.isnot(None),
            StockItem.expiry_date <= horizon,
        )
        .order_by(StockItem.expiry_date)
    ).all()
    return [
        ExpiryAlertOut(
            **_to_out(item, name).model_dump(),
            days_left=(item.expiry_date - today).days,
        )
        for item, name in rows
    ]
