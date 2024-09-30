import matplotlib.pyplot as plt

import yfinance as yf


def plot_nifty500_investment(start_date, end_date, initial_investment=100000):
    # Fetch historical data for Nifty 500
    nifty500 = yf.Ticker("^CRSLDX")

    data = nifty500.history(start=start_date, end=end_date)

    print(f"Plotting graph {start_date}, {end_date}")
    if data.empty:
        print("No data available for the given date range.")
        return

    # Calculate normalized returns
    initial_price = data["Close"].iloc[0]
    data["Investment Value"] = (data["Close"] / initial_price) * initial_investment
    return data["Investment Value"].to_dict()
    # Example usage


start_date = "2023-01-01"  # Replace with your start date
end_date = "2023-09-01"  # Replace with your end date
plot_nifty500_investment(start_date, end_date)
