"""拍照识别通道（03 设计 / 020 票）。

流程：multipart 图 → MinIO 存档 → LLMClient.vision_structured 识别名称+置信度。
**识别结果绝不直接入库**（002 人工确认闸门）——本端点只返回候选列表，
入库必须走 017 的 POST /api/fridges/{id}/items（前端逐条确认后调）。
"""

import base64

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.llm import LLMError, llm_client
from app.models import User
from app.storage import put_image

router = APIRouter(tags=["recognize"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif", "image/heic"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB

PROMPT = (
    "识别这张照片里的全部食材或食物（生鲜、熟食、剩菜都算）。规则：\n"
    "1. 只报名称和置信度，不要数量、不要估计重量\n"
    "2. 生鲜食材用中文常用名（如 五花肉、卷心菜、番茄）\n"
    "3. 做好的菜/熟食：能认出是什么菜就报菜名（如 烤五花肉、红烧肉、炒青菜）；"
    "认不出或装在容器里的混合剩菜，统一叫 剩菜盒\n"
    "4. 只有照片里完全没有任何食物/食材时，items 才为空数组\n"
    '输出形如 {"items":[{"name":"五花肉","confidence":0.92}]}'
)


class RecItem(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    confidence: float = Field(ge=0, le=1)


class RecOut(BaseModel):
    items: list[RecItem]


@router.post("/recognize", response_model=RecOut)
def recognize(
    image: UploadFile,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    data = image.file.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="图片超过 10MB")
    if not data:
        raise HTTPException(status_code=400, detail="空文件")

    # 存档（识别失败也留图，便于排查 prompt 质量）
    try:
        put_image(user.id, data, image.content_type)
    except Exception:
        pass  # 存储不可用不阻断识别

    # data url 直传（免公网预签名，内网/公网通用）
    b64 = base64.b64encode(data).decode()
    mime = image.content_type
    url = f"data:{mime};base64,{b64}"

    try:
        out = llm_client.vision_structured(url, PROMPT, RecOut)
    except LLMError:
        # 识别失败 → 空 items：前端退回文字表单（03 设计）
        import logging

        logging.getLogger(__name__).exception("识别失败 user=%s", user.id)
        return RecOut(items=[])
    return out
