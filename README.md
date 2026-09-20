# ResearchPilot：AI 科研文献分析平台

ResearchPilot 是一个面向科研论文阅读与分析的 AI Web 应用。用户可以上传多篇本地 PDF 论文，系统自动提取论文内容，并通过 DeepSeek 对论文进行结构化分析。

系统能够生成专业关键词、研究主题簇、概念关系图谱和论文对比矩阵；用户还可以使用中文提问，由 AI 综合多篇论文内容进行回答，并展示对应论文页码和原文证据。

## 核心功能

- 多 PDF 论文上传与文本提取
- AI 生成专业关键词、中英文术语与研究主题簇
- AI 生成论文对比矩阵，包括研究问题、方法、任务、结论和局限性
- 主题簇式知识图谱与中英文标签切换
- 支持中文的多论文智能问答
- 问答结果关联论文名称、页码与可展开原文证据
- SQLite 本地项目保存、加载与恢复
- 一键导出 Markdown 研究报告

## 技术实现

前端使用 **Streamlit** 构建交互式 Web 页面，负责 PDF 上传、项目管理、图谱展示、问答和报告下载。

论文处理使用 **pypdf** 提取 PDF 文本，并保留每页页码标记，为后续 AI 引用和证据定位提供支持。

AI 分析使用 **DeepSeek API**。系统将论文文本、项目上下文和明确的结构化提示词发送给模型，要求模型以 JSON 格式返回关键词、主题簇、概念关系、论文对比信息和项目总结。

知识图谱使用 **PyVis** 构建。节点大小表示 AI 判断的关键词重要性，节点颜色表示所属研究主题，连线粗细表示概念关联强度。

数据持久化使用 **SQLite**。项目名称、论文文本和 AI 分析结果会保存到本地数据库，用户刷新页面或重启程序后仍可加载历史项目。

## 项目结构

```text
ResearchPilot
├── app.py
├── main.py
├── pdf_service.py
├── ai_service.py
├── keyword_service.py
├── knowledge_graph_service.py
├── evidence_service.py
├── insight_service.py
├── rag_service.py
├── database_service.py
├── report_service.py
├── .gitignore
└── README.md

## 系统流程
上传多篇 PDF
↓
提取论文文本并保留页码
↓
DeepSeek 生成结构化论文分析
↓
主题簇、关键词、论文对比矩阵与知识图谱
↓
用户使用中文提问
↓
AI 基于论文内容生成回答
↓
展示论文名称、页码和原文证据
## 快速开始
安装依赖：
pip install -r requirements.txt
配置环境变量：
DEEPSEEK_API_KEY=your_api_key
启动项目：
streamlit run app.py
安全说明
API Key 等敏感信息请保存在 .env 文件中。
.env 和本地数据库文件不应上传到 GitHub。
项目目标
ResearchPilot 的目标不是替代研究者阅读论文，而是帮助用户更快理解多篇论文之间的研究主题、方法差异、关键结论和证据来源。
