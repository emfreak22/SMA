from datetime import datetime

import matplotlib.pyplot as plt


def create_curve2(data, benchmark):
    dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in data.keys()]

    # Convert the values to a list

    formatted_benchmark_data = {
        ts.strftime("%Y-%m-%d"): value for ts, value in benchmark.items()
    }
    formatted_algo_data = {
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"): value
        for date, value in data.items()
    }
    common_keys = set(formatted_algo_data.keys()).intersection(
        set(formatted_benchmark_data.keys())
    )
    # Extract the common data points
    x = [key for key in common_keys]
    y1 = [formatted_algo_data[key] for key in common_keys]
    y2 = [formatted_benchmark_data[key] for key in common_keys]

    # Sort the data by the common keys (which are dates)
    x, y1, y2 = zip(*sorted(zip(x, y1, y2)))

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(x, y1, label="Algorithm curve", color="blue")
    plt.plot(x, y2, label="Nifty 500 curve", color="green")

    # Enhancing the plot
    plt.title("Comparison between Two Datasets", fontsize=16)
    plt.xlabel("Date", fontsize=14)
    plt.ylabel("Value", fontsize=14)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Show the plot
    plt.show()
