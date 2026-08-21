# 015 数据库 schema + ORM models

- Labels: wayfinder:task
- Status: open
- Assignee: Yk
- Blocked-by: 14
- Parent: 1

## Question

把 01 领域模型的全部实体落成 SQLAlchemy ORM + 首个 alembic migration。

关联设计文档：`docs/design/01-domain-model.md`（实体/字段/约束）、`CONTEXT.md`（词汇对齐）。

### 范围

`backend/app/models/` 下建全部 ORM：
- User（username unique, password_hash, is_admin, created_at）
- Fridge（name, owner_id, status[active/archived], created_at）
- Membership（user_id, fridge_id, role[owner/member], joined_at）
- StockItem（fridge_id, name 自由文本, quantity 自由文本, zone[freezer/fridge/pantry], state[raw/cooked/leftover], expiry_date nullable, created_by, created_at, updated_at）
- FridgeEvent（fridge_id, actor_id, stockitem_id, action[created/updated/deleted/consumed/discarded], snapshot JSON, created_at）
- Recipe（author_id, title, steps, duration_min nullable, servings nullable, difficulty[easy/medium/hard], meat_type[meat/veg/mixed], status[private/pending/approved/rejected], rejection_reason nullable, created_at, updated_at）
- RecipeIngredientLine（recipe_id, name 自由文本, quantity 自由文本, role[main/seasoning]）
- CaseFile（fridge_id, author_id, cooked_at, rating 1-5, note, created_at）
- CaseFileEntry（casefile_id, stockitem_name 快照, quantity_used text）
- InviteCode（code 6 位, type[registration/fridge], fridge_id nullable, created_by, expires_at, revoked bool, used_count int）
- TasteSignal（预留：从卷宗派生，V1 可先占位表或留到 021）
- OAuthBinding（预留占位表，V1 不实现）
- 关系 + 外键 + check 约束（role/status/zone/state 枚举）。
- 首个 alembic migration（`alembic revision --autogenerate`）。

### 验收

1. `docker-compose exec backend alembic upgrade head` → 全表建成，`\dt` 列出全部。
2. 枚举列插错值 → DB 拒（check 约束生效）。
3. 关系可级联查（User→Membership→Fridge）。
