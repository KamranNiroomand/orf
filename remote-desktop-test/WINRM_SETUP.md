# Enabling Remote Clock Check (WinRM) on This Computer

We need to compare this computer's clock with the technician's computer clock,
so we can tell if the device's timing is off. To do that accurately, we need
a small Windows feature called **PowerShell Remoting (WinRM)** turned on here.

Please follow these steps **on this computer**, logged in as Administrator.

## Step 1 — Check if it's already enabled

Open **PowerShell as Administrator** (right-click Start → "Windows PowerShell (Admin)"
or "Terminal (Admin)"), then run:

```powershell
Get-Service WinRM
```

- If **Status** shows `Running` → WinRM is likely already on. Skip to Step 3 to confirm.
- If **Status** shows `Stopped` → continue to Step 2.

## Step 2 — Enable WinRM

Still in the same Administrator PowerShell window, run:

```powershell
Enable-PSRemoting -Force
```

This will:
- Start the WinRM service and set it to start automatically.
- Open the required firewall rule.
- You may see a few confirmation prompts — they are answered automatically by `-Force`.

## Step 3 — Confirm it worked

Run:

```powershell
Get-Service WinRM
```

You should see:

```
Status   Name    DisplayName
------   ----    -----------
Running  WinRM   Windows Remote Management (WS-Management)
```

That's it — no further changes are needed on this computer.

## What this is for

Once this is enabled, we can remotely read this computer's exact time from
our side (read-only, no changes to your system), to check whether its clock
matches ours within an acceptable margin. This does **not** give us any
access to your files, desktop, or applications — only the system time.

## Notes

- This works on Windows 7 and later, including Home editions.
- If this computer is not joined to a company domain (i.e., it's on a
  workgroup), let us know after enabling WinRM — we may need to add this
  computer's address to a trusted list on our side before the check works.
