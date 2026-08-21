# ADR 0001: 技术栈选型（FastAPI + Vue + PG/Redis + MinIO + JWT）

- 状态：已接受
- 日期：2026-08
- 关联票：[技术栈与数据架构](../../.scratch/006-tech-stack/issue.md)

## 背景

README 占位畅想的技术栈是 Flutter/React Native + FastAPI+Node 双后端 + GPT-4 + YOLOv8 + PostgreSQL + Redis。项目开始时已确认：桌面网页为主（做饭时看手机，响应式即可），V1 内网先行预留公网迁移，AI 能力 provider 可切换，Yk + AI agent 协作实现（文档要细到逐模块交给 agent）。需要正式拍板 V1 的技术栈与分层架构。

## 决策

- **后端**：单一 FastAPI（Python），删除 README 的 Node 层。Python 与 LLM/CV 生态最亲，单人维护避免双语言负担。
- **前端**：Vue 3 + Vite + 组件库（Element Plus 候选），SPA 不上 SSR。响应式覆盖桌面+手机浏览器。
- **数据库**：PostgreSQL 单库。
- **缓存**：保留 Redis，但限定用途（热门组合缓存、LLM 响应缓存、限流），**不**承载会话。
- **对象存储**：MinIO（自托管 S3 兼容），存拍照/识别图片；通过存储接口抽象便于内网→公网迁移。
- **认证**：JWT 无状态，多端最简，预留公网 HTTPS 钩子。
- **仓库**：Monorepo（backend/ frontend/ docs/ .scratch/）。
- **部署**：docker-compose（应用 + DB + MinIO），环境变量预留公网迁移。

## 备选与权衡

- **删除 Node 层**：README 写双后端，但无跨语言硬需求；单一 Python 后端降低维护面。代价：若未来某能力只有 Node 生态现成库，需自行移植或独立微服务。
- **保留 Redis vs 删繁就简**：单家庭规模缓存价值有限，但 LLM 响应缓存（同一冰箱组合反复推荐）和限流有实际收益，且 docker-compose 加一个容器成本极低，故保留。
- **MinIO vs 文件系统**：MinIO 略重但 S3 兼容、迁移公网不返工；文件系统最简但迁移时要重写存储层。
- **Vue vs React vs Next.js**：Vue 3 + Vite 轻量、上手快；React 生态更大但 Yk 倾向轻量；Next.js 的 SSR 在内网家庭项目收益不足以抵消运行时复杂度。
- **Flutter/RN 原生**：被 Q4 桌面网页为主决策覆盖，不在路线（已记地图 Out of scope）。

## 后果

- 难逆转：前后端框架与对象存储一旦铺开，迁移成本高（故立此 ADR）。
- 留下的钩子：存储接口抽象、provider 配置化、JWT 预留 HTTPS，三条都是为内网→公网不返工预留。
