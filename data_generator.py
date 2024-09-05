import datetime

import numpy as np

import yfinance as yf

FAST_MA = 13
SLOW_MA = 34
STARTING_BALANCE = 1000000
NUM_TOP_STOCKS = 10
START = datetime.datetime(2020, 7, 7)
END = datetime.datetime.now()
YEARS = (END - START).days / 365.25
import pandas as pd


def get_nifty_500_list():
    # Read the 'Symbol' column from the CSV file and append '.BO' to each entry
    nifty500_with_suffix = (
        pd.read_csv("ind_nifty500list.csv")["Symbol"].astype(str) + ".BO"
    )

    return nifty500_with_suffix.tolist()


all_stocks = pd.read_csv("ind_nifty500list.csv")


def generate_data(done=[], split=None):
    """
    Returns a list of stocks from the DataFrame, excluding those in the 'done' list and optionally applying a filter.

    Parameters:
    done (list): List of stock symbols to exclude.
    split (function): Optional function to apply as a filter to the DataFrame.

    Returns:
    list: List of stock symbols after filtering.
    """
    list_of_symbols = get_nifty_500_list()
    for symbol in list_of_symbols:
        try:
            # Attempt to download the data
            price = yf.download(symbol, start=START, end=END)
            print(symbol)

            # Check if the DataFrame is empty
            if price.empty:
                print(f"No data found for {symbol}. Skipping...")
                continue

            # Perform data processing
            price = price.drop(
                ["High", "Low", "Adj Close"], axis=1
            )  # Keep Volume for the new condition
            price["Return"] = price.Close / price.Close.shift(1)
            price["Bench_Bal"] = STARTING_BALANCE * price.Return.cumprod()
            price["Bench_Peak"] = price.Bench_Bal.cummax()
            price["Bench_DD"] = price.Bench_Bal - price.Bench_Peak

            # Calculate moving averages
            price["Fast_MA"] = price.Close.rolling(window=FAST_MA).mean()
            price["Slow_MA"] = price.Close.rolling(window=SLOW_MA).mean()

            # Calculate the average volume of the past 10 days
            price["Avg_Volume_10D"] = price.Volume.rolling(window=10).mean()

            # Define the trading signal (Long) based on moving average crossover and volume condition
            price["Long"] = (price.Fast_MA > price.Slow_MA) & (
                price.Volume > price["Avg_Volume_10D"]
            )

            price["Sys_Ret"] = np.where(
                price.Long == False,
                1,
                np.where(price.Long.shift(1) == True, price.Return, 1),
            )
            price["Sys_Bal"] = STARTING_BALANCE * price.Sys_Ret.cumprod()
            price["Sys_Peak"] = price.Sys_Bal.cummax()
            price["Sys_DD"] = price.Sys_Bal - price.Sys_Peak
            price["Symbol"] = symbol
            price.to_csv(f"downloads/{symbol}.csv")
            # Ensure the DataFrame has enough rows for calculations
            if len(price) < max(
                FAST_MA, SLOW_MA, 10
            ):  # At least enough days for calculations
                print(f"Not enough data for {symbol}. Skipping...")
        except Exception as e:
            print(f"Exception occured : {e}")


def fetch_stock_data(symbol: str) -> pd.DataFrame:
    """
    Fetch stock data for a given symbol.

    Parameters:
    symbol (str): The stock symbol.

    Returns:
    pd.DataFrame: The stock data for the symbol.
    """
    price = yf.download(symbol, start=START, end=START + datetime.timedelta(days=1))
    return price

if __name__ == '__main__':
    generate_data()