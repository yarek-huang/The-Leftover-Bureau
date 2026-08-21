from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.llm import LLMError, llm_client
from app.models import Recipe, RecipeIngredientLine, User
from app.schemas import (
    RecipeCreateIn,
    RecipeLineOut,
    RecipeOut,
    StatusOut,
)

router = APIRouter(tags=["recipes"])


class _MeatTypeOut(BaseModel):
    meat_type: str


def derive_meat_type(lines: list) -> str:
    """荤素派生（005 决议）：LLM 按主料标 meat/veg/mixed，仅供套餐搭配、可改。

    非硬依赖：LLM 不可用时静默 fallback mixed（区别于推荐的报错不降级，011）。
    """
    mains = "; ".join(
        f"{ln.name} {ln.quantity}".strip() for ln in lines if ln.role == "main"
    )
    if not mains:
        return "mixed"
    prompt = (
        "以下是这道菜的主料清单，判断荤素类型：\n"
        f"{mains}\n\n"
        "规则：含明显肉类/海鲜→meat；纯植物原料（蛋奶素算 veg）→veg；"
        "混合或难判断→mixed。只回类型。"
    )
    try:
        out = llm_client.chat_structured(
            prompt + "\nmeat_type 只能取 meat/veg/mixed 三个值之一。",
            _MeatTypeOut,
        )
        if out.meat_type in ("meat", "veg", "mixed"):
            return out.meat_type
    except LLMError:
        pass
    return "mixed"


def _to_out(recipe: Recipe, author_name: str) -> RecipeOut:
    return RecipeOut(
        id=recipe.id,
        title=recipe.title,
        steps=recipe.steps,
        duration_min=recipe.duration_min,
        servings=recipe.servings,
        difficulty=recipe.difficulty,
        meat_type=recipe.meat_type,
        status=recipe.status,
        rejection_reason=recipe.rejection_reason,
        author_id=recipe.author_id,
        author_name=author_name,
        ingredient_lines=[
            RecipeLineOut(
                id=ln.id, name=ln.name, quantity=ln.quantity, role=ln.role
            )
            for ln in recipe.ingredient_lines
        ],
    )


def _get_recipe(db: Session, recipe_id: int) -> Recipe:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="食谱不存在")
    return recipe


@router.post("/recipes", response_model=RecipeOut, status_code=201)
def create_recipe(
    body: RecipeCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建食谱。admin 创建直接 approved（跳队列建种子，013）；submit_for_review → pending；否则 private。"""
    if user.is_admin:
        status = "approved"
    elif body.submit_for_review:
        status = "pending"
    else:
        status = "private"
    recipe = Recipe(
        author_id=user.id,
        title=body.title,
        steps=body.steps,
        duration_min=body.duration_min,
        servings=body.servings,
        difficulty=body.difficulty,
        meat_type=derive_meat_type(body.ingredient_lines),
        status=status,
    )
    db.add(recipe)
    db.flush()
    for ln in body.ingredient_lines:
        db.add(
            RecipeIngredientLine(
                recipe_id=recipe.id,
                name=ln.name,
                quantity=ln.quantity,
                role=ln.role,
            )
        )
    db.commit()
    db.refresh(recipe)
    return _to_out(recipe, user.username)


@router.get("/recipes", response_model=list[RecipeOut])
def list_public_recipes(
    meat_type: str | None = None,
    difficulty: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """公开库：approved only（002 统一库决议），按荤素/难度筛选。"""
    q = (
        select(Recipe, User.username)
        .join(User, User.id == Recipe.author_id)
        .where(Recipe.status == "approved")
        .order_by(Recipe.id.desc())
    )
    if meat_type is not None:
        q = q.where(Recipe.meat_type == meat_type)
    if difficulty is not None:
        q = q.where(Recipe.difficulty == difficulty)
    return [_to_out(r, name) for r, name in db.execute(q).all()]


@router.get("/me/recipes", response_model=list[RecipeOut])
def my_recipes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """我的食谱：全部状态可见，含 rejection_reason（站内标记反馈，013）。"""
    rows = db.execute(
        select(Recipe, User.username)
        .join(User, User.id == Recipe.author_id)
        .where(Recipe.author_id == user.id)
        .order_by(Recipe.id.desc())
    ).all()
    return [_to_out(r, name) for r, name in rows]


@router.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """详情：approved 全员可见；其余状态仅作者与 admin（审核预览用）。"""
    recipe = _get_recipe(db, recipe_id)
    if recipe.status != "approved" and recipe.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=404, detail="食谱不存在")
    author = db.get(User, recipe.author_id)
    return _to_out(recipe, author.username)


@router.post("/recipes/{recipe_id}/submit", response_model=StatusOut)
def submit_recipe(
    recipe_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交审核：private|rejected → pending（状态机闭环）。admin 的已 approved 食谱无需提交。"""
    recipe = _get_recipe(db, recipe_id)
    if recipe.author_id != user.id:
        raise HTTPException(status_code=403, detail="只能操作自己的食谱")
    if recipe.status not in ("private", "rejected"):
        raise HTTPException(status_code=400, detail=f"当前状态 {recipe.status} 不可提交审核")
    recipe.status = "pending"
    recipe.rejection_reason = None
    db.commit()
    return StatusOut(status=recipe.status)
