# orf

A fullscreen slideshow that runs an **offline N-Back cognitive test** session.
It shows a sequence of instruction slides; on each keypress it runs a
position-based N-Back task (a 3x3 grid, one colored square per trial) directly
in the same fullscreen window, then saves the results to a per-session JSON log.

The task no longer depends on any external website — it's implemented locally
in [nback.py](nback.py) with pygame.

## Using this with ThoughtTech on a second laptop

If you run this interface on one computer (e.g. a Mac) and **ThoughtTech** on
another, and you want your Space presses to create markers on the signal, see
[remote-desktop-test/HELP_MAC_TWO_LAPTOPS.md](remote-desktop-test/HELP_MAC_TWO_LAPTOPS.md). Short version: a USB cable
between two laptops does **not** forward keystrokes, and ThoughtTech must be
the frontmost window on its own machine to register a Space press.
That guide also covers installing and running this interface on macOS.

## Requirements

- **Python 3.12+**
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
   - A 3x3 grid appears. On each trial, one cell lights up briefly.
   - Press **Space** whenever the lit cell's position matches the position
     shown N trials ago (N is 2 or 3, alternating per level — see below).
   - A correct match shows **"Match!"** feedback on screen.
   - If `DEBUG` is enabled, a live corner overlay shows the running trial
     count and Hits/Misses/False Alarms/Correct Rejections/Premature counts.
   - The level runs for `NBACK_LEVEL_DURATION` seconds (see **Behavior at the
     time limit** below), results are logged, and the next slide appears.
3. Press **Esc** during a level to abort just that level (its trial-so-far
   still counts toward the log). Press **Esc** on a slide (outside a level)
   to quit the whole app.

### Behavior at the time limit

Each level is meant to run for `NBACK_LEVEL_DURATION` seconds (default 60).
**Currently implemented:** when the time limit is reached mid-trial, the
in-progress trial is always allowed to finish before the level ends — so the
actual level length can run slightly longer than `NBACK_LEVEL_DURATION`
(by at most one trial length, i.e. `STIMULUS_DURATION_MS + ISI_MS`, currently
up to 2.5s).

This was a deliberate placeholder choice pending confirmation. If a hard cutoff
at exactly `NBACK_LEVEL_DURATION` is required instead, the alternatives are:

- **Hard cutoff, discard the partial trial** — stop the instant the timer
  expires, even mid-stimulus, and drop that in-progress trial from the
  results (don't count it as a hit/miss/false alarm/correct rejection since
  it wasn't shown for its full duration).
- **Hard cutoff, keep the partial trial's response so far** — stop instantly,
  but still score whatever response state that last trial had at the cutoff
  moment (e.g. if the user already pressed Space, count it; otherwise count
  it as a miss/correct rejection based on time elapsed, even though the
  trial's stimulus window wasn't shown in full).
- **Round down to whole trials** — compute how many whole trials fit in
  `NBACK_LEVEL_DURATION` up front and run exactly that many, so the level
  always ends at a trial boundary and is always slightly *shorter* than
  `NBACK_LEVEL_DURATION` rather than slightly longer.

### Output

Each run creates a timestamped log file:

```
results_log/full_run_YYYY-MM-DD_HH-MM-SS.json
```

containing the session start time and every test's N-Back level, timestamp, and results
(Target Accuracy, Avg Response Time, Hits, Misses, False Alarms, Correct Rejections,
Premature, Total Trials).

## Configuration

Edit the constants near the top of [main.py](main.py):

| Constant               | Default        | Meaning                                          |
| ----------------------- | -------------- | ------------------------------------------------ |
| `NBACK_LEVELS`          | `[2, 3]`       | N-Back levels to cycle through, in order          |
| `NBACK_LEVEL_DURATION`  | `60`           | Target length of each level, in seconds           |
| `DEBUG`                 | `True`         | Show the live trial/stats overlay during a level  |
| `IMAGE_FOLDER`          | `slides`       | Folder of instruction slides to display           |
| `LOG_FOLDER`            | `results_log`  | Where session JSON logs are written               |

Additional N-Back task constants (grid size, colors, trial timing, response
key, match probability, position-generation strategy) are defined near the
top of [nback.py](nback.py).

## Building a Windows executable

[make-exe.bat](make-exe.bat) bundles the app (and the `slides/` folder) into a
single `.exe` with PyInstaller:

```bat
make-exe.bat
```

The result is written to the `dist/` folder.
