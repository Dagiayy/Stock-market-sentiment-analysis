import pandas as pd
from textblob import TextBlob

def align_dates(stock_datasets, news_data):
    """
    Aligns multiple stock datasets with news data based on their date columns.

    Parameters:
    stock_datasets (list of pd.DataFrame): A list of stock dataframes, each containing at least a 'date' column.
    news_data (pd.DataFrame): A dataframe containing news data with a 'date' column.

    Returns:
    pd.DataFrame: A merged dataframe containing aligned dates from news and all stock datasets.
    """
    # Normalize the date format in all stock datasets
    for stock_data in stock_datasets:
        stock_data['date'] = pd.to_datetime(stock_data['date'])
        
    # Normalize the news data
    news_data['date'] = pd.to_datetime(news_data['date'])

    # Merge datasets based on date
    merged_data = pd.merge(news_data, stock_datasets[0], on='date', how='inner')
    for stock_data in stock_datasets[1:]:
        merged_data = pd.merge(merged_data, stock_data, on='date', how='inner')
    return merged_data

def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using TextBlob.

    Parameters:
    text (str): The input text (e.g., news headline) to analyze.

    Returns:
    float: The sentiment polarity score ranging from -1 (negative) to 1 (positive).
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity

def process_news_sentiment(news_data):
    """
    Adds a sentiment score column to the news data based on headlines.

    Parameters:
    news_data (pd.DataFrame): A dataframe with a 'headline' column.

    Returns:
    pd.DataFrame: The original dataframe with an added 'sentiment' column.
    """
    news_data['sentiment'] = news_data['headline'].apply(analyze_sentiment)
    return news_data

def calculate_daily_returns(stock_data):
    """
    Calculates daily return percentages for stock data.

    Parameters:
    stock_data (pd.DataFrame): A dataframe with a 'close' column representing closing prices.

    Returns:
    pd.DataFrame: The original dataframe with an added 'daily_return' column.
    """
    stock_data['daily_return'] = stock_data['close'].pct_change() * 100
    return stock_data

def calculate_correlation(stock_data, news_data):
    """
    Calculates the Pearson correlation between aggregated daily sentiment and daily stock returns.

    Parameters:
    stock_data (list of pd.DataFrame): A list of stock dataframes to align and analyze.
    news_data (pd.DataFrame): A dataframe containing sentiment-analyzed news data.

    Returns:
    float: The Pearson correlation coefficient between daily sentiment and daily stock return.
    """
    # Align stock data and news sentiment by date
    merged_data = align_dates(stock_data, news_data)
    # Aggregate sentiment by date
    aggregated_sentiment = merged_data.groupby('date')['sentiment'].mean()
    # Calculate correlation
    correlation = aggregated_sentiment.corr(merged_data['daily_return'], method='pearson')
    return correlation
