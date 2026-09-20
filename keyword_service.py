import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from collections import Counter
from itertools import combinations

ACADEMIC_STOP_WORDS = {
    "abstract", "approach", "based", "dataset", "datasets",
    "different", "experiments", "figure", "introduction",
    "method", "methods", "model", "models", "paper",
    "proposed", "research", "result", "results",
    "section", "show", "study", "table", "using", "use", "used","graph","lin","liu","wang",
    "et", "al", "etal", "fig", "eq",
    "https", "http", "www", "com"
}

STOP_WORDS = list(
    ENGLISH_STOP_WORDS.union(ACADEMIC_STOP_WORDS)
)

def clean_paper_text(text):
    """
    清理论文中的引用编号和常见引用格式，
    降低作者姓名进入关键词的概率。
    """

    text = re.sub(
        r"\[[0-9,\s-]+\]",
        " ",
        text
    )

    text = re.sub(
        r"\b[A-Z][a-zA-Z-]+\s+et\s+al\.?,?\s*\(?\d{4}[a-z]?\)?",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text

def analyze_papers(papers, top_n=20):
    """
    papers 是一个论文列表。
    每篇论文需要包含：
    title：论文名称
    text：论文全文
    """

    valid_papers = []

    for paper in papers:
        if paper["text"].strip():
            valid_papers.append(paper)

    if not valid_papers:
        return {
            "paper_keywords": {},
            "project_keywords": [],
            "message": "没有可分析的文本。"
        }

    vectorizer = TfidfVectorizer(
        stop_words=STOP_WORDS,
        lowercase=True,
        ngram_range=(2, 3),
        sublinear_tf=True,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9-]{2,}\b"
    )

    try:
        cleaned_texts = []

        for paper in valid_papers:
            cleaned_text = clean_paper_text(
                paper["text"]
            )

            cleaned_texts.append(cleaned_text)

        tfidf_matrix = vectorizer.fit_transform(
            cleaned_texts
        )

    except ValueError:
        return {
            "paper_keywords": {},
            "project_keywords": [],
            "message": "没有找到足够的英文关键词。"
        }

    terms = vectorizer.get_feature_names_out()

    paper_keywords = {}
    cooccurrence_counts = Counter()


    for paper_index, paper in enumerate(valid_papers):

        row = tfidf_matrix.getrow(paper_index)

        sorted_positions = row.data.argsort()[::-1][:top_n]

        keywords = []

        for position in sorted_positions:

            keyword = terms[row.indices[position]]
            score = round(float(row.data[position]), 4)

            keywords.append({
                "keyword": keyword,
                "tfidf": score
            })

        paper_keywords[paper["title"]] = keywords

        top_terms = sorted(
            item["keyword"]
            for item in keywords[:5]
        )

        for source, target in combinations(top_terms, 2):
            cooccurrence_counts[(source, target)] += 1

    document_frequency = (tfidf_matrix > 0).sum(axis=0).A1
    average_tfidf = tfidf_matrix.mean(axis=0).A1

    ranked_indices = sorted(
        range(len(terms)),
        key=lambda index: (
            average_tfidf[index],
            document_frequency[index]
        ),
        reverse=True
    )[:top_n]

    project_keywords = []

    for index in ranked_indices:

        project_keywords.append({
            "keyword": terms[index],
            "average_tfidf": round(float(average_tfidf[index]), 4),
            "document_frequency": int(document_frequency[index])
        })
    cooccurrence_edges = []

    for (source, target), count in cooccurrence_counts.items():
        cooccurrence_edges.append({
            "source": source,
            "target": target,
            "cooccurrence": count
        })

    cooccurrence_edges.sort(
        key=lambda edge: edge["cooccurrence"],
        reverse=True
    )

    return {
        "paper_keywords": paper_keywords,
        "project_keywords": project_keywords,
        "cooccurrence_edges": cooccurrence_edges,
        "message": ""
    }