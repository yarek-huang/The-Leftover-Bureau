# 03 · 食材管理与录入

> 来源决策：004 食材条目、008 拍照识别路线、012 录入三通道。技术栈 006（MinIO/Vue3）。

## StockItem 模型（单层、无字典）

见 `01-domain-model.md`。关键点：
- **无字典层**：name 是自由文本，不做归一化。
- **数量纯文本**："大概半个""约 200g""两袋"皆可。
- **位置三区**：freezer / fridge / pantry，默认 fridge。
- **状态**：raw / cooked / leftover。熟食剩菜保质期短、推荐优先级高。
- **到期日**：完全手填、可跳过（推翻 002 的字典自动带出）。
- **留痕**：增删改 + 已用/丢弃均写 FridgeEvent。

## 文字录入（批量多行表单）

- 一次性多行表单：每行 = name + quantity + zone + state + expiry_date。
- "再添一行"动态加行；一次提交批量创建。
- 适合买完菜集中录。

## 拍照录入（008：GLM-4.6V-Flash 识别只报名称+置信度）

### 流程
```
拍/上传图 → POST /api/recognize (图传 MinIO，调 GLM-4.6V-Flash)
  → 返回 [{ name, confidence }]   // 不含量量，数量交人工
→ 前端展示结构化确认列表（每条 name 可改、quantity 手填、zone/state/expiry 选）
→ 逐条确认 → POST /api/fridges/{id}/items (批量)
```
- **识别结果绝不直接入库**（002 闸门），每条必经人工确认/修正。
- 识别全错 → "全清重来"按钮。
- 识别失败 → 退回文字录入表单，预填已识别的部分名称供改。

### 识别接口契约
```
POST /api/recognize
Body: multipart image
→ 200 { items: [{ name: str, confidence: float }] }
```
- 走 provider 抽象层 `vision` 槽位（见 06），默认 GLM-4.6V-Flash，可切 Qwen3.5-omni-plus/GPT-5.6。
- prompt 输出 json_object：`{"items":[{"name":"五花肉","confidence":0.92}]}`，仅名称+置信度。

## 录入后管理

- 食材列表**行内编辑/删除**。
- **手动"已用/丢弃"按钮** → 触发 FridgeEvent 留痕（action=consumed/discarded），条目随之移出在库视图。
- 过期/临期只读高亮，不可手动改状态（自动按 expiry_date 算）。

## 红色通缉令（3 天内到期）

- **首页聚合视图顶部独立面板**：跨冰箱汇总 3 天内到期列表，按到期远近排序。
- 面板点击 → 跳极速清场推荐（用这些临期食材）。

## API 契约草案

### 批量录入
```
POST /api/fridges/{fridge_id}/items
Body: { items: [{ name, quantity, zone, state, expiry_date? }] }
→ 201 [{ id, ... }]
```

### 列表（聚合/单冰箱）
```
GET /api/fridges/{fridge_id}/items?fridge_id=all
→ 200 [{ id, name, ..., fridge_id, fridge_name }]
```

### 更新/删除
```
PATCH /api/items/{id}
DELETE /api/items/{id}?action=consumed|discarded|deleted
```

### 红色通缉令
```
GET /api/fridges/expiry-alerts
→ 200 [{ ..., days_left }]
```

## 验收用例

1. **临期五花肉**：录入"五花肉、约 300g、冷冻、生鲜、到期日=今天+2天" → 首页红色通缉令面板出现 → 点推荐。
2. **半颗卷心菜**：录入"半个卷心菜、冷藏、生鲜、无到期日" → 推荐时 LLM 语义匹配到"卷心菜/包菜"食谱（不靠精确名）。
3. **不明剩菜盒**：拍照识别返回 [{name:"剩菜盒", confidence:0.6}] → 用户改成"红烧肉剩菜"、状态=leftover → 入库 → 推荐优先"翻热/改造"。
4. **识别失败兜底**：拍照识别返回空 → 退回文字表单，预填上次部分结果。
