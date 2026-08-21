# 023 部署联调与迁移清单

- Labels: wayfinder:task
- Status: open
- Assignee: Yk
- Blocked-by: 14, 15, 16, 17, 18, 19, 20, 21, 22
- Parent: 1

## Question

收尾：完整 docker-compose 起全栈、内网部署验收、公网迁移清单验证。

关联设计文档：`docs/design/08-deployment.md`（compose + env + 迁移表）、`010`（安全钩子）。

### 范围

- 014 的 docker-compose 扩到全栈（含全部业务路由联调）。
- `.env.example` 补齐所有模块 env（LLM/MinIO/JWT/安全钩子/权重）。
- 内网部署步骤文档化（08 已有，此票跑一遍验证）。
- 公网迁移清单验证：安全开关切 true / CORS 白名单 / JWT 缩短 / 切 provider env → 业务码不动 → 跑通。
- 数据备份：pg_dump + MinIO 版本化（V1 手动 dump，定时留 TODO）。

### 验收

1. **内网起服**：一台内网机 `docker-compose up` → 浏览器 `http://<内网IP>` → 注册首个 admin → 全流程可用（三场景走通）。
2. **迁移演练**：复制配置到公网机 → 安全开关 true → 切 provider env → 业务码不动 → 跑通。
3. **LLM 切换**：内网智谱 → 改 env 切 DeepSeek → 重启 backend → 推荐仍工作。
4. 全部 014-022 验收用例在此环境复跑通过 → V1 完工，地图收口。
