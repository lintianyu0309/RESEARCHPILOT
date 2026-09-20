from datetime import datetime


def clean_markdown_cell(value):
    """
    清理 Markdown 表格单元格中的换行和竖线。
    """

    text = str(value or "")

    text = text.replace("\n", " ")

    text = text.replace("|", "／")

    return text.strip()


def build_markdown_report(
    project_name,
    papers,
    analysis
):
    """
    根据当前项目和 AI 分析生成 Markdown 研究报告。
    """

    project_summary = analysis.get(
        "project_summary",
        "暂无项目总结。"
    )

    project_keywords = analysis.get(
        "project_keywords",
        []
    )

    theme_clusters = analysis.get(
        "theme_clusters",
        []
    )

    paper_comparisons = analysis.get(
        "paper_comparisons",
        []
    )

    cooccurrence_edges = analysis.get(
        "cooccurrence_edges",
        []
    )

    created_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    lines = []

    lines.append(f"# {project_name}")
    lines.append("")
    lines.append("## ResearchPilot AI Research Report")
    lines.append("")
    lines.append(f"- 生成时间：{created_time}")
    lines.append(f"- 论文数量：{len(papers)}")
    lines.append("")

    lines.append("## 项目总结")
    lines.append("")
    lines.append(project_summary)
    lines.append("")

    lines.append("## 研究主题簇")
    lines.append("")

    if theme_clusters:

        for cluster in theme_clusters:

            theme_zh = cluster.get(
                "theme_zh",
                "未命名主题"
            )

            theme = cluster.get(
                "theme",
                ""
            )

            description = cluster.get(
                "description",
                ""
            )

            keywords = cluster.get(
                "keywords",
                []
            )

            lines.append(
                f"### {theme_zh} · {theme}"
            )

            lines.append("")
            lines.append(description)
            lines.append("")
            lines.append(
                "**关键词：** "
                + " · ".join(keywords)
            )
            lines.append("")

    else:

        lines.append("暂未生成主题簇。")
        lines.append("")

    lines.append("## 项目关键词")
    lines.append("")

    if project_keywords:

        for item in project_keywords:

            keyword = item.get("keyword", "")
            chinese_label = item.get(
                "chinese_label",
                ""
            )
            theme = item.get("theme", "")

            lines.append(
                f"- **{keyword}**"
                f"（{chinese_label}，主题：{theme}）"
            )

    else:

        lines.append("暂未生成关键词。")

    lines.append("")

    lines.append("## 论文对比矩阵")
    lines.append("")

    lines.append(
        "| 论文 | 研究问题 | 核心方法 | 任务 / 数据 | 主要发现 | 局限性 |"
    )

    lines.append(
        "| --- | --- | --- | --- | --- | --- |"
    )

    for item in paper_comparisons:

        row = [
            clean_markdown_cell(
                item.get("title", "")
            ),
            clean_markdown_cell(
                item.get("research_question", "")
            ),
            clean_markdown_cell(
                item.get("core_method", "")
            ),
            clean_markdown_cell(
                item.get("task_or_data", "")
            ),
            clean_markdown_cell(
                item.get("main_finding", "")
            ),
            clean_markdown_cell(
                item.get("limitation", "")
            )
        ]

        lines.append(
            "| " + " | ".join(row) + " |"
        )

    lines.append("")

    lines.append("## 概念关系")
    lines.append("")

    if cooccurrence_edges:

        for edge in cooccurrence_edges:

            lines.append(
                f"- {edge.get('source', '')} "
                f"↔ {edge.get('target', '')} "
                f"（关联强度："
                f"{edge.get('cooccurrence', '')}）"
            )

    else:

        lines.append("暂未生成概念关系。")

    lines.append("")

    lines.append("## 论文列表")
    lines.append("")

    for index, paper in enumerate(
        papers,
        start=1
    ):

        lines.append(
            f"{index}. {paper['title']} "
            f"（{paper['pages']} 页）"
        )

    lines.append("")
    lines.append("---")
    lines.append(
        "本报告由 ResearchPilot 基于上传论文和 AI 分析生成。"
    )

    return "\n".join(lines)