import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_sales_mandala(
    csv_path="data/warehouse_sales.csv",
    save_path="static/generated/mandala.png",
    n_points=2500,
    seed=7
):
    """
    Mandala-like scatter using sales data as color + radius modulation.
    """
    rng = np.random.default_rng(seed)

    df = pd.read_csv(csv_path)
    df["DATE"] = pd.to_datetime(df["YEAR"].astype(str) + "-" + df["MONTH"].astype(str) + "-01")
    monthly = (df.groupby("DATE")[["RETAIL SALES", "WAREHOUSE SALES"]]
                 .sum()
                 .reset_index()
                 .sort_values("DATE"))

    values = (monthly["RETAIL SALES"] + monthly["WAREHOUSE SALES"]).to_numpy(dtype=float)

    # normalize 0..1
    mn, mx = values.min(), values.max()
    norm = (values - mn) / (mx - mn) if mx != mn else np.full_like(values, 0.5)

    # sample norm values repeatedly to create many points
    u = rng.choice(norm, size=n_points, replace=True)

    # spiral mandala coordinates
    theta = np.linspace(0, 20*np.pi, n_points) + rng.normal(0, 0.08, n_points)
    r = 0.02 + (0.95 * (np.linspace(0, 1, n_points)**0.85))
    r = r * (0.75 + 0.5*u)  # data controls radius

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    # point size also data-driven
    sizes = 8 + 40*(u**1.2)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig = plt.figure(figsize=(8, 6))
    ax = plt.subplot(111)
    ax.set_aspect("equal")
    ax.axis("off")

    sc = ax.scatter(x, y, c=u, s=sizes, cmap="plasma", alpha=0.75, linewidths=0)
    ax.add_patch(plt.Circle((0, 0), 1.02, fill=False, linewidth=1.0, alpha=0.6))

    cbar = plt.colorbar(sc, fraction=0.046, pad=0.04)
    cbar.set_label("Normalized Sales (Retail + Warehouse)")

    ax.set_title("Sales Mandala : Data as Digital Art", pad=12)

    plt.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)

    return save_path
