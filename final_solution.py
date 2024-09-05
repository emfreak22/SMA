import os
from data_generator import generate_data
START_BALANCE = 1000000
CSV_FOLDER_PATH = "downloads/"
n = 10
N = 50  # Number of stocks to pick if 'long' condition is satisfied

import pandas as pd


def make_a_beautiful_excel(transaction_history=None):
    # Create DataFrame from the provided transaction history
    df = pd.DataFrame(data=transaction_history)

    # Calculate the percentage change from Buy Price to Sell Price
    df["Percentage Change"] = (
        (df["Sell Price"] - df["Buy Price"]) / df["Buy Price"]
    ) * 100
    df["Date of selling"] = df["Date of selling"].dt.date
    df["Date of buying"] = df["Date of buying"].dt.date
    # Print DataFrame to check the results
    print(df)

    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(
        "transaction history/transaction_data.xlsx", engine="xlsxwriter"
    )

    # Write the DataFrame to the Excel file
    df.to_excel(writer, sheet_name="Sheet1", index=False)

    # Access the XlsxWriter workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # Define formats for the cells
    green_fill = workbook.add_format({"bg_color": "#00FF00", "font_color": "#000000"})
    red_fill = workbook.add_format({"bg_color": "#FF0000", "font_color": "#FFFFFF"})

    # Apply conditional formatting to the 'Percentage Change' column
    worksheet.conditional_format(
        "I2:I{}".format(len(df) + 1),
        {"type": "cell", "criteria": ">", "value": 1, "format": green_fill},
    )

    worksheet.conditional_format(
        "I2:I{}".format(len(df) + 1),
        {"type": "cell", "criteria": "<=", "value": 1, "format": red_fill},
    )

    # Save the Excel file
    writer.close()


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
    transaction_history = []
    all_dates = combined_df.index.get_level_values("Date").unique()

    for date in all_dates:
        max_trades_for_the_day = 0

        today_data = combined_df.loc[date]
        print(f"Portfolio {len(portfolio)}")
        if len(portfolio) < N:
            potential_stocks = today_data[
                today_data.apply(check_long_condition, axis=1)
            ]
            if potential_stocks.empty:
                print("No long for the day, sadly...")
                continue
            top_stocks = get_top_stocks_by_volume(potential_stocks, date, top_n=pick_n)

            for symbol in top_stocks:
                try:
                    if symbol not in portfolio and len(portfolio)< N:
                        stock_data = potential_stocks.loc[symbol]
                        buy_price = stock_data["Close"]
                        quantity = balance / N // buy_price
                        portfolio[symbol] = {
                            "quantity": quantity,
                            "buy_price": buy_price,
                        }

                        balance -= quantity * buy_price
                        print(
                            f"Bought {quantity} of {symbol} at {buy_price}. Remaining balance: {balance} on date {date}"
                        )
                        max_trades_for_the_day+=1
                        history = {
                            "Stock": symbol,
                            "Date of buying": date,
                            "Buy Price": buy_price,
                            "Quantity": quantity,
                            "Remaining Balance": balance,
                        }
                        transaction_history.append(history)
                except Exception as e:
                    print(f"No data for {date}, {symbol}: {e}")

        # 2. Check for Long Close and Manage Portfolio
        portfolio_to_remove = []
        for symbol in list(portfolio.keys()):
            try:
                try:
                    close_price = today_data.loc[symbol]["Close"]
                    refresh_final_portfolio(portfolio, symbol, close_price)
                    stock_data = today_data.loc[symbol]
                except Exception:
                    pass
                    # print(f" No data for {date} for {symbol}")
                    raise Exception
                if check_long_close_condition(stock_data):

                    sell_price = stock_data["Close"]
                    quantity = portfolio[symbol]["quantity"]
                    balance += quantity * sell_price
                    sell_history = {
                        "Stock": symbol,
                        "Sell Price": sell_price,
                        "Date of selling": date,
                        "Balance after selling": balance,
                    }
                    for i in transaction_history:
                        if i["Stock"] == symbol and "Sell Price" not in i:
                            i.update(sell_history)
                    print(
                        f"Sold {quantity} of {symbol} at {sell_price}. Remaining balance: {balance} on date {date}."
                    )
                    portfolio_to_remove.append(symbol)

                    # Attempt to fill the slot with a new stock
                    if len(portfolio) < N:
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
                                history = {
                                    "Stock": symbol,
                                    "Buy Price": buy_price,
                                    "Quantity": quantity,
                                    "Remaining Balance": balance,
                                }
                                max_trades_for_the_day+=1
                                transaction_history.append(history)
                                print(
                                    f"Bought {quantity_next} of {new_symbol} at {buy_price_next}. Remaining balance: {balance}"
                                )

            except Exception as e:
                print(f"No data for {date}, {symbol}: {e}")
        print(f'Date {date} portfolio {len(portfolio)}, max_trades_for_the_day : {max_trades_for_the_day}')


        # Remove sold stocks from the portfolio
        for symbol in portfolio_to_remove:
            del portfolio[symbol]

    return balance, portfolio, transaction_history


def main():
    try:
        combined_df = load_and_merge_stock_data(CSV_FOLDER_PATH)
    except ValueError:
        print("Seems like downloads folder is not populated... \n populating now...")
        generate_data()
        combined_df = load_and_merge_stock_data(CSV_FOLDER_PATH)

    final_balance, final_portfolio, transaction_history = process_trades(
        combined_df, START_BALANCE, max_stocks=N, pick_n=n
    )

    print(f"Starting balance : {START_BALANCE}")
    print(f"Final portfolio: {final_portfolio}")
    print(
        "Converting final portfolio stock quantities into rupees and calculating final amount..."
    )
    remaining_portfolio_value = 0
    for remaining_stocks in final_portfolio:
        current_value = final_portfolio[remaining_stocks]["current_value"].astype(int)
        remaining_portfolio_value += current_value
    print(final_balance + remaining_portfolio_value)
    make_a_beautiful_excel(transaction_history)
    df = pd.DataFrame(data=transaction_history)


if __name__ == "__main__":
    main()
