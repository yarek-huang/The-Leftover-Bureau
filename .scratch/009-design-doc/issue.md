# 设计文档成稿并验收

- Labels: wayfinder:task
- Status: closed
- Assignee: Yk
- Blocked-by: 2, 3, 4, 5, 6, 10, 11, 12, 13
- Parent: 1

## Question

汇聚票：把 002–012 的全部决议整合成一份**可逐模块派给 AI agent 实现的设计文档**（Yk 的验收标准），这是地图前半程（决策段）的终点。

- 文档位置与结构：`docs/design/` 下分模块（领域模型、账号与冰箱、食材管理、食谱与推荐、AI provider 层、前端信息架构、部署）。
- 每个模块章节须包含：数据模型（对齐 CONTEXT.md 词汇）、API 契约草案、UI 流程、验收用例（Yk 的真实场景走查：临期五花肉、半颗卷心菜、不明剩菜盒）。
- 与 ADR（tech-stack 等）、research 文档（007/008 产物）交叉引用。
- 产出后请 Yk 逐模块验收签字，缺口回灌对应决策票或直接补文档。

Task 票（AFK 为主）：agent 起草，Yk 验收。Resolution 记录文档路径与验收结论。
