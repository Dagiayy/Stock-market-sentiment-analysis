"""Topic modeling over cleaned headlines (TF-IDF + Latent Dirichlet Allocation)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer

from stock_sentiment.config import settings


@dataclass
class TopicModelResult:
    vectorizer: TfidfVectorizer
    model: LatentDirichletAllocation
    document_topics: np.ndarray
    topics: list[str]


def fit_topic_model(
    headlines: list[str], n_topics: int | None = None, top_n_words: int = 10
) -> TopicModelResult:
    n_topics = n_topics or settings.lda_topics
    vectorizer = TfidfVectorizer(stop_words="english", min_df=2, max_df=0.95)
    doc_term_matrix = vectorizer.fit_transform(headlines)

    model = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    document_topics = model.fit_transform(doc_term_matrix)

    terms = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_words = [terms[i] for i in topic.argsort()[-top_n_words:][::-1]]
        topics.append(f"Topic {topic_idx}: {', '.join(top_words)}")

    return TopicModelResult(
        vectorizer=vectorizer, model=model, document_topics=document_topics, topics=topics
    )
