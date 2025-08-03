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
    Auto-update N0vaTools.exe in-place:
     1. Fetch latest release metadata from GitHub
     2. Download new EXE beside the old one (same folder)
     3. If hashes differ:
        - Write a minimal batch script to delete the old EXE,
          start the new EXE, then delete itself
        - Launch that batch via cmd and immediately terminate
     4. If up-to-date, just delete the temp file
    """
    try:
        # ── 1. GitHub release lookup ───────────────────────────────────────────────
        api_url = "https://api.github.com/repos/SuperGamer474/N0vaTools/releases/latest"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "N0vaTools-Updater",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req) as resp:
            release_info = json.load(resp)

        # ── 2. Find our EXE asset ───────────────────────────────────────────────────
        assets = release_info.get("assets", [])
        exe_asset = next((a for a in assets if a.get("name") == "N0vaTools.exe"), None)
        if not exe_asset:
            print("⚠️ Couldn’t find N0vaTools.exe in the latest release!")
            return

        download_url = exe_asset["browser_download_url"]
        base_dir     = os.path.dirname(sys.executable)
        old_name     = os.path.basename(sys.executable)

        # ── 3. Download new EXE to temp file in same folder ─────────────────────────
        fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=base_dir)
        os.close(fd)
        urllib.request.urlretrieve(download_url, tmp_path)

        # ── 4. Hash comparison ───────────────────────────────────────────────────────
        def file_hash(path):
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()

        if file_hash(tmp_path) != file_hash(sys.executable):
            # ── 5. Write the batch updater ────────────────────────────────────────────
            bat_path = os.path.join(base_dir, "update.bat")
            new_name = os.path.basename(tmp_path)
            bat_contents = f"""@echo off
del "{old_name}"
start "" "{new_name}"
del "%~f0"
"""
            # Write ANSI (default) so Windows cmd can parse it
            with open(bat_path, "w") as bat:
                bat.write(bat_contents)

            # ── 6. Launch the batch and *immediately* terminate this process! ───────
            subprocess.Popen(
                ["cmd", "/c", bat_path],
                cwd=base_dir,
                shell=False,
                close_fds=True
            )
            # os._exit kills the process without cleanup handlers, freeing the EXE file
            os._exit(0)

        else:
            # ── 7. No update needed ─────────────────────────────────────────────────
            os.remove(tmp_path)

    except Exception as e:
        print(f"❌ Update failed: {e}")
