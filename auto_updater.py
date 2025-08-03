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
    1. Grab latest release metadata from GitHub.
    2. Download N0vaTools.exe to a temp file in the EXE folder.
    3. If SHA256 differs:
         • Write a robust update.bat that waits, deletes, renames, starts, self-destructs.
         • Launch that batch, then exit the current process.
       Else:
         • Delete the temp file and continue.
    """
    try:
        # Locate your running EXE
        if getattr(sys, "frozen", False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(sys.argv[0])

        base_dir = os.path.dirname(app_path)
        real_name = os.path.basename(app_path)

        # 1. GitHub API call
        api_url = "https://api.github.com/repos/SuperGamer474/N0vaTools/releases/latest"
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "N0vaTools-Updater",
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req) as resp:
            info = json.load(resp)

        # 2. Find the EXE asset
        asset = next((a for a in info.get("assets", [])
                      if a.get("name") == real_name), None)
        if not asset:
            print("⚠️ No matching asset found!")
            return

        download_url = asset["browser_download_url"]

        # 3. Download to temp file right next to the real EXE
        fd, tmp_path = tempfile.mkstemp(suffix=".exe", dir=base_dir)
        os.close(fd)
        urllib.request.urlretrieve(download_url, tmp_path)

        # 4. Hash helper
        def sha256(path):
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()

        # 5. Compare; if different, write & launch batch
        if sha256(tmp_path) != sha256(app_path):
            bat_path = os.path.join(base_dir, "update.bat")
            new_name = os.path.basename(tmp_path)

            bat_content = f"""@echo off
pushd "%~dp0"
:waitloop
del "{real_name}" 2>nul || (
    timeout /t 1 /nobreak >nul
    goto waitloop
)
ren "{new_name}" "{real_name}"
start "" "{real_name}"
popd
del "%~f0"
"""

            with open(bat_path, "w", encoding="utf-8") as bat:
                bat.write(bat_content)

            # Launch the batch and exit so the old EXE lock is released
            subprocess.Popen(
                ["cmd", "/c", bat_path],
                cwd=base_dir,
                shell=False
            )
            os._exit(0)

        else:
            # Already latest—cleanup
            os.remove(tmp_path)

    except Exception as e:
        print(f"❌ Update failed: {e}")