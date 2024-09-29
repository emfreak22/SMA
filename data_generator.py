import datetime
import os

import numpy as np
import pandas as pd
from tqdm import tqdm

import yfinance as yf
from config.configs import FAST_MA, SLOW_MA, START_BALANCE
START = datetime.datetime(1988, 8, 1)
END = datetime.datetime.now()
INCLUSION ='Inclusion into Index'
EXCLUSION = 'Exclusion from Index'
def get_nifty_500_list():
    nifty500_with_suffix = (
        pd.read_csv("ind_nifty500list.csv")["Symbol"].astype(str) + ".BO"
    )
    return nifty500_with_suffix.tolist()

def get_list_data(date='01-08-1998', symbol_data=[]):
    data = pd.read_excel('files/all_sheets_with_symbols.xlsx', sheet_name='Nifty 500')
    working_data = data[data['Event Date'] == date]
    for row, data in working_data.iterrows():
        if data['Description'] == INCLUSION:
            symbol_data.append(data['Symbol'])
    # print(symbol_data)
    return list(set(symbol_data))


def generate_data():
    wrong_symbols = []
    list_of_symbols = get_list_data()
    list_of_symbols = [i+".NS" for i in list_of_symbols]
    print(list_of_symbols)
    for symbol in tqdm(list_of_symbols, desc="Processing Stocks"):
        try:
            price = yf.download(symbol, start=START, end=END)

            if price.empty:
                wrong_symbols.append(symbol)
                print(f"No data found for {symbol}. Skipping...")
                continue

            price = price.drop(["High", "Low", "Adj Close"], axis=1)
            price["Return"] = price.Close / price.Close.shift(1)
            price["Bench_Bal"] = START_BALANCE * price.Return.cumprod()
            price["Bench_Peak"] = price.Bench_Bal.cummax()
            price["Bench_DD"] = price.Bench_Bal - price.Bench_Peak

            price["Fast_MA"] = price.Close.rolling(window=FAST_MA).mean()
            price["Slow_MA"] = price.Close.rolling(window=SLOW_MA).mean()

            price["Avg_Volume_10D"] = price.Volume.rolling(window=10).mean()

            price["Long"] = (price.Fast_MA > price.Slow_MA) & (
                price.Volume > price["Avg_Volume_10D"]
            )

            price["Sys_Ret"] = np.where(
                price.Long == False,
                1,
                np.where(price.Long.shift(1) == True, price.Return, 1),
            )
            price["Sys_Bal"] = START_BALANCE * price.Sys_Ret.cumprod()
            price["Sys_Peak"] = price.Sys_Bal.cummax()
            price["Sys_DD"] = price.Sys_Bal - price.Sys_Peak
            price["Symbol"] = symbol
            price["Long_Condition"] = price.Fast_MA > price.Slow_MA
            price["Sell_Condition"] = price.Fast_MA < price.Slow_MA
            price["New_Sell_Condition"] = (price.Fast_MA < price.Slow_MA) & (
                price.Return < 0.90
            )
            price.to_csv(f"downloads/{symbol}.csv")

            if len(price) < max(FAST_MA, SLOW_MA, 10):
                print(f"Not enough data for {symbol}. Skipping...")

        except Exception as e:
            print(f"Exception occurred for {symbol}: {e}")


def adjust_moving_averages(slow_ma, fast_ma):
    list_of_symbols = get_nifty_500_list()
    FAST_MA = int(fast_ma)
    SLOW_MA = int(slow_ma)
    for symbol in tqdm(list_of_symbols, desc="Adjusting Moving Averages"):
        file_path = f"downloads/{symbol}.csv"
        if not os.path.exists(file_path):
            print(f"No existing data for {symbol}. Skipping...")
            continue

        try:
            price = pd.read_csv(file_path, index_col=0)

            # Recalculate Moving Averages
            price["Fast_MA"] = price.Close.rolling(window=FAST_MA).mean()
            price["Slow_MA"] = price.Close.rolling(window=SLOW_MA).mean()

            price["Long"] = (price.Fast_MA > price.Slow_MA) & (
                price.Volume > price["Avg_Volume_10D"]
            )

            price["Sys_Ret"] = np.where(
                price.Long == False,
                1,
                np.where(price.Long.shift(1) == True, price.Return, 1),
            )
            price["Sys_Bal"] = START_BALANCE * price.Sys_Ret.cumprod()
            price["Sys_Peak"] = price.Sys_Bal.cummax()
            price["Sys_DD"] = price.Sys_Bal - price.Sys_Peak
            price["Long_Condition"] = price.Fast_MA > price.Slow_MA
            price["Sell_Condition"] = price.Fast_MA < price.Slow_MA
            price['Symbol'] = symbol
            price["New_Sell_Condition"] = (price.Fast_MA < price.Slow_MA) & (
                price.Return < 0.90
            )

            # Save the updated data
            price.to_csv(file_path)
        except Exception as e:
            print(f"Exception occurred for {symbol}: {e}")


if __name__ == "__main__":
    get_list_data()
    choice = input(
        "Do you want to generate new data (1) or adjust moving averages (2)? Enter 1 or 2: "
    )
    if choice == "1":
        generate_data()
    elif choice == "2":
        slow_ma = input("New Slow MA: ")
        fast_ma = input("New Fast MA")
        adjust_moving_averages(slow_ma, fast_ma)
    else:
        print("Invalid choice. Exiting.")
