# 01 · 领域模型

> 来源决策：003 冰箱共享、004 食材条目、005 食谱推荐、013 审核工作流。词汇对齐 `CONTEXT.md`。

## 实体关系（ERD 草案）

```
User 1───* Membership *───1 Fridge
  │                          │
  │                          │ 1───* StockItem
  │                          │        (name, qty_text, zone, state, expiry_date)
  │                          │
  │                          └ 1───* FridgeEvent  (条目级留痕)
  │
  ├ 1───* Recipe  (食谱属用户不属冰箱)
  │        ├ 1───* RecipeIngredientLine (name, qty_text, role=主料/调料)
  │        └ 荤素派生字段 (derived, AI 标)
  │
  ├ 1───* CaseFile  (案件卷宗，做饭归档)
  │        └ 1───* CaseFileEntry (用了哪些食材、评价)
  │
  └ 1───* TasteSignal  (口味偏好信号，从卷宗派生)

ReviewQueue: Recipe.status=pending 的集合（视图，非独立表）
InviteCode: 两套独立 token —— RegistrationInviteCode（注册）/ FridgeInviteCode（入冰箱）
```

## 实体字段

### User
- `id`, `username` (unique), `password_hash`, `is_admin` (bool), `created_at`
- 无邮箱、无手机号。OAuth 绑定预留 `oauth_bindings` 表（V1 不实现，仅占位）。

### Fridge
- `id`, `name`, `owner_id` (FK User), `status` (active/archived), `created_at`
- 只归档不删除；归档可逆。

### Membership
- `id`, `user_id`, `fridge_id`, `role` (owner/member), `joined_at`
- 每冰箱上限 10 人。

### StockItem（单层，无字典）
- `id`, `fridge_id`, `name` (自由文本), `quantity` (自由文本), `zone` (freezer/fridge/pantry, 默认 fridge), `state` (raw/cooked/leftover), `expiry_date` (nullable, 手填可跳过), `created_by`, `created_at`, `updated_at`
- 无字典层、无归一化表。

### FridgeEvent（条目级留痕）
- `id`, `fridge_id`, `actor_id`, `stockitem_id`, `action` (created/updated/deleted/consumed/discarded), `snapshot` (JSON, 操作时的条目快照), `created_at`
- 成员离开留痕署名保留。

### Recipe
- `id`, `author_id` (FK User), `title`, `steps` (text), `duration_min` (nullable), `servings` (nullable), `difficulty` (easy/medium/hard), `meat_type` (derived: meat/veg/mixed, AI 标), `status` (private/pending/approved/rejected), `rejection_reason` (nullable), `created_at`, `updated_at`
- 食谱属用户不属冰箱。

### RecipeIngredientLine
- `id`, `recipe_id`, `name` (自由文本), `quantity` (自由文本), `role` (main/seasoning)

### CaseFile（案件卷宗）
- `id`, `fridge_id`, `author_id`, `cooked_at`, `rating` (1-5), `note` (text), `created_at`
- 完整版：手动归档 + 评价。

### CaseFileEntry
- `id`, `casefile_id`, `stockitem_name` (快照), `quantity_used` (text)

### InviteCode
- `id`, `code` (6 位), `type` (registration/fridge), `fridge_id` (nullable, fridge 类型才有), `created_by`, `expires_at`, `revoked` (bool), `used_count`
- 一码多人（fridge 类型）；registration 类型可设上限。

## 关键约束

- **无字典层**：StockItem.name 与 RecipeIngredientLine.name 都是自由文本，匹配靠 LLM 语义匹配（非精确 ID）。
- **食谱不属冰箱**：Recipe.author_id 指向 User；冰箱只通过 CaseFile 关联做饭历史。
- **留痕双轨**：FridgeEvent（条目级操作历史）+ CaseFile（卷宗级做饭记录）。
- **状态机**：Recipe.status ∈ {private, pending, approved, rejected}，rejected 可改后重提→pending。
