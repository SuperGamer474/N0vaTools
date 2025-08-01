import os
import zipfile
import urllib.request
import time
import winreg
import ctypes

def install_java():
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