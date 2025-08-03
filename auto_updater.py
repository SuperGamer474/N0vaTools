# updater.py

import urllib.request
import json
import sys
import os
import tempfile
import hashlib
import subprocess

def auto_update():
    """
    1. Fetches the latest release info from GitHub
    2. Downloads N0vaTools.exe asset into the same folder but with a temp name
    3. If hashes differ:
       • Writes an update.bat that deletes the old EXE, starts the new one, then self-deletes
       • Launches update.bat and exits
    4. Cleans up if already up-to-date
    """
    try:
        # ── 1. GitHub API call ─────────────────────────────────────────────────────
        api_url = "https://api.github.com/repos/SuperGamer474/N0vaTools/releases/latest"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "N0vaTools-Updater",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req) as resp:
            release_info = json.load(resp)

        # ── 2. Locate the EXE asset ─────────────────────────────────────────────────
        assets = release_info.get("assets", [])
        exe_asset = next((a for a in assets if a.get("name") == "N0vaTools.exe"), None)
        if not exe_asset:
            print("⚠️ Couldn’t find N0vaTools.exe in the latest release!")
            return

        download_url = exe_asset["browser_download_url"]
        base_dir     = os.path.dirname(sys.executable)
        old_name     = os.path.basename(sys.executable)

        # ── 3. Download into a temp file alongside the old EXE ────────────────────────
        fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=base_dir)
        os.close(fd)
        print(f"🔽 Downloading new EXE to: {tmp_path}")
        urllib.request.urlretrieve(download_url, tmp_path)

        # ── 4. SHA-256 hash helper ───────────────────────────────────────────────────
        def file_hash(path):
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()

        # ── 5. Compare old vs new ───────────────────────────────────────────────────
        old_hash = file_hash(sys.executable)
        new_hash = file_hash(tmp_path)
        if new_hash != old_hash:
            print("✨ New update found! Installing… ✨")

            # ── 6. Write the batch updater ────────────────────────────────────────────
            bat_path = os.path.join(base_dir, "update.bat")
            new_name = os.path.basename(tmp_path)
            bat_contents = f"""
@echo off
echo 🔄 Running updater in: %cd%
timeout /t 2 /nobreak >nul
echo 🗑️  Deleting old: {old_name}
del "{old_name}"
echo 🚀 Starting new EXE: {new_name}
start "" "{new_name}"
echo 🧹 Cleaning up updater…
del "%~f0"
"""
            with open(bat_path, "w") as bat:
                bat.write(bat_contents.strip())

            # ── 7. Launch the updater script, then exit this process ────────────────
            subprocess.Popen(
                ["cmd", "/c", f'"{bat_path}"'],
                cwd=base_dir,
                shell=False
            )
            sys.exit()

        else:
            # ── No update needed ────────────────────────────────────────────────────
            print("🚀 Already up to date!")
            os.remove(tmp_path)

    except Exception as e:
        print(f"❌ Update failed: {e}")
