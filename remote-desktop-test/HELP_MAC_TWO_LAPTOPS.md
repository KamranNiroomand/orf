# Help — Running the Interface on a Mac with ThoughtTech on a Second Laptop

This guide is for the setup where:

- **Laptop A (your Mac)** runs this interface (the N-Back slideshow app).
- **Laptop B (Windows)** runs **ThoughtTech**, which records the signal and
  draws the markers.

It explains why markers only appear when you press Space on Laptop B, and how
to make a Space press on your Mac create a marker on Laptop B.

---

## 1. Why it currently doesn't work

**A USB cable between two laptops does not share the keyboard.**

This is the key point, and it is the reason nothing happens. A plain USB
cable (even a USB-A to USB-A or USB-C to USB-C cable) between two computers
does **not** create a keyboard link, a network link, or any data link at all.
Both laptops are "hosts" — neither one can act as a keyboard for the other.
So when you press Space on the Mac, that keypress never leaves the Mac.

On top of that, ThoughtTech only creates a marker when **ThoughtTech itself
is the focused, active window** on Laptop B and receives the Space keypress.
It does not listen for keys sent to any other program or any other computer.

So there are two separate requirements, and both must be true:

1. The Space press must physically arrive at Laptop B.
2. On Laptop B, ThoughtTech must be the frontmost / active window when it arrives.

---

## 2. Installing the interface on your Mac

Do this once, on the Mac. It takes about five minutes.

### Step 1 — Install Python 3.12 or newer

macOS comes with an old Python that will **not** work. Check what you have by
opening **Terminal** (press `Cmd + Space`, type `Terminal`, press Enter) and
running:

```bash
python3 --version
```

If it prints `Python 3.12.x` or higher, skip to Step 2. Otherwise install it:

- Download the macOS installer from <https://www.python.org/downloads/macos/>
  and run it, **or**
- If you have [Homebrew](https://brew.sh):

  ```bash
  brew install python@3.12
  ```

Close and reopen Terminal, then check `python3 --version` again.

### Step 2 — Get the project folder onto the Mac

Copy the whole project folder (the one containing `main.py`, `nback.py`, and
the `slides` folder) onto the Mac — via USB stick, AirDrop, email, or:

```bash
git clone <repository-url>
```

Keep the folder structure intact. The `slides` folder must stay next to
`main.py`, otherwise the app exits with *"No images found in slides folder!"*.

### Step 3 — Open Terminal in the project folder

In Terminal, type `cd ` (with a space after it), then **drag the project folder
from Finder onto the Terminal window** — this pastes the path for you — and
press Enter:

```bash
cd /path/to/orf
```

Confirm you're in the right place:

```bash
ls
```

You should see `main.py`, `nback.py`, `requirements.txt`, and `slides`.

### Step 4 — Create a virtual environment and install the packages

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note the macOS activation command is `source .venv/bin/activate` — **not**
`.venv\Scripts\activate`, which is the Windows form shown in some of our other
guides.

Once activated, your Terminal prompt starts with `(.venv)`. Installing takes a
minute or two.

> This installs `pygame` plus `selenium`, `undetected-chromedriver` and
> `webdriver-manager`. The N-Back task itself is fully offline and no longer
> uses a browser, but `main.py` still imports those three at startup, so they
> must be installed or the app won't launch.

### Step 5 — Run it

```bash
python main.py
```

The app opens **fullscreen** and shows the first instruction slide. Press
**Space**, **Enter**, or **→** to start a test. Press **Esc** on a slide to
quit.

Every time you come back to it later, you only need Steps 3 and 5, plus the
activate line:

```bash
cd /path/to/orf
source .venv/bin/activate
python main.py
```

### If something goes wrong

| Message | Fix |
| --- | --- |
| `command not found: python3` | Python isn't installed — redo Step 1. |
| `No such file or directory: requirements.txt` | You're in the wrong folder — redo Step 3. |
| `No images found in slides folder!` | The `slides` folder is missing or not next to `main.py`. |
| `ModuleNotFoundError: No module named 'pygame'` | The venv isn't active — run `source .venv/bin/activate` again. |
| The window opens but the keyboard does nothing | Click once on the app window so it has focus. |
| macOS blocks the app / asks about keyboard access | System Settings → Privacy & Security → **Input Monitoring** and **Accessibility** → enable **Terminal**. |

> **Note:** [make-exe.bat](../make-exe.bat) builds a Windows `.exe` and cannot
> be used on the Mac. On macOS you run it from Terminal as shown above.

---

## 3. Requirements on Laptop B (the ThoughtTech machine)

Do this **every session**, before you start pressing Space on the Mac:

1. **ThoughtTech must be running**, with the recording session open and live
   (i.e. the signal is actually being recorded, not just the app sitting on a
   start screen).
2. **ThoughtTech must be the top window on the desktop** — click on its window
   once so its title bar is highlighted and it is in front of everything else.
3. **Do not minimise it, and do not click on any other window afterwards.**
   If you click on File Explorer, a browser, Notepad, or anything else, the
   Space presses go to *that* program instead and no marker is created.
4. **Turn off the screen saver, sleep, and lock screen** on Laptop B for the
   duration of the session (Settings → System → Power & battery → Screen and
   sleep → set all to *Never*). If the screen locks, ThoughtTech loses focus
   and markers stop.
5. Verify manually first: press Space **on Laptop B's own keyboard** and
   confirm a marker appears. If that doesn't work, the problem is in
   ThoughtTech's own configuration, not in the link between the laptops —
   fix that first before continuing.

> Quick sanity check: if a marker appears when you press Space directly on
> Laptop B, but not when you press Space on the Mac, then Laptop B is fine and
> the problem is purely the missing link between the two machines — see below.

---

## 4. Connecting the two laptops

Pick **one** of the options below. Option A is the recommended one.

### Option A — Remote Desktop from the Mac (recommended)

You open Laptop B's desktop in a window on your Mac. Anything you type into
that window is delivered to Laptop B, exactly as if you were typing on its own
keyboard — so Space creates a marker.

**On Laptop B (Windows), enable Remote Desktop once:**

1. Windows Settings → **System** → **Remote Desktop** → turn it **On**.
   (This requires Windows Pro/Enterprise. If Laptop B is Windows Home, the
   Remote Desktop option is not available — use Option B instead.)
2. Note the PC name shown there, and find its IP address:
   open Command Prompt and run:

   ```
   ipconfig
   ```

   Write down the **IPv4 Address** (something like `192.168.1.2`).
3. Note the Windows **username** and **password** you use to log in — you will
   need them from the Mac.

**On your Mac:**

1. Install **Windows App** (formerly "Microsoft Remote Desktop") from the Mac
   App Store — it is free.
2. Open it → **Add PC** → enter Laptop B's IP address → add the username and
   password → connect.
3. When Laptop B's desktop appears on your Mac, click **inside that window**,
   then bring **ThoughtTech** to the front inside it.
4. Now press Space with that Remote Desktop window focused on your Mac.
   The marker should appear.

**Both laptops must be on the same network** for this. Either:

- Connect both to the same Wi-Fi network, **or**
- Connect them with a single **Ethernet cable** directly between the two
  laptops (use a USB-C-to-Ethernet adapter on the Mac if it has no Ethernet
  port). A direct Ethernet cable *does* work — unlike a USB cable — because
  Ethernet is a real network link. With a direct cable, each machine gives
  itself an address automatically after a moment; run `ipconfig` on Windows
  again to see the new address to connect to.

> ⚠️ **Important limitation of this option:** while you are pressing Space into
> the Remote Desktop window, your Mac's own interface window is *not* focused,
> so **the N-Back app on the Mac will not receive those keypresses**. You can
> only send Space to one of the two at a time. If you need a single Space press
> to be seen by both the Mac app and ThoughtTech, use Option C.

### Option B — Share one keyboard across both laptops

Software like **Synergy** or **Barrier**/**Input Leap** lets one keyboard and
mouse control two computers over the network — you move the cursor to the edge
of the Mac's screen and it "crosses over" to Laptop B.

1. Install the software on **both** laptops (Mac = server, Windows = client).
2. Configure the Mac as the server and add Laptop B to the right (or left) of
   the Mac's screen in the layout.
3. On the Mac, grant the app **Accessibility** and **Input Monitoring**
   permissions: System Settings → Privacy & Security → Accessibility /
   Input Monitoring → enable the app.
4. Move the cursor across onto Laptop B's screen, click ThoughtTech to focus
   it, then press Space.

Same limitation as Option A: at any moment the keyboard is going to **one**
machine, not both.

### Option C — Have the interface send the marker automatically (best long-term)

The proper fix is for the interface on the Mac to send the marker to
ThoughtTech itself, so you press Space **once**, on the Mac, and both the
N-Back app and ThoughtTech respond.

This is a code change, not something you can configure. Options, roughly in
order of reliability:

1. **A hardware trigger / parallel-port or serial marker box** into
   ThoughtTech's trigger input — the standard approach in psychophysiology,
   and the only one with sub-millisecond timing accuracy.
2. **A small helper program running on Laptop B** that listens on the network;
   the Mac app sends it a message on each Space press, and the helper
   synthesises a Space keypress into the focused ThoughtTech window. This is
   what [main.py](main.py) prototypes,
   but note that script is Windows-only (it uses `mstsc`, `cmdkey`, and
   `ctypes.windll`) — it cannot run on the Mac as-is.
3. **ThoughtTech's own API / marker input**, if the version in use exposes one.

Tell us which of these is available on your ThoughtTech licence and hardware,
and we can implement it.

---

## 5. Timing accuracy — please read

Every option above sends the marker over a **network**, which adds a delay
between the moment you press Space on the Mac and the moment the marker lands
in the signal. Typically this is a few milliseconds on a direct cable and tens
of milliseconds over Wi-Fi, and it is **not constant** — it varies from press
to press.

Also, the two laptops' **clocks are not synchronised**, so timestamps recorded
on the Mac and marker positions recorded on Laptop B cannot be compared
directly without a correction.

If your analysis needs precise event timing:

- Prefer a **direct Ethernet cable** over Wi-Fi.
- Prefer **Option C.1 (hardware trigger)** over any software method.
- See [WINRM_SETUP.md](WINRM_SETUP.md)
  or [SSH_SETUP.md](SSH_SETUP.md) for
  enabling a remote clock check on Laptop B, so the offset between the two
  clocks can be measured.

---

## 6. Checklist before each session

- [ ] Mac: interface installed and confirmed to run on its own (section 2).
- [ ] Both laptops on the same network (same Wi-Fi, or joined by an Ethernet cable — **not** USB).
- [ ] Laptop B: ThoughtTech running, recording live.
- [ ] Laptop B: ThoughtTech is the frontmost window.
- [ ] Laptop B: sleep / screen saver / lock screen disabled.
- [ ] Verified: Space on Laptop B's own keyboard creates a marker.
- [ ] Mac: Remote Desktop (or keyboard-sharing) window open and focused on ThoughtTech.
- [ ] Verified: one Space press from the Mac creates one marker.

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No marker from the Mac, but Space on Laptop B works | No real link between the laptops | Set up Option A or B. USB alone does nothing. |
| No marker even on Laptop B's own keyboard | ThoughtTech isn't focused, or isn't configured for keyboard markers | Click the ThoughtTech window; check its marker/keyboard settings. |
| Worked for a while, then stopped | Laptop B's screen locked, or another window took focus | Disable sleep/lock; click ThoughtTech again. |
| Can't connect over Remote Desktop | Wrong IP, different networks, Windows firewall, or Windows Home edition | Re-check `ipconfig`; allow Remote Desktop through the firewall; use Option B on Windows Home. |
| Mac's own N-Back app stops responding to Space | Focus is on the Remote Desktop window, not the app | Expected — see the limitation note in Option A; Option C is the real fix. |
| Markers appear but are late or jittery | Network delay | Use a direct Ethernet cable, or move to a hardware trigger (Option C.1). |
