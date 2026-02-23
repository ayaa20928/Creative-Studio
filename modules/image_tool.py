import os
from PIL import Image, ImageFilter, ImageOps

ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp"}

def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT

def apply_edit(
    input_path: str,
    output_path: str,
    effect="none",
    rotate_deg=0,
    flip="none",
    resize_w=None,
    resize_h=None,
):
    img = Image.open(input_path).convert("RGB")

    # resize
    if resize_w and resize_h and resize_w > 0 and resize_h > 0:
        img = img.resize((resize_w, resize_h))

    # rotate
    if rotate_deg:
        img = img.rotate(-rotate_deg, expand=True)

    # flip
    if flip == "horizontal":
        img = ImageOps.mirror(img)
    elif flip == "vertical":
        img = ImageOps.flip(img)

    # effects
    if effect == "grayscale":
        img = ImageOps.grayscale(img).convert("RGB")
    elif effect == "blur":
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
    elif effect == "sharpen":
        img = img.filter(ImageFilter.SHARPEN)
    elif effect == "edges":
        img = img.filter(ImageFilter.FIND_EDGES)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)
    return output_path
