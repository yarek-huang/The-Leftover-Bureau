# The Leftover Bureau 
### "专接剩菜剩肉的大单，定制一顿体面的盛宴。"

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-iOS%20%7C%20Android%20%7C%20Web-brightgreen)]()
[![Status](https://img.shields.io/badge/status-Under%20Cover-brightgreen)]()

"别让你冰箱里的肉，死不瞑目。"

---

## 案件背景 (Project Overview)

你家冰箱的冷冻层，是否藏匿着"案发时间不详"的冻肉？蔬菜抽屉里是否有"身份不明"的半颗卷心菜？

The Leftover Bureau（剩宴事务所）是一款基于 AI 的智能食谱推荐引擎。我们将您的冰箱视为"案发现场"，将剩余的食材视为"关键证物"。只需输入您手头的肉类与蔬菜，我们的高级"食材探员"将立即进行交叉比对，为您完美重构一场"餐桌盛宴"。

**我们的使命：** 终结囤货焦虑，让每一份剩菜都有尊严地退场。

---

## 行动方案 (Key Features)

- **全食材"尸检"扫描**：支持文字输入、拍照识别（CV模型）或语音录入。精准识别冰箱内剩余肉、菜、调味品的种类与数量。
- **赏味期限追踪**：自动标记食材的"保鲜期危险等级"。红色通缉令食材（即将过期）将获得优先推荐权重，帮你从源头减少浪费。
- **AI 高级审讯（推荐算法）**：
  - 模式一：极速清场 —— 输入食材后，仅输出耗时最短、清空食材最多的方案。
  - 模式二：饕餮盛宴 —— 基于海量菜谱，利用现有食材生成媲美餐厅的"高配版"家常菜。
- **案件卷宗归档**：自动记录每次"清空冰箱"的成功案例，建立专属的家庭饮食数据库，越用越懂你的口味。

---

## 技术装备 (Tech Stack)

- **前端框架**：Flutter / React Native（跨平台作案工具）
- **后端核心**：Python (FastAPI) + Node.js
- **AI 模型**：OpenAI GPT-4 / Claude API (用于逻辑推理与食谱生成) + YOLOv8 (用于食材图像识别)
- **数据库**：PostgreSQL（存储案件卷宗） + Redis（缓存热门组合）

---

## 入职指南 (Getting Started / 新手探员入职)

想本地运行该项目进行二次开发？请遵循以下"入职流程"：

1. **克隆案件档案**
   git clone https://github.com/your-username/the-leftover-bureau.git
   cd the-leftover-bureau

2. **配置环境变量（领取探员装备）**
   - 复制 .env.example 为 .env。
   - 填写你的 API Keys（OpenAI / 图像识别接口）。

3. **启动后端服务（后勤支援）**
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload

4. **启动前端应用（前线出勤）**
   cd frontend
   npm install
   npm run dev

---

## 加入特别行动组 (Contributing)

我们欢迎所有"厨艺高超"或"代码逆天"的特工加入！

1. Fork 本仓库（领取任务）。
2. 创建你的功能分支 (git checkout -b feature/AmazingRecipe)。
3. 提交你的修改 (git commit -m 'Add some amazing recipe logic')。
4. 推送至分支 (git push origin feature/AmazingRecipe)。
5. 提交 Pull Request（上交卷宗等待审核）。

---

## 许可证 (License)

本项目采用 **MIT** 许可证。软件免费开源，但使用本软件导致冰箱被彻底清空、体重增加的，事务所概不负责。

---

**2026 The Leftover Bureau. All rights reserved.**
*—— 案件终了，剩宴开始。*
