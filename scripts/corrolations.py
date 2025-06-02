import pandas as pd
from textblob import TextBlob

def align_dates(stock_datasets, news_data):

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
    blob = TextBlob(text)
    return blob.sentiment.polarity

def process_news_sentiment(news_data):
    news_data['sentiment'] = news_data['headline'].apply(analyze_sentiment)
    return news_data

def calculate_daily_returns(stock_data):
    stock_data['daily_return'] = stock_data['close'].pct_change() * 100
    return stock_data

def calculate_correlation(stock_data, news_data):
    # Align stock data and news sentiment by date
    merged_data = align_dates(stock_data, news_data)
    # Aggregate sentiment by date
    aggregated_sentiment = merged_data.groupby('date')['sentiment'].mean()
    # Calculate correlation
    correlation = aggregated_sentiment.corr(merged_data['daily_return'], method='pearson')
    return correlation