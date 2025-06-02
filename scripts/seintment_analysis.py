
from nltk.sentiment import SentimentIntensityAnalyzer

def sentiment_analysis(news):
    sia = SentimentIntensityAnalyzer()
    
    def classify_sentiment(score):
        if score > 0.05:
            return 'Positive'
        elif score < -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    news['sentiment_score'] = news['cleaned_headline'].apply(lambda x: sia.polarity_scores(x)['compound'])
    news['sentiment'] = news['sentiment_score'].apply(classify_sentiment)
    return news
