import os
import sys
import time
import hashlib
import tempfile
import subprocess
import urllib.request
import json
from colorama import init, Fore, Style
import msvcrt
import zipfile
import winreg
import ctypes
init()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_password(prompt="Please enter the password: "):
    print(prompt, end='', flush=True)
    password = ""
    while True:
        char = msvcrt.getch()
        if char in [b'\r', b'\n']:  # Enter key
            print('')
            break
        elif char == b'\x08':  # Backspace
            if len(password) > 0:
                password = password[:-1]
                print('\b \b', end='', flush=True)
        elif char == b'\x03':  # Ctrl+C
            raise KeyboardInterrupt
        else:
            password += char.decode('utf-8')
            print('*', end='', flush=True)
    return password

def print_main():
    clear_terminal()
    print(Fore.GREEN + r""" _   _            _            _____           _ 
| | | | __ _  ___| | _____ _ _|_   _|__   ___ | |
| |_| |/ _` |/ __| |/ / _ \ '__|| |/ _ \ / _ \| |
|  _  | (_| | (__|   <  __/ |   | | (_) | (_) | |
|_| |_|\__,_|\___|_|\_\___|_|   |_|\___/ \___/|_|
    """ + Style.RESET_ALL)

def arrow_menu(options):
    # Hide the cursor
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()

    # Print the header and the initial menu
    print_main()
    for i, option in enumerate(options):
        prefix = "➤ " if i == 0 else "  "
        colour = Fore.YELLOW if i == 0 else Fore.WHITE
        print(f"{Fore.GREEN if i == 0 else ''}{prefix}{colour}{option}{Style.RESET_ALL}")

    index = 0
    # How many lines we need to move up to overwrite our menu:
    menu_height = len(options)

    try:
        while True:
            key = msvcrt.getch()
            if key == b'\xe0':        # Arrow keys prefix
                key2 = msvcrt.getch()
                if key2 == b'H':       # Up
                    index = (index - 1) % len(options)
                elif key2 == b'P':     # Down
                    index = (index + 1) % len(options)
                else:
                    continue
            elif key == b'\r':        # Enter
                break
            else:
                continue

            # Move cursor up to the first menu line
            sys.stdout.write(f"\x1b[{menu_height}A")
            # Re‑print the menu with the new selection
            for i, option in enumerate(options):
                prefix = "➤ " if i == index else "  "
                colour = Fore.YELLOW if i == index else Fore.WHITE
                sys.stdout.write(f"\r")  # return to start of line
                sys.stdout.write(" " * 80)  # clear old text (assumes max width <80)
                sys.stdout.write("\r")  # back again
                sys.stdout.write(f"{Fore.GREEN if i == index else ''}{prefix}{colour}{option}{Style.RESET_ALL}\n")
            sys.stdout.flush()
    finally:
        # Show the cursor again
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

    return index

def auto_update():
    """
    Downloads the latest hackertool.exe from the GitHub Releases API,
    compares SHA256 hashes, and if different,
    swaps in the new version and restarts.
    """
    # 1️⃣ Query the GitHub API for the latest release
    api_url = "https://api.github.com/repos/SuperGamer474/hackertool-simulator/releases/latest"
    req = urllib.request.Request(api_url, headers={
        "User-Agent": "HackerTool-Updater",
        "Accept": "application/vnd.github.v3+json"
    })
    with urllib.request.urlopen(req) as resp:
        release_info = json.load(resp)

    # 2️⃣ Find the hackertool.exe asset
    assets = release_info.get("assets", [])
    exe_asset = next((a for a in assets if a.get("name") == "hackertool.exe"), None)
    if not exe_asset:
        print("⚠️ There was an error while updating!")
        return

    download_url = exe_asset["browser_download_url"]

    # 3️⃣ Download remote EXE to a temp file
    local_exe = sys.executable  # current running .exe
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=os.path.dirname(local_exe))
    os.close(tmp_fd)
    urllib.request.urlretrieve(download_url, tmp_path)

    # 4️⃣ Hash helper
    def file_hash(path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    # 5️⃣ Compare hashes
    if file_hash(tmp_path) != file_hash(local_exe):
        print("✨ Installing new update... ✨")
        base_dir = os.path.dirname(local_exe)
        new_name = os.path.basename(tmp_path)
        old_name = os.path.basename(local_exe)
        bat_path = os.path.join(base_dir, "update.bat")

        # 6️⃣ Write batch script to swap and restart
        bat_content = f"""
@echo off
timeout /t 2 /nobreak >nul
del "{old_name}"
ren "{new_name}" "{old_name}"
start "" "{old_name}"
del "%~f0"
"""
        with open(bat_path, "w") as bat:
            bat.write(bat_content.strip())

        # 7️⃣ Launch the updater and exit
        subprocess.Popen(["cmd", "/c", bat_path], cwd=base_dir)
        sys.exit()
    else:
        # 🚀 Already up to date
        os.remove(tmp_path)

# ========= Hacking Terminal =========
def loadHackingTerminal():

    # initialise colour mapping
    colour_map = {
        'red': Fore.RED,
        'orange': Fore.LIGHTRED_EX,
        'yellow': Fore.YELLOW,
        'green': Fore.GREEN,
        'blue': Fore.BLUE,
        'purple': Fore.MAGENTA,
        'pink': Fore.LIGHTMAGENTA_EX,
        'white': Fore.WHITE,
        'black': Fore.BLACK,
        'grey': Fore.LIGHTBLACK_EX,
        'default': Style.RESET_ALL
    }
    # use mutable dict to allow wrapper access to current colour
    colour_state = {'code': Style.RESET_ALL}

    class ColourWriter:
        def __init__(self, orig):
            self.orig = orig
        def write(self, text):
            # prefix and reset to ensure all text is coloured
            self.orig.write(colour_state['code'] + text + Style.RESET_ALL)
        def flush(self):
            self.orig.flush()
        def isatty(self):
            return getattr(self.orig, 'isatty', lambda: False)()

    # wrap stdout and stderr
    sys.stdout = ColourWriter(sys.stdout)
    sys.stderr = ColourWriter(sys.stderr)

    def coloured_input(prompt):
        # write prompt & flush so it actually appears
        sys.stdout.write(colour_state['code'] + prompt)
        sys.stdout.flush()

        buffer = ''
        while True:
            ch = msvcrt.getwch()  # gets a str
            if ch == '\r':  # Enter
                sys.stdout.write('\n')
                sys.stdout.flush()
                break

            elif ch == '\x08':  # Backspace
                if buffer:
                    buffer = buffer[:-1]
                    # move cursor back, overwrite with space, move back
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()

            else:
                buffer += ch
                # echo the character in the current colour, then flush
                sys.stdout.write(colour_state['code'] + ch)
                sys.stdout.flush()

        return buffer.strip()

    def ensure_home():
        home = os.path.join(
            os.environ.get('USERPROFILE', os.path.expanduser('~')),
            'hacking-terminal'
        )
        os.makedirs(home, exist_ok=True)
        return home

    clear_terminal()
    home = ensure_home()
    cwd = home

    while True:
        # build Windows-style prompt with backslashes only
        rel = os.path.relpath(cwd, home)
        if rel == '.':
            display = "~\\"
        else:
            display = "~\\" + rel.replace("/", "\\") + "\\"
        # get coloured input including echo
        try:
            line = coloured_input(f"{display}> ")
        except (EOFError, KeyboardInterrupt):
            sys.stdout.write('\n')
            break

        if not line:
            continue

        parts = line.split(None, 1)
        cmd = parts[0].lower()

        # colour command
        if cmd in ('colour', 'color'):
            if len(parts) < 2:
                sys.stdout.write("Usage: colour <colorname>\n")
            else:
                choice = parts[1].strip().lower()
                if choice in colour_map:
                    colour_state['code'] = colour_map[choice]
                else:
                    sys.stdout.write(f"Unknown colour '{choice}'. Available: {', '.join(colour_map.keys())}\n")
            continue

        # exit or quit
        if cmd in ('exit', 'quit'):
            # === RESET terminal state after exit ===
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            colour_state['code'] = Style.RESET_ALL
            print(Style.RESET_ALL, end='')  # ensure it visually resets the terminal
            break

        # cd command
        if cmd == 'cd':
            target = parts[1] if len(parts) > 1 else ''
            if target in ('', '~', '~/'):
                cwd = home
            else:
                if target.startswith('~/') or target.startswith('~\\'):
                    path = os.path.join(home, target[2:].lstrip("\\/"))
                else:
                    path = os.path.join(cwd, target)
                real = os.path.abspath(path)
                if os.path.isdir(real) and real.startswith(home):
                    cwd = real
                else:
                    sys.stdout.write(f"cd: no such file or directory: {target}\n")
            continue

        # mkdir command
        if cmd == 'mkdir':
            if len(parts) < 2 or not parts[1].strip():
                sys.stdout.write("mkdir: missing operand\n")
                continue
            target = parts[1].strip()
            if target.startswith('~/') or target.startswith('~\\'):
                path = os.path.join(home, target[2:].lstrip("\\/"))
            else:
                path = os.path.join(cwd, target)
            try:
                os.makedirs(path)
            except FileExistsError:
                sys.stdout.write(f"mkdir: cannot create directory '{target}': File exists\n")
            except Exception as e:
                sys.stdout.write(f"mkdir: cannot create directory '{target}': {e}\n")
            continue

        # scan command
        if cmd == 'scan':
            if len(parts) < 2:
                sys.stdout.write("Usage: scan <code>\n")
                continue
            code = parts[1].strip()
            
            import socket
            import ipaddress
            import concurrent.futures
            from tqdm import tqdm
            
            def get_local_ip():
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    return s.getsockname()[0]
                except Exception:
                    sys.stdout.write("⚠️ Couldn't auto-detect IP. Please check your network.\n")
                    return None
                finally:
                    s.close()

            def ping(ip: str) -> bool:
                cmd = ["ping", "-n", "1", "-w", "1000", ip]
                res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return res.returncode == 0

            def get_hostname(ip: str) -> str:
                try:
                    name = socket.gethostbyaddr(ip)[0]
                    return name.lower()
                except Exception:
                    return ""

            local_ip = get_local_ip()
            if not local_ip:
                continue
            
            subnet = ipaddress.ip_network(f"{local_ip}/24", strict=False)
            hosts = [str(h) for h in subnet.hosts()]
            total_hosts = len(hosts)
            sys.stdout.write(f"Scanning WiFi for '{code}'...\n")

            found = False
            with concurrent.futures.ThreadPoolExecutor(max_workers=total_hosts) as executor:
                future_to_ip = {executor.submit(ping, ip): ip for ip in hosts}
                with tqdm(total=total_hosts, unit="ip", desc="Scanning", ascii=False, leave=False) as pbar:
                    for future in concurrent.futures.as_completed(future_to_ip):
                        ip = future_to_ip[future]
                        pbar.update(1)
                        try:
                            alive = future.result()
                        except Exception:
                            continue

                        if alive:
                            name = get_hostname(ip)
                            if name and code in name:
                                found = True
                                # Clear the progress bar
                                sys.stdout.write("\r" + " " * 80 + "\r")
                                sys.stdout.write(f"🎉 Success! {ip} → {name}!\n")
                                pbar.close()
                                sys.stdout.flush()
                                break
                if not found:
                    print(f"😅 '{code}' was not found!")
            continue

        # unknown command
        sys.stdout.write(f"{cmd}: command not found\n")


# === Program start ===
clear_terminal()
passw = input_password()

if passw == "hack1ng":
    updatess = input("Do you want to check for updates? Y/n ")
    if updatess.lower() == "y":
        auto_update()
else:
    sys.exit()

# === Main menu ===
while True:
    choice = arrow_menu([
        "Install apps",
        "UEN v1",
        "Hacking Terminal",
        "Quit"
    ])

    if choice == 0:
        sub = arrow_menu(["Install Java 21", "Back"] )
        if sub == 0:
            # Java installer logic
            user_profile = os.environ['USERPROFILE']
            install_dir = os.path.join(user_profile, 'Java21')
            zip_path     = os.path.join(install_dir, 'java21.zip')
            url          = "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.zip"

            os.makedirs(install_dir, exist_ok=True)
            print("\n📥 Downloading...")
            urllib.request.urlretrieve(url, zip_path)

            print("📦 Installing...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            os.remove(zip_path)

            extracted_dir = next(os.scandir(install_dir)).path
            bin_path      = os.path.join(extracted_dir, "bin")

            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0,
                                     winreg.KEY_READ | winreg.KEY_WRITE) as key:
                    current_path, reg_type = winreg.QueryValueEx(key, "Path")
                    if bin_path.lower() not in current_path.lower():
                        new_path = current_path + ";" + bin_path
                        winreg.SetValueEx(key, "Path", 0, reg_type, new_path)
                ctypes.windll.user32.SendMessageTimeoutW(
                    0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None
                )
                print("✅ Java Successfully Installed!")
            except Exception as e:
                print(f"⚠️ Failed to update PATH: {e}")
            time.sleep(3)

    elif choice == 1:
        print_main()
        print("UEN is coming soon...")
        time.sleep(3)

    elif choice == 2:
        print_main()
        print("Loading Hacking Terminal...")
        time.sleep(2)
        loadHackingTerminal()
        time.sleep(3)

    elif choice == 3:
        print_main()
        print("Closing HackerTool...")
        time.sleep(2)
        clear_terminal()
        sys.exit()
