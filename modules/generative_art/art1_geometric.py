import os
import random
import matplotlib.pyplot as plt

PALETTES = {
    "sunset": ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93"],
    "ocean":  ["#001219", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6"],
    "mono":   ["#111111", "#333333", "#555555", "#777777", "#999999"],
}

def generate_geometric_storm(
    n_shapes=250,
    palette="sunset",
    seed=None,
    save_path="static/generated/art1.png",
    background="#ffffff",
):
    if seed is not None:
        random.seed(seed)

    colors = PALETTES.get(palette, PALETTES["sunset"])
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor(background)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    for i in range(n_shapes):
        x, y = random.uniform(0, 100), random.uniform(0, 100)
        c = random.choice(colors)
        r = random.uniform(0.2, 6.0)

        if i % 7 == 0:
            x2 = x + random.uniform(-15, 15)
            y2 = y + random.uniform(-15, 15)
            lw = random.uniform(0.3, 2.5)
            alpha = random.uniform(0.2, 0.8)
            ax.plot([x, x2], [y, y2], linewidth=lw, alpha=alpha, color=c)
        else:
            alpha = 0.15 if r > 4 else random.uniform(0.2, 0.9)
            ax.add_patch(plt.Circle((x, y), r, color=c, alpha=alpha))

    plt.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    return save_path
