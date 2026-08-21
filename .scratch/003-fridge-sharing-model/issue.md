# 冰箱共享与权限模型怎么建？

- Labels: wayfinder:grilling
- Status: closed
- Assignee: Yk
- Blocked-by:
- Parent: 1

## Question

已定事实：多用户平台；冰箱可共享；一个用户可拥有/加入多个冰箱。需要敲定共享的完整语义：

- 冰箱的角色模型：Owner / Member / 只读 Viewer？还是更简单的全员平权？
- 邀请机制：邀请码 / 链接 / 按用户名搜索添加？要不要冰箱内成员审批？
- 一人多冰箱的交互：当前冰箱切换器？所有列表按冰箱过滤？
- 成员退出/被移除、冰箱归档/删除时，食材与卷宗数据的去向（级联删除？仅解除关联？）。
- 食谱（Recipe）的归属：属于冰箱还是属于平台/用户？共享冰箱成员能否互看食谱？（此问影响 005，先粗定）

HITL：与 Yk 对谈定案。定案时把核心词（Fridge、Membership、Owner 等）写进根目录 `CONTEXT.md`（不存在则创建），权限取舍若够重（难逆转+有真实权衡）记 ADR 到 `docs/adr/`。
