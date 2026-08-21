# 04 · 食谱与审核

> 来源决策：005 食谱推荐模型、013 审核工作流、002 V1 切片（统一库+现场生成存私有）。

## Recipe 模型

见 `01-domain-model.md`。精简字段：
- title / steps / duration_min / servings / difficulty(easy/medium/hard)
- **不建标签体系**（菜系/口味不设用户标签维度）。
- **荤素派生字段** meat_type(meat/veg/mixed)：入库时 AI 顺手标，可改，仅供套餐搭配。

### RecipeIngredientLine
- name（自由文本）+ quantity（自由文本）+ role（main/seasoning）
- role 自建时用户标、AI 生成时模型标、可改。

## 食谱归属

- 食谱**属用户不属冰箱**（003）。
- 私有（private）食谱仅作者可见；提交过审后 approved 对全平台公开。
- 盛宴模式现场生成的食谱自动存入作者的私有库（private），想公开再走提交审核（002 Q10）。

## 状态机（013）

```
private → pending → approved（全平台公开）
                 ↘ rejected（带拒绝理由）→ 可修改后重提 → pending
```
- admin 直接创建的食谱**跳过队列**直接 approved（admin 建种子/起步食谱不必自审）。

## 种子食谱（修订 002）

- **V1 不做 AI 批量生成种子**——Yk 上线后通过 admin 创建入口手动批量添加（直接 approved，跳过队列）。
- 库空起步：极速清场在库空/无匹配时降级为 LLM 现场生成"出清方案"（详见 05）。

## 审核工作流（013）

### admin 权限范围
- 审核 + 下架已公开食谱 + 编辑种子食谱 + 重置用户密码（010）。
- admin 可转让、可任命多个（010）。

### 审核后台（极简）
- 待审列表 + 食谱全貌预览 + 通过/驳回（驳回填理由）按钮，**仅此**。不做批量审核。

### 反馈
- **站内标记**：提交者个人页看到自己食谱的状态 + 理由，无推送。

### 审核标准
- 不成文，admin 个人判断。

## API 契约草案

### 创建食谱
```
POST /api/recipes
Body: { title, steps, duration_min?, servings?, difficulty, ingredient_lines: [{name, quantity, role}], submit_for_review? }
→ 201 { id, status: "private" | "pending" }
```
- submit_for_review=true → status=pending；否则 private。
- admin 创建 → 直接 approved。

### 提交审核
```
POST /api/recipes/{id}/submit
→ 200 { status: "pending" }
```

### 审核
```
POST /api/admin/recipes/{id}/review
Body: { action: "approve" | "reject", reason? }
Auth: admin
→ 200 { status }
```

### 下架（admin）
```
POST /api/admin/recipes/{id}/unpublish
→ 200 { status: "private" }  // 退回私有
```

### 我的食谱（含状态+理由）
```
GET /api/me/recipes
→ 200 [{ id, title, status, rejection_reason? }]
```

## 验收用例

1. 妻子自建"番茄炒蛋"（私有）→ 提交审核 → Yk(admin) 在待审列表看到 → 预览 → 通过 → 全平台可见。
2. Yk 驳回某食谱（理由"主料不全"）→ 作者个人页看到 rejected+理由 → 改后重提 → pending。
3. Yk(admin) 直接创建"红烧肉" → 跳过队列直接 approved → 立刻全平台可见。
4. 盛宴模式现场生成"创意烩饭" → 自动存私有 → Yk 想公开 → 提交审核。
