# orf

A fullscreen slideshow that runs an automated **N-Back cognitive test** session.
It shows a sequence of instruction slides; on each keypress it launches Chrome,
runs a 5-minute N-Back test on [cognitivetrain.com](https://cognitivetrain.com/n-back-test/),
scrapes the results, and saves them to a per-session JSON log.

## Requirements

- **Python 3.12+**
- **Google Chrome** installed (the script auto-downloads a matching ChromeDriver)
- Works on Windows, macOS, and Linux (built/packaged primarily for Windows)

## Setup

This project uses [uv](https://docs.astral.sh/uv/). With uv installed:

```bash
uv sync
```

Or with plain pip + a virtual environment:

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install pygame selenium undetected-chromedriver webdriver-manager pyinstaller
```

## Running

```bash
uv run main.py
# or, with the venv activated:
python main.py
```

### How it works

1. The app opens **fullscreen** and displays the first slide from the `slides/` folder.
2. Press **Space**, **Enter**, or **→** to begin a test:
   - Pygame minimizes, Chrome opens in kiosk mode on the N-Back test page.
   - The test auto-starts and runs for **5 minutes** (`GAME_DURATION`).
   - Results (accuracy, response time, hits, misses, etc.) are extracted and logged.
   - The N-Back level increments, Chrome closes, and the next slide appears.
3. Press **Esc** (or close the window) to quit.

### Output

Each run creates a timestamped log file:

```
results_log/full_run_YYYY-MM-DD_HH-MM-SS.json
```

containing the session start time and every test's N-Back level, timestamp, and results.

## Configuration

Edit the constants near the top of [main.py](main.py):

| Constant             | Default     | Meaning                                    |
| -------------------- | ----------- | ------------------------------------------ |
| `START_NBACK_LEVEL`  | `2`         | N-Back level the first test starts at      |
| `GAME_DURATION`      | `5 * 60`    | Test length in seconds (5 minutes)         |
| `IMAGE_FOLDER`       | `slides`    | Folder of instruction slides to display    |
| `LOG_FOLDER`         | `results_log` | Where session JSON logs are written      |

To set the difficulty level automatically, uncomment the `set_nback_level(...)`
call inside `main()`.

## Building a Windows executable

[make-exe.bat](make-exe.bat) bundles the app (and the `slides/` folder) into a
single `.exe` with PyInstaller:

```bat
make-exe.bat
```

The result is written to the `dist/` folder.
