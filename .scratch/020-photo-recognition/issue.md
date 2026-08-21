# 020 拍照识别通道

- Labels: wayfinder:task
- Status: closed
- Assignee: agent
- Blocked-by: 19
- Parent: 1

## Question

实现 03 设计文档的拍照识别通道：上传图 → MinIO → GLM-4.6V-Flash 识别名称+置信度 → 前端逐条确认 → 入库。识别结果绝不直接入库（人工确认闸门）。

关联设计文档：`docs/design/03-ingredient-mgmt.md`（拍照流 + 识别接口契约）、`008` 调研（GLM-4.6V-Flash json_object）、`004`（人工确认闸门）。

### 范围

- `POST /api/recognize`（multipart image）：图传 MinIO → 调 019 `LLMClient.vision` → prompt 要求 json_object `{"items":[{"name","confidence"}]}` → 返回名称+置信度（不含量量）。
- 识别失败/空 → 返回空 items，前端退回文字表单预填。
- 前端拍照流（在 022 落地 UI，此票先给 API + 交互契约）：拍/上传 → loading → 识别结果列表（每条 name 可改、quantity 手填、zone/state/expiry 选）→ 逐条确认 → 调 017 批量入库 API。
- 不含：数量估计（不可靠，交人工）、直接入库（禁止）。

### 验收

1. 拍"五花肉+卷心菜" → 识别返回 [{五花肉,0.9},{卷心菜,0.85}] → 逐条补 quantity/zone/state → 确认入库。
2. **不明剩菜盒**：拍照 → [{剩菜盒,0.6}] → 改成"红烧肉剩菜"+state=leftover → 入库 → 021 推荐带剩菜改造方案。
3. 识别返回空 → 前端退文字表单，预填已识别部分。
4. 识别结果不直接写库（确认前无 StockItem 产生）。
