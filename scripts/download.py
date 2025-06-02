import nltk

def download_vader_lexicon():
    """
    Downloads the VADER sentiment lexicon required for sentiment analysis using NLTK.

    This function ensures that the 'vader_lexicon' resource is available locally.
    It's commonly used with nltk.sentiment.vader.SentimentIntensityAnalyzer.
    """
    nltk.download('vader_lexicon')
