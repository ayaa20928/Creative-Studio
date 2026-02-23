import os
import time

from flask import Flask, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
from pydub import AudioSegment

# ===== Let Python/Flask find ffmpeg.exe and ffprobe.exe =====
# Use the ffmpeg-8.0.1-essentials_build/bin folder which has both executables
ffmpeg_bin_path = os.path.join(os.path.abspath("."), "ffmpeg-8.0.1-essentials_build", "bin")
os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
os.environ["PATH"] += os.pathsep + os.path.abspath(".")

# ===== Your modules =====
from modules.image_tool import allowed_file, apply_edit
from modules.data_visualization import generate_sales_wave_art
from modules.generative_art.art1_geometric import generate_geometric_storm
from modules.generative_art.art2_oop_shapes import generate_oop_art
from modules.audio_tool import (
    allowed_audio, change_speed, add_echo, add_reverb,
    pitch_shift_file, generate_ambient
)

app = Flask(__name__)

# ---------------- PATHS / FOLDERS (centralized) ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
GEN_DIR = os.path.join(STATIC_DIR, "generated")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
OUTPUT_DIR = os.path.join(STATIC_DIR, "outputs")

AUDIO_UPLOAD_DIR = os.path.join(STATIC_DIR, "audio_uploads")
AUDIO_OUTPUT_DIR = os.path.join(STATIC_DIR, "audio_outputs")

for d in [STATIC_DIR, GEN_DIR, UPLOAD_DIR, OUTPUT_DIR, AUDIO_UPLOAD_DIR, AUDIO_OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

OUTPUT_FOLDERS = [
    ("generated", GEN_DIR),
    ("outputs", OUTPUT_DIR),
    ("uploads", UPLOAD_DIR),
    ("audio_outputs", AUDIO_OUTPUT_DIR),
    ("audio_uploads", AUDIO_UPLOAD_DIR),
]


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- MOBILE VERSION ----------------
@app.route("/mobile")
def mobile():
    return render_template("mobile_index.html")


# ---------------- MODULE 1 : GENERATIVE ART ----------------
@app.route("/generative", methods=["GET", "POST"])
def generative():
    n_shapes = 250
    palette = "sunset"
    seed = None

    if request.method == "POST":
        n_shapes = int(request.form.get("n_shapes", 250))
        palette = request.form.get("palette", "sunset")
        seed_raw = request.form.get("seed", "").strip()
        seed = int(seed_raw) if seed_raw else None

    out_path = os.path.join(GEN_DIR, "art1.png")
    generate_geometric_storm(
        n_shapes=n_shapes,
        palette=palette,
        seed=seed,
        save_path=out_path,
    )

    img_url = url_for("static", filename="generated/art1.png") + f"?v={int(time.time())}"

    return render_template(
        "generative_art.html",
        img_url=img_url,
        n_shapes=n_shapes,
        palette=palette,
        seed="" if seed is None else seed,
    )


@app.route("/generative/oop", methods=["GET", "POST"])
def generative_oop():
    n_shapes = 180
    palette = "ocean"
    seed = None

    if request.method == "POST":
        n_shapes = int(request.form.get("n_shapes", 180))
        palette = request.form.get("palette", "ocean")
        seed_raw = request.form.get("seed", "").strip()
        seed = int(seed_raw) if seed_raw else None

    out_path = os.path.join(GEN_DIR, "art2.png")
    generate_oop_art(
        n_shapes=n_shapes,
        palette=palette,
        seed=seed,
        save_path=out_path,
    )

    img_url = url_for("static", filename="generated/art2.png") + f"?v={int(time.time())}"

    return render_template(
        "generative_oop.html",
        img_url=img_url,
        n_shapes=n_shapes,
        palette=palette,
        seed="" if seed is None else seed,
    )


@app.route("/generative/interactive")
def generative_interactive():
    return render_template("generative_interactive.html")


# ---------------- MODULE 2 : DATA ART ----------------
@app.route("/data-art")
def data_art():
    out_path = os.path.join(GEN_DIR, "data_art.png")
    generate_sales_wave_art(
        csv_path="data/warehouse_sales.csv",
        save_path=out_path,
    )
    img_url = url_for("static", filename="generated/data_art.png") + f"?v={int(time.time())}"
    return render_template("data_art.html", img_url=img_url)


@app.route("/api/sales-series")
def sales_series():
    df = pd.read_csv("data/warehouse_sales.csv")

    # Normalize column names to reduce CSV mismatch issues
    df.columns = [c.strip().upper() for c in df.columns]

    # Ensure required columns exist
    required = {"YEAR", "MONTH", "RETAIL SALES", "WAREHOUSE SALES"}
    missing = required - set(df.columns)
    if missing:
        return jsonify({"error": f"CSV is missing columns: {sorted(list(missing))}"}), 400

    df["MONTH"] = df["MONTH"].astype(str).str.zfill(2)
    df["DATE"] = pd.to_datetime(df["YEAR"].astype(str) + "-" + df["MONTH"] + "-01", errors="coerce")
    df = df.dropna(subset=["DATE"])

    monthly = (
        df.groupby("DATE")[["RETAIL SALES", "WAREHOUSE SALES"]]
        .sum()
        .reset_index()
        .sort_values("DATE")
    )

    values = (monthly["RETAIL SALES"] + monthly["WAREHOUSE SALES"]).tolist()
    labels = monthly["DATE"].dt.strftime("%Y-%m").tolist()

    if not values:
        return jsonify({"labels": [], "values": [], "norm": []})

    mn, mx = min(values), max(values)
    norm = [(v - mn) / (mx - mn) if mx != mn else 0.5 for v in values]

    return jsonify({"labels": labels, "values": values, "norm": norm})


@app.route("/data-art/multi")
def data_art_multi():
    return render_template("data_art_multi.html")


# ---------------- MODULE 3 : IMAGE TOOL ----------------
@app.route("/image-tool", methods=["GET", "POST"])
def image_tool():
    output_url = None

    if request.method == "POST":
        f = request.files.get("image")
        if not f or f.filename == "":
            return render_template("image_tool.html", output_url=None)

        filename = secure_filename(f.filename)
        if not allowed_file(filename):
            return render_template("image_tool.html", output_url=None)

        # Unique upload name to avoid overwriting
        in_name = f"in_{int(time.time())}_{filename}"
        in_path = os.path.join(UPLOAD_DIR, in_name)
        f.save(in_path)

        effect = request.form.get("effect", "none")
        rotate = int(request.form.get("rotate", "0") or 0)
        flip = request.form.get("flip", "none")

        w_raw = request.form.get("w", "").strip()
        h_raw = request.form.get("h", "").strip()
        w = int(w_raw) if w_raw else None
        h = int(h_raw) if h_raw else None

        out_name = f"edited_{int(time.time())}_{filename}"
        out_path = os.path.join(OUTPUT_DIR, out_name)

        apply_edit(
            input_path=in_path,
            output_path=out_path,
            effect=effect,
            rotate_deg=rotate,
            flip=flip,
            resize_w=w,
            resize_h=h,
        )

        output_url = url_for("static", filename=f"outputs/{out_name}") + f"?v={int(time.time())}"

    return render_template("image_tool.html", output_url=output_url)


# ---------------- MODULE 3B : AUDIO TOOL ----------------
@app.route("/audio-tool", methods=["GET", "POST"])
def audio_tool():
    output_url = None

    if request.method == "POST":
        action = request.form.get("action", "speed")

        # Ambient generation (no upload)
        if action == "ambient":
            out_name = f"ambient_{int(time.time())}.wav"
            out_path = os.path.join(AUDIO_OUTPUT_DIR, out_name)
            generate_ambient(out_path)
            output_url = url_for("static", filename=f"audio_outputs/{out_name}") + f"?v={int(time.time())}"
            return render_template("audio_tool.html", output_url=output_url)

        f = request.files.get("audio")
        if not f or f.filename == "":
            return render_template("audio_tool.html", output_url=None)

        name = secure_filename(f.filename)
        if not allowed_audio(name):
            return render_template("audio_tool.html", output_url=None)

        in_name = f"in_{int(time.time())}_{name}"
        in_path = os.path.join(AUDIO_UPLOAD_DIR, in_name)
        f.save(in_path)

        # Pitch shifting (librosa) -> outputs wav
        if action == "pitch":
            semis = float(request.form.get("semitones", "0") or 0)
            out_name = f"pitch_{int(time.time())}.wav"
            out_path = os.path.join(AUDIO_OUTPUT_DIR, out_name)
            pitch_shift_file(in_path, out_path, semis)
            output_url = url_for("static", filename=f"audio_outputs/{out_name}") + f"?v={int(time.time())}"
            return render_template("audio_tool.html", output_url=output_url)

        # PyDub effects
        seg = AudioSegment.from_file(in_path)

        if action == "speed":
            speed = float(request.form.get("speed", "1") or 1)
            seg2 = change_speed(seg, speed)
        elif action == "echo":
            seg2 = add_echo(seg)
        elif action == "reverb":
            seg2 = add_reverb(seg)
        else:
            seg2 = seg

        out_name = f"{action}_{int(time.time())}.wav"
        out_path = os.path.join(AUDIO_OUTPUT_DIR, out_name)
        seg2.export(out_path, format="wav")

        output_url = url_for("static", filename=f"audio_outputs/{out_name}") + f"?v={int(time.time())}"

    return render_template("audio_tool.html", output_url=output_url)


# ---------------- GALLERY ----------------
@app.route("/gallery")
def gallery():
    items = []
    allowed_ext = (".png", ".jpg", ".jpeg", ".gif", ".wav")

    for label, folder in OUTPUT_FOLDERS:
        os.makedirs(folder, exist_ok=True)
        for f in os.listdir(folder):
            if f.lower().endswith(allowed_ext):
                rel = os.path.relpath(os.path.join(folder, f), STATIC_DIR).replace("\\", "/")
                items.append({
                    "label": label,
                    "filename": f,
                    "static_path": rel
                })

    # Newest first (works well with timestamped names)
    items.sort(key=lambda x: x["filename"], reverse=True)

    return render_template("gallery.html", items=items)


@app.route("/gallery/clear", methods=["POST"])
def gallery_clear():
    """Clear all files in gallery folders"""
    deleted_count = 0
    for label, folder in OUTPUT_FOLDERS:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                try:
                    file_path = os.path.join(folder, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_count += 1
                except Exception as e:
                    pass
    
    return jsonify({"ok": True, "deleted": deleted_count})


# ---------------- OPTIONAL UPLOAD (remove if unused) ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    filename = None
    if request.method == "POST":
        f = request.files.get("file")
        if f and f.filename:
            filename = secure_filename(f.filename)
            # Make it unique to avoid overwrites
            safe_name = f"in_{int(time.time())}_{filename}"
            f.save(os.path.join(UPLOAD_DIR, safe_name))
            filename = safe_name

    return render_template("upload.html", filename=filename)

import base64

@app.route("/save_canvas", methods=["POST"])
def save_canvas():
    try:
        data = request.get_json(force=True) or {}
        img_data = data.get("image", "")

        if not img_data.startswith("data:image/png;base64,"):
            return jsonify({"ok": False, "error": "Invalid image data"}), 400

        b64 = img_data.split(",", 1)[1]
        raw = base64.b64decode(b64)

        filename = f"canvas_{int(time.time())}.png"
        out_path = os.path.join(GEN_DIR, filename)

        with open(out_path, "wb") as f:
            f.write(raw)

        return jsonify({"ok": True, "filename": filename})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
@app.route("/data-art/animated")
def data_art_animated():
    return render_template("data_art_animated.html")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


