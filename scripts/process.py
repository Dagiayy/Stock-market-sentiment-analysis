import pandas as pd
from datetime import datetime
import re

def load_data(file_path):
    """
    Loads and cleans news data from a CSV file.
    
    - Removes punctuation from headlines.
    - Converts headlines to lowercase.
    - Parses the date column into datetime format.
    - Drops unnecessary columns like 'Unnamed: 0' if present.
    
    Args:
        file_path (str): The path to the CSV file.
    
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    try:
        # Read CSV file
        news = pd.read_csv(file_path)

        # Drop unnamed index column if it exists
        news = news.loc[:, ~news.columns.str.contains('^Unnamed')]

        # Clean and preprocess the headline column
        news['cleaned_headline'] = news['headline'].astype(str).apply(
            lambda x: re.sub(r'[^\w\s]', '', x).lower()
        )

        # Convert 'date' column to datetime
        news['date'] = pd.to_datetime(news['date'], errors='coerce')

        # Drop rows with invalid or missing dates
        news = news.dropna(subset=['date'])

        return news

    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error occurs
