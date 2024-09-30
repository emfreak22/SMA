import os

from config.configs import END, START
from config.configs import Compounding_n as N
from data_generator import generate_data
from nifty_data import plot_nifty500_investment
from pretty_printing import print_blue, print_golden, print_green, print_red
from excel_creation import make_a_beautiful_excel
from graph_creation import create_curve2
from metric_calculation import calculate

DELISTED = []
START_BALANCE = 1000000
CSV_FOLDER_PATH = "downloads/"
per_stock_allocation = START_BALANCE / N
from datetime import datetime

import pandas as pd

START_DATE = datetime(1998, 8, 1)
END_DATE = datetime.now()
n = 10


INCLUSION = "Inclusion into Index"
EXCLUSION = "Exclusion from Index"


def get_list_data_v2(date="01-08-1998", symbol_data=None):
    if symbol_data is None:
        symbol_data = []

    # Load Excel data only once
    data = pd.read_excel("files/all_sheets_with_symbols.xlsx", sheet_name="Nifty 500")

    # Filter rows by event date
    working_data = data[data["Event Date"] == date]
    if working_data.empty:
        return symbol_data

    # Use a set for faster membership checks
    existing_symbols = {entry["Symbol"] for entry in symbol_data}

    # Process each row in the filtered data
    for _, row_data in working_data.iterrows():
        if row_data["Description"] == INCLUSION:
            if row_data["Symbol"] not in existing_symbols:
                print(f"📈 Inclusion of {row_data['Symbol']}")
                symbol_data.append(
                    {
                        "Symbol": row_data["Symbol"],
                        "Name": row_data["Scrip Name"],
                        "Description": INCLUSION,
                    }
                )
        else:
            # Only remove if it exists in symbol_data
            symbol_data = [
                entry for entry in symbol_data if entry["Symbol"] != row_data["Symbol"]
            ]
            print(f"📉 Exclusion of {row_data['Symbol']}")

    return symbol_data


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
    combined_df.set_index(["Date", "Symbol"], inplace=True, drop=False)

    return combined_df


def get_top_stocks_by_volume(combined_df, date, top_n=100):
    """
    Get the top N stocks by volume for a given day from the combined DataFrame.
    """
    try:
        # today_data = combined_df.loc[symbol]
        top_stocks = (
            combined_df.groupby(level="Symbol")["Volume"]
            .sum()
            .nlargest(top_n)
            .index.tolist()
        )
        return top_stocks
    except Exception:
        # print("No data today")
        return []


def check_long_condition(stock_data):
    """
    Check if the stock satisfies the long condition (Slow_MA > Fast_MA).
    """
    return stock_data["Fast_MA"] > stock_data["Slow_MA"]


def check_long_close_condition(stock_data, updated_stock_symbol):
    """
    Check if the stock satisfies the long close condition (Fast_MA > Slow_MA).
    """
    # Return True if stock is not in the updated stock list or if Fast_MA < Slow_MA
    condition1 = stock_data["Symbol"] not in updated_stock_symbol
    condition2 = stock_data["Fast_MA"] < stock_data["Slow_MA"]
    if condition1:
        print_red(
            f" 💀 💀 💀 💀 💀 💀💀 💀Condition 1 met: {stock_data['Symbol']} is delisted, hence selling. 💀 💀 💀 💀 💀 💀 💀 💀 💀 💀 💀 💀"
        )
        DELISTED.append(stock_data)
        return True
    elif condition2:
        print(
            f"Condition 2 met: Fast_MA ({stock_data['Fast_MA']}) is less than Slow_MA ({stock_data['Slow_MA']})."
        )
        return True
    else:
        return False


def refresh_final_portfolio(portfolio, date, combined_data):
    worth = 0
    for symbol in portfolio:
        try:
            close_price = combined_data.loc[date].loc[symbol]["Close"]
        except Exception:
            # print("No data for today, not setting it to any value then")
            try:
                close_price = portfolio[symbol]["last_day_closing_value"]
            except Exception:
                print(
                    f"The data for symbol {symbol} is not available, so setting close price as buy_price as of now"
                )
                close_price = portfolio[symbol]["buy_price"]

        amount = close_price * portfolio[symbol]["quantity"]
        portfolio[symbol]["current_value"] = amount
        portfolio[symbol]["last_day_closing_value"] = close_price
        worth += amount

    return worth, portfolio


def refresh_final_portfolio_v2(portfolio, date, combined_data):
    worth = 0
    for symbol in portfolio:
        try:
            close_price = combined_data.loc[date].loc[symbol]["Close"]
        except Exception:
            # print("No data for today, not setting it to any value then")
            try:
                close_price = portfolio[symbol]["last_day_closing_value"]
            except Exception:
                print(
                    f"The data for symbol {symbol} is not available, so setting close price as buy_price as of now"
                )
                close_price = portfolio[symbol]["buy_price"]

        amount = close_price * portfolio[symbol]["quantity"]
        portfolio[symbol]["current_value"] = amount
        portfolio[symbol]["last_day_closing_value"] = close_price
        worth += amount

    return worth, portfolio


class Trader:
    def __init__(self):
        self.list_data = []

    def get_list_data_updated(
        self, date="01-08-1998 00:00:00", symbol_data=[], symbols=[]
    ):
        data = self.list_data
        working_data = data[data["Event Date"] == date]

        # TODO
        # data_to_include = working_data[working_data['Description']== INCLUSION]
        # data_to_exclude = working_data[working_data['Description'] == EXCLUSION]
        # list_to_include = [{'Symbol': row['Symbol'], 'Name': row['Scrip Name'], 'Date': row['Event Date']}
        #           for _, row in data_to_include.iterrows()]
        # list_to_exclude = [{'Symbol': row['Symbol'], 'Name': row['Scrip Name'], 'Date': row['Event Date']}
        #           for _, row in data_to_exclude.iterrows()]
        # output = data_to_include[['Symbol', 'Scrip Name', 'Event Date','Description']].rename(columns={'Scrip Name': 'Name', 'Event Date' :'Date'}).to_dict('records')
        # output_2 = data_to_exclude[['Symbol', 'Scrip Name', 'Event Date','Description']].rename(columns={'Scrip Name': 'Name', 'Event Date' :'Date'}).to_dict(
        #     'records')

        for row, data in working_data.iterrows():
            entry = {}
            entry["Symbol"] = data["Symbol"] + ".NS"
            entry["Name"] = data["Scrip Name"]
            entry["Desciption"] = INCLUSION
            if data["Description"] == INCLUSION and entry not in symbol_data:
                print(
                    f"📈📈📈📈📈📈📈📈📈📈Inclusion of {data['Symbol']} :📈📈📈📈📈📈📈📈📈📈📈📈📈"
                )
                symbol_data.append(entry)
                symbols.append(entry["Symbol"])
            if data["Description"] == EXCLUSION and entry in symbol_data:
                print(
                    f"📉📉📉📉📉📉📉📉📉📉📉Exclusion of {entry['Symbol']} is done 📉📉📉📉📉📉📉📉📉"
                )
                symbol_data.remove(entry)
                symbols.remove(entry["Symbol"])
        return symbol_data, symbols

    #TODO
    def get_list_data_updated_v2(
        self, date="01-08-1998 00:00:00", symbol_data=[], symbols=[]
    ):
        data = self.list_data
        working_data = data[data["Event Date"] == date]

        # TODO
        data_to_include = working_data[working_data['Description']== INCLUSION]
        data_to_exclude = working_data[working_data['Description'] == EXCLUSION]
        list_to_include = [{'Symbol': row['Symbol'], 'Name': row['Scrip Name'], 'Date': row['Event Date']}
                  for _, row in data_to_include.iterrows()]
        list_to_exclude = [{'Symbol': row['Symbol'], 'Name': row['Scrip Name'], 'Date': row['Event Date']}
                  for _, row in data_to_exclude.iterrows()]
        output = data_to_include[['Symbol', 'Scrip Name', 'Event Date','Description']].rename(columns={'Scrip Name': 'Name', 'Event Date' :'Date'}).to_dict('records')
        output_2 = data_to_exclude[['Symbol', 'Scrip Name', 'Event Date','Description']].rename(columns={'Scrip Name': 'Name', 'Event Date' :'Date'}).to_dict(
            'records')
        print(f"Included {output}")
        print(f"Excluded {output_2}")
        symbol_data.extend(output)
        from collections import OrderedDict
        result = list(OrderedDict.fromkeys(symbol_data).keys() - set(output_2))
        return symbol_data, symbols

    def fix_dates(self, data):
        # Convert the column to datetime format, specifying dayfirst=True
        data["Event Date"] = pd.to_datetime(
            data["Event Date"], errors="coerce", dayfirst=True
        )

        # Format the dates to 'dd-mm-yyyy'
        data["Event Date"] = data["Event Date"].dt.strftime("%m-%d-%Y 00:00:00")

        return data

    def process_trades(self, combined_df, start_balance, N=N):
        """
        Process trades based on stock conditions and balance.
        """
        balance = start_balance

        portfolio = {}
        transaction_history = []
        symbol_data = []
        list_data = pd.read_excel(
            "files/all_sheets_with_symbols.xlsx", sheet_name="Nifty 500"
        )
        list_data["Event Date"] = pd.to_datetime(
            list_data["Event Date"], format="%d-%m-%Y %H:%M:%S"
        )
        list_data["Event Date"] = list_data["Event Date"].dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.list_data = list_data
        inclusion_dates = list(list_data["Event Date"].unique())
        balance_sheet = {}
        wallet_balance = START_BALANCE
        updated_stocks_symbols = []
        dates = pd.date_range(
            start=START_DATE, end=END_DATE
        )  # Replace this with your actual DatetimeIndex
        for date in dates:
            print(date)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            if date in inclusion_dates:
                symbol_data, updated_stocks_symbols = self.get_list_data_updated(
                    date=date, symbol_data=symbol_data, symbols=updated_stocks_symbols
                )
            try:
                today_data = combined_df.loc[date]
                print("Data found")
            except Exception:
                print(f"{date} is a weekend or there is no data..")
                continue
            filtered_data = today_data[
                today_data.index.get_level_values("Symbol").isin(updated_stocks_symbols)
            ]
            if len(portfolio) < N:

                potential_stocks = filtered_data[
                    filtered_data.apply(check_long_condition, axis=1)
                ]
                if potential_stocks.empty:
                    continue
                top_stocks = get_top_stocks_by_volume(potential_stocks, date, top_n=N)

                for symbol in top_stocks:
                    try:
                        if symbol not in portfolio and len(portfolio) < N:
                            stock_data = potential_stocks.loc[symbol]
                            buy_price = stock_data["Close"]
                            print(f"{symbol}: BP {buy_price} , WB: {wallet_balance}")
                            if buy_price > wallet_balance:
                                print(
                                    f"💸 We are fucked, no money for {symbol}💸💸💸💸💸💸💸💸💸💸💸💸💸💸💸💸💸"
                                )
                                continue
                            if symbol == "CESC":
                                print("Stop right here")

                            buying_capacity = (
                                per_stock_allocation
                                if wallet_balance > per_stock_allocation
                                else wallet_balance
                            )
                            quantity = buying_capacity // buy_price
                            if symbol == "CESC.NS":
                                print("Right here")
                            wallet_balance = wallet_balance - quantity * buy_price
                            portfolio[symbol] = {
                                "quantity": quantity,
                                "buy_price": buy_price,
                                "Symbol": symbol,
                            }

                            print_green(
                                f"1DATE : {date}  |  Bought {quantity} of {symbol} at {buy_price} for rs: {quantity * buy_price} Remaining balance: {wallet_balance}"
                            )
                            buy_history = {
                                "Stock": symbol,
                                "Date of buying": date,
                                "Buy Price": buy_price,
                                "Quantity": quantity,
                            }
                            transaction_history.append(buy_history)
                    except Exception:
                        pass

            # 2. Check for Long Close and Manage Portfolio
            portfolio_to_remove = []
            for portfolio_symbol in list(portfolio.keys()):
                try:
                    try:
                        stock_data = today_data.loc[portfolio_symbol]
                    except Exception:
                        print_red(
                            f"The data of stock {portfolio_symbol} is not available for the day {date}, this could cause issues."
                        )
                        pass
                    if check_long_close_condition(stock_data, updated_stocks_symbols):
                        sell_price = stock_data["Close"]
                        quantity = portfolio[portfolio_symbol]["quantity"]
                        money_gained = quantity * sell_price
                        wallet_balance = wallet_balance + money_gained
                        sell_history = {
                            "Stock": portfolio_symbol,
                            "Sell Price": sell_price,
                            "Date of selling": date,
                        }
                        for i in transaction_history:
                            if i["Stock"] == portfolio_symbol and "Sell Price" not in i:
                                i.update(sell_history)
                        print_red(
                            f"DATE : {date}  |  Sold {quantity} of {portfolio_symbol} at {sell_price} for rs: {quantity * sell_price} Remaining balance: {wallet_balance}"
                        )
                        accumulated_profit = (
                            quantity * sell_price
                            - portfolio[portfolio_symbol]["buy_price"] * quantity
                        )
                        print_golden(
                            f"DATE : {date}  | Accumulated profit: {accumulated_profit} 🪙🪙🪙🪙"
                        )
                        portfolio_to_remove.append(portfolio_symbol)
                        del portfolio[portfolio_symbol]

                        # Attempt to fill the slot with a new stock
                        if len(portfolio) < N:
                            potential_stocks = filtered_data[
                                filtered_data.apply(check_long_condition, axis=1)
                            ]
                            new_symbols = get_top_stocks_by_volume(
                                potential_stocks, date, top_n=500
                            )
                            if new_symbols:
                                for new_symbol in new_symbols:
                                    if len(portfolio) >= N:
                                        break
                                    if (
                                        new_symbol != portfolio_symbol
                                        and new_symbol not in portfolio
                                    ):
                                        next_stock_data = potential_stocks.loc[
                                            new_symbol
                                        ]
                                        buy_price_next = next_stock_data["Close"]
                                        if buy_price_next > wallet_balance:
                                            continue

                                        buying_capacity = (
                                            per_stock_allocation
                                            if wallet_balance > per_stock_allocation
                                            else wallet_balance
                                        )
                                        quantity_next = (
                                            buying_capacity // buy_price_next
                                        )
                                        if (
                                            new_symbol == "CESC.NS"
                                            and date == "2003-04-14 00:00:00"
                                        ):
                                            print("Here we go")
                                        portfolio[new_symbol] = {
                                            "quantity": quantity_next,
                                            "buy_price": buy_price_next,
                                            "Symbol": new_symbol,
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
                                            wallet_balance
                                            - quantity_next * buy_price_next
                                        )
                                        print_green(
                                            f"2DATE : {date}  |  Bought {quantity_next} of {new_symbol} at {buy_price_next} for rs: {quantity_next*buy_price_next} Remaining balance: {wallet_balance}"
                                        )
                        if accumulated_profit >= START_BALANCE / N:
                            # Take a new entry
                            new_entries = int(
                                accumulated_profit // per_stock_allocation
                            )
                            N = N + new_entries
                            potential_stocks = filtered_data[
                                filtered_data.apply(check_long_condition, axis=1)
                            ]
                            new_symbols = get_top_stocks_by_volume(
                                potential_stocks, date, top_n=500
                            )
                            if new_symbols:
                                for new_symbol in new_symbols:
                                    if len(portfolio) >= N:
                                        break
                                    if (
                                        new_symbol != symbol
                                        and new_symbol not in portfolio
                                    ):
                                        next_stock_data = potential_stocks.loc[
                                            new_symbol
                                        ]
                                        buy_price_next = next_stock_data["Close"]

                                        buying_capacity = (
                                            per_stock_allocation
                                            if wallet_balance > per_stock_allocation
                                            else wallet_balance
                                        )
                                        quantity_next = (
                                            buying_capacity // buy_price_next
                                        )
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
                                            wallet_balance
                                            - quantity_next * buy_price_next
                                        )
                                        print_blue(
                                            f"3Compounded: Bought {quantity_next} of {new_symbol} at {buy_price_next} for rs: {quantity_next * buy_price_next} Remaining balance: {wallet_balance}"
                                        )
                except Exception as e:
                    print(f"No data for {date}, {symbol}: {e}")

            worth, daily_change = refresh_final_portfolio(portfolio, date, combined_df)
            portfolio = daily_change
            balance_sheet[str(date)] = worth + wallet_balance
        print(DELISTED)
        return portfolio, transaction_history, wallet_balance, balance_sheet, worth


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
        last_day_worth,
    ) = Trader().process_trades(combined_df, START_BALANCE, N)
    print(
        f"Starting balance : {START_BALANCE}, End balance : {wallet_balance + last_day_worth}"
    )
    print(
        f"Converting final portfolio stock quantities into rupees and calculating final amount... {wallet_balance + last_day_worth}"
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
        nifty_data = plot_nifty500_investment(START_DATE, END_DATE, START_BALANCE)
        create_curve2(balance_sheet, nifty_data)
    else:
        print("Exiting")
        exit()


if __name__ == "__main__":
    main()
