# 剩宴事务所 Wayfinder 地图（The Leftover Bureau）

- Labels: wayfinder:map
- Status: open
- Assignee: Yk
- Blocked-by:
- Parent:

## Destination

先锁定一份可逐模块交给 AI agent 实现的设计文档，然后在本仓库落地成日常可用的 V1：多用户、可共享冰箱（一人多冰箱）的食材管理 + AI 菜谱推荐 Web 应用。V1 功能范围以「V1 切片」决议为准（双模式推荐、文字+拍照录入、赏味期限追踪、完整案件卷宗、共享冰箱、统一食谱库+审核流），内网部署先行、预留公网迁移。

## Notes

- 本图**携带执行**（Yk 已确认）：决策票走完后继续出建造票，直到 V1 跑起来，图才结束。
- 领域：家庭食材管理 + 菜谱推荐（消费级 Web 应用）。语言用中文，代码与接口用英文命名。
- 每个会话开工前先读本地图定向；解票时按票的类型调用 Skill 工具：grilling 票调 "grilling" + "domain-modeling"，research 票调 "research"。
- 领域建模票（冰箱共享、食材条目、食谱模型）必须边聊边维护仓库根的 `CONTEXT.md` 词汇表（当前不存在，首次定词时创建）；重大取舍按 domain-modeling 技能标准记 ADR（`docs/adr/`）。
- 已定的站桩决策（本轮 grilling 确认，勿再开票）：
  - 多用户平台，冰箱可共享，一个用户可拥有/加入多个冰箱。
  - 功能范围取 README 全集（含拍照识别、语音录入、赏味期限、双模式推荐、案件归档）。
  - 形态：桌面网页为主（电脑管理、做饭时手机看），响应式即可；原生 app 出范围。
  - 部署：先内网，架构预留公网迁移。
  - AI 能力设计为可切换多提供商（配置化 provider，部署时再定）。
  - 实现方式：Yk + AI agent 协作在本仓库写代码；设计文档要细到能逐模块派给 agent。
- Tracker 是本地 markdown（`.scratch/`），操作约定见 `docs/agents/issue-tracker.md`。

## Decisions so far

<!-- 一行一张已关闭的票：[票名](../002-slug/issue.md 这样的相对路径指到票目录)：一句话答案要点 -->

- [AI Provider 抽象层调研](../007-ai-provider-research/issue.md)：六家 LLM 提供商能力矩阵已核实（国内直连：DeepSeek+GLM，GLM 有免费视觉模型；OpenAI/Anthropic 需代理）；抽象层建议 LiteLLM 库形态；结构化输出用「schema 约束+校验+重试+降级」四层兜底。详见 docs/research/ai-provider.md。
- [V1 切片](../002-v1-slice/issue.md)：V1 = 双模式推荐全上 + 文字/拍照录入（识别必经人工确认）+ 完整案件卷宗（手动归档+评价）+ 预置保质期字典 + 完整共享冰箱 + 统一食谱库（私有自建→提交→管理员审核→公开，种子 AI 生成，现场生成存私有）；语音录入延后。
- [拍照识别技术路线调研](../008-recognition-route-research/issue.md)：YOLO 自建被判死（无中国家庭生鲜食材公开数据集，Food-101 等全是菜品）；V1 走多模态 LLM，GLM-4.6V-Flash 免费档起步（支持计数+json_object），Qwen/GPT 备选；数量估计不可靠由人工确认闸门兜底。详见 docs/research/food-recognition.md。
- [冰箱共享与权限模型](../003-fridge-sharing-model/issue.md)：两级角色（Owner+Member，上限 10 人）；6 位邀请码一码多人、有效期可撤销；成员离开留痕署名；冰箱只归档不删除、归档可逆；聚合视图为默认、推荐跟随筛选；食谱属用户不属冰箱。词汇已入 CONTEXT.md。
- [食材条目建模](../004-ingredient-item-model/issue.md)：单层 StockItem（自由文本名，无字典层，推翻 002 的保质期字典自动带出→完全手填可跳过）；数量纯文本；位置三区（默认冷藏）；状态生鲜/熟食/剩菜（熟剩推荐加权）；红色通缉令=3 天内高亮；条目删除/消耗留痕入冰箱历史。推荐匹配须容忍自由文本名（LLM 语义匹配）。词汇已入 CONTEXT.md。
- [食谱与推荐的领域模型](../005-recipe-recommendation-model/issue.md)：Recipe 精简字段（食材行带主料/调料标记+荤素派生，不建标签体系）；极速清场=主料全或差一附补购单、LLM 语义匹配自由文本名；饕餮盛宴库内检索优先不够再 LLM 生成存私有；推荐=2-4 菜套餐；口味信号卷宗加权；剩菜优先翻热/改造重做。词汇已入 CONTEXT.md。
- [技术栈与数据架构](../006-tech-stack/issue.md)：单一 FastAPI 后端 + Vue3/Vite SPA 前端 + PostgreSQL + Redis（限缓存/限流不存会话）+ MinIO 对象存储 + JWT 无状态认证 + Monorepo + docker-compose；存储接口与 provider 配置化预留公网迁移。ADR 0001 已立。
- [账号体系设计](../010-auth-design/issue.md)：V1 纯用户名+密码+邀请制注册，无邮箱无手机；找回靠 admin 重置；admin 可转让/多任（首个注册用户自动 admin）；JWT 多端在线不踢人；社交登录预留 OAuth 接口位 V1 不实现；内网→公网安全升级靠环境变量开关。词汇已入 CONTEXT.md。
- [审核工作流](../013-review-workflow/issue.md)：状态机 private→pending→approved/rejected(带理由可重提)；admin 审核兼下架/编辑种子/重置密码；种子食谱 V1 不做 AI 批量生成（Yk 后台手动添加直接 approved，修订 002）；库空/无匹配时极速清场降级 LLM 现场生成（修订 005）；审核后台极简（待审列表+预览+通过/驳回填理由）；站内标记反馈无推送；审核标准不成文。词汇已入 CONTEXT.md。
- [推荐引擎设计](../011-recommendation-engine/issue.md)：规则打分器（主料覆盖率/临期/口味）产候选集 + LLM 语义匹配/组套餐/剩菜改造；GLM json_object 结构化输出；极速清场同步、饕餮盛宴异步；LLM 不可用不降级直接报错（V1 推荐硬依赖 LLM）；临期/口味权重可调；Redis 按冰箱食材签名缓存 LLM 响应。词汇已入 CONTEXT.md。
- [食材录入三通道交互](../012-entry-ux/issue.md)：文字批量多行表单；拍照=拍→识别→逐条人工确认入库（绝不直接入库，失败退回文字表单预填）；列表行内编辑/删除+手动已用/丢弃按钮（触发004留痕）；红色通缉令=首页聚合顶部跨冰箱临期面板；V1 两通道移动端响应式、拍照为主入口（语音延后）。词汇已入 CONTEXT.md。
- [设计文档成稿并验收](../009-design-doc/issue.md)：docs/design/ 9 模块（00 概览 + 01 领域模型 + 02 账号冰箱 + 03 食材管理 + 04 食谱审核 + 05 推荐引擎 + 06 AI provider + 07 前端 IA + 08 部署）全写完，每模块含数据模型/API 契约/流程/验收用例（临期五花肉、半颗卷心菜、不明剩菜盒三场景贯穿）；三处跨票修订（种子库手动、库空降级 LLM、保质期手填）已在 04/05/01+03 体现；Yk 验收通过。决策段收口，进入建造期。
- [014 项目脚手架](../014-project-scaffold/issue.md)：Monorepo 空壳落地（backend FastAPI + frontend Vue3/Vite + db/redis/minio），docker-compose up 五服务全 Up，/health 经 nginx 反代可达，alembic 可连 DB（无 migration，015 才建）。实现修了两 bug（nginx 反代尾斜杠重写 /api→裸路由、DB dialect psycopg2）。详见 resolution。
- [015 数据库 schema + ORM models](../015-database-models/issue.md)：11 业务表 + alembic_version 全建成（User/OAuthBinding/Fridge/Membership/InviteCode/StockItem/FridgeEvent/Recipe/RecipeIngredientLine/CaseFile/CaseFileEntry）；枚举用 String+CheckConstraint；留痕双轨（FridgeEvent ondelete SET NULL 保留署名）；alembic 首个 migration 落地。修了 default vs server_default bug（裸 SQL insert 现可用）。详见 resolution。
- [016 账号与冰箱共享](../016-auth-fridge/issue.md)：注册（空库首个豁免码自动 admin）/登录 JWT/多端不互踢/注册邀请码（任意登录用户可发）/admin 重置密码+任命转让（最后一名保护）/冰箱 CRUD+owner 权限矩阵+6 位码 join（上限 10 人）+归档恢复/聚合视图空壳与 accessible_fridge_ids 范围解析（021 复用）。验收 16/16。详见 resolution。
- [017 食材管理与录入（文字通道）](../017-ingredient-mgmt/issue.md)：批量录入/聚合视图（含 fridge_name，expiry nulls_last）/红色通缉令（跨冰箱 ≤3 天含过期，days_left 升序）/行内编辑 PATCH（model_fields_set 显式更新）/删除三态 consumed|discarded|deleted 全量 FridgeEvent 留痕带 snapshot。验收 15/15。详见 resolution。
- [018 食谱与审核工作流](../018-recipe-review/issue.md)：Recipe CRUD + 状态机 private→pending→approved/rejected(带理由可重提) + admin 直建跳队列 approved（种子入口）+ 下架退私有 + 待审列表/审核/公开库筛选 + 可见性（approved 全员，其余作者与 admin，他人 404）。meat_type 留 019 TODO。验收 19+3 全过。详见 resolution。
- [019 AI Provider 抽象层](../019-ai-provider-layer/issue.md)：app/llm.py LLMClient（LiteLLM 封装）chat/vision 双槽 + chat_structured/vision_structured 四层兜底（schema 注入→pydantic 校验→重试 1 次降温+错误反馈→LLMStructuredError 不降级）；provider 配置化切 deepseek 只改 env；补齐 018 meat_type LLM 派生（失败静默 fallback mixed）。mock 5/5 + 真实验收通过（文本 glm-5.3@coding 端点/视觉 glm-4.6v-flash@标准端点，litellm 1.50 无 zhipu 原生 → OpenAI 兼容模式）。详见 resolution。

## Not yet specified

- 建造期进行中（014-023 建造票已出）。实现中可能冒出的细化 fog（前端组件交互细节、LLM prompt 调优、缓存失效边界）随各票实现就地处理或开补丁票。

## Out of scope

- 硬件接入（智能冰箱 IoT、传感器、扫码枪自动盘点）——Yk 明确只要信息管理，不接硬件。
- 原生移动 App（Flutter / React Native）——已定桌面响应式 Web 为主；README 中的跨平台原生表述被此决策覆盖。
- 语音录入——V1 切片决议延后至 V1 后迭代；本图路线止于 V1，需要时开新图。
