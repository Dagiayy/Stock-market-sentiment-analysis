from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def topic_modeling(news, n_topics=5):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(news['cleaned_headline'])
    
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    
    terms = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        topic_words = [terms[i] for i in topic.argsort()[-10:]]
        topics.append(f"Topic {topic_idx}: {', '.join(topic_words)}")
    
    return topics, lda, X