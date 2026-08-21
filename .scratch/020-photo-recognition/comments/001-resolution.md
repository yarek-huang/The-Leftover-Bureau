# 020 Resolution · 拍照识别通道

- 状态：**完成，真机验收通过**
- 日期：2026-08-22

## 产出

| 文件 | 内容 |
|---|---|
| `app/storage.py` | MinIO 封装：`get_minio`/`ensure_bucket`（幂等）/`put_image`（key=`images/recognize/{uid}/{ts}.{ext}`，content-type 透传）。内网 http secure=False，公网迁移改 true+TLS 注释在位 |
| `app/routers/recognize.py` | `POST /api/recognize`（multipart image）：校验格式/大小（10MB，白名单 jpeg/png/webp/gif/heic）→ MinIO 存档（失败不阻断识别）→ base64 data url → `vision_structured` → `{items:[{name,confidence}]}`；LLMError → 空 items + 日志留痕（前端退文字表单，03 设计） |

**人工确认闸门**（002/004 决议）：本端点只返回候选，绝不写 StockItem；入库必须走 017 的 `POST /api/fridges/{id}/items`（前端逐条确认后调，UI 在 022）。

## Prompt 调优（真机迭代两轮）

初版 prompt 把熟食排除在"食材"外 → 韩式烤五花肉照稳定返回空。修正规则：
1. 生鲜/熟食/剩菜都算食物
2. 生鲜报常用名（五花肉、卷心菜）
3. **熟食能认出菜名就报菜名（烤五花肉、红烧肉）；认不出/容器混合剩菜 → 剩菜盒**
4. 完全无食物才空数组

## 真机验收（GLM-4.6V-Flash @ 标准端点）

| 用例 | 结果 |
|---|---|
| 生五花肉（Schweinebauch 生照） | `{五花肉, 0.95}` 3-10s ✓ |
| 熟食烤五花（韩式 samgyeopsal） | `{烤五花肉, 0.95}` 6.4s ✓（新 prompt 生效） |
| 生鲜卷心菜 | `{卷心菜, 0.99}` 11.8s ✓ |
| 纯色拼图（无食物） | `{items:[]}` ✓（退文字表单契约） |
| 闸门：全程识别后 StockItem=0 | ✓ |
| MinIO 存档 | 每次识别落一对象 ✓ |

验收 1/3/4 API 侧全过；验收 2 的"改成红烧肉剩菜+state=leftover 入库"与推荐联动属 022 前端 + 021 推荐范围（入库 API 即 017 批量端点，已验收）。

## 踩坑

- **智谱免费档偶发秒拒**：密集连续大图请求会被 API 拒（~2s 失败），间隔数秒即恢复——测试脚本加 sleep(3) 规避；生产风险低（人工拍照天然有间隔），若 022 上线后复现再加重试。
- **`except LLMError` 静默空 items 会掩盖真实错误**：初判"模型不识别熟食"实际混有限流拒——已加 `logging.exception` 留痕，排查靠日志不靠猜。
- 测试图必须真实照片：纯色/几何拼图会被 GLM 正确判为"无食物"，测不出识别力。
- rebuild 容器会清 /tmp：测试图片要重拷（docker compose cp）。

## 给 022 的交互契约

```
POST /api/recognize (multipart image, Bearer token)
→ 200 { items: [{name, confidence}] }   // 空 = 退文字表单预填
→ 每条 name 可改、quantity 手填、zone/state/expiry 选
→ 确认后 POST /api/fridges/{id}/items {items:[...]}  // 017 批量入库
```
