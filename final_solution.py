import os

from config.configs import END, START, START_BALANCE, N, n
from data_generator import generate_data
from metric_calculation import calculate
from nifty_data import plot_nifty500_investment

CSV_FOLDER_PATH = "downloads/"
from excel_creation import make_a_beautiful_excel

per_stock_allocation = START_BALANCE / N
import pandas as pd

from graph_creation import create_curve2


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


def refresh_final_portfolio(portfolio, date, combined_data):
    # close_price = today_data.loc[symbol]["Close"]
    worth = 0
    for symbol in portfolio:
        try:
            close_price = combined_data.loc[date].loc[symbol]["Close"]
        except Exception:
            print("No data for today, not setting it to any value then")
            close_price = portfolio[symbol]["last_day_closing_value"]
        amount = close_price * portfolio[symbol]["quantity"]
        portfolio[symbol]["current_value"] = amount
        portfolio[symbol]["last_day_closing_value"] = close_price
        worth += amount

    return worth, portfolio


def process_trades(combined_df, start_balance, max_stocks=N, pick_n=n):
    """
    Process trades based on stock conditions and balance.
    """
    balance = start_balance
    portfolio = {}
    transaction_history = []
    all_dates = combined_df.index.get_level_values("Date").unique()
    # Sort the dates
    all_dates = all_dates.sort_values()
    balance_sheet = {}
    wallet_balance = START_BALANCE
    for date in all_dates:
        today_data = combined_df.loc[date]
        print(f"Date {date} , Portfolio {len(portfolio)}")
        if len(portfolio) < N:
            potential_stocks = today_data[
                today_data.apply(check_long_condition, axis=1)
            ]
            if potential_stocks.empty:
                # print("No long for the day, sadly...")
                continue
            top_stocks = get_top_stocks_by_volume(potential_stocks, date, top_n=pick_n)

            for symbol in top_stocks:
                try:
                    if symbol not in portfolio and len(portfolio) < N:
                        stock_data = potential_stocks.loc[symbol]
                        buy_price = stock_data["Close"]
                        buying_capacity = (
                            per_stock_allocation
                            if wallet_balance > per_stock_allocation
                            else wallet_balance
                        )
                        quantity = buying_capacity // buy_price
                        print(
                            f" {wallet_balance} / {N-len(portfolio)} // {buy_price}: {quantity*buy_price} "
                        )

                        wallet_balance = wallet_balance - quantity * buy_price
                        portfolio[symbol] = {
                            "quantity": quantity,
                            "buy_price": buy_price,
                        }

                        money_spent = quantity * buy_price
                        print(
                            f"Bought {quantity} of {symbol} at {buy_price}. Remaining balance: {balance} on date {date}"
                        )
                        buy_history = {
                            "Stock": symbol,
                            "Date of buying": date,
                            "Buy Price": buy_price,
                            "Quantity": quantity,
                        }
                        transaction_history.append(buy_history)
                except Exception as e:
                    pass
                    # print(f"No data for {date}, {symbol}: {e}")

        # 2. Check for Long Close and Manage Portfolio
        portfolio_to_remove = []
        for symbol in list(portfolio.keys()):
            try:
                try:
                    stock_data = today_data.loc[symbol]
                except Exception:
                    pass
                    # print(f" No data for {date} for {symbol}")
                    raise Exception
                if check_long_close_condition(stock_data):

                    sell_price = stock_data["Close"]
                    quantity = portfolio[symbol]["quantity"]
                    money_gained = quantity * sell_price
                    wallet_balance = wallet_balance + money_gained
                    sell_history = {
                        "Stock": symbol,
                        "Sell Price": sell_price,
                        "Date of selling": date,
                    }
                    for i in transaction_history:
                        if i["Stock"] == symbol and "Sell Price" not in i:
                            i.update(sell_history)
                    print(
                        f"Sold {quantity} of {symbol} at {sell_price} of price {quantity*sell_price} on date {date} total portfolio value : {wallet_balance}."
                    )
                    portfolio_to_remove.append(symbol)
                    del portfolio[symbol]

                    # Attempt to fill the slot with a new stock
                    if len(portfolio) < N:
                        potential_stocks = today_data[
                            today_data.apply(check_long_condition, axis=1)
                        ]
                        new_symbols = get_top_stocks_by_volume(
                            potential_stocks, date, top_n=500
                        )
                        if new_symbols:
                            for new_symbol in new_symbols:
                                if len(portfolio) >= N:
                                    break
                                if new_symbol != symbol and new_symbol not in portfolio:
                                    next_stock_data = potential_stocks.loc[new_symbol]
                                    buy_price_next = next_stock_data["Close"]

                                    buying_capacity = (
                                        per_stock_allocation
                                        if wallet_balance > per_stock_allocation
                                        else wallet_balance
                                    )
                                    quantity_next = buying_capacity // buy_price_next
                                    portfolio[new_symbol] = {
                                        "quantity": quantity_next,
                                        "buy_price": buy_price_next,
                                    }
                                    balance -= quantity_next * buy_price_next
                                    buy_history = {
                                        "Stock": new_symbol,
                                        "Date of buying": date,
                                        "Buy Price": buy_price_next,
                                        "Quantity": quantity_next,
                                    }
                                    transaction_history.append(buy_history)
                                    wallet_balance = (
                                        wallet_balance - quantity_next * buy_price_next
                                    )
                                    print(
                                        f"Bought {quantity_next} of {new_symbol} at {buy_price_next} for rs: {quantity_next*buy_price_next} Remaining balance: {wallet_balance}"
                                    )

            except Exception as e:
                print(f"No data for {date}, {symbol}: {e}")

        worth, daily_change = refresh_final_portfolio(portfolio, date, combined_df)
        portfolio = daily_change
        balance_sheet[str(date)] = worth + wallet_balance
    return portfolio, transaction_history, wallet_balance, balance_sheet


def main():
    try:
        combined_df = load_and_merge_stock_data(CSV_FOLDER_PATH)
    except ValueError:
        print("Seems like downloads folder is not populated... \n populating now...")
        generate_data()
        combined_df = load_and_merge_stock_data(CSV_FOLDER_PATH)

    (
        final_portfolio,
        transaction_history,
        wallet_balance,
        balance_sheet,
    ) = process_trades(combined_df, START_BALANCE, max_stocks=N, pick_n=n)

    print(f"Starting balance : {START_BALANCE}")
    print(f"Final portfolio: {final_portfolio}")
    print(
        "Converting final portfolio stock quantities into rupees and calculating final amount..."
    )
    remaining_portfolio_value = 0
    for remaining_stocks in final_portfolio:
        for entry in transaction_history:
            if entry["Stock"] == remaining_stocks and not entry.get("Sell Price"):
                entry["Sell Price"] = final_portfolio[remaining_stocks][
                    "last_day_closing_value"
                ]
                entry["Percentage Change"] = (
                    (entry["Sell Price"] - entry["Buy Price"]) / entry["Buy Price"]
                ) * 100

        current_value = final_portfolio[remaining_stocks]["current_value"].astype(int)
        remaining_portfolio_value += current_value
    print(wallet_balance + remaining_portfolio_value)
    make_a_beautiful_excel(transaction_history)
    calculate()
    x = input("Do you want an equity curve? Y/Yes or N/No: ")

    if x.lower() in ["y", "yes"]:
        # Fetch historical data for Nifty 500
        nifty_data = plot_nifty500_investment(START, END, START_BALANCE)
        create_curve2(balance_sheet, nifty_data)
    else:
        print("Exiting")
        exit()


if __name__ == "__main__":
    main()
