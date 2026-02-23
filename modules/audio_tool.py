import os
import numpy as np
from pydub import AudioSegment
from pydub.effects import normalize
import soundfile as sf
import librosa

# Get absolute path to project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Use ffmpeg-8.0.1-essentials_build/bin folder which has both executables
FFMPEG_BIN = os.path.join(PROJECT_ROOT, "ffmpeg-8.0.1-essentials_build", "bin")
FFMPEG_PATH = os.path.join(FFMPEG_BIN, "ffmpeg.exe")
FFPROBE_PATH = os.path.join(FFMPEG_BIN, "ffprobe.exe")

# Tell PyDub where ffmpeg and ffprobe are located (full paths)
AudioSegment.converter = FFMPEG_PATH  
AudioSegment.ffmpeg = FFMPEG_PATH  
AudioSegment.ffprobe = FFPROBE_PATH  

# Also add to PATH for other libraries that might need it  
os.environ["PATH"] += os.pathsep + FFMPEG_BIN  
os.environ["PATH"] += os.pathsep + PROJECT_ROOT
os.environ["FFMPEG_BINARY"] = FFMPEG_PATH  
os.environ["FFPROBE_BINARY"] = FFPROBE_PATH 

ALLOWED_AUDIO = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}

def allowed_audio(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_AUDIO

def change_speed(seg, speed):
    new_rate = int(seg.frame_rate * speed)
    s = seg._spawn(seg.raw_data, overrides={"frame_rate": new_rate})
    return s.set_frame_rate(seg.frame_rate)

def add_echo(seg, delay_ms=180, repeats=4):
    out = seg
    for i in range(1, repeats + 1):
        echo = seg - (6 * i)
        # Create silent delay and append echo to it
        silence = AudioSegment.silent(duration=delay_ms * i)
        delayed_echo = silence + echo
        out = out.overlay(delayed_echo)
    return out

def add_reverb(seg):
    return add_echo(seg, delay_ms=60, repeats=10)

def layer_two(seg1, seg2, gain2_db=-6):
    seg2 = seg2 + gain2_db
    return seg1.overlay(seg2)

def pitch_shift_file(input_path, output_path, semitones):
    """Apply pitch shift to audio file using librosa with keyword arguments."""
    y, sr = sf.read(input_path)
    if y.ndim > 1:
        y = y.mean(axis=1)
    # Use keyword arguments for librosa 0.10+
    y2 = librosa.effects.pitch_shift(y=y.astype(float), sr=sr, n_steps=semitones)
    sf.write(output_path, y2, sr)
    return output_path

def generate_ambient(output_path, seconds=10, sr=22050):
    t = np.linspace(0, seconds, int(sr * seconds))
    base = 0.2 * np.sin(2 * np.pi * 110 * t)
    pad = 0.1 * np.sin(2 * np.pi * 220 * t)
    noise = 0.03 * np.random.randn(len(t))
    y = base + pad + noise
    y = np.clip(y, -1, 1)
    sf.write(output_path, y, sr)
    return output_path
