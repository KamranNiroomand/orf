import ctypes
import re
import subprocess
import time
import datetime

import pyautogui
import pygetwindow as gw


# ================= CONFIG =================
RDP_ADDRESS = "192.168.1.2"
RDP_PORT = 3389  # change if the remote listens on a non-default RDP port
USERNAME = "pc1"
PASSWORD = "123456"

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

    # print("Sending text...")
    # pyautogui.write(text, interval=0.02)

    print("Done.")


def close_rdp():
    subprocess.run(["taskkill", "/IM", "mstsc.exe", "/F"], capture_output=True)
    subprocess.run(["cmdkey", f"/delete:TERMSRV/{RDP_TARGET}"], capture_output=True)


def print_ping_latency():
    """
    Ping RDP_ADDRESS and report the network delay in plain language,
    for a non-technical operator calibrating the remote device's timing.
    """
    print("Measuring network delay between this computer and the remote device...")
    result = subprocess.run(
        ["ping", "-n", "4", RDP_ADDRESS],
        capture_output=True,
        text=True,
    )

    times_ms = [int(m) for m in re.findall(r"time[=<](\d+)ms", result.stdout)]

    if not times_ms:
        print(
            "Could not measure network delay (device did not respond). "
            "For accurate calibration, first make sure the device is connected to the network."
        )
        return

    avg_rtt = sum(times_ms) / len(times_ms)
    one_way = avg_rtt / 2

    print(f"Round-trip network delay: about {avg_rtt:.0f} ms")
    print(f"One-way delay (estimated): about {one_way:.0f} ms")
    print(
        "Note: this number is only the network delay, not the clock difference "
        "between the two devices. If your calibration needs higher accuracy than this, "
        "the remote device's clock must be checked separately against an accurate time "
        "source (NTP)."
    )


def print_clock_skew():
    """
    Read the remote machine's exact clock via PowerShell Remoting (WinRM)
    and compare it to our own, printing the difference in seconds.

    Requires WinRM to be enabled on the remote machine first
    (see WINRM_SETUP.md).
    """
    print("Checking remote clock via WinRM...")

    ps_command = (
        f"$s = New-PSSession -ComputerName {RDP_ADDRESS} -Credential "
        f"(New-Object System.Management.Automation.PSCredential('{USERNAME}', "
        f"(ConvertTo-SecureString '{PASSWORD}' -AsPlainText -Force))); "
        f"Invoke-Command -Session $s {{ Get-Date -Format o }}; "
        f"Remove-PSSession $s"
    )

    before = datetime.datetime.now()
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_command],
        capture_output=True,
        text=True,
    )
    after = datetime.datetime.now()

    output = result.stdout.strip()
    if not output:
        print("Could not read the remote clock. Is WinRM enabled? See WINRM_SETUP.md.")
        if result.stderr.strip():
            print(result.stderr.strip())
        return

    try:
        remote_time = datetime.datetime.fromisoformat(output.splitlines()[-1])
    except ValueError:
        print("Unexpected response from remote machine:", output)
        return

    rtt_seconds = (after - before).total_seconds()
    local_midpoint = before + (after - before) / 2
    skew_seconds = (remote_time.replace(tzinfo=None) - local_midpoint).total_seconds()

    print(f"Remote clock is {skew_seconds:+.2f} seconds relative to this computer.")
    print(
        f"(Positive = remote clock is ahead. Margin of error: "
        f"±{rtt_seconds / 2 * 1000:.0f} ms, based on a measured round-trip of "
        f"{rtt_seconds * 1000:.0f} ms for this request.)"
    )


def print_clock_skew_ssh():
    """
    Read the remote machine's exact clock via SSH (OpenSSH Server on Windows)
    and compare it to our own, printing the difference in seconds.

    Requires an SSH server enabled on the remote machine and this machine's
    SSH key (or password) to be accepted.
    """
    print("Checking remote clock via SSH...")

    before = datetime.datetime.now()
    result = subprocess.run(
        [
            "ssh",
            f"{USERNAME}@{RDP_ADDRESS}",
            "powershell", "-NoProfile", "-Command", "Get-Date -Format o",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    after = datetime.datetime.now()

    output = result.stdout.strip()
    if not output:
        print("Could not read the remote clock over SSH. Is the SSH server enabled?")
        if result.stderr.strip():
            print(result.stderr.strip())
        return

    try:
        remote_time = datetime.datetime.fromisoformat(output.splitlines()[-1])
    except ValueError:
        print("Unexpected response from remote machine:", output)
        return

    rtt_seconds = (after - before).total_seconds()
    local_midpoint = before + (after - before) / 2
    skew_seconds = (remote_time.replace(tzinfo=None) - local_midpoint).total_seconds()

    print(f"Remote clock is {skew_seconds:+.2f} seconds relative to this computer.")
    print(
        f"(Positive = remote clock is ahead. Margin of error: "
        f"±{rtt_seconds / 2 * 1000:.0f} ms, based on a measured round-trip of "
        f"{rtt_seconds * 1000:.0f} ms for this request.)"
    )


def main():
    open_rdp()
    send_text()

    input("Press ENTER to close RDP...")
    close_rdp()
    # print_clock_skew()  # uncomment once WinRM is enabled on the remote machine (see WINRM_SETUP.md)
    # print_clock_skew_ssh()  # uncomment once SSH server is enabled on the remote machine


if __name__ == "__main__":
    main()
