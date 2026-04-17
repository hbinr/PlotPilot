# PlotPilot (墨枢) - 核心代码百科 (Code Wiki)

> **版本：** 详细架构版
> **定位：** AI 驱动的长篇小说创作平台，集自动驾驶生成、知识图谱管理、文风分析于一体。

---

## 1. 项目整体架构

PlotPilot 采用了严格的**领域驱动设计（DDD，Domain-Driven Design）**四层架构，确保了核心业务规则与外部技术实现（如特定的大模型、数据库框架、Web 框架）的彻底隔离。

### 1.1 架构分层
- **Domain（领域层）**：系统的绝对核心，没有任何外部依赖。定义了小说、设定集、知识图谱等聚合根（Aggregate Root）、实体（Entity）、值对象（Value Object）和领域事件。
- **Application（应用层）**：业务用例的编排者。它负责统筹多个领域模型，并调用基础设施层的接口，完成如“自动驾驶生成一章”、“宏观剧情诊断”等复杂工作流。
- **Infrastructure（基础设施层）**：技术实现层。负责实现领域层定义的仓储接口（Repository）和外部服务接口。包括 SQLite 数据库读写、Qdrant 向量检索引擎接入、以及各大模型（Claude、Doubao）的 SDK 封装。
- **Interfaces（接口层）**：对外的交互边界。主要由 FastAPI 构成的 RESTful API 提供支持，通过依赖注入（Dependency Injection）将请求路由到应用层。

### 1.2 核心技术栈
- **后端**：Python 3.9+ / FastAPI / Uvicorn / Pydantic
- **数据库**：SQLite（关系型数据） / Qdrant 或 ChromaDB（向量数据）
- **AI / 大模型**：Anthropic Claude SDK / OpenAI 兼容协议（用于接入豆包等） / BAAI bge-small-zh（本地 Embedding 模型）
- **前端**：Vue 3 / TypeScript / Vite / Pinia / Naive UI / ECharts

---

## 2. 主要模块职责

项目按照功能域被精细化拆分，以下是各个核心模块的职责说明：

### 2.1 核心领域 (Domain)
* **`domain/novel`（小说引擎）**：管理小说的整体生命周期、章节（Chapter）、剧情张力曲线（PlotArc）、多线并行的故事线（Storyline）以及用于追踪悬念的伏笔台账（ForeshadowingRegistry）。
* **`domain/bible`（世界观设定）**：存储静态设定的“百科全书”，管理角色（Character）、地点（Location）、世界观法则（WorldSetting）和专属文风约束。
* **`domain/cast`（角色图谱）**：管理角色间的动态关系网络。记录角色之间的关系变化轨迹以及导致这些变化的关键故事事件（StoryEvent）。
* **`domain/knowledge`（叙事记忆）**：负责解决长文本记忆遗忘。将大段文本压缩为章节摘要（ChapterSummary），并提取出精确的知识三元组（KnowledgeTriple）以供向量检索。
* **`domain/blueprint`（蓝图与结构）**：用于宏观故事规划，包含幕-卷-章的多级树状结构（Story Node）。

### 2.2 应用服务 (Application)
* **`engine`（生成引擎与自动驾驶）**：
  - 核心功能：维持后台守护进程运转，实现无人值守的连续生成。
  - 上下文管理：智能计算 Token 预算，按“洋葱模型”组装必须设定、历史摘要和向量召回知识。
* **`analyst`（数据分析师）**：
  - **文风漂移检测**：监控大模型生成的文本风格是否与作者设定的基准偏离。
  - **张力分析**：通过提取文本的情绪和冲突密度，绘制张力曲线，并在“卡文”时提供破局建议（张力弹弓）。
* **`audit`（质量审计）**：
  - 在不打断生成的前提下，通过“幽灵批注”提示设定冲突。
  - 扫描全书人设，提供宏观逻辑诊断（Macro Diagnosis）和重构提案。
* **`blueprint`（大纲与节拍表）**：
  - 基于检索增强（RAG）将章节大纲扩展为具备 3-5 个场景的细化节拍表（Beat Sheet）。

---

## 3. 关键类与函数说明

### 3.1 实体与聚合根 (Domain Layer)
- **`Novel`** `[domain/novel/entities/novel.py]`
  - **职责**：小说聚合根。控制整个小说的元数据、自动驾驶状态机（`AutopilotState`）和生成上限。
  - **关键方法**：`can_generate_next_chapter()` 判断是否触发了熔断机制或达到了连续生成上限。
- **`StoryKnowledge`** `[domain/knowledge/story_knowledge.py]`
  - **职责**：管理所有动态生成的叙事事实。
  - **关键机制**：将非结构化的章节文本提取为主谓宾结构的三元组（`KnowledgeTriple`），并在后续生成中作为精确记忆提供给 LLM。

### 3.2 核心服务 (Application Layer)
- **`AutopilotDaemon.run()`** `[application/engine/services/autopilot_daemon.py]`
  - **逻辑**：死循环轮询数据库中处于 `RUNNING` 状态的小说。基于状态机模式，按顺序调用工作流，具备节拍级的幂等性（中途崩溃重启后能从断点继续）。
- **`ContextBuilder.build_context()`** `[application/engine/services/context_builder.py]`
  - **逻辑**：上下文构建器。这是生成质量的核心。它会根据最大 Token 限制（如 35K），动态分配空间给：1) 强制内容（当前大纲、设定集）；2) 动态内容（最近 3 章全文）；3) 检索内容（Qdrant 召回的相关三元组和历史摘要）。
- **`TensionAnalyzer.analyze_tension()`** `[application/analyst/services/tension_analyzer.py]`
  - **逻辑**：统计叙事事件中的冲突词频，计算当前章节的“张力分数”。如果发现连续章节张力低迷，会调用大模型生成“张力弹弓”策略。

### 3.3 基础设施实现 (Infrastructure Layer)
- **`AnthropicProvider` / `OpenAIProvider`** `[infrastructure/ai/providers/]`
  - **逻辑**：实现了 `LLMService` 协议。其中 `stream_generate()` 封装了底层的异步 HTTPX 或官方 SDK 调用，向外抛出标准的 Server-Sent Events (SSE) 数据流，供前端实时打字机渲染。
- **`QdrantVectorStore`** `[infrastructure/ai/qdrant_vector_store.py]`
  - **逻辑**：封装了 `qdrant_client`。在存储时除了向量本身，还会存储丰富的 Payload（如所属章节、数据类型等），在 `search()` 阶段通过 Payload Filter 实现精准的混合召回。

---

## 4. 依赖关系

### 4.1 后端核心依赖 (`requirements.txt`)
* **Web 与路由**：`fastapi` (>=0.109.0), `uvicorn[standard]`, `pydantic`
* **大模型 SDK**：`anthropic` (Claude 官方支持), `openai` (用于兼容所有类 OpenAI 接口，如豆包), `volcengine-python-sdk[ark]` (火山引擎支持)
* **向量检索**：`qdrant-client` (向量库连接), `sentence-transformers` (用于本地离线生成文本 Embedding 向量), `faiss-cpu`, `numpy`
* **网络与测试**：`httpx` (异步 HTTP 请求), `pytest`

### 4.2 前端核心依赖 (`frontend/package.json`)
* **框架与工具**：`vue` (^3.5), `vite`, `typescript`, `vue-router`, `pinia` (状态管理)
* **UI 与图表**：`naive-ui` (组件库), `echarts`, `vue-echarts` (用于绘制张力曲线、角色关系图谱)
* **其他**：`axios`, `marked` (Markdown 渲染), `dompurify`

---

## 5. 项目运行方式

> ⚠️ **规范提醒**：按照项目规范，后端环境管理、包安装及运行**统一使用 `uv` 命令**。

### 5.1 前置环境
* Python 3.9 或以上版本
* Node.js 18 或以上版本
* Docker（用于运行 Qdrant 向量数据库）

### 5.2 后端启动流程

1. **克隆代码库**
   ```bash
   git clone git@github.com:hbinr/PlotPilot.git
   cd PlotPilot
   ```

2. **初始化环境与依赖 (使用 uv)**
   ```bash
   # 创建并激活虚拟环境
   uv venv  --python 3.11
   source py311/bin/activate # Windows 用户使用: py311\Scripts\activate
   
   # 安装所有依赖
   uv pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 打开 .env 文件，填写你的大模型 API 密钥。例如：
   # ANTHROPIC_API_KEY=sk-ant-xxx
   # 或者使用豆包：ARK_API_KEY=xxx
   ```

4. **启动向量数据库**
   ```bash
   # 依赖 Docker，启动本地 Qdrant 服务 (端口 6333)
   docker-compose up -d
   ```

5. **下载本地 Embedding 模型 (首次运行必须)**
   ```bash
   # 该脚本会下载 bge-small-zh 模型到本地，用于知识库的离线向量化
   uv run python scripts/utils/download_embedding_model.py
   # 若国内网络不佳，可使用 modelscope 镜像源脚本：
   # uv run python scripts/utils/download_model_via_modelscope.py
   ```

6. **启动 FastAPI 后端服务**
   ```bash
   uv run uvicorn interfaces.main:app --host 127.0.0.1 --port 8005 --reload
   ```
   *服务启动后，可以访问 [http://localhost:8005/docs](http://localhost:8005/docs) 查看交互式 API 文档。*

### 5.3 前端启动流程

打开一个新的终端窗口：

```bash
cd frontend
pnpm install
pnpm run dev
```

前端将默认运行在 [http://localhost:3000](http://localhost:3000)，在浏览器中打开即可开始创作。
