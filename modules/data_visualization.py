import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def generate_sales_wave_art(
    csv_path="data/warehouse_sales.csv",
    save_path="static/generated/data_art.png"
):
    """
    Turns real sales data into an artistic wave visualization.
    """

    # Load dataset
    df = pd.read_csv(csv_path)

    # Create a date column
    df["DATE"] = pd.to_datetime(
        df["YEAR"].astype(str) + "-" + df["MONTH"].astype(str) + "-01"
    )

    # Aggregate sales by month
    monthly = (
        df.groupby("DATE")[["RETAIL SALES", "WAREHOUSE SALES"]]
        .sum()
        .reset_index()
    )

    # Build artistic signal
    values = monthly["RETAIL SALES"] + monthly["WAREHOUSE SALES"]
    x = np.arange(len(values))
    y = values.values

    # Normalize values for art effect
    y = (y - y.min()) / (y.max() - y.min())

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Create artwork
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_facecolor("#0b132b")

    for i in range(len(x) - 1):
        ax.plot(
            [x[i], x[i + 1]],
            [y[i], y[i + 1] + i * 0.002],
            color=plt.cm.plasma(i / len(x)),
            linewidth=2,
        )

    ax.axis("off")
    plt.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

    return save_path
