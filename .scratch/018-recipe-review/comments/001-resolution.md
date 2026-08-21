# 018 Resolution · 食谱与审核工作流

- 状态：**完成，验收通过（19/19 主断言 + 3 边界补验）**
- 日期：2026-08-21

## 产出

| 文件 | 内容 |
|---|---|
| `app/routers/recipes.py` | 创建（admin 直建跳队列 approved / submit_for_review→pending / 默认 private）、公开库列表（approved only + 荤素/难度筛选）、`GET /api/me/recipes`（全状态+rejection_reason）、详情（approved 全员/其余作者与 admin）、`POST /{id}/submit`（private\|rejected→pending，重提清理由） |
| `app/routers/admin.py` 扩展 | `GET /admin/recipes/pending` 待审列表、`POST /admin/recipes/{id}/review`（approve\|reject，reject 必填理由）、`POST /admin/recipes/{id}/unpublish`（approved→private） |
| `app/schemas.py` 扩展 | RecipeLineIn/RecipeCreateIn/RecipeLineOut/RecipeOut/StatusOut/ReviewIn |

## 设计落地要点

- **状态机**（013）：private→pending→approved；pending→rejected(带理由)→重提→pending；admin 下架 approved→private。非法迁移全拒（approved 重提 400、非 pending 审核 400）。
- **admin 直建跳队列**：create 时 `user.is_admin → status=approved`（种子食谱入口，013 修订 002）。
- **归属**：食谱属用户不属冰箱（003）；审核预览走详情端点的 admin 可见性。
- **可见性**：approved 全员；private/pending/rejected 仅作者与 admin（他人 404 不泄漏存在性）。
- **meat_type**：LLM 派生留 `derive_meat_type()` TODO 占位 mixed，019 就绪后补一行调用。

## 验收（全过）

1. 妻子建番茄炒蛋(private)→submit→admin 待审列表见→approve→双方公开库可见 ✓
2. 驳回（无理由 400 / 填理由 rejected）→作者 me/recipes 见 rejected+理由 ✓
3. admin 直建红烧肉→直接 approved 进公开库，待审队列不增 ✓
4. rejected 重提→pending 闭环 ✓
- 边界：非 admin 审核 403、非作者 submit 403、他人看 private/pending 404、下架退私有、难度筛选 ✓

## 测试脚本两处假阳性说明

首轮 19/21，两个 fail 均为脚本缺陷非代码 bug：①"私有非作者不可见"用 yk(admin) 测——admin 本有预览权，200 正确；换第三普通用户 kid 验证 404 通过。②"非作者 submit"脚本把两次 curl 状态码拼接输出。修正后全绿。

## 下一步

019（AI provider 层）unblocked——018 的 meat_type TODO 等 019 的 LLMClient 补齐。
