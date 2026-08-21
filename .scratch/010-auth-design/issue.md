# 用户账号体系怎么设计？

- Labels: wayfinder:grilling
- Status: closed
- Assignee: Yk
- Blocked-by:
- Parent: 1

## Question

多用户平台已定，但账号体系的厚度未定：

- 注册方式：邮箱+密码？用户名+密码？要不要邮箱验证/找回密码（内网阶段邮件服务并不好搭）？
- 第三方登录（微信/GitHub OAuth）：V1 要不要？公网迁移后再加是否伤筋动骨？
- 会话机制：JWT vs server-side session，多端（电脑+手机浏览器）同时登录的语义。
- 用户与冰箱的关系落地：注册后的引导流程（建第一个冰箱 / 加入家人的冰箱）——与 003 的邀请机制衔接。
- 内网→公网迁移时的账号安全升级路径（HTTPS 强制、密码策略、限流）留什么钩子。

HITL：与 Yk 对谈定案，写入设计文档。核心词（User、Session 等）进 `CONTEXT.md`。
