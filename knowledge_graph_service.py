from pyvis.network import Network


THEME_COLORS = [
    "#2563EB",
    "#7C3AED",
    "#DB2777",
    "#EA580C",
    "#16A34A",
    "#0891B2",
    "#CA8A04"
]


def get_node_label(keyword, chinese_label, label_mode):
    """
    根据用户选择，生成英文、中文或双语节点标签。
    """

    if label_mode == "中文":
        return chinese_label or keyword

    if label_mode == "双语":
        if chinese_label:
            return f"{keyword}\n{chinese_label}"

    return keyword


def create_knowledge_graph(
    edges,
    project_keywords,
    theme_clusters,
    label_mode
):
    """
    创建按研究主题着色的知识图谱。
    """

    if not edges:
        return ""

    graph = Network(
        height="680px",
        width="100%",
        bgcolor="#F8FAFC",
        font_color="#0F172A",
        directed=False,
        notebook=False,
        cdn_resources="in_line"
    )

    keyword_info = {}

    for item in project_keywords:
        keyword_info[item["keyword"]] = item

    theme_names = []

    for cluster in theme_clusters:
        theme = cluster.get("theme", "Uncategorized")

        if theme not in theme_names:
            theme_names.append(theme)

    if not theme_names:
        theme_names = ["Uncategorized"]

    theme_colors = {}

    for index, theme in enumerate(theme_names):
        theme_colors[theme] = THEME_COLORS[
            index % len(THEME_COLORS)
        ]

    graph_keywords = set()

    for edge in edges:
        graph_keywords.add(edge["source"])
        graph_keywords.add(edge["target"])

    importance_scores = []

    for keyword in graph_keywords:
        info = keyword_info.get(keyword, {})

        score = info.get("average_tfidf", 1)

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 1

        importance_scores.append(score)

    minimum_score = min(importance_scores)
    maximum_score = max(importance_scores)

    for keyword in graph_keywords:

        info = keyword_info.get(keyword, {})

        chinese_label = info.get(
            "chinese_label",
            ""
        )

        theme = info.get(
            "theme",
            "Uncategorized"
        )

        score = info.get("average_tfidf", 1)

        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 1

        document_frequency = info.get(
            "document_frequency",
            0
        )

        if maximum_score == minimum_score:
            normalized_score = 0.5
        else:
            normalized_score = (
                (score - minimum_score)
                / (maximum_score - minimum_score)
            )

        node_size = 18 + normalized_score * 35

        node_color = theme_colors.get(
            theme,
            "#64748B"
        )

        node_label = get_node_label(
            keyword,
            chinese_label,
            label_mode
        )

        graph.add_node(
            keyword,
            label=node_label,
            title=(
                f"<b>{keyword}</b>"
                f"<br>中文：{chinese_label}"
                f"<br>主题：{theme}"
                f"<br>AI 重要性：{score}"
                f"<br>相关论文数：{document_frequency}"
            ),
            size=node_size,
            shape="dot",
            group=theme,
            color={
                "background": node_color,
                "border": "#0F172A",
                "highlight": {
                    "background": "#F59E0B",
                    "border": "#92400E"
                }
            },
            borderWidth=2,
            font={
                "size": 16,
                "face": "Arial",
                "color": "#0F172A",
                "strokeWidth": 3,
                "strokeColor": "#FFFFFF"
            }
        )

    for edge in edges:

        strength = edge.get(
            "cooccurrence",
            1
        )

        try:
            strength = float(strength)
        except (TypeError, ValueError):
            strength = 1

        graph.add_edge(
            edge["source"],
            edge["target"],
            width=1 + min(strength, 5),
            title=f"AI 关联强度：{strength}",
            color={
                "color": "#64748B",
                "highlight": "#F59E0B",
                "opacity": 0.45
            }
        )

    graph.set_options("""
    {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -3200,
          "springLength": 200,
          "springConstant": 0.04
        },
        "stabilization": {
          "iterations": 250
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 100
      }
    }
    """)

    return graph.generate_html()