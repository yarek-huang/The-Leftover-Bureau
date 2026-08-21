# 016 Resolution · 账号与冰箱共享

- 状态：**完成，验收通过（16/16）**
- 日期：2026-08-21

## 产出

### 新增文件

| 文件 | 内容 |
|---|---|
| `app/security.py` | bcrypt 哈希/校验、JWT 签发/解析（HS256, sub=user_id）、6 位邀请码生成（去易混淆字符字母表）、now_utc |
| `app/deps.py` | `get_current_user`（HTTPBearer→JWT→User）、`require_admin`、`get_membership` |
| `app/schemas.py` | 全部 Pydantic 入参/出参模型；密码强度校验留 TODO(PASSWORD_STRENGTH_CHECK) |
| `app/routers/auth.py` | 注册/登录/生成注册邀请码 |
| `app/routers/admin.py` | 重置密码、任命/转让 admin（最后一名 admin 保护） |
| `app/routers/fridges.py` | 冰箱 CRUD/邀请码/join/移除成员/归档恢复/聚合视图空壳 |

### 端点清单（19 路由）

- `POST /api/auth/register` — 空库首个用户豁免邀请码（鸡生蛋引导，010 决议：首个注册自动 admin）；此后必须有注册邀请码
- `POST /api/auth/login` — 发 JWT（30 天），多端不互踢
- `POST /api/auth/invite-codes` — 任意已登录用户可生成注册邀请码（010 决议）
- `POST /api/admin/users/{id}/reset-password` / `set-admin` — admin only
- `POST/GET /api/fridges`、`GET /{id}/members`、`POST /{id}/invite-codes`（owner only）、`POST /join`（凭码，成员上限 10）、`DELETE /{id}/members/{uid}`（owner，不可移除 owner）、`POST /{id}/archive|unarchive`（owner）
- `GET /api/fridges/items?fridge_id=all|<id>` — 权限与范围解析打通，食材数据 017 填
- `accessible_fridge_ids()` 范围解析函数导出供 021 推荐复用：归档冰箱永远不在范围

### 权限矩阵落地（02 设计）

owner 独占：生成邀请码/移除成员/归档恢复。member 与 owner 同权：食材/推荐/卷宗（017+021 落地时复用 `get_membership` 校验）。

### 安全钩子

`ENFORCE_HTTPS/PASSWORD_STRENGTH_CHECK/LOGIN_RATE_LIMIT` 读入 settings（内网 false），代码内 TODO 标注挂点，公网迁移时打开。

## 验收（16/16 全过）

1. 无码注册 403 / 有码 201 + token ✓（空库豁免另测 ✓）
2. 首个注册 is_admin=true，第二人 false ✓
3. 建冰箱→owner 生成码→第二人凭码 join→双方都见该冰箱 ✓
4. member 生成邀请码 → 403 ✓
5. 归档 → 单查 403、不进聚合范围 → 恢复后回来 ✓
6. 多端登录同账号双 token 均有效 ✓
7. 加分：admin 重置密码生效、非 admin 调 admin 接口 403 ✓

## 实现中修正

- **邀请码端点 body 改可选**：测试裸 POST 无 body 得 422（FastAPI 对必填 body 模型校验失败）；`InviteCodeCreateIn | None = None` + 默认 30 天。
- **钉 bcrypt==4.0.1**：passlib 1.7.4 读 bcrypt 4.x 版本号报 AttributeError 风险，钉回 4.0.1（requirements 已加）。
- **空库豁免邀请码**：010 决议只说"首个注册自动 admin"未说码从哪来；按鸡生蛋逻辑豁免（register 里 user_count==0 跳过校验），已在代码注释标明出处。

## 下一步

017（食材管理）已 unblocked——聚合视图空壳等它填；018（食谱审核）也已 unblocked（admin 体系就位）。
