# 技术栈与数据架构怎么定？

- Labels: wayfinder:grilling
- Status: closed
- Assignee: Yk
- Blocked-by: 2, 7
- Parent: 1

## Question

README 写的技术栈（Flutter/RN、FastAPI+Node 双后端、GPT-4+YOLOv8、PostgreSQL+Redis）是占位畅想，不是决策。在这张票里按 V1 清单（002 的结论）与 AI provider 调研（007 的结论）正式定案：

- 后端：单一 FastAPI（Python，与 AI/ML 生态最亲）是否足够？Node 层删掉？README 双后端表述被覆盖。
- 前端：桌面为主响应式 Web 的框架选择（React / Vue 系），SSR 要不要，组件库取向。
- 数据库：PostgreSQL 单库是否够用；Redis 缓存在单家庭规模下是否值得引入（Yk 倾向删繁就简还是照 README 全上）。
- 部署单元：docker-compose 一把梭（内网）+ 预留公网迁移的架构含义（环境变量、对象存储抽象、HTTPS 终止点）。
- 仓库结构：monorepo（backend/ frontend/ docs/）目录约定，agent 逐模块实现时的模块边界。

HITL：与 Yk 对谈定案。这是典型 ADR 素材（难逆转+真实权衡），定案记 `docs/adr/0001-tech-stack.md`。
