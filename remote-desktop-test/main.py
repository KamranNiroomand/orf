import ctypes
import subprocess
import time
import datetime

import pyautogui
import pygetwindow as gw


# ================= CONFIG =================
RDP_ADDRESS = "192.168.1.2"
RDP_PORT = 3389  # change if the remote listens on a non-default RDP port
USERNAME = "pc2"
PASSWORD = "123"

WAIT_AFTER_LOGIN = 15

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3
# ==========================================


user32 = ctypes.windll.user32

# mstsc / cmdkey want "host:port" only when the port is non-default.
RDP_TARGET = RDP_ADDRESS if RDP_PORT == 3389 else f"{RDP_ADDRESS}:{RDP_PORT}"


def force_foreground(hwnd):
    """
    Reliably bring a window to the foreground on Windows.

    pygetwindow's .activate() silently fails a lot because Windows blocks
    SetForegroundWindow for background processes. The workaround is to attach
    our thread's input to the target window's thread first.
    """
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE

    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
    tgt_thread = user32.GetWindowThreadProcessId(hwnd, None)

    user32.AttachThreadInput(fg_thread, tgt_thread, True)
    user32.BringWindowToTop(hwnd)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(fg_thread, tgt_thread, False)


def find_rdp_window(timeout=30):
    """Find the mstsc window, waiting until it appears."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for title in (RDP_ADDRESS, "Remote Desktop Connection", "Remote Desktop"):
            windows = gw.getWindowsWithTitle(title)
            if windows:
                return windows[0]
        print("Waiting for RDP window...")
        time.sleep(1)
    raise RuntimeError("RDP window never appeared")


def ensure_rdp_focused(timeout=15):
    """
    Bring the RDP window to the front AND verify it actually got focus.

    This is the critical part: we do NOT send any keystrokes unless the RDP
    window is confirmed to be the active window. Otherwise keys leak into the
    local machine.
    """
    win = find_rdp_window()
    deadline = time.time() + timeout

    while time.time() < deadline:
        force_foreground(win._hWnd)
        time.sleep(0.5)

        active = gw.getActiveWindow()
        if active and win._hWnd == active._hWnd:
            print("RDP window is focused:", active.title)
            return win

        print("RDP not focused yet (active:", active.title if active else None, ")")
        time.sleep(0.5)

    raise RuntimeError(
        "Could NOT focus the RDP window. Aborting so keys don't leak locally."
    )


def open_rdp():
    """
    Store credentials with cmdkey so mstsc auto-logs-in, then launch it.
    This avoids typing username/password into the (unreliable) CredUI dialog.
    """
    print("Storing credentials...")
    # NOTE: cmdkey only STORES the password, it does NOT validate it.
    # mstsc only uses a stored credential when the target is "TERMSRV/<host[:port]>".
    subprocess.run(
        [
            "cmdkey",
            f"/generic:TERMSRV/{RDP_TARGET}",
            f"/user:{USERNAME}",
            f"/pass:{PASSWORD}",
        ],
        capture_output=True,
    )

    print("Opening RDP to", RDP_TARGET, "...")
    subprocess.Popen(["mstsc", f"/v:{RDP_TARGET}"])


def verify_connected():
    """
    A successful RDP session shows the host address in the mstsc title bar.
    If we can't find such a window, the login almost certainly failed
    (wrong password, host down, etc.) and we must NOT keep going.
    """
    if not gw.getWindowsWithTitle(RDP_ADDRESS):
        raise RuntimeError(
            f"Not connected to {RDP_ADDRESS}. "
            "Login likely failed (wrong password / host unreachable / cert prompt)."
        )
    print("Connection to", RDP_ADDRESS, "confirmed.")


def send_text():
    print("Waiting for desktop...")
    time.sleep(WAIT_AFTER_LOGIN)

    verify_connected()
    ensure_rdp_focused()

    text = f"Hello from Python {datetime.datetime.now():%H:%M:%S}"

    print("Sending SPACE...")
    pyautogui.press("space")
    time.sleep(1)

    #print("Sending text...")
    #pyautogui.write(text, interval=0.02)

    print("Done.")


def close_rdp():
    subprocess.run(["taskkill", "/IM", "mstsc.exe", "/F"], capture_output=True)
    subprocess.run(["cmdkey", f"/delete:TERMSRV/{RDP_TARGET}"], capture_output=True)


def main():
    open_rdp()
    send_text()

    input("Press ENTER to close RDP...")
    close_rdp()


if __name__ == "__main__":
    main()
