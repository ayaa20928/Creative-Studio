# Creative Studio

A Flask-based creative web application for generating art, visualizing data, and processing images and audio.

## Features

- **Generative Art**: Create algorithmic visuals with customizable seeds, palettes & shapes
- **Data Art**: Transform CSV datasets into beautiful visualizations
- **Image Tool**: Upload images, apply filters, rotation, flipping, resizing
- **Audio Tool**: Upload audio and apply effects (speed, echo, reverb, pitch)
- **Gallery**: View all your generated artworks
- **Mobile Version**: Dedicated mobile-optimized interface at `/mobile`

## Requirements

- Python 3.8+
- FFmpeg (for audio processing) - see installation instructions below
- See `requirements.txt` for dependencies

## FFmpeg Installation

### Windows:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the zip file
3. Copy `ffmpeg.exe` to the project root folder (next to app.py)
4. OR add FFmpeg to your system PATH

### Mac:
```
bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian):
```
bash
sudo apt update
sudo apt install ffmpeg
```

## Installation

1. Clone the repository:
```
bash
git clone https://github.com/ayaa20928/creative-studio.git
cd creative-studio
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

4. Install dependencies:
```
bash
pip install -r requirements.txt
```

## Usage

1. Run the Flask server:
```
bash
python app.py
```

2. Open your browser:
- Local: http://127.0.0.1:5000
- Mobile (same network): http://YOUR_IP:5000
- Mobile version: http://127.0.0.1:5000/mobile

## Project Structure

```
creative-studio/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── modules/               # Backend modules
│   ├── audio_tool.py
│   ├── data_mandala.py
│   ├── data_visualization.py
│   ├── image_tool.py
│   └── generative_art/
├── templates/             # HTML templates
├── static/               # CSS, JS, uploaded files
└── data/                 # CSV data files
```

## License

MIT
