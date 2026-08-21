# 017 Resolution · 食材管理与录入（文字通道）

- 状态：**完成，验收通过（15/15）**
- 日期：2026-08-21

## 产出

| 文件 | 内容 |
|---|---|
| `app/routers/items.py` | 批量录入 `POST /api/fridges/{id}/items`、聚合列表 `GET /api/fridges/items?fridge_id=all|<id>`、红色通缉令 `GET /api/fridges/expiry-alerts`、`_log_event`/`_to_out` 共用件 |
| `app/routers/item_ops.py` | `PATCH /api/items/{id}`（行内编辑，只更新显式传入字段）、`DELETE /api/items/{id}?action=consumed\|discarded\|deleted`（留痕+移出在库） |
| `app/schemas.py` 扩展 | StockItemIn/BatchItemsIn/StockItemOut/ItemPatchIn/ExpiryAlertOut；zone/state 用 Literal 白名单 |
| `fridges.py` | 删掉 016 的 items 空壳（防路由遮蔽），`accessible_fridge_ids` 升级为 items 与 021 共用 |

## 设计落地要点

- **无字典层**：name/quantity 纯自由文本，无归一化（004）。
- **留痕全链路**：created/updated/consumed/discarded/deleted 均写 FridgeEvent，snapshot 存全字段 JSON（含 expiry_date isoformat）；actor 署名。
- **通缉令**：跨全部活跃冰箱、≤3 天（含已过期负数 days_left）、按到期升序；ExpiryAlertOut 继承 StockItemOut 加 days_left。
- **聚合排序**：expiry_date nulls_last（无到期日排最后）+ id desc（新录入靠前）。
- **权限**：录入/编辑/删除 = 成员即可（02 权限矩阵 owner/member 同权）；归档冰箱拒写拒读（403）。
- **PATCH 语义**：`model_fields_set` 判断显式传值，expiry_date 传 null 可清空。

## 验收（15/15 全过）

1. 临期五花肉（expiry=+2d, freezer, raw）→ 通缉令出现，days_left=2；过期豆腐 days_left=-1 ✓
2. 半颗卷心菜（无到期日）→ 聚合可见、fridge_name 正确 ✓
3. DELETE action=discarded → FridgeEvent 写入 snapshot（`discarded|豆腐`）→ 条目移出在库 ✓；created×3、updated×1 事件齐全 ✓
4. 聚合默认全部（3 条），切单冰箱只显该冰箱（2 条，无跨冰箱混入）✓

## 踩坑

- **并行 edit 同一文件互相覆盖**：一次消息里对 items.py 发了两个 edit，import 修复被另一处覆盖 → 容器 crash loop（NameError: ExpiryAlertOut）。同一文件的多处编辑必须串行或改用整文件重写。
- **psql `->>` 优先级**：`a || b ->> 'k'` 会把左侧整体当 jsonb 操作数，`(snapshot->>'name')` 加括号才行（校验脚本问题，非代码 bug）。
- **路由遮蔽**：016 的空壳 `GET /fridges/items` 若留在 fridges.py 会与 items.py 的真实实现冲突（FastAPI 同 path 先注册者赢），删旧换新。

## 下一步

018（食谱审核）unblocked；021（推荐引擎）的食材侧输入（聚合查询+accessible_fridge_ids+days_left 语义）已就位。
