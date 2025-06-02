import pandas as pd
from datetime import datetime

def load_data(file_path):
    news = pd.read_csv(file_path)
    news['cleaned_headline'] = news['headline'].str.replace(r'[^\w\s]', '').str.lower()
    news['date'] = pd.to_datetime(news['date'], errors='coerce')
    news = news.drop(columns=['Unnamed: 0'])
    return news