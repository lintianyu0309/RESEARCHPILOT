def generate_insights(project_keywords, cooccurrence_edges, paper_count):
    """
    根据关键词统计和共现关系，生成基础研究洞察。
    """

    if not project_keywords:
        return {
            "main_theme": "暂时没有足够的数据生成洞察。",
            "shared_theme": "暂时没有足够的数据生成洞察。",
            "key_connections": "暂时没有足够的数据生成洞察。",
            "paper_count": paper_count,
            "keyword_count": 0,
            "edge_count": 0
        }

    top_keywords = [
        item["keyword"]
        for item in project_keywords[:5]
    ]

    shared_keywords = [
        item["keyword"]
        for item in project_keywords
        if item["document_frequency"] >= 2
    ]

    strongest_edges = cooccurrence_edges[:3]

    main_theme = (
        "这组论文的主要研究主题集中在："
        + "、".join(top_keywords)
        + "。"
    )

    if shared_keywords:
        shared_theme = (
            "跨多篇论文重复出现的共同主题包括："
            + "、".join(shared_keywords[:5])
            + "。"
        )
    else:
        shared_theme = (
            "目前上传论文之间的共同关键词较少；"
            "继续上传主题相近的论文后，跨论文趋势会更明显。"
        )

    if strongest_edges:
        connection_text = []

        for edge in strongest_edges:
            connection_text.append(
                f"{edge['source']} — {edge['target']}"
            )

        key_connections = (
            "当前最值得关注的关键词关联是："
            + "；".join(connection_text)
            + "。"
        )
    else:
        key_connections = "暂时没有足够的关键词关系。"

    return {
        "main_theme": main_theme,
        "shared_theme": shared_theme,
        "key_connections": key_connections,
        "paper_count": paper_count,
        "keyword_count": len(project_keywords),
        "edge_count": len(cooccurrence_edges)
    }