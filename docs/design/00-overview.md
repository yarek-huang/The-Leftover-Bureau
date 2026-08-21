# 00 · 设计概览

> 本文档是 The Leftover Bureau（剩宴事务所）V1 的设计规格，由 wayfinder 地图全部决策票汇编而成，目标是可逐模块交给 AI agent 实现。验收以 Yk 真实场景走查为准。

## V1 范围（来源：V1 切片 002）

| 模块 | V1 | V1 后 |
|---|---|---|
| 双模式推荐 | 极速清场 + 饕餮盛宴全上 | — |
| 录入通道 | 文字（批量）+ 拍照（识别→人工确认→入库） | 语音 |
| 案件卷宗 | 完整版：手动归档（做了什么+用了哪些食材）+ 评价，作口味学习信号 | 自动化评价体系 |
| 赏味期限 | 完全手填到期日（推翻字典自动带出）；3 天内到期=红色通缉令高亮 | — |
| 多用户/共享 | 完整：两级角色 + 邀请码共享冰箱 + 一人多冰箱 | — |
| 食谱库 | 统一公共库（私有自建→提交→管理员审核→公开）；盛宴现场生成存私有 | AI 批量种子生成（Yk 后台手动添加起步） |
| 审核工作流 | V1 就上：管理员审核后台 | — |

## 技术栈（来源：技术栈 006 / ADR 0001）

- 后端：单一 FastAPI（Python），删掉 README 的 Node 层
- 前端：Vue 3 + Vite + 组件库（Element Plus 候选），SPA 不上 SSR
- 数据库：PostgreSQL 单库
- 缓存：Redis（限缓存/限流，**不**承载会话）
- 对象存储：MinIO（S3 兼容，存拍照/识别图片）
- 认证：JWT 无状态，多端在线不踢人
- 仓库：Monorepo（backend/ frontend/ docs/ .scratch/）
- 部署：docker-compose（应用 + DB + MinIO），环境变量预留公网迁移
- AI provider 抽象：LiteLLM 库形态，作为 backend 内模块，配置化多提供商

详见 `docs/adr/0001-tech-stack.md`。

## 仓库结构

```
The-Leftover-Bureau/
├── backend/              # FastAPI 应用
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/             # Vue 3 + Vite
│   ├── src/
│   └── package.json
├── docs/
│   ├── design/           # 本设计文档
│   ├── research/         # 调研产出（ai-provider.md, food-recognition.md）
│   └── adr/              # 架构决策记录
├── .scratch/             # wayfinder 地图与票（本地 markdown tracker）
├── CONTEXT.md            # 领域词汇表
└── docker-compose.yml
```

## 模块地图

| 编号 | 模块 | 文档 | 关联决策票 |
|---|---|---|---|
| 01 | 领域模型 | 01-domain-model.md | 003, 004, 005, 013 |
| 02 | 账号与冰箱共享 | 02-auth-fridge.md | 003, 010 |
| 03 | 食材管理与录入 | 03-ingredient-mgmt.md | 004, 008, 012 |
| 04 | 食谱与审核 | 04-recipe-review.md | 005, 013 |
| 05 | 推荐引擎 | 05-recommendation.md | 005, 007, 011 |
| 06 | AI Provider 抽象层 | 06-ai-provider.md | 007, 008 |
| 07 | 前端信息架构 | 07-frontend-ia.md | 012, 006 |
| 08 | 部署 | 08-deployment.md | 006 |

## 验收场景（贯穿全文）

1. **临期五花肉**：冰箱里有块五花肉 3 天内到期 → 红色通缉令面板出现 → 极速清场推荐用它的套餐
2. **半颗卷心菜**：自由文本"半个卷心菜"入库 → 推荐时 LLM 语义匹配到"卷心菜/包菜"食谱
3. **不明剩菜盒**：剩菜状态条目录入 → 推荐优先"翻热/改造"而非生鲜食谱
