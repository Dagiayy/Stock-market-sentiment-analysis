import pandas as pd
import matplotlib.pyplot as plt

def sentiment_trends(news):
    """
    Plots sentiment trends over time based on the classified sentiment in the news dataset.

    This function:
    - Groups the news headlines by date and sentiment category (Positive, Neutral, Negative).
    - Counts occurrences per sentiment per date.
    - Plots a line chart showing how sentiment frequencies change over time.

    Args:
        news (pd.DataFrame): A DataFrame containing 'date' and 'sentiment' columns.

    Returns:
        None
    """
    # Group by date and sentiment, then reshape for plotting
    sentiment_trends = news.groupby([news['date'].dt.date, 'sentiment']).size().unstack().fillna(0)
    
    # Plot the sentiment trends
    sentiment_trends.plot(kind='line', title="Sentiment Trends Over Time")
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.grid(True)
    plt.show()

def topic_trends(news, lda, X):
    """
    Plots topic trends over time based on the topic distribution from LDA model.

    This function:
    - Uses the LDA model to get topic probabilities for each headline.
    - Groups and averages topic probabilities by date.
    - Plots how each topic's presence changes over time.

    Args:
        news (pd.DataFrame): DataFrame containing a 'date' column.
        lda (LatentDirichletAllocation): Trained LDA model.
        X (sparse matrix): TF-IDF feature matrix from the news headlines.

    Returns:
        None
    """
    # Transform TF-IDF matrix into topic probabilities using the LDA model
    topic_probs = lda.transform(X)
    
    # Create a DataFrame of topic probabilities with appropriate column names
    topic_trends = pd.DataFrame(topic_probs, columns=[f"Topic {i}" for i in range(lda.n_components)])
    topic_trends['date'] = news['date'].dt.date

    # Group by date and calculate average topic distribution per day
    topic_trends_grouped = topic_trends.groupby('date').mean()

    # Plot topic trends
    topic_trends_grouped.plot(kind='line', title="Topic Trends Over Time")
    plt.xlabel('Date')
    plt.ylabel('Topic Probability')
    plt.grid(True)
    plt.show()
