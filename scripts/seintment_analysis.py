from nltk.sentiment import SentimentIntensityAnalyzer

def sentiment_analysis(news):
    """
    Performs sentiment analysis on cleaned news headlines using NLTK's VADER SentimentIntensityAnalyzer.

    - Calculates a compound sentiment score for each headline.
    - Classifies the sentiment as 'Positive', 'Negative', or 'Neutral' based on the score.

    Args:
        news (pd.DataFrame): A DataFrame containing a 'cleaned_headline' column.

    Returns:
        pd.DataFrame: The original DataFrame with two new columns:
            - 'sentiment_score': VADER compound score of the headline.
            - 'sentiment': Classified sentiment label.
    """
    # Initialize the VADER sentiment analyzer
    sia = SentimentIntensityAnalyzer()

    # Define rules for converting compound scores to sentiment categories
    def classify_sentiment(score):
        if score > 0.05:
            return 'Positive'
        elif score < -0.05:
            return 'Negative'
        else:
            return 'Neutral'

    # Apply sentiment scoring and classification
    news['sentiment_score'] = news['cleaned_headline'].apply(
        lambda x: sia.polarity_scores(x)['compound']
    )
    news['sentiment'] = news['sentiment_score'].apply(classify_sentiment)

    return news
