from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def topic_modeling(news, n_topics=5):
    """
    Performs topic modeling on cleaned news headlines using TF-IDF and Latent Dirichlet Allocation (LDA).

    This function:
    - Converts cleaned headlines into a TF-IDF feature matrix.
    - Fits an LDA model to discover latent topics.
    - Extracts top keywords for each topic.

    Args:
        news (pd.DataFrame): A DataFrame containing a 'cleaned_headline' column.
        n_topics (int): Number of topics to extract (default is 5).

    Returns:
        tuple:
            - topics (list of str): List of topics with top 10 keywords each.
            - lda (LatentDirichletAllocation): The trained LDA model.
            - X (scipy.sparse matrix): TF-IDF matrix of the input headlines.
    """
    # Convert cleaned headlines into a TF-IDF feature matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(news['cleaned_headline'])

    # Train an LDA model on the TF-IDF matrix
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)

    # Extract topic keywords from the model
    terms = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        # Get the top 10 words for each topic
        topic_words = [terms[i] for i in topic.argsort()[-10:]]
        topics.append(f"Topic {topic_idx}: {', '.join(topic_words)}")

    return topics, lda, X
