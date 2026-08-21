from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Recipe, User
from app.schemas import OkOut, ResetPasswordIn, ReviewIn, SetAdminIn, StatusOut
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


# ---- 食谱审核（013 极简后台：待审列表 + 通过/驳回填理由，仅此） ----


@router.get("/recipes/pending", response_model=list[dict])
def pending_recipes(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Recipe, User.username)
        .join(User, User.id == Recipe.author_id)
        .where(Recipe.status == "pending")
        .order_by(Recipe.id)
    ).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "author_name": name,
            "submitted_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r, name in rows
    ]


@router.post("/recipes/{recipe_id}/review", response_model=StatusOut)
def review_recipe(recipe_id: int, body: ReviewIn, db: Session = Depends(get_db)):
    """审核：pending → approved | rejected(带理由)。"""
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="食谱不存在")
    if recipe.status != "pending":
        raise HTTPException(status_code=400, detail=f"当前状态 {recipe.status} 不可审核")
    if body.action == "approve":
        recipe.status = "approved"
        recipe.rejection_reason = None
    else:
        if not body.reason:
            raise HTTPException(status_code=400, detail="驳回必须填理由")
        recipe.status = "rejected"
        recipe.rejection_reason = body.reason
    db.commit()
    return StatusOut(status=recipe.status)


@router.post("/recipes/{recipe_id}/unpublish", response_model=StatusOut)
def unpublish_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """下架：approved → private（退回作者私有库）。"""
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="食谱不存在")
    if recipe.status != "approved":
        raise HTTPException(status_code=400, detail=f"当前状态 {recipe.status} 不可下架")
    recipe.status = "private"
    db.commit()
    return StatusOut(status=recipe.status)
