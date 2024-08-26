import yfinance as yf
from niftyy import get_nifty_500
from datetime import datetime
import re
import utils
import pandas as pd


def generate_file(data):
    file = pd.DataFrame(data=data)
    file.to_csv("downloads/data.csv")


def check_moving_averages(stock, date=datetime.today().strftime("%Y-%m-%d")):
    """
    Check if the stock's opening price crossed the 13-day and 21-day moving averages on the given date.

    :param stock: The stock symbol
    :param date: The date to check (format: yyyy-mm-dd)
    """
    try:
        # Download daily stock data for the past 3 months
        yahoo_data = yf.download(tickers=stock, interval="1d", period="3mo")

        if yahoo_data.empty:
            print(f"No data found for {stock}.")
            return

        # Ensure date is in correct format and exists in the data
        if date not in yahoo_data.index:
            print(f"Date {date} not available in the data for {stock}.")
            return

        # Compute the 13-day and 21-day moving averages
        yahoo_data["SMA13"] = yahoo_data["Close"].rolling(window=13).mean()
        yahoo_data["SMA34"] = yahoo_data["Close"].rolling(window=34).mean()

        # Get today's data
        today_data = yahoo_data.loc[date]
        open_price = today_data["Open"]
        close_price = today_data["Close"]
        sma13_price = today_data["SMA13"]
        sma34_price = today_data["SMA34"]
        stock_data = {
            "Stock": stock,
            "Today Closed": close_price,
            "Today Open": open_price,
            "Crossed?": True
        }

        crossing_condition = sma13_price > sma34_price

        # crossed_sma21 = open_price > sma21_price

        if crossing_condition:
            print(f'{stock} has crossed 13 SMA')
        else:
            stock_data['Crossed'] = False
        return stock_data

    except Exception as e:
        print(f"An error occurred for {stock}: {e}")


def main():
    try:
        all_crossed = []
        stocks = get_nifty_500()
        date = utils.get_today_date()
        print(f"Checking stocks for today’s date: {date}")

        for stock in stocks:
            all_crossed.append(check_moving_averages(f"{stock}.BO", date))
        generate_file(all_crossed)
    except Exception as e:
        print(f"An error occurred: {e}")
        # Prompt user for a specific date if desired
        user_input = input("Wanna check for a specific date? (y/n): ").strip().lower()
        if user_input == "y":
            specific_date = input("Enter date (yyyy-mm-dd): ").strip()
            date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")

            if date_pattern.match(specific_date):
                for stock in stocks:
                    all_crossed.append(
                        check_moving_averages(f"{stock}.BO", specific_date)
                    )
                generate_file(all_crossed)
            else:
                print(
                    "Invalid date format. Please enter the date in yyyy-mm-dd format."
                )
        else:
            print("Exiting without checking a specific date.")


if __name__ == "__main__":
    main()
