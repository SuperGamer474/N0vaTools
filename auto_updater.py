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
    1. Find our running EXE path
    2. Hit GitHub API for latest release
    3. Download new EXE into temp file beside the real one
    4. If SHA256 differs:
         - Write update.bat to delete old, rename temp→real, start real, delete itself
         - Launch that .bat and immediately exit this process
       Else:
         - Delete the temp EXE (no update needed)
    """
    try:
        # 1️⃣ Determine app path (frozen or script)
        if getattr(sys, "frozen", False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(sys.argv[0])

        base_dir = os.path.dirname(app_path)
        real_name = os.path.basename(app_path)

        # 2️⃣ GitHub API for latest release
        api_url = "https://api.github.com/repos/SuperGamer474/N0vaTools/releases/latest"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "N0vaTools-Updater",
            "Accept": "application/vnd.github.v3+json"
        })
        with urllib.request.urlopen(req) as resp:
            info = json.load(resp)

        exe_asset = next((a for a in info.get("assets", []) if a.get("name") == real_name), None)
        if not exe_asset:
            print("⚠️ Couldn’t find the EXE in the latest release!")
            return

        url = exe_asset["browser_download_url"]

        # 3️⃣ Download into temp file
        fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=base_dir)
        os.close(fd)
        urllib.request.urlretrieve(url, tmp_path)

        # 4️⃣ Compare hashes
        def hash256(p):
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()

        if hash256(tmp_path) != hash256(app_path):
            # 🔄 New version! Write the batch updater
            bat = os.path.join(base_dir, "update.bat")
            tmp_name = os.path.basename(tmp_path)
            bat_content = f"""@echo off
del "{real_name}"
ren "{tmp_name}" "{real_name}"
start "" "{real_name}"
del "%~f0"
"""
            with open(bat, "w", encoding="utf-8", errors="ignore") as f:
                f.write(bat_content)

            # 🚀 Launch updater and kill current process to free the EXE lock
            subprocess.Popen(['cmd', '/c', bat], cwd=base_dir, shell=False)
            os._exit(0)

        else:
            # ✅ Up-to-date: ditch the temp EXE
            os.remove(tmp_path)

    except Exception as e:
        print(f"❌ Update failed: {e}")
