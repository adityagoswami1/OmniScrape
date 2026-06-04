# 🕸️ OmniScrape

**Elite Image Harvesting & Deduplication Engine**

OmniScrape is a powerful, self-hosted web scraping tool that collects high-resolution images from multiple stock photo platforms simultaneously. It features a sleek browser-based UI, real-time progress streaming, smart deduplication, and a human-in-the-loop CAPTCHA system that lets you bypass anti-bot firewalls effortlessly.

---

## ✨ Features

- **Multi-Source Scraping** — Harvest images from Unsplash, Pexels, Pixabay, and Pinterest in parallel.
- **Human-in-the-Loop** — When a site throws a CAPTCHA, a real browser window pops up for you to solve it. The scraper resumes automatically once you're through.
- **Live Terminal & Gallery** — Watch logs stream in real-time and see every downloaded image appear instantly in a live gallery.
- **Granular Stop Controls** — Stop everything, stop a specific source, or stop a specific search category mid-run.
- **Perceptual Deduplication** — Built-in script to scan your entire dataset and remove visually identical images using perceptual hashing.
- **Premium UI** — A dark, minimalist interface inspired by modern portfolio design.

---

## 🖼️ Screenshot

> _Run the app and visit `http://localhost:5001` to see OmniScrape in action._

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

#Windows (PowerShell)
git clone https://github.com/adityagoswami1/OmniScrape.git
cd OmniScrape

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

playwright install chromium

python app.py

If PowerShell blocks script execution, run:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Then activate the virtual environment again.

#MacOs/ Linux
```bash
# Clone the repo
git clone https://github.com/adityagoswami1/OmniScrape.git
cd OmniScrape

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for scraping)
playwright install chromium
```

### Run

```bash
python app.py
```

Then open your browser and go to **http://localhost:5001**.

---

## 🛠️ How It Works

1. **Enter a topic** (e.g., `cats, dogs, birds`) and select your sources.
2. **Hit "Initialize Build"** — OmniScrape launches headless browsers for each source and begins scrolling and collecting image URLs.
3. **CAPTCHA detected?** A visible browser window pops up. Solve the puzzle, and the scraper takes back control automatically.
4. **Images stream in** to the live gallery as they download, and full logs appear in the terminal panel.
5. **Stop anytime** — Use the granular stop controls to abort specific sources or categories without killing the whole pipeline.

---

## 📁 Project Structure

```
OmniScrape/
├── app.py                      # Flask backend & API routes
├── requirements.txt            # Python dependencies
├── deduplicate_dataset.py      # Standalone deduplication script
├── dataset_builder/
│   ├── __init__.py
│   ├── main.py                 # Pipeline orchestrator
│   ├── cleaner.py              # Image cleaning utilities
│   ├── metadata.py             # Metadata extraction
│   ├── statistics.py           # Dataset statistics
│   └── collectors/
│       ├── base_collector.py   # Abstract base class
│       ├── unsplash.py         # Unsplash scraper
│       ├── pexels.py           # Pexels scraper
│       ├── pixabay.py          # Pixabay scraper
│       └── pinterest.py        # Pinterest scraper
└── static/
    ├── index.html              # OmniScrape UI
    ├── style.css               # Dark slate theme
    └── script.js               # Frontend logic & SSE
```

---

## 🧹 Deduplication

After collecting images, run the deduplication script to remove visually identical copies:

```bash
python deduplicate_dataset.py
```

This uses perceptual hashing (pHash) to compare images and automatically deletes duplicates.

---

## ⚠️ Disclaimer

This tool is intended for **personal use and research purposes only**. Always respect the Terms of Service of the websites you scrape. The developers are not responsible for any misuse of this tool.

---

## 📄 License

MIT License — feel free to fork, modify, and share.
