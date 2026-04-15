# PlotPilot (墨枢) - Code Wiki

## 1. 项目整体架构

PlotPilot 是一个 AI 驱动的长篇小说创作平台，后端采用了严格的**领域驱动设计（DDD）**四层架构，将核心业务逻辑与外部依赖、框架实现彻底解耦。前端采用现代化的 Vue 3 生态构建。

整体架构分为以下几个层级：

- **Domain（领域层）**：系统的核心，包含领域实体（Entities）、值对象（Value Objects）和仓储接口（Repository Interfaces）。不依赖任何外部框架。
- **Application（应用层）**：用例的编排层，负责协调领域模型与基础设施层，实现诸如自动驾驶生成、知识图谱分析、内容审计等核心工作流。
- **Infrastructure（基础设施层）**：技术实现层，负责实现领域层定义的接口，包括数据库持久化（SQLite）、AI 大模型接入（Claude、Doubao 等）以及向量数据库集成（Qdrant）。
- **Interfaces（接口层）**：系统对外的边界，主要由 FastAPI 构成的 RESTful API 路由和依赖注入（DI）容器组成。
- **Frontend（前端层）**：基于 Vue 3 + TypeScript + Vite 构建的用户交互界面。

---

## 2. 主要模块职责

### 2.1 领域层 (Domain)
- **`novel`**：小说核心引擎模块，管理小说的生命周期、章节（Chapter）、剧情张力曲线（PlotArc）、故事线（Storyline）以及伏笔台账（ForeshadowingRegistry）。
- **`bible`**：世界观与设定集模块，作为静态数据库管理角色（Character）、地点（Location）、世界设定（WorldSetting）及文风设定。
- **`cast`**：角色动态关系图谱模块，追踪角色在剧情中的动态交互、关系演变及关联的故事事件（StoryEvent）。
- **`knowledge`**：叙事记忆与动态知识库模块，通过提取章节摘要（ChapterSummary）和知识三元组（KnowledgeTriple），解决大模型长文本生成的“记忆遗忘”问题。

### 2.2 应用层 (Application)
- **`engine` (Autopilot)**：核心生成引擎，负责后台守护进程的自动驾驶连续生成、智能上下文组装（洋葱模型）以及章节生成后的异步后处理管线。
- **`analyst`**：数据分析师，负责文风漂移检测（VoiceDrift）、张力分析与卡文破局建议、以及动态实体的状态提取追踪。
- **`audit`**：质量审计模块，进行多维度的一致性检查、逻辑冲突检测（幽灵批注）以及宏观结构重构提案。
- **`blueprint`**：故事蓝图模块，负责高层叙事设计，包括多级结构规划（部-卷-幕-章）和基于混合检索的节拍表（Beat Sheet）生成。
- **`workflows`**：工作流编排，将上述各个子服务串联起来，形成完整的小说创建、章节生成、审核和反馈的全自动闭环。

### 2.3 基础设施层与接口层 (Infrastructure & Interfaces)
- **AI Providers**：统一实现了 `LLMService` 接口，支持 Anthropic (Claude) 和兼容 OpenAI 协议的模型（如字节 Doubao）。支持普通请求与流式请求（SSE）的双端点策略。
- **Vector Store**：封装了 `Qdrant`（可选 ChromaDB），将小说的核心记忆向量化存储，支持基于 Payload 的精确过滤与余弦相似度检索。
- **FastAPI 路由**：按子域（如 `/core`, `/world`, `/engine`, `/audit`）精细化拆分路由，并深度使用 FastAPI 的 `Depends` 机制进行依赖注入，保持 Controller 的轻量化。

---

## 3. 关键类与函数说明

### 3.1 核心实体与服务
- **`Novel`** ([domain/novel/entities/novel.py](file:///Users/rui/Code/ai/novle-related/PlotPilot/domain/novel/entities/novel.py))：小说聚合根，管理全局元数据、章节列表和自动驾驶状态，控制生成管线的护城河边界（如熔断机制）。
- **`StoryKnowledge`** ([domain/knowledge/story_knowledge.py](file:///Users/rui/Code/ai/novle-related/PlotPilot/domain/knowledge/story_knowledge.py))：管理小说推演出的所有动态叙事知识，统筹章节摘要和知识三元组，是 RAG 机制的核心数据源。
- **`AutopilotDaemon`** ([application/engine/services/autopilot_daemon.py](file:///Users/rui/Code/ai/novle-related/PlotPilot/application/engine/services/autopilot_daemon.py))：自动驾驶守护进程，轮询 `RUNNING` 状态的小说并推进生成，具备节拍级幂等和断点续写能力。
- **`ContextBuilder`** ([application/engine/services/context_builder.py](file:///Users/rui/Code/ai/novle-related/PlotPilot/application/engine/services/context_builder.py))：上下文构建器，根据可用 Token 预算，智能组装强制内容（伏笔/设定）、摘要和向量召回的知识片段。
- **`ChapterAftermathPipeline`** ([application/engine/services/chapter_aftermath_pipeline.py](file:///Users/rui/Code/ai/novle-related/PlotPilot/application/engine/services/chapter_aftermath_pipeline.py))：章节后处理管线，章节生成后统一执行摘要提取、三元组落库、向量索引和文风评分。

### 3.2 基础设施实现
- **`AnthropicProvider` / `OpenAIProvider`** ([infrastructure/ai/providers/](file:///Users/rui/Code/ai/novle-related/PlotPilot/infrastructure/ai/providers/))：大模型接口的底层实现，屏蔽了不同厂商 SDK 的差异，统一对外提供 `generate` 和 `stream_generate` 方法。
- **`QdrantVectorStore`** ([infrastructure/ai/qdrant_vector_store.py](file:///Users/rui/Code/ai/novle-related/PlotPilot/infrastructure/ai/qdrant_vector_store.py))：Qdrant 向量库封装，为每本小说动态创建独立的 Collection，并支持复杂的元数据（Payload）过滤检索。

---

## 4. 依赖关系

### 4.1 后端依赖 (Python)
- **核心框架**：`fastapi`, `uvicorn[standard]`, `pydantic`
- **AI 与大模型 SDK**：`anthropic`, `openai`, `volcengine-python-sdk[ark]` (用于接入豆包等)
- **向量检索引擎**：`qdrant-client`, `sentence-transformers` (本地 Embedding 生成), `faiss-cpu`
- **其他辅助**：`httpx`, `jinja2`, `pytest`

### 4.2 前端依赖 (Node.js)
- **核心框架**：`vue` (Vue 3), `vue-router`
- **构建与语言**：`vite`, `typescript`
- **状态管理**：`pinia`
- **UI 与可视化**：`naive-ui`, `echarts`, `vue-echarts`
- **工具库**：`axios`, `dayjs`, `marked`, `@vueuse/core`

---

## 5. 项目运行方式

本项目要求 Python 3.9+ 和 Node.js 18+。后端环境及依赖管理统一使用 **`uv`**。

### 5.1 环境配置与后端启动

1. **克隆仓库并进入目录**：
   ```bash
   git clone git@github.com:hbinr/PlotPilot.git
   cd PlotPilot
   ```

2. **使用 uv 创建虚拟环境并安装依赖**：
   ```bash
   # 创建虚拟环境
   uv venv
   
   # 激活虚拟环境 (macOS/Linux)
   source .venv/bin/activate
   
   # 安装依赖包
   uv pip install -r requirements.txt
   ```

3. **配置环境变量**：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，填写 LLM API 密钥，例如：
   # ANTHROPIC_API_KEY=your_claude_key
   # 或 ARK_API_KEY=your_doubao_key
   ```

4. **启动 Qdrant 向量数据库（依赖 Docker）**：
   ```bash
   docker-compose up -d
   ```

5. **下载本地 Embedding 模型（首次运行需执行）**：
   ```bash
   uv run python scripts/utils/download_embedding_model.py
   # 或使用国内镜像源下载：
   # uv run python scripts/utils/download_model_via_modelscope.py
   ```

6. **启动后端服务**：
   ```bash
   uv run uvicorn interfaces.main:app --host 127.0.0.1 --port 8005 --reload
   ```
   后端启动后，可在 `http://localhost:8005/docs` 访问 Swagger API 交互文档。

### 5.2 前端启动

打开一个新的终端标签页，执行以下命令：

```bash
cd frontend
npm install
npm run dev
```
前端服务默认将运行在 `http://localhost:3000`。
