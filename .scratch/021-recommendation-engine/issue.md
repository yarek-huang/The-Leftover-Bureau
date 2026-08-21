# 021 推荐引擎

- Labels: wayfinder:task
- Status: open
- Assignee: Yk
- Blocked-by: 17, 18, 19
- Parent: 1

## Question

实现 05 设计文档全部：规则打分器 + LLM 语义匹配/组套餐/剩菜改造 + 极速清场同步 + 饕餮盛宴异步 + Redis 缓存 + 库空降级 LLM 现场生成。

关联设计文档：`docs/design/05-recommendation.md`（双模式 + MealSet + 打分器 + 缓存 + 剩菜优先）、`011` 决议（硬依赖不降级/权重可调/签名缓存）、`013`（库空降级）。

### 范围

- 规则打分器：候选 approved 食谱，按主料覆盖率（StockItem.name ⟷ RecipeIngredientLine.name，LLM 语义匹配）/ 临期加权 / 口味信号（CaseFile 评价）排序；权重 `w_coverage/w_expiry/w_taste` 配置可调。
- LLM 组套餐：调 019 `LLMClient.chat`，json_object 输出 MealSet（2-4 菜 + 补购清单 + 剩菜 is_reheat/is_rework）。
- 极速清场 `POST /api/recommend/clear`：同步 ≤30s，LLM 失败直接报错（不降级规则兜底）。库空/无匹配 → LLM 现场生成存私有。
- 饕餮盛宴 `POST /api/recommend/feast` → 202 task_id，`GET /api/recommend/tasks/{id}` 轮询。
- Redis 缓存：冰箱食材签名（StockItem 集合哈希）作 key，食材变动失效；TTL 可配。
- 剩菜优先：state=leftover 的食材在 prompt 注入，优先翻热/改造方案。
- 口味信号：从 CaseFile 评价派生（V1 可先简化为好评菜系加权）。

### 验收

1. **临期五花肉**：通缉令 → 极速清场 → LLM 语义匹配"五花肉"↔"三层肉"食谱 → 套餐 + 无补购。
2. **半颗卷心菜**：盛宴 → 语义匹配"卷心菜/包菜/甘蓝" → 套餐含卷心菜菜 + 蛋花汤 + 米饭。
3. **不明剩菜盒**：state=leftover → 返回 is_reheat 或 is_rework 方案。
4. **库空降级**：新冰箱无食谱 → 盛宴 → LLM 现场生成存私有 → MealSet 返回。
5. **LLM 不可用**：调 GLM 失败 → 极速清场报错（无规则兜底）。
6. 食材变动 → 缓存失效，下次重算。
