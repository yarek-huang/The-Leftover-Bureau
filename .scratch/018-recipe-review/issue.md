# 018 食谱与审核工作流

- Labels: wayfinder:task
- Status: open
- Assignee: Yk
- Blocked-by: 15, 16
- Parent: 1

## Question

实现 04 设计文档全部：Recipe CRUD/状态机/提交审核/admin 审核/下架/admin 直建跳队列/荤素派生 AI 标。

关联设计文档：`docs/design/04-recipe-review.md`（状态机 + API + admin 权限）、`013` 决议（状态机/不成文标准/种子手动）、`005`（RecipeIngredientLine role + meat_type 派生）。

### 范围

- `POST /api/recipes`（创建，submit_for_review? → private|pending；admin 创建直接 approved）。
- `POST /api/recipes/{id}/submit`（private→pending）。
- `POST /api/admin/recipes/{id}/review`（approve|reject+reason）。
- `POST /api/admin/recipes/{id}/unpublish`（approved→private）。
- `GET /api/recipes`（公开库，approved only，按荤素/难度筛）、`GET /api/me/recipes`（我的，含 status+rejection_reason）。
- 荤素派生：创建时调 019 的 LLMClient 标 meat_type（019 未就绪先留 TODO 占位，019 完成后补）。

### 验收

1. 妻子建"番茄炒蛋"(private) → submit → Yk(admin) 待审列表见 → 通过 → 公开库可见。
2. Yk 驳回某食谱(填理由) → 作者个人页见 rejected+理由 → 改后重提 → pending。
3. Yk(admin) 直建"红烧肉" → 跳队列直接 approved → 立刻公开可见。
4. rejected 重提 → pending（状态机闭环）。
