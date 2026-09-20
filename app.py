from typing import cast
import html

import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime.uploaded_file_manager import UploadedFile

import ai_service
import database_service
import evidence_service
import knowledge_graph_service
import pdf_service
import report_service


THEME_COLORS = [
    "#78A9D1",
    "#82BFA3",
    "#9CC6E8",
    "#A8D5BA",
    "#86BFC0",
    "#B5D8F0"
]


def render_theme_cards(theme_clusters):
    """
    将 AI 主题簇渲染为彩色概览卡片。
    """

    if not theme_clusters:
        st.info(
            "当前分析尚未包含主题簇。"
            "请重新生成 AI Keyword Analysis。"
        )
        return

    columns = st.columns(
        min(len(theme_clusters), 3)
    )

    for index, cluster in enumerate(theme_clusters):

        theme_zh = html.escape(
            str(cluster.get("theme_zh", "未命名主题"))
        )

        theme = html.escape(
            str(cluster.get("theme", ""))
        )

        description = html.escape(
            str(cluster.get("description", ""))
        )

        keywords = cluster.get("keywords", [])

        keyword_text = html.escape(
            " · ".join(keywords[:6])
        )

        color = THEME_COLORS[
            index % len(THEME_COLORS)
        ]

        with columns[index % len(columns)]:

            st.markdown(
                f"""
                <div style="
                    border-left: 6px solid {color};
                    background: #F1F8F5;
                    border-radius: 10px;
                    padding: 16px;
                    min-height: 185px;
                    margin-bottom: 12px;
                ">
                    <div style="
                        color: {color};
                        font-size: 18px;
                        font-weight: 700;
                        margin-bottom: 4px;
                    ">
                        {theme_zh}
                    </div>
                    <div style="
                        color: #64748B;
                        font-size: 13px;
                        margin-bottom: 10px;
                    ">
                        {theme}
                    </div>
                    <div style="
                        color: #334155;
                        font-size: 14px;
                        margin-bottom: 12px;
                    ">
                        {description}
                    </div>
                    <div style="
                        color: #475569;
                        font-size: 12px;
                    ">
                        {keyword_text}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


st.set_page_config(
    page_title="ResearchPilot",
    page_icon="🔬",
    layout="wide"
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                linear-gradient(
                    135deg,
                    #F4FAF8 0%,
                    #F6FBFF 55%,
                    #F1F8F5 100%
                );
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid #D5E8E2;
        }

        .stTabs [data-baseweb="tab"] {
            background: #EDF7F4;
            border-radius: 10px 10px 0 0;
            color: #42675C;
            font-weight: 600;
            padding: 10px 18px;
        }

        .stTabs [aria-selected="true"] {
            background: #E4F2EE;
            color: #1F5E4D;
            border-bottom: 3px solid #69A98E;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid #D5E8E2;
            border-radius: 12px;
            padding: 14px;
        }

        div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.68);
            border: 1px solid #D8EAE5;
            border-radius: 10px;
        }

        .stButton > button,
        .stDownloadButton > button {
            background: #6FAE9A;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: #568F7D;
            color: white;
            border: none;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid #D5E8E2;
            border-radius: 10px;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)
if "ai_analysis" not in st.session_state:
    st.session_state["ai_analysis"] = None

if "ai_analysis_signature" not in st.session_state:
    st.session_state["ai_analysis_signature"] = ""

if "loaded_papers" not in st.session_state:
    st.session_state["loaded_papers"] = []

if "project_name_input" not in st.session_state:
    st.session_state["project_name_input"] = ""

if "load_notice" not in st.session_state:
    st.session_state["load_notice"] = ""


st.title("🔬 ResearchPilot")

st.caption(
    "AI-powered research literature exploration platform"
)

st.markdown(
    """
    <div style="
        background: linear-gradient(
            135deg,
            #EAF6F2 0%,
            #EAF4FB 100%
        );
        border: 1px solid #CFE5DD;
        border-radius: 18px;
        padding: 26px 30px;
        margin: 12px 0 24px 0;
        box-shadow: 0 6px 18px rgba(93, 140, 122, 0.08);
    ">
        <div style="
            color: #245C50;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        ">
            从论文库到可验证的研究洞察
        </div>
        <div style="
            color: #47675E;
            font-size: 16px;
            line-height: 1.8;
            max-width: 900px;
        ">
            ResearchPilot 是一个面向科研文献理解的 AI 工作台。
            上传多篇 PDF 后，系统会自动生成研究主题、论文对比、
            知识图谱和中文问答，并提供可追溯的论文页码证据。
        </div>
        <div style="
            margin-top: 18px;
            color: #2D6A5A;
            font-size: 14px;
            font-weight: 600;
        ">
            📄 多论文分析　　🧠 AI 主题洞察　　🗺️ 知识图谱　　📌 页码证据
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("了解 ResearchPilot 如何工作"):

    st.markdown(
        """
        **ResearchPilot 的工作流程**

        ```text
        上传多篇 PDF
        ↓
        提取论文文本与页码
        ↓
        DeepSeek 生成结构化分析
        ↓
        主题簇、关键词、论文对比与知识图谱
        ↓
        中文智能问答与页码证据卡片
        ```

        **核心能力**

        - 自动提取专业关键词、中英文术语和研究主题；
        - 对比多篇论文的研究问题、方法、发现与局限性；
        - 用主题簇式知识图谱呈现概念关系；
        - 支持中文提问，并展示可展开的论文页码证据；
        - 支持本地项目保存与 Markdown 研究报告导出。
        """
    )

if st.session_state["load_notice"]:

    st.success(st.session_state["load_notice"])

    st.session_state["load_notice"] = ""


st.subheader("💾 Saved Projects")

saved_projects = database_service.list_projects()

if saved_projects:

    project_options = {}

    for project in saved_projects:

        label = (
            f"{project['name']} "
            f"（最后保存：{project['updated_at']}）"
        )

        project_options[label] = project["id"]

    selected_project_label = st.selectbox(
        "选择一个已保存项目",
        list(project_options.keys())
    )

    if st.button("Load Selected Project"):

        selected_project_id = project_options[
            selected_project_label
        ]

        saved_project = database_service.load_project(
            selected_project_id
        )

        if saved_project:

            loaded_papers = saved_project["papers"]

            loaded_signature = "|".join(
                f"{paper['title']}:{len(paper['text'])}"
                for paper in loaded_papers
            )

            st.session_state["loaded_papers"] = (
                loaded_papers
            )

            st.session_state["ai_analysis"] = (
                saved_project["analysis"]
            )

            st.session_state["ai_analysis_signature"] = (
                loaded_signature
            )

            st.session_state["project_name_input"] = (
                saved_project["name"]
            )

            st.session_state["load_notice"] = (
                f"已加载项目：{saved_project['name']}"
            )

            st.rerun()

else:

    st.info("暂时没有已保存的项目。")


st.divider()

st.subheader("📁 Research Project")

project_name = st.text_input(
    "项目名称",
    placeholder="例如：Few-shot Molecular Learning",
    key="project_name_input"
) or ""


st.subheader("📄 Upload Papers")

uploaded_files = st.file_uploader(
    "上传论文 PDF",
    type=["pdf"],
    accept_multiple_files=True
)

uploaded_files = cast(
    list[UploadedFile],
    uploaded_files
)


uploaded_papers = []

if uploaded_files:

    with st.spinner("正在提取论文文本..."):

        for uploaded_file in uploaded_files:

            result = pdf_service.extract_pdf_text(
                uploaded_file
            )

            if result["success"]:

                uploaded_papers.append({
                    "title": uploaded_file.name,
                    "filename": uploaded_file.name,
                    "pages": result["pages"],
                    "text": result["text"]
                })

            else:

                st.error(
                    f"{uploaded_file.name}："
                    f"{result['message']}"
                )


if uploaded_papers:

    papers = uploaded_papers

    st.success(
        f"已成功解析 {len(papers)} 篇新上传论文"
    )

elif st.session_state["loaded_papers"]:

    papers = st.session_state["loaded_papers"]

    st.success(
        f"当前已加载 {len(papers)} 篇已保存论文"
    )

else:

    papers = []


if papers:

    paper_signature = "|".join(
        f"{paper['title']}:{len(paper['text'])}"
        for paper in papers
    )

    if (
        st.session_state["ai_analysis_signature"]
        != paper_signature
    ):

        st.session_state["ai_analysis"] = None
        st.session_state["ai_analysis_signature"] = ""

    overview_tab, library_tab, comparison_tab, map_tab, ask_tab = (
        st.tabs([
            "🏠 Overview",
            "📚 Paper Library",
            "📊 Comparison",
            "🗺️ Theme Map",
            "💬 Ask AI"
        ])
    )

    with overview_tab:

        st.subheader("🧠 AI Research Analysis")

        st.caption(
            "由 DeepSeek 阅读论文原文后，自动生成关键词、"
            "主题簇、概念关系与论文对比。"
        )

        if st.button("Generate AI Keyword Analysis"):

            try:

                with st.spinner(
                    "DeepSeek 正在阅读论文并生成分析..."
                ):

                    st.session_state["ai_analysis"] = (
                        ai_service.generate_ai_keyword_analysis(
                            papers
                        )
                    )

                    st.session_state["ai_analysis_signature"] = (
                        paper_signature
                    )

            except Exception as error:

                st.error(
                    f"AI 关键词分析失败：{error}"
                )

        analysis = st.session_state["ai_analysis"]

        if not analysis:

            st.info(
                "请点击 Generate AI Keyword Analysis，"
                "由 DeepSeek 生成项目分析。"
            )

        else:

            project_keywords = analysis.get(
                "project_keywords",
                []
            )

            cooccurrence_edges = analysis.get(
                "cooccurrence_edges",
                []
            )

            theme_clusters = analysis.get(
                "theme_clusters",
                []
            )

            metric_col1, metric_col2, metric_col3, metric_col4 = (
                st.columns(4)
            )

            metric_col1.metric(
                "论文数量",
                len(papers)
            )

            metric_col2.metric(
                "AI 专业关键词",
                len(project_keywords)
            )

            metric_col3.metric(
                "主题簇",
                len(theme_clusters)
            )

            metric_col4.metric(
                "概念关系",
                len(cooccurrence_edges)
            )
            st.markdown("#### 📥 Export Research Report")

            report_markdown = (
                report_service.build_markdown_report(
                    project_name or "Untitled Research Project",
                    papers,
                    analysis
                )
            )

            report_file_name = (
                (project_name or "ResearchPilot_Report")
                .replace(" ", "_")
                + "_report.md"
            )

            st.download_button(
                label="Download Markdown Research Report",
                data=report_markdown,
                file_name=report_file_name,
                mime="text/markdown"
            )

            st.markdown("#### 💡 AI Project Insight")

            st.info(
                analysis.get(
                    "project_summary",
                    "DeepSeek 尚未生成项目总结。"
                )
            )

            st.markdown("#### 🎨 Research Themes")

            theme_names = []

            for cluster in theme_clusters:
                theme_names.append(
                    cluster.get(
                        "theme_zh",
                        "未命名主题"
                    )
                )

            if theme_names:
                st.caption(
                    "当前研究主题："
                    + " · ".join(theme_names)
                )
            else:
                st.caption(
                    "暂未生成主题簇。"
                )

            st.markdown("#### 💾 Project Storage")

            if st.button("Save Current Project"):

                if not project_name.strip():

                    st.warning("请先填写项目名称。")

                else:

                    try:

                        with st.spinner("正在保存项目..."):

                            project_id = (
                                database_service.save_project(
                                    project_name,
                                    papers,
                                    analysis
                                )
                            )

                        st.session_state["loaded_papers"] = (
                            papers
                        )

                        st.success(
                            f"项目已保存，项目编号：{project_id}"
                        )

                    except Exception as error:

                        st.error(
                            f"项目保存失败：{error}"
                        )

    with library_tab:

        st.subheader("📚 Paper Library")

        st.caption(
            "查看每篇论文的提取文本和页码标记。"
        )

        for index, paper in enumerate(
            papers,
            start=1
        ):

            with st.expander(
                f"{index}. {paper['filename']}"
            ):

                st.write(
                    f"📄 页数：{paper['pages']}"
                )

                st.write(
                    f"📝 提取字符数："
                    f"{len(paper['text'])}"
                )

                st.text_area(
                    "论文文本预览",
                    value=paper["text"][:5000],
                    height=350,
                    key=f"text_preview_{index}"
                )

    with comparison_tab:

        st.subheader("📊 AI Paper Comparison Matrix")

        analysis = st.session_state["ai_analysis"]

        if not analysis:

            st.info(
                "请先在 Overview 中生成 AI 分析。"
            )

        else:

            paper_comparisons = analysis.get(
                "paper_comparisons",
                []
            )

            if paper_comparisons:

                comparison_rows = []

                for item in paper_comparisons:

                    comparison_rows.append({
                        "论文": item.get("title", ""),
                        "研究问题": item.get(
                            "research_question",
                            ""
                        ),
                        "核心方法": item.get(
                            "core_method",
                            ""
                        ),
                        "任务 / 数据": item.get(
                            "task_or_data",
                            ""
                        ),
                        "主要发现": item.get(
                            "main_finding",
                            ""
                        ),
                        "局限性": item.get(
                            "limitation",
                            ""
                        )
                    })

                st.dataframe(
                    comparison_rows,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "当前 AI 分析尚未包含论文对比数据。"
                    "请重新生成 AI 分析。"
                )

    with map_tab:

        st.subheader("🗺️ AI Theme Knowledge Map")

        analysis = st.session_state["ai_analysis"]

        if not analysis:

            st.info(
                "请先在 Overview 中生成 AI 分析。"
            )

        else:

            project_keywords = analysis.get(
                "project_keywords",
                []
            )

            paper_keywords = analysis.get(
                "paper_keywords",
                {}
            )

            cooccurrence_edges = analysis.get(
                "cooccurrence_edges",
                []
            )

            theme_clusters = analysis.get(
                "theme_clusters",
                []
            )

            st.markdown("#### Theme Cluster Guide")

            render_theme_cards(theme_clusters)

            st.markdown("#### AI Project Keywords")

            st.dataframe(
                project_keywords,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("#### AI Paper Keywords")

            for title, keywords in paper_keywords.items():

                keyword_text = " · ".join(
                    item["keyword"]
                    for item in keywords
                )

                st.write(
                    f"**{title}**：{keyword_text}"
                )

            st.markdown("#### AI Concept Relationships")

            st.dataframe(
                cooccurrence_edges,
                use_container_width=True,
                hide_index=True
            )

            label_mode = st.selectbox(
                "图谱标签语言",
                ["双语", "English", "中文"],
                key="map_label_mode"
            )

            graph_html = (
                knowledge_graph_service.create_knowledge_graph(
                    cooccurrence_edges,
                    project_keywords,
                    theme_clusters,
                    label_mode
                )
            )

            if graph_html:

                components.html(
                    graph_html,
                    height=700,
                    scrolling=False
                )

            else:

                st.info(
                    "DeepSeek 暂未生成足够的概念关系。"
                )

    with ask_tab:

        st.subheader("💬 Ask ResearchPilot")

        analysis = st.session_state["ai_analysis"]

        if not analysis:

            st.info(
                "请先在 Overview 中生成 AI 分析。"
            )

        else:

            project_keywords = analysis.get(
                "project_keywords",
                []
            )

            cooccurrence_edges = analysis.get(
                "cooccurrence_edges",
                []
            )

            st.caption(
                "支持中文提问。DeepSeek 会结合论文原文、"
                "主题簇与概念关系生成带页码引用的回答。"
            )

            question = st.text_input(
                "输入你的研究问题",
                placeholder=(
                    "例如：这些论文的方法有什么差异？"
                ),
                key="research_question"
            ) or ""

            if st.button("Ask AI", key="ask_ai_button"):

                if not question.strip():

                    st.warning("请先输入一个问题。")

                else:

                    try:

                        with st.spinner(
                            "DeepSeek 正在阅读论文并生成分析..."
                        ):

                            answer = (
                                ai_service.generate_research_analysis(
                                    question,
                                    papers,
                                    project_keywords,
                                    cooccurrence_edges
                                )
                            )

                        st.markdown(
                            "#### 🤖 ResearchPilot Analysis"
                        )

                        st.write(answer)

                        citations = (
                            evidence_service.extract_citations(
                                answer
                            )
                        )

                        if citations:

                            st.markdown(
                                "#### 📌 Evidence Cards"
                            )

                            for index, citation in enumerate(
                                citations,
                                start=1
                            ):

                                title = citation["title"]
                                page = citation["page"]

                                page_text = (
                                    evidence_service.get_page_text(
                                        papers,
                                        title,
                                        page
                                    )
                                )

                                with st.expander(
                                    f"证据 {index}：{title}，"
                                    f"第 {page} 页"
                                ):

                                    if page_text:

                                        st.caption(
                                            "以下是 AI 引用的原文页："
                                        )

                                        st.text_area(
                                            "论文原文",
                                            value=page_text,
                                            height=280,
                                            key=(
                                                f"evidence_"
                                                f"{index}_{page}"
                                            )
                                        )

                                    else:

                                        st.warning(
                                            "没有找到该页原文。"
                                            "请确认 PDF 已重新上传"
                                            "并保存。"
                                        )

                        else:

                            st.info(
                                "AI 回答中暂未识别到页码引用。"
                            )

                    except Exception as error:

                        st.error(
                            f"AI 分析失败：{error}"
                        )

else:

    st.info(
        "请上传 PDF，或从顶部已保存项目列表加载项目。"
    )