from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def split_text(text, chunk_size=800, overlap=150):
    """
    将长论文切成有少量重叠的文本块。
    """

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def search_papers(question, papers, top_k=5):
    """
    在所有论文文本块中寻找与问题最相关的内容。
    """

    document_chunks = []

    for paper in papers:
        title = paper["title"]

        chunks = split_text(paper["text"])

        for chunk in chunks:
            document_chunks.append({
                "title": title,
                "text": chunk
            })

    if not document_chunks:
        return []

    texts = [question]

    for chunk in document_chunks:
        texts.append(chunk["text"])

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    try:
        matrix = vectorizer.fit_transform(texts)

    except ValueError:
        return []

    question_vector = matrix[0]
    chunk_vectors = matrix[1:]

    scores = cosine_similarity(
        question_vector,
        chunk_vectors
    ).flatten()

    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:
        score = float(scores[index])

        if score <= 0:
            continue

        results.append({
            "title": document_chunks[index]["title"],
            "text": document_chunks[index]["text"],
            "score": round(score, 3)
        })

    return results