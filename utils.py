import datetime

import matplotlib.pyplot as plt
import pandas as pd
# import seaborn as sns


def get_today_date():
    weekno = datetime.datetime.today().weekday()

    if weekno > 5:
        raise Exception("Its a weekend, market is closed")
    else:
        return str(datetime.date.today())


def create_plot(data):
    lengths = {
        "Stock": len(data["Stock"]),
        "Date of buying": len(data["Date of buying"]),
        "Buy Price": len(data["Buy Price"]),
        "Quantity": len(data["Quantity"]),
        "Remaining Balance": len(data["Remaining Balance"]),
        "Sell Price": len(data["Sell Price"]),
        "Date of selling": len(data["Date of selling"]),
        "Balance after selling": len(data["Balance after selling"]),
        "Percentage Change": len(data["Percentage Change"]),
    }

    print(lengths)
    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert date columns to datetime
    df["Date of buying"] = pd.to_datetime(df["Date of buying"])
    df["Date of selling"] = pd.to_datetime(df["Date of selling"])

    # Set up the plotting style
    sns.set(style="whitegrid")

    # Create a figure and axes
    fig, axes = plt.subplots(3, 1, figsize=(12, 18))

    # 1. Bar Plot for Percentage Change
    sns.barplot(
        x="Percentage Change", y="Stock", data=df, palette="coolwarm", ax=axes[0]
    )
    axes[0].set_title("Percentage Change for Each Stock")

    # 2. Line Plot for Buy and Sell Prices
    df.sort_values(by="Date of buying", inplace=True)  # Sort by buying date
    axes[1].plot(
        df["Date of buying"],
        df["Buy Price"],
        marker="o",
        linestyle="-",
        color="b",
        label="Buy Price",
    )
    axes[1].plot(
        df["Date of selling"],
        df["Sell Price"],
        marker="o",
        linestyle="-",
        color="r",
        label="Sell Price",
    )
    axes[1].set_title("Buy Price and Sell Price Over Time")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Price")
    axes[1].legend()

    # 3. Histogram of Percentage Change
    sns.histplot(df["Percentage Change"], bins=10, kde=True, ax=axes[2])
    axes[2].set_title("Distribution of Percentage Change")
    axes[2].set_xlabel("Percentage Change")
    axes[2].set_ylabel("Frequency")

    # Adjust layout
    plt.tight_layout()

    # Show plot
    plt.show()


import pandas as pd

# Load the Excel file with all sheets
def replace_occurences():
    file_path = 'files/all_sheets_with_symbols.xlsx'
    sheets = pd.read_excel(file_path, sheet_name=None)

    # Define the string you want to replace and its replacement
    old_value = "RAMCOCEMENT"
    new_value = "RAMCOCEM"

    # Iterate through all sheets and replace values
    for sheet_name, df in sheets.items():
        sheets[sheet_name] = df.replace(old_value, new_value, regex=True)

    # Save back to Excel
    with pd.ExcelWriter('files/all_sheets_with_symbols.xlsx') as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
replace_occurences()

