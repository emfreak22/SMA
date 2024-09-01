import pandas as pd


def make_a_beautiful_excel(transaction_history=None):
    from final_solution import START_BALANCE

    # Create DataFrame from the provided transaction history
    df = pd.DataFrame(data=transaction_history)

    # Calculate the percentage change from Buy Price to Sell Price
    df["Percentage Change"] = (
        (df["Sell Price"] - df["Buy Price"]) / df["Buy Price"]
    ) * 100
    df["Date of selling"] = df["Date of selling"].dt.date
    df["Date of buying"] = df["Date of buying"].dt.date
    df["Relative Gain"] = (
        df["Sell Price"] / df["Buy Price"] / df["Buy Price"]
    ) / START_BALANCE
    df["Risk"] = (df["Buy Price"] - df["Sell Price"]) * df["Quantity"]  # Potential Loss
    df["Reward"] = (df["Sell Price"] - df["Buy Price"]) * df[
        "Quantity"
    ]  # Potential Gain

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
        "G2:G{}".format(len(df) + 1),
        {"type": "cell", "criteria": ">", "value": 1, "format": green_fill},
    )

    worksheet.conditional_format(
        "G2:G{}".format(len(df) + 1),
        {"type": "cell", "criteria": "<=", "value": 1, "format": red_fill},
    )

    # Save the Excel file
    writer.close()
