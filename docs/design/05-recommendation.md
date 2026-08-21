# 05 · 推荐引擎

> 来源决策：005 食谱推荐模型、011 推荐引擎设计、013（库空降级 LLM 现场生成）、002（双模式 + 剩菜优先）。

## 双模式

| 模式 | 触发 | 数据源 | 时机 |
|---|---|---|---|
| 极速清场（Clear-It） | 临期/红色通缉令入口、用户主动 | 冰箱在库食材 | 同步返回 |
| 饕餮盛宴（Feast） | 主入口"给我推荐晚餐" | 冰箱食材 + 统一食谱库 | 异步返回 |

## 极速清场（Clear-It）

### 目标
用掉当前在库食材（尤其临期），最多差一个主料、附补购单。

### 流程
```
1. 规则打分器：候选食谱集
   - 从统一食谱库检索 approved 食谱
   - 按主料覆盖率(StockItem.name ⟷ RecipeIngredientLine.name, LLM 语义匹配)排序
   - 临期食材加权、熟剩食材加权
2. LLM 组套餐：2-4 菜套餐，确保主料全或差一附补购单
3. 返回 MealSet + 补购清单(可选)
```

### 库空 / 无匹配降级（013 修订 005）
- 统一食谱库无匹配（主料覆盖率 < 阈值）→ **降级 LLM 现场生成**"出清方案"。
- 现场生成食谱自动存私有（见 04），不公开。

### 同步返回
- 极速清场走同步 HTTP，超时（如 30s）报错给前端"请稍后重试"。

## 饕餮盛宴（Feast）

### 流程
```
1. 规则打分器：候选集（同上候选逻辑）
2. LLM 组套餐 + 剩菜改造方案
3. 异步：POST /api/recommend/feast → 202 { task_id }
   轮询 GET /api/recommend/tasks/{task_id} → 200 { MealSet } | 202 仍处理中
```

## 推荐结果结构（MealSet）

```
{
  mode: "clear" | "feast",
  dishes: [{
    recipe_id?,          // 库内匹配有，现场生成无
    title, steps,        // 现场生成则全量给
    matched_items: [{ stockitem_id, name }],  // 用了哪些冰箱食材
    missing_mains: [{ name }],                // 需补购的主料
    is_reheat: bool,                         // 剩菜翻热
    is_rework: bool                          // 剩菜改造重做
  }],
  pantry_list: [{ name }]                    // 补购清单
}
```

## 规则打分器（可调权重）

- **主料覆盖率**：StockItem.name ⟷ RecipeIngredientLine.name，靠 LLM 语义匹配（非精确名）。
- **临期加权**：days_left ≤ 3 的食材命中主料加分。
- **口味信号**：CaseFile 评价加权——做过且好评的菜系/食材组合加分。
- 三个权重 `w_coverage / w_expiry / w_taste` 存配置表，admin 可调。

## LLM 硬依赖（011）

- **不降级**：LLM 调用失败 → 直接报错给前端，V1 不做规则兜底。
- LLM 是推荐引擎的硬依赖（语义匹配 + 组套餐 + 现场生成均靠它）。

## 缓存（011）

- Redis 按冰箱食材签名缓存 LLM 响应。
- 签名 = 冰箱内 StockItem 集合的稳定哈希（name+zone+state+expiry_bucket）。
- 食材变动（增删改）→ 失效该冰箱缓存。
- TTL 可配（默认 6h）。

## 剩菜优先（002 + 004）

- StockItem.state=leftover 的食材在推荐时优先走"翻热/改造重做"方案，而非"新做"。
- LLM prompt 中注入剩菜清单，要求优先给出翻热/改造方案。

## API 契约草案

### 极速清场
```
POST /api/recommend/clear?fridge_id=<id|all>
→ 200 { MealSet }
→ 5xx { error: "LLM 不可用" }   // 不降级
```

### 饕餮盛宴
```
POST /api/recommend/feast?fridge_id=<id|all>
→ 202 { task_id }
GET /api/recommend/tasks/{task_id}
→ 200 { MealSet } | 202 { status: "processing" }
```

## 验收用例

1. **临期五花肉**：红色通缉令面板 → 点极速清场 → 规则打分器命中含"五花肉"主料的食谱（LLM 语义匹配"五花肉"↔"三层肉"）→ 返回套餐 + 无补购。
2. **半颗卷心菜**：盛宴模式 → LLM 语义匹配"卷心菜/包菜/甘蓝"食谱 → 套餐含卷心菜主菜 + 蛋花汤 + 米饭。
3. **不明剩菜盒**：state=leftover → 推荐返回 is_reheat=true 方案"微波翻热配新米饭"或 is_rework=true"剩菜改造粥"。
4. **库空降级**：新冰箱无任何食谱 → 盛宴模式 → LLM 现场生成"创意烩饭"存私有 → 返回 MealSet。
5. **LLM 不可用**：调 GLM 失败 → 前端报错"推荐暂不可用"，无规则兜底。
