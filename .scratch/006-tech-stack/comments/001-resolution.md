# Resolution

## 技术栈与数据架构（Yk 定案，2026-08）

| 层 | 选型 | 说明 |
|---|---|---|
| 后端 | **单一 FastAPI（Python）** | 与 AI/ML 生态最亲；删掉 README 的 Node 层 |
| 前端 | **Vue 3 + Vite + 组件库（Element Plus 候选）** | 轻量、上手快 |
| 数据库 | **PostgreSQL** | 单库 |
| 缓存 | **Redis** | 照搬 README 留作：热门组合缓存、LLM 响应缓存、限流；**不**用于会话 |
| 对象存储 | **MinIO（自托管 S3 兼容）** | 存拍照/识别图片；预留公网迁移友好 |
| 认证 | **JWT 无状态** | 多端（电脑+手机浏览器）最简；预留公网 HTTPS 钩子 |
| 仓库结构 | **Monorepo** | backend/ frontend/ docs/ .scratch/ 一仓库内，模块边界靠目录 |
| 部署 | **docker-compose** | 应用+DB+MinIO 一把梭；环境变量预留公网迁移 |

### 边界澄清

- JWT 无状态认证；Redis 不存会话，仅作缓存/限流。
- 前端走 SPA（Vite），不上 SSR。
- 对象存储抽象一层存储接口（本地路径 vs S3/MinIO 可切），方便内网→公网迁移。
- AI provider 抽象层（007 建议的 LiteLLM 库形态）作为 backend 内的一个模块，不独立成服务。

### 已记 ADR

`docs/adr/0001-tech-stack.md`（难逆转 + 偏离 README 的原因记录）。

## 对地图的影响

- 010 账号体系设计获得认证机制输入（JWT 无状态 + 用户名密码）。
- 009 设计文档成稿获得架构骨架（backend/frontend/docs 模块切分 + docker-compose 服务清单）。
