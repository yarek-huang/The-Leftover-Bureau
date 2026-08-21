# 02 · 账号与冰箱共享

> 来源决策：003 冰箱共享与权限、010 账号体系、006 技术栈（JWT/Redis）。

## 账号

### 注册（邀请制）
- 纯用户名 + 密码，无邮箱无手机。
- 需**注册邀请码**（现有用户生成）方可注册。
- 首个注册用户自动为 admin；admin 可转让、可任命多个。

### 登录与会话
- JWT 无状态；允许多端同时在线、互不踢。
- Refresh token 可选（V1 用长有效期 JWT 简化，迁移公网再加 refresh）。

### 找回密码
- V1 不提供自助找回；忘密码找 admin 重置。

### 社交登录
- 预留 OAuth provider 接口位（`oauth_bindings` 表 + provider 抽象），V1 不实现；公网迁移后接微信。

### 内网→公网安全钩子
- 环境变量开关：`ENFORCE_HTTPS` / `PASSWORD_STRENGTH_CHECK` / `LOGIN_RATE_LIMIT`；内网全关，迁移一行打开。

## API 契约草案

### 注册
```
POST /api/auth/register
Body: { username, password, invite_code }
→ 201 { user_id, username, token }
Err: 400 用户名已存在 / 403 邀请码无效或已撤销
```

### 登录
```
POST /api/auth/login
Body: { username, password }
→ 200 { token, user: {id, username, is_admin} }
```

### 重置密码（admin only）
```
POST /api/admin/users/{user_id}/reset-password
Body: { new_password }
Auth: admin
→ 200
```

## 冰箱共享

### 角色与权限矩阵

| 操作 | Owner | Member |
|---|---|---|
| 增删改食材 | ✅ | ✅ |
| 发起推荐 | ✅ | ✅ |
| 记录卷宗 | ✅ | ✅ |
| 生成/撤销邀请码 | ✅ | ❌ |
| 管理成员（移除） | ✅ | ❌ |
| 归档/恢复冰箱 | ✅ | ❌ |

- 每冰箱成员上限 10 人。

### 邀请码（入冰箱）
- Owner 生成 6 位码，**一码多人**（全家共用），带有效期、可撤销。
- 与注册邀请码是两套独立 token。

### 冰箱生命周期
- 只归档、不真删除。归档 = 冻结只读 + 保留全部历史；Owner 可恢复（unarchive）。
- 归档冰箱不进聚合视图与推荐范围。

### 一人多冰箱交互
- **聚合视图为默认**：汇总全部活跃冰箱食材，可按单冰箱筛选。
- 推荐范围跟随筛选：单冰箱按单冰箱推，"全部"跨冰箱合推。

## API 契约草案

### 创建冰箱
```
POST /api/fridges
Body: { name }
→ 201 { fridge_id, name, role: "owner" }
```

### 生成冰箱邀请码
```
POST /api/fridges/{fridge_id}/invite-codes
Body: { expires_in_days? }
Auth: owner
→ 201 { code, expires_at }
```

### 加入冰箱（凭码）
```
POST /api/fridges/join
Body: { invite_code }
→ 200 { fridge_id, name, role: "member" }
```

### 聚合视图食材
```
GET /api/fridges/items?fridge_id=<all|id>
→ 200 [{ stockitem..., fridge_id, fridge_name }]
```
默认 `fridge_id=all` 返回聚合。

## 验收用例

1. Yk 注册（首个→admin）→ 创建"家"冰箱 → 生成邀请码 → 妻子凭码加入 → 两人都看到同一冰箱食材。
2. Yk 创建第二个冰箱"父母家" → 聚合视图默认显示两个冰箱食材汇总 → 切到单冰箱筛选 → 推荐只按该冰箱食材算。
3. 妻子被移除 → 她的历史操作记录留痕署名保留在冰箱历史里。
4. Yk 归档"父母家"冰箱 → 不出现在聚合视图 → 一个月后恢复 → 食材历史全在。
