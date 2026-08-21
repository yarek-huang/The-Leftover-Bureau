# 016 账号与冰箱共享

- Labels: wayfinder:task
- Status: open
- Assignee: Yk
- Blocked-by: 15
- Parent: 1

## Question

实现 02 设计文档全部：注册（邀请制）/登录/JWT/冰箱 CRUD/邀请码/成员管理/聚合视图。

关联设计文档：`docs/design/02-auth-fridge.md`（API 契约 + 权限矩阵 + 生命周期）、`010` 决议（admin 转让/重置/安全钩子 env）。

### 范围

- 认证：`POST /api/auth/register`（校验注册邀请码）、`POST /api/auth/login`（发 JWT）、JWT 依赖（FastAPI `Depends` 取 current_user）。
- admin：首个注册自动 admin；`POST /api/admin/users/{id}/reset-password`（admin only）；admin 转让/任命（最小）。
- 冰箱：`POST /api/fridges`（创建）、`POST /api/fridges/{id}/invite-codes`（owner 生成 6 位码）、`POST /api/fridges/join`（凭码入）、归档/恢复（owner）、移除成员（owner）。
- 聚合视图：`GET /api/fridges/items?fridge_id=all|<id>`（此票先返回空壳，食材数据在 017 填；此票只把路由和权限打通）。
- 权限矩阵按 02 表落地（owner vs member）。
- 安全钩子读 env：`ENFORCE_HTTPS/PASSWORD_STRENGTH_CHECK/LOGIN_RATE_LIMIT`（内网 false，开关就位不实现强校验逻辑也可，留 TODO）。

### 验收

1. 无注册邀请码 → 注册 403；有码 → 201 + token。
2. 首个注册 → is_admin=true。
3. 创建冰箱 → 生成邀请码 → 第二人凭码 join → 两人都见该冰箱。
4. member 尝试生成邀请码 → 403。
5. 归档冰箱 → 不进聚合视图 → 恢复后回来。
6. 多端登录同账号 → 不互踢。
