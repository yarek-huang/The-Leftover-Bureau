# 017 食材管理与录入（文字通道）

- Labels: wayfinder:task
- Status: open
- Assignee: Yk
- Blocked-by: 15, 16
- Parent: 1

## Question

实现 03 设计文档的食材 CRUD/批量文字录入/聚合视图/红色通缉令/FridgeEvent 留痕。拍照通道在 020（依赖 019）。

关联设计文档：`docs/design/03-ingredient-mgmt.md`（StockItem 模型 + 文字录入 + 通缉令 + API）、`004` 决议（单层无字典/手填到期日/留痕）。

### 范围

- `POST /api/fridges/{id}/items`（批量录入，body items[]）。
- `GET /api/fridges/items?fridge_id=all|<id>`（聚合/单冰箱，含 fridge_name）。
- `PATCH /api/items/{id}`、`DELETE /api/items/{id}?action=consumed|discarded|deleted`（删除/消耗写 FridgeEvent 留痕，带 snapshot）。
- `GET /api/fridges/expiry-alerts`（跨冰箱 3 天内到期，按 days_left 排序）。
- 行内编辑/删除（前端在 022，此票只给 API）。
- 不含拍照识别（020）。

### 验收

1. **临期五花肉**：录入"五花肉、约300g、freezer、raw、expiry=今天+2天" → 通缉令面板出现 → days_left=2。
2. **半颗卷心菜**：录入"半个卷心菜、fridge、raw、无到期日" → 聚合列表可见。
3. 删除一条标 action=discarded → FridgeEvent 写入 snapshot → 条目移出在库视图。
4. 聚合视图默认全部冰箱，切单冰箱只显该冰箱。
