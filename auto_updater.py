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
    1. Fetch latest GitHub release metadata
    2. Download N0vaTools.exe into a temp file alongside the current EXE
    3. If hashes differ:
       - Write update.bat that deletes old EXE, starts the new one, then self-deletes
       - Launch update.bat and exit current process
    4. Clean up temp if already up-to-date
    """
    try:
        # ── 1. Query GitHub API ────────────────────────────────────────────────────
        api_url = "https://api.github.com/repos/SuperGamer474/N0vaTools/releases/latest"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "N0vaTools-Updater",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req) as resp:
            release_info = json.load(resp)

        # ── 2. Find the EXE asset ───────────────────────────────────────────────────
        assets = release_info.get("assets", [])
        exe_asset = next((a for a in assets if a.get("name") == "N0vaTools.exe"), None)
        if not exe_asset:
            print("⚠️ Couldn’t find N0vaTools.exe in the latest release!")
            return

        download_url = exe_asset["browser_download_url"]
        base_dir     = os.path.dirname(sys.executable)
        old_name     = os.path.basename(sys.executable)

        # ── 3. Download remote EXE into temp file ──────────────────────────────────
        fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=base_dir)
        os.close(fd)
        urllib.request.urlretrieve(download_url, tmp_path)

        # ── 4. Hash helper ─────────────────────────────────────────────────────────
        def file_hash(path):
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()

        # ── 5. Compare old vs new ─────────────────────────────────────────────────
        if file_hash(tmp_path) != file_hash(sys.executable):
            # New update! Write batch script to swap & launch
            bat_path = os.path.join(base_dir, "update.bat")
            new_name = os.path.basename(tmp_path)
            bat_contents = f"""@echo off
del "{old_name}"
start "" "{new_name}"
del "%~f0"
"""
            with open(bat_path, "w", encoding="utf-8", errors="ignore") as bat:
                bat.write(bat_contents)

            # Launch the updater batch file (with proper quoting) and exit
            subprocess.Popen(f'cmd /c "{bat_path}"', cwd=base_dir, shell=True)
            sys.exit()

        else:
            # Already up-to-date: just clean up
            os.remove(tmp_path)

    except Exception as e:
        print(f"❌ Update failed: {e}")