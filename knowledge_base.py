from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load your knowledge base file
with open("knowledge.txt", "r", encoding="utf-8") as f:
    KNOWLEDGE_BASE = [line.strip() for line in f if line.strip()]

def get_relevant_context(query, top_k=3):
    """Return the most relevant lines from knowledge base using TF-IDF similarity."""
    docs = KNOWLEDGE_BASE + [query]
    vectorizer = TfidfVectorizer().fit_transform(docs)
    vectors = vectorizer.toarray()

    query_vec = vectors[-1]
    similarities = cosine_similarity([query_vec], vectors[:-1])[0]

    top_indices = similarities.argsort()[-top_k:][::-1]
    top_matches = [KNOWLEDGE_BASE[i] for i in top_indices]
    return "\n".join(top_matches)
