import os
from preprocess import load_data
from sentiment_analysis import sentiment_analysis
from topic_modeling import topic_modeling
from trend_analysis import sentiment_trends, topic_trends

def main(file_path):
    # Load data
    news = load_data(file_path)
    
    # Perform sentiment analysis
    news = sentiment_analysis(news)
    
    # Perform topic modeling
    topics, lda, X = topic_modeling(news)
    
    # Print discovered topics
    print("Topics discovered by LDA:")
    for topic in topics:
        print(topic)
    
    # Plot sentiment and topic trends
    sentiment_trends(news)
    topic_trends(news, lda, X)

if __name__ == '__main__':
    file_path = os.path.join('..', 'raw_analyst_ratings.csv')
    main(file_path)