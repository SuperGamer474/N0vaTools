import urllib.request
import json
import sys
import os
import tempfile
import hashlib
import subprocess

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