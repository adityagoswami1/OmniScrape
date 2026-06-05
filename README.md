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

# OmniScrape - Beginner Setup Guide (Windows)

## Prerequisites

Before running OmniScrape, make sure the following are installed:

* Python 3.11 or later
* Git (optional if downloading ZIP)
* Internet connection (required for installing dependencies and Playwright browsers)

---

# Step 1: Download the Project

## Option A: Using Git (Recommended)

Open PowerShell and run:

```powershell
git clone https://github.com/adityagoswami1/OmniScrape.git
cd OmniScrape
```

### If you get:

```text
git : The term 'git' is not recognized
```

Git is not installed.

Install Git from:

https://git-scm.com/download/win

After installation:

1. Close PowerShell
2. Open PowerShell again
3. Run:

```powershell
git --version
```

If a version number appears, Git is installed correctly.

---

## Option B: Download ZIP

1. Open the GitHub repository.
2. Click **Code → Download ZIP**.
3. Extract the ZIP file.
4. Open the extracted folder.

---

# Step 2: Verify Python Installation

Open PowerShell and run:

```powershell
python --version
```

or

```powershell
py --version
```

Expected output:

```text
Python 3.x.x
```

---

## If Python is not found

Example error:

```text
Python was not found
```

Install Python from:

https://www.python.org/downloads/windows/

IMPORTANT:

During installation, enable:

```text
✓ Add Python to PATH
```

After installation:

1. Close PowerShell
2. Open a new PowerShell window
3. Run:

```powershell
py --version
```

---

# Step 3: Open PowerShell in the Project Folder

Navigate to the OmniScrape folder.

Example:

```powershell
cd C:\Users\YourName\Downloads\OmniScrape-main
```

Verify you are inside the project:

```powershell
dir
```

You should see files such as:

```text
app.py
requirements.txt
README.md
```

---

# Step 4: Create a Virtual Environment

Create an isolated Python environment:

```powershell
py -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

After activation you should see:

```text
(venv)
```

at the beginning of your terminal line.

---

## If PowerShell Blocks Activation

You may see an execution policy error.

Run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

---

# Step 5: Install Project Dependencies

Install required Python packages:

```powershell
pip install -r requirements.txt
```

Wait for installation to complete.

---

## If Flask Error Appears

If you see:

```text
ModuleNotFoundError: No module named 'flask'
```

Install Flask manually:

```powershell
pip install flask
```

Then run the application again.

Note:
This usually indicates Flask is missing from requirements.txt.

---

# Step 6: Install Playwright Browser

OmniScrape uses Playwright for browser automation.

Install Chromium:

```powershell
py -m playwright install chromium
```

This may take several minutes on the first run.

---

# Step 7: Run the Application

Start OmniScrape:

```powershell
py app.py
```

Expected output should indicate that the Flask server has started successfully.

---

# Common Issues

## Git Not Found

Error:

```text
git : The term 'git' is not recognized
```

Solution:

Install Git and restart PowerShell.

---

## Python Not Found

Error:

```text
Python was not found
```

Solution:

Install Python and ensure "Add Python to PATH" is enabled.

---

## Virtual Environment Won't Activate

Error:

```text
running scripts is disabled on this system
```

Solution:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Missing Python Package

Error:

```text
ModuleNotFoundError
```

Example:

```text
No module named 'flask'
```

Solution:

```powershell
pip install <package-name>
```

or update requirements.txt to include the missing dependency.

---

# Updating Dependencies

After installing additional packages:

```powershell
pip freeze > requirements.txt
```

This ensures future users install all required packages automatically.

---

# Complete Installation Commands

For users who already have Python installed:

```powershell
git clone https://github.com/adityagoswami1/OmniScrape.git
cd OmniScrape

py -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

py -m playwright install chromium

py app.py
```

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
