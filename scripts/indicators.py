import pandas as pd
import talib as ta
import matplotlib.pyplot as plt

# =========================
# Indicator Calculation Functions
# =========================

def calculate_rsi(data, column='Close', period=14):
    """
    Calculate the Relative Strength Index (RSI) for the given stock data.

    Parameters:
        data (pd.DataFrame): The stock data.
        column (str): The column on which to calculate RSI (default is 'Close').
        period (int): The number of periods to use for the RSI calculation.

    Returns:
        pd.DataFrame: The stock data with a new 'RSI' column.
    """
    data['RSI'] = ta.RSI(data[column], timeperiod=period)
    return data

def calculate_macd(data, column='Close', fastperiod=12, slowperiod=26, signalperiod=9):
    """
    Calculate the MACD and signal line for the given stock data.

    Parameters:
        data (pd.DataFrame): The stock data.
        column (str): The column on which to calculate MACD (default is 'Close').
        fastperiod (int): The fast EMA period.
        slowperiod (int): The slow EMA period.
        signalperiod (int): The signal line EMA period.

    Returns:
        pd.DataFrame: The stock data with new 'MACD' and 'MACD_Signal' columns.
    """
    data['MACD'], data['MACD_Signal'], _ = ta.MACD(data[column],
                                                   fastperiod=fastperiod,
                                                   slowperiod=slowperiod,
                                                   signalperiod=signalperiod)
    return data

def calculate_bollinger_bands(data, column='Close', timeperiod=20, nbdevup=2, nbdevdn=2):
    """
    Calculate Bollinger Bands for the given stock data.

    Parameters:
        data (pd.DataFrame): The stock data.
        column (str): The column on which to calculate Bollinger Bands (default is 'Close').
        timeperiod (int): The number of periods for the moving average.
        nbdevup (int): The number of standard deviations for the upper band.
        nbdevdn (int): The number of standard deviations for the lower band.

    Returns:
        pd.DataFrame: The stock data with 'Upper_Band', 'Middle_Band', and 'Lower_Band' columns.
    """
    data['Upper_Band'], data['Middle_Band'], data['Lower_Band'] = ta.BBANDS(data[column],
                                                                            timeperiod=timeperiod,
                                                                            nbdevup=nbdevup,
                                                                            nbdevdn=nbdevdn)
    return data

def calculate_ema(data, column='Close', period=14):
    """
    Calculate the Exponential Moving Average (EMA) for the given stock data.

    Parameters:
        data (pd.DataFrame): The stock data.
        column (str): The column on which to calculate EMA (default is 'Close').
        period (int): The number of periods for the EMA.

    Returns:
        pd.DataFrame: The stock data with a new 'EMA' column.
    """
    data['EMA'] = ta.EMA(data[column], timeperiod=period)
    return data

def calculate_sma(data, column='Close', period=14):
    """
    Calculate the Simple Moving Average (SMA) for the given stock data.

    Parameters:
        data (pd.DataFrame): The stock data.
        column (str): The column on which to calculate SMA (default is 'Close').
        period (int): The number of periods for the SMA.

    Returns:
        pd.DataFrame: The stock data with a new 'SMA' column.
    """
    data['SMA'] = ta.SMA(data[column], timeperiod=period)
    return data

# =========================
# Visualization Functions
# =========================

def plot_stock_data(data, ticker):
    """
    Plot the closing price of the stock.

    Parameters:
        data (pd.DataFrame): The stock data.
        ticker (str): The stock ticker symbol.

    Displays:
        A line plot of the stock's closing price.
    """
    plt.figure(figsize=(10, 5))
    data['Close'].plot(title=f"{ticker} Stock Price (Close)", color='blue')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid()
    plt.show()

def plot_macd(data, ticker):
    """
    Plot the MACD and its signal line.

    Parameters:
        data (pd.DataFrame): The stock data with MACD values.
        ticker (str): The stock ticker symbol.

    Displays:
        A line plot showing MACD and signal line.
    """
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
    """
    Plot the RSI (Relative Strength Index) of the stock.

    Parameters:
        data (pd.DataFrame): The stock data with RSI values.
        ticker (str): The stock ticker symbol.

    Displays:
        A line plot of RSI with overbought and oversold lines.
    """
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
    """
    Plot Bollinger Bands with the stock's closing price.

    Parameters:
        data (pd.DataFrame): The stock data with Bollinger Band values.
        ticker (str): The stock ticker symbol.

    Displays:
        A line plot of the stock's closing price with upper, middle, and lower bands.
    """
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
    """
    Plot the Exponential Moving Average (EMA) with the stock's closing price.

    Parameters:
        data (pd.DataFrame): The stock data with EMA values.
        ticker (str): The stock ticker symbol.

    Displays:
        A line plot of the stock's closing price and EMA.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data['Close'], label='Close Price', color='blue')
    plt.plot(data.index, data['EMA'], label='EMA', color='orange')
    plt.title(f"{ticker} EMA")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()
