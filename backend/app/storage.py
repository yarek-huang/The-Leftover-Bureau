"""MinIO 对象存储封装（08 部署设计：图片缓存层，可换云 OSS）。

ensure_bucket 幂等建桶；put_image 存原图（content-type 透传）。
对象 key: images/recognize/{user_id}/{ts}.{ext}
"""

import io
from datetime import datetime

from minio import Minio

from app.config import settings

_client: Minio | None = None


def get_minio() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False,  # 内网 http；公网迁移改 true + TLS
        )
    return _client


def ensure_bucket() -> None:
    client = get_minio()
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


def put_image(user_id: int, data: bytes, content_type: str) -> str:
    """返回对象 key。识别图不设过期，V1 量级小不做生命周期清理。"""
    ensure_bucket()
    ext = "jpg"
    for e in ("jpeg", "png", "webp", "gif", "heic"):
        if e in content_type:
            ext = "jpg" if e == "jpeg" else e
            break
    ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
    key = f"images/recognize/{user_id}/{ts}.{ext}"
    get_minio().put_object(
        settings.minio_bucket, key, io.BytesIO(data), length=len(data),
        content_type=content_type,
    )
    return key
