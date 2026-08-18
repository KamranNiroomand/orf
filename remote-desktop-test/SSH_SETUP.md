# Enabling Remote Clock Check (SSH) on This Computer

This is an alternative to the WinRM method (see `WINRM_SETUP.md`) — only one
of the two is needed. We need to compare this computer's clock with the
technician's computer clock, so we can tell if the device's timing is off.
To do that, we need **OpenSSH Server** turned on here.

Please follow these steps **on this computer**, logged in as Administrator.

## Step 1 — Check if it's already enabled

Open **PowerShell as Administrator** (right-click Start → "Windows PowerShell (Admin)"
or "Terminal (Admin)"), then run:

```powershell
Get-Service sshd
```

- If **Status** shows `Running` → SSH is likely already on. Skip to Step 4 to confirm.
- If you get an error saying the service doesn't exist → continue to Step 2.
- If **Status** shows `Stopped` → skip to Step 3.

## Step 2 — Install OpenSSH Server (if not installed)

Still in the same Administrator PowerShell window, run:

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
```

Wait for it to finish (may take a minute).

## Step 3 — Start the SSH service and enable auto-start

```powershell
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
```

Make sure the firewall allows it (this is usually created automatically,
but run this to be sure):

```powershell
New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH SSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22
```

## Step 4 — Confirm it worked

```powershell
Get-Service sshd
```

You should see:

```
Status   Name    DisplayName
------   ----    -----------
Running  sshd    OpenSSH SSH Server
```

That's it — no further changes are needed on this computer.

## What this is for

Once this is enabled, we can remotely read this computer's exact time from
our side (read-only, no changes to your system), to check whether its clock
matches ours within an acceptable margin. This does **not** give us any
access to your files, desktop, or applications beyond running that one
time-check command.

## Notes

- This works on Windows 10 (1809+) and Windows 11, including Home editions.
  On older Windows (e.g. Windows 7), OpenSSH Server must be installed
  manually from a separate installer — let us know if that's the case and
  we'll send different instructions.
- The first time we connect, you may be asked to accept the connection
  (SSH host key prompt) — this is normal and only happens once.
