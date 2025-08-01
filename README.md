# 🛠️ HackerTool

**HackerTool** is a Windows-based terminal utility written in Python. It includes a stylized menu system, an interactive "Hacking Terminal" shell, built-in app installers (e.g., Java), and a self-update feature using GitHub Releases.

---

##  😎 Install HackerTool
- Download the latest release [here](https://github.com/SuperGamer474/hackertool-simulator/releases/latest)!

---

## 📦 Features

- 🎯 **Arrow-Key Menu Navigation** with Color Output  
- 🔐 **Password Protection** (Default: `hack1ng`)  
- 🔄 **Auto-Updater** that checks for the latest executable via GitHub  
- 💻 **Custom Command-Line Shell** (`Hacking Terminal`) with:
  - Windows-style prompt
  - Built-in `cd`, `mkdir`, `scan`, and `colour` commands
  - Command output with dynamic ANSI color wrapping
- ☕ **Java 21 Installer** with PATH auto-updating  

---

## 🚀 Getting Started

### 📝 Usage

1. **Run the compiled EXE**

   Unfortunately, running the uncompiled script will not work due to the auto-updating system.

   The script prompts for a password (`hack1ng`) before proceeding.

3. **Navigate the menu** using ↑ ↓ and **select** with **Enter**.

4. Available menu options:
   - **Install apps** → Install Java 21
   - **UEN v1** → Coming Soon
   - **Hacking Terminal** → Launch interactive shell
   - **Quit** → Exit HackerTool

---

## 🧠 Hacking Terminal Commands

- `cd [dir]` — Change directory (only within `~/hacking-terminal`)
- `mkdir <name>` — Make a new directory
- `scan <name>` — Scans your local network for devices whose hostnames contain `<name>`.
- `colour <name>` — Change prompt/output color  
  Available colors: `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `white`, `black`, `grey`, `default`
- `exit` / `quit` — Exit terminal

---

## 🔄 Auto-Updating

If a newer `hackertool.exe` is published on the linked GitHub repository, the app will:
- Download the EXE to a temp location
- Verify it with SHA256
- Replace the running executable with the new one
- Restart automatically

**GitHub Release API endpoint:**
```
https://api.github.com/repos/SuperGamer474/hackertool-simulator/releases/latest
```

---

## ☕ Java 21 Installer

Downloads Java 21 from Oracle, extracts it to `%userprofile%\Java21`, and adds it to the system `Path` via the Windows Registry.

---

## 📁 Directory Structure

```
C:\Users\<user>\
└── hacking-terminal\
    ├── ... (user files created in terminal)
└── Java21\
    └── jdk-21\ (Java install)
```

---

## ⚠️ Warning

- This is Windows-only due to `msvcrt`, `winreg`, and `ctypes.windll` usage

---

## 🙋 Author

Developed by [SuperGamer474](https://supergamer474.rf.gd)
