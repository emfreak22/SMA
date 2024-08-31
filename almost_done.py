import os

import pandas as pd

# Constants
START_BALANCE = 1000000
CSV_FOLDER_PATH = "downloads/"  # Path where your CSV files are stored
N = 50  # Maximum number of stocks in the portfolio
n = 10  # Number of stocks to pick if 'long' condition is satisfied


def load_and_merge_stock_data(csv_folder_path):
    """
    Load and merge all CSV files into a single DataFrame.
    """
    csv_files = [
        os.path.join(csv_folder_path, f)
        for f in os.listdir(csv_folder_path)
        if f.endswith(".csv")
    ]
    df_list = [pd.read_csv(file) for file in csv_files]

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_df["Date"] = pd.to_datetime(combined_df["Date"])
    combined_df.set_index(["Date", "Symbol"], inplace=True)

    return combined_df


def get_top_stocks_by_volume(combined_df, date, top_n=1):
    """
    Get the top N stocks by volume for a given day from the combined DataFrame.
    """
    try:
        # today_data = combined_df.loc[symbol]
        top_stocks = (
            combined_df.groupby("Symbol")["Volume"].sum().nlargest(top_n).index.tolist()
        )
        return top_stocks
    except Exception:
        print("No data today")
        return []


def check_long_condition(stock_data):
    """
    Check if the stock satisfies the long condition (Slow_MA > Fast_MA).
    """
    return stock_data["Fast_MA"] > stock_data["Slow_MA"]


def check_long_close_condition(stock_data):
    """
    Check if the stock satisfies the long close condition (Fast_MA > Slow_MA).
    """
    return stock_data["Fast_MA"] < stock_data["Slow_MA"]


def refresh_final_portfolio(portfolio, symbol, close_price):
    portfolio[symbol]["current_value"] = close_price * portfolio[symbol]["quantity"]
    portfolio[symbol]["last_day_closing_value"] = close_price


def process_trades(combined_df, start_balance, max_stocks=N, pick_n=n):
    """
    Process trades based on stock conditions and balance.
    """
    balance = start_balance
    portfolio = {}

    all_dates = combined_df.index.get_level_values("Date").unique()

    for date in all_dates:
        today_data = combined_df.loc[date]

        # 1. Create Long Positions
        if len(portfolio) < n:
            potential_stocks = today_data[
                today_data.apply(check_long_condition, axis=1)
            ]
            if potential_stocks.empty:
                print("No long for the day, sadly...")
                continue
            top_stocks = get_top_stocks_by_volume(potential_stocks, date, top_n=pick_n)

            for symbol in top_stocks:
                print(portfolio)
                try:
                    if symbol not in portfolio:
                        stock_data = potential_stocks.loc[symbol]
                        buy_price = stock_data["Close"]
                        quantity = balance / n // buy_price
                        portfolio[symbol] = {
                            "quantity": quantity,
                            "buy_price": buy_price,
                        }
                        balance -= quantity * buy_price
                        print(
                            f"Bought {quantity} of {symbol} at {buy_price}. Remaining balance: {balance}"
                        )
                except Exception as e:
                    print("Pata ni kya hua bc")

        # 2. Check for Long Close and Manage Portfolio
        portfolio_to_remove = []
        for symbol in list(portfolio.keys()):

            try:
                try:
                    close_price = today_data.loc[symbol]["Close"]
                    refresh_final_portfolio(portfolio, symbol, close_price)
                    stock_data = today_data.loc[symbol]
                except Exception:
                    print(f" No data for {date} for {symbol}")
                    raise Exception
                if check_long_close_condition(stock_data):

                    sell_price = stock_data["Close"]
                    quantity = portfolio[symbol]["quantity"]
                    balance += quantity * sell_price
                    print(
                        f"Sold {quantity} of {symbol} at {sell_price}. Remaining balance: {balance}."
                    )
                    portfolio_to_remove.append(symbol)

                    # Attempt to fill the slot with a new stock
                    if len(portfolio) < n:
                        potential_stocks = today_data[
                            today_data.apply(check_long_condition, axis=1)
                        ]
                        new_symbols = get_top_stocks_by_volume(
                            potential_stocks, date, top_n=1
                        )
                        if new_symbols:
                            new_symbol = new_symbols[0]

                            if new_symbol != symbol and new_symbol not in portfolio:
                                next_stock_data = potential_stocks.loc[new_symbol]
                                buy_price_next = next_stock_data["Close"]
                                quantity_next = balance // buy_price_next
                                portfolio[new_symbol] = {
                                    "quantity": quantity_next,
                                    "buy_price": buy_price_next,
                                }
                                balance -= quantity_next * buy_price_next
                                print(
                                    f"Bought {quantity_next} of {new_symbol} at {buy_price_next}. Remaining balance: {balance}"
                                )
            except Exception as e:
                print("Pata ni kya hua bc")

        # Remove sold stocks from the portfolio
        for symbol in portfolio_to_remove:
            del portfolio[symbol]

    return balance, portfolio


def main():
    combined_df = load_and_merge_stock_data(CSV_FOLDER_PATH)
    final_balance, final_portfolio = process_trades(
        combined_df, START_BALANCE, max_stocks=N, pick_n=n
    )

    print(f"Starting balance : {START_BALANCE}")
    print(f"Final balance: {final_balance}")
    print(f"Final portfolio: {final_portfolio}")
    remaining_portfolio_value = 0
    for remaining_stocks in final_portfolio:
        current_value = final_portfolio[remaining_stocks]["current_value"].astype(int)
        remaining_portfolio_value += current_value
    print(final_balance + remaining_portfolio_value)


if __name__ == "__main__":
    main()
