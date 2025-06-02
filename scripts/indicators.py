import pandas as pd
import talib as ta
import matplotlib.pyplot as plt

# Indicator Calculation Functions
def calculate_rsi(data, column='Close', period=14):
    data['RSI'] = ta.RSI(data[column], timeperiod=period)
    return data

def calculate_macd(data, column='Close', fastperiod=12, slowperiod=26, signalperiod=9):
    data['MACD'], data['MACD_Signal'], _ = ta.MACD(data[column], 
                                                   fastperiod=fastperiod, 
                                                   slowperiod=slowperiod, 
                                                   signalperiod=signalperiod)
    return data

def calculate_bollinger_bands(data, column='Close', timeperiod=20, nbdevup=2, nbdevdn=2):
    data['Upper_Band'], data['Middle_Band'], data['Lower_Band'] = ta.BBANDS(data[column], 
                                                                            timeperiod=timeperiod, 
                                                                            nbdevup=nbdevup, 
                                                                            nbdevdn=nbdevdn)
    return data

def calculate_ema(data, column='Close', period=14):
    data['EMA'] = ta.EMA(data[column], timeperiod=period)
    return data

def calculate_sma(data, column='Close', period=14):
    data['SMA'] = ta.SMA(data[column], timeperiod=period)
    return data

# Visualization Functions
def plot_stock_data(data, ticker):
    """Plot the closing price of the stock."""
    plt.figure(figsize=(10, 5))
    data['Close'].plot(title=f"{ticker} Stock Price (Close)", color='blue')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid()
    plt.show()

def plot_macd(data, ticker):
    """Plot the MACD and Signal line."""
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['MACD'], label='MACD', color='blue')
    plt.plot(data.index, data['MACD_Signal'], label='Signal Line', color='red')
    plt.title(f"{ticker} MACD")
    plt.xlabel('Date')
    plt.ylabel('MACD Value')
    plt.legend()
    plt.grid()
    plt.show()

def plot_rsi(data, ticker):
    """Plot the RSI."""
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['RSI'], label='RSI', color='purple')
    plt.axhline(70, color='red', linestyle='--', label='Overbought')
    plt.axhline(30, color='green', linestyle='--', label='Oversold')
    plt.title(f"{ticker} RSI")
    plt.xlabel('Date')
    plt.ylabel('RSI Value')
    plt.legend()
    plt.grid()
    plt.show()

def plot_bollinger_bands(data, ticker):
    """Plot Bollinger Bands."""
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['Upper_Band'], label='Upper Band', color='red')
    plt.plot(data.index, data['Middle_Band'], label='Middle Band', color='black')
    plt.plot(data.index, data['Lower_Band'], label='Lower Band', color='green')
    plt.title(f"{ticker} Bollinger Bands")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

def plot_ema(data, ticker):
    """Plot EMA."""
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['EMA'], label='EMA', color='orange')
    plt.title(f"{ticker} EMA")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()