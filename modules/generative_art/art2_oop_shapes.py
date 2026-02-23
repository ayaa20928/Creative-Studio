import os
import random
import matplotlib.pyplot as plt


PALETTES = {
    "sunset": ["#ff595e", "#ffca3a", "#8ac926", "#1982c4", "#6a4c93"],
    "ocean":  ["#001219", "#005f73", "#0a9396", "#94d2bd", "#e9d8a6"],
    "mono":   ["#111111", "#333333", "#555555", "#777777", "#999999"],
}


class Shape:
    def __init__(self, x, y, size, color, alpha=0.7):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.alpha = alpha

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def recolor(self, new_color):
        self.color = new_color

    def draw(self, ax):
        raise NotImplementedError


class Circle(Shape):
    def draw(self, ax):
        ax.add_patch(plt.Circle((self.x, self.y), self.size, color=self.color, alpha=self.alpha))


class Square(Shape):
    def draw(self, ax):
        s = self.size * 2
        ax.add_patch(plt.Rectangle((self.x - self.size, self.y - self.size), s, s,
                                   color=self.color, alpha=self.alpha))


class Triangle(Shape):
    def draw(self, ax):
        s = self.size * 2
        points = [
            (self.x, self.y + self.size),
            (self.x - self.size, self.y - self.size),
            (self.x + self.size, self.y - self.size),
        ]
        ax.add_patch(plt.Polygon(points, closed=True, color=self.color, alpha=self.alpha))


def generate_oop_art(
    n_shapes=180,
    palette="ocean",
    seed=None,
    save_path="static/generated/art2.png",
    background="#ffffff",
):
    """
    Artwork 2: Object-Oriented generative art using Shape classes.
    """
    if seed is not None:
        random.seed(seed)

    colors = PALETTES.get(palette, PALETTES["ocean"])
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor(background)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    shape_classes = [Circle, Square, Triangle]
    shapes = []

    for i in range(n_shapes):
        x, y = random.uniform(5, 95), random.uniform(5, 95)
        size = random.uniform(1.0, 6.0)
        color = random.choice(colors)
        alpha = random.uniform(0.25, 0.85)

        cls = random.choice(shape_classes)
        shp = cls(x, y, size, color, alpha=alpha)

        # Small OOP behavior: some shapes "drift" diagonally
        if i % 5 == 0:
            shp.move(random.uniform(-4, 4), random.uniform(-4, 4))

        # Conditional recolor rule
        if size > 5.0 and i % 3 == 0:
            shp.recolor(random.choice(colors))

        shapes.append(shp)

    for shp in shapes:
        shp.draw(ax)

    plt.tight_layout()
    fig.savefig(save_path, dpi=200)
    plt.close(fig)
    return save_path
