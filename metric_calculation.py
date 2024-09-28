import pandas as pd
from rich.console import Console
from rich.table import Table


def calculate():
    data_dict = {}
    file_path = "transaction history"
    df = pd.read_excel(f"{file_path}/transaction_data.xlsx")

    # Adding a cumulative return column
    df["Cumulative_Return"] = df["Reward"].cumsum()

    # Calculate drawdown
    df["Peak"] = df["Cumulative_Return"].cummax()
    df["Drawdown"] = (df["Cumulative_Return"] - df["Peak"]) / df["Peak"]
    max_drawdown = df["Drawdown"].min()

    data_dict["total_trades"] = len(df)
    winning_trades = df[df["Reward"] >= 0]
    data_dict["winning_trades_count"] = (df["Reward"] >= 0).sum()
    losing_trades = df[df["Risk"] > 0]
    data_dict["losing_trades_count"] = (df["Risk"] > 0).sum()
    data_dict["win_percent"] = (
        data_dict["winning_trades_count"] / data_dict["total_trades"]
    )
    data_dict["lose_percent"] = (
        data_dict["losing_trades_count"] / data_dict["total_trades"]
    )
    data_dict["total_risk"] = df[df["Risk"] > 0][
        "Risk"
    ].sum()  # Sum of losses (where risk is positive)
    data_dict["total_reward"] = df[df["Reward"] > 0][
        "Reward"
    ].sum()  # Sum of gains (where reward is positive)
    data_dict["R:R"] = (
        data_dict["total_reward"] / data_dict["total_risk"]
        if data_dict["total_risk"] != 0
        else float("inf")
    )
    data_dict["average_win"] = winning_trades["Reward"].mean()
    data_dict["average_loss"] = losing_trades["Risk"].mean()
    data_dict["expectancy"] = (data_dict["win_percent"] * data_dict["average_win"]) - (
        data_dict["lose_percent"] * data_dict["average_loss"]
    )
    data_dict[
        "max_drawdown"
    ] = max_drawdown  # Add maximum drawdown to the data dictionary

    table_data = [[key, value] for key, value in data_dict.items()]

    console = Console()
    table = Table(title="Trading Metrics")

    table.add_column("Metric")
    table.add_column("Value")

    for i in table_data:
        key, value = i[0], i[1]
        table.add_row(str(key), str(value))

    console.print(table)
    print(table)
