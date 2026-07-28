# Setup Guide

This guide explains how to configure and run this program.

## 1. Configure the settings

Open [main.py](main.py) and edit the values in the `CONFIG` section near the top of the file:

```python
RDP_ADDRESS = "borhan.naptech.ir"   # address of the remote computer
RDP_PORT = 33220                    # RDP port (use 3389 if it's the default)
USERNAME = "pc2"                    # remote login username
PASSWORD = "123"                    # remote login password

WAIT_AFTER_LOGIN = 15               # seconds to wait after login before typing
```

Replace each value with the ones for your own remote computer.

## 2. Set up the Python environment

You need Python installed on your computer first (Python 3.9 or newer is recommended).

Open a terminal in the project folder and run:

```powershell
python -m venv .venv
```

This creates a virtual environment folder named `.venv`.

Next, activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Then install the required packages:

```powershell
pip install -r requirements.txt
```

## 3. Run the program

With the virtual environment activated, run:

```powershell
python main.py
```

The script will:
1. Open a Remote Desktop (RDP) connection using the settings from step 1.
2. Wait for the login to finish.
3. Type a test message into the remote desktop.
4. Ask you to press ENTER before it closes the connection.

## Notes

- Make sure the RDP address, port, username, and password are correct before running, otherwise the connection will fail.
- Do not move the mouse or type on your keyboard while the script is sending text — it needs the remote window to stay focused.
