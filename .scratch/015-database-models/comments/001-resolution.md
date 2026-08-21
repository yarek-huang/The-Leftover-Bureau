# 015 Resolution · 数据库 schema + ORM models

- 状态：**完成，验收通过**
- 日期：2026-08-21

## 产出

`backend/app/models/` 全部 ORM 落地，alembic 首个 migration `07aa1113d06a_init_schema.py`：

| 表 | 来源 model |
|---|---|
| users | User |
| oauth_bindings | OAuthBinding（预留占位） |
| fridges | Fridge |
| memberships | Membership |
| invite_codes | InviteCode |
| stock_items | StockItem |
| fridge_events | FridgeEvent |
| recipes | Recipe |
| recipe_ingredient_lines | RecipeIngredientLine |
| case_files | CaseFile |
| case_file_entries | CaseFileEntry |

外加 `alembic_version`（迁移版本表），共 12 张。

设计落地：
- 枚举列用 `String + CheckConstraint`（非 SQLAlchemy Enum，迁移可移植性更好）。
- 留痕双轨：FridgeEvent（条目级，`ondelete=SET NULL` 保留署名）+ CaseFile（卷宗级）。
- 食谱不属冰箱：Recipe.author_id 指向 User；CaseFile 才关联 fridge。
- 剩菜/临期：StockItem.state(zone)/expiry_date 字段就位（017/021 用）。
- 关系级联：Fridge→Memberships / Recipe→IngredientLines / CaseFile→Entries 均 `cascade=all, delete-orphan`。

## 验收（全过）

1. `alembic upgrade head` → 全 11 业务表建成（`\dt` 列出）✓
2. check 约束：`INSERT fridges status='bogus'` → 被 `fridge_status_chk` 拒 ✓
3. 级联：User→Membership→Fridge join 查询返回 yk/home/owner ✓

## 实现中修正的 bug

**ORM `default` vs `server_default`**：初版只有 Python 端 `default=False`，裸 SQL/迁移不带值时 DB 拿 NULL 违反 NOT NULL（`INSERT users` 不带 is_admin 报 not-null）。给所有有默认值的 NOT NULL 列加 `server_default`：
- bool 列 `server_default="false"`（is_admin/revoked）
- 字符串默认 `server_default="..."`（status/role/zone/state/difficulty/meat_type/quantity 等）
- 整数 `server_default="0"`（used_count）
- created_at/joined_at `server_default=func.now()`

修正后裸 SQL `INSERT users(username,password_hash)` 成功，is_admin 自动取 false。

## 脚手架补件

- 补 `backend/alembic/script.py.mako`（alembic init 模板，014 漏建）。
- `alembic/env.py` 加 `import app.models` 让所有表注册到 `Base.metadata` 供 autogenerate。
- `models/__init__.py` 集中导出全部模型类。

## 下一步

016（账号与冰箱）已 unblocked（依赖 015），是 frontier；017/018 也随后 unblocked。
