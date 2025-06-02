import pandas as pd
import matplotlib.pyplot as plt

def sentiment_trends(news):
    sentiment_trends = news.groupby([news['date'].dt.date, 'sentiment']).size().unstack().fillna(0)
    sentiment_trends.plot(kind='line', title="Sentiment Trends Over Time")
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.show()

def topic_trends(news, lda, X):
    topic_probs = lda.transform(X)
    topic_trends = pd.DataFrame(topic_probs, columns=[f"Topic {i}" for i in range(lda.n_components)])
    topic_trends['date'] = news['date'].dt.date
    
    topic_trends_grouped = topic_trends.groupby('date').mean()
    topic_trends_grouped.plot(kind='line', title="Topic Trends Over Time")
    plt.xlabel('Date')
    plt.ylabel('Topic Probability')
    plt.show()