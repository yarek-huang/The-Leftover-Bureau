# 014 Resolution · 项目脚手架

- 状态：**完成，验收通过**
- 日期：2026-08-21

## 产出

Monorepo 空壳落地，`docker-compose up` 起五服务全 Up，backend `/health` 经 nginx 反代可达：

```
The-Leftover-Bureau/
  .gitignore / .env.example / docker-compose.yml
  backend/
    Dockerfile / requirements.txt / alembic.ini
    alembic/{env.py, versions/}
    app/{__init__.py, config.py, database.py, main.py}
  frontend/
    Dockerfile / nginx.conf / package.json / vite.config.ts
    {index.html, tsconfig.json, src/vite-env.d.ts}
    src/{main.ts, App.vue, api/request.ts}
```

## 验收（全过）

1. `docker compose up -d` → backend/frontend/db/redis/minio 五服务全 Up ✓
2. `curl :8010/health` 与 `curl :8888/api/health`（经 nginx 反代）→ `{"status":"ok"}` ✓
3. `curl :8888/` → 前端占位页 + 顶部导航（首页聚合/我的冰箱/食谱库/我的食谱/卷宗）✓
4. `alembic current` → 连 DB 成功（PostgresqlImpl），无 migration（015 才建）✓

## 实现中修正的两个 bug（已落地）

1. **nginx 反代路径**：原 `proxy_pass http://backend:8000;`（无尾斜杠）保留 `/api` 前缀转发，backend 路由是 `/health` 无前缀 → 404。改 `proxy_pass http://backend:8000/;`（尾斜杠重写去掉 `/api`）。前端 `request.ts` baseURL `/api`，nginx 重写后命中 backend 裸路由。
2. **DB dialect**：`DATABASE_URL` 原用 `postgresql+psycopg://`（psycopg3 dialect）但 requirements 装的是 `psycopg2-binary`（psycopg2），alembic 报 `No module named 'psycopg'`。改为 `postgresql+psycopg2://`（.env / .env.example / config.py default 三处）。

## 环境适配（沙箱特有，非设计缺陷）

沙箱已有 `rustfs` 占 9000-9001、宿主占 8000/8080。compose host 端口映射改为 8010→8000（backend）、8888→80（frontend）、9002→9000/9003→9001（minio）。容器间通信走内部网络名（backend:8000 / minio:9000）不受影响。用户部署环境若无占用可改回标准端口。

## 下一步

015（数据库 ORM + 首个 migration）已 unblocked，是 frontier。
