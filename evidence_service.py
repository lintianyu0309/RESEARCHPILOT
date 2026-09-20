import re


CITATION_PATTERN = re.compile(
    r"\[论文：(?P<title>.*?)，第\s*(?P<page>\d+)\s*页\]"
)


def extract_citations(answer):
    """
    从 AI 回答中提取：
    [论文：文件名.pdf，第 N 页]
    """

    citations = []
    seen_citations = set()

    matches = CITATION_PATTERN.finditer(answer)

    for match in matches:

        title = match.group("title").strip()
        page = int(match.group("page"))

        citation_key = (title, page)

        if citation_key not in seen_citations:

            citations.append({
                "title": title,
                "page": page
            })

            seen_citations.add(citation_key)

    return citations


def get_page_text(papers, title, page):
    """
    根据论文名称和页码，从保存的论文文本中提取对应页原文。
    """

    target_paper = None

    for paper in papers:

        if paper["title"].strip() == title.strip():
            target_paper = paper
            break

    if not target_paper:
        return ""

    paper_text = target_paper["text"]

    page_pattern = re.compile(
        rf"【第 {page} 页】"
        rf"(?P<text>.*?)"
        rf"(?=【第 \d+ 页】|\Z)",
        re.DOTALL
    )

    match = page_pattern.search(paper_text)

    if not match:
        return ""

    return match.group("text").strip()