# 014 项目脚手架

- Labels: wayfinder:task
- Status: closed
- Assignee: Yk
- Blocked-by:
- Parent: 1

## Question

落地 Monorepo 空壳，让 `docker-compose up` 起来一个能访问的 backend + frontend，作为后续所有模块的地基。

关联设计文档：`docs/design/08-deployment.md`（仓库结构 + compose）、`docs/design/00-overview.md`。

### 范围

- `backend/`：FastAPI 骨架——`app/main.py`（含 `/health` 200）、`app/config.py`（pydantic-settings 读 env）、`requirements.txt`（fastapi/uvicorn/sqlalchemy/alembic/pydantic-settings/psycopg2-binary/python-jose/passlib[bcrypt]/redis/minio/litellm/pillow，版本钉到兼容区）、`alembic/` 初始化（alembic.ini + env.py 接 DATABASE_URL）、`Dockerfile`。
- `frontend/`：Vue3+Vite+Pinia 骨架——`npm create vite` 级别的空壳（App.vue 占位页 + 顶部导航占位 + api 封装 `request.ts` 带 baseURL `/api`）、`Dockerfile`（build dist + nginx serve，反代 `/api` → backend:8000）。
- 根：`docker-compose.yml`（backend/frontend/db/postgres/redis/minio 五服务，按 08 文档）、`.env.example`（08 全部 env）、`.gitignore`（node_modules/venv/__pycache__/.env）。
- 不含：任何业务路由、任何 ORM model（015）、任何真实页面。

### 验收

1. `cp .env.example .env` + `docker-compose up --build` → 五服务全 healthy。
2. `curl http://localhost/health`（经 nginx 反代）→ 200。
3. 浏览器开 `http://localhost` → 见前端占位页 + 顶部导航。
4. `docker-compose exec backend alembic current` → 无 migration（015 才建）。
