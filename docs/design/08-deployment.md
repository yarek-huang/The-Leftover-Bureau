# 08 · 部署与迁移

> 来源决策：006 技术栈（docker-compose / Monorepo）、010 内网→公网安全钩子、007 provider 切换。

## 仓库结构（Monorepo）

```
The-Leftover-Bureau/
  backend/            # FastAPI
    app/
      main.py
      config.py
      llm.py          # LLMClient（06）
      models/         # SQLAlchemy ORM
      routers/        # API 路由
      services/       # 推荐引擎、识别、审核
    alembic/          # DB 迁移
    requirements.txt
  frontend/           # Vue3 + Vite
    src/
      views/
      components/
      stores/         # Pinia
      api/
    package.json
  docker-compose.yml
  .env.example
  docs/               # 本设计文档 + research + adr
  .scratch/           # tracker
  CONTEXT.md
```

## docker-compose（内网 V1）

```yaml
services:
  backend:
    build: ./backend
    env_file: .env
    depends_on: [db, redis, minio]
    ports: ["8000:8000"]

  frontend:
    build: ./frontend
    ports: ["80:80"]   # nginx serve dist

  db:        # PostgreSQL
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
    env_file: .env

  redis:     # 限缓存/限流，不存会话
    image: redis:7-alpine

  minio:    # 图片存储
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    volumes: [miniodata:/data]

volumes:
  pgdata:
  miniodata:
```

## 环境变量（.env.example）

```env
# DB
DATABASE_URL=postgresql+psycopg://app:app@db:5432/leftover
# Redis
REDIS_URL=redis://redis:6379/0
# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
MINIO_BUCKET=leftover
# JWT
JWT_SECRET=...
JWT_EXPIRES_DAYS=30
# LLM（06）
LLM_TEXT_PROVIDER=zhipu
LLM_TEXT_MODEL=glm-4.6-flash
LLM_TEXT_API_KEY=...
LLM_VISION_PROVIDER=zhipu
LLM_VISION_MODEL=glm-4.6v-flash
LLM_VISION_API_KEY=...
# 安全钩子（010，内网全 false）
ENFORCE_HTTPS=false
PASSWORD_STRENGTH_CHECK=false
LOGIN_RATE_LIMIT=false
```

## 内网部署

1. `cp .env.example .env` 填 key。
2. `docker-compose up -d --build`。
3. 后端启动跑 alembic 迁移建表。
4. 前端 nginx serve dist，反代 `/api` → backend:8000。
5. 首个注册用户自动 admin。

## 内网→公网迁移清单

| 项 | 内网 | 公网 |
|---|---|---|
| HTTPS | 关 | `ENFORCE_HTTPS=true` + 反代 TLS |
| 密码强度 | 关 | `PASSWORD_STRENGTH_CHECK=true` |
| 登录限流 | 关 | `LOGIN_RATE_LIMIT=true`（Redis 计数） |
| CORS | `*` | 白名单域名 |
| JWT | 长有效期 | 缩短 + 加 refresh token |
| LLM provider | 智谱直连 | 可切 OpenAI/DeepSeek（改 env） |
| 社交登录 | 占位 | 接微信 OAuth（010 预留位） |
| 备份 | 手动 dump | 定时 pg_dump + MinIO 版本化 |

## 验收用例

1. **内网起服**：一台内网机 `docker-compose up` → 浏览器开 `http://<内网IP>` → 注册首个 admin → 全流程可用。
2. **迁移演练**：复制 compose 配置到公网机 → 改安全开关为 true → 切 provider env → 业务代码不动 → 跑通。
3. **LLM 切换**：内网用智谱免费档 → 改 env 切 DeepSeek → 重启 backend → 推荐仍工作。
