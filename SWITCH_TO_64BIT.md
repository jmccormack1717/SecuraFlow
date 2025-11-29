# Switch to 64-bit Python - Step by Step Guide

## Why This is Necessary
32-bit Python 3.11 doesn't have pre-built wheels for scipy, pandas, and scikit-learn. 
64-bit Python has pre-built wheels for all packages, so installation is instant and reliable.

## Steps to Switch

### 1. Download 64-bit Python 3.11
- Go to: https://www.python.org/downloads/windows/
- Click "Download Python 3.11.x" (the main download button)
- This will download the 64-bit version by default

### 2. Install Python
- Run the installer
- **IMPORTANT**: Check "Add Python to PATH" at the bottom
- Click "Install Now"
- Wait for installation to complete

### 3. Verify Installation
Open a NEW PowerShell window and run:
```powershell
python --version
```
You should see Python 3.11.x

### 4. Create Virtual Environment
```powershell
cd C:\Users\james\SecuraFlow\backend
python -m venv venv
```

### 5. Activate Virtual Environment
```powershell
venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### 6. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This should work instantly with pre-built wheels!

### 7. Train Model
```powershell
python ml/train.py
```

## If You Want to Keep Both Python Versions
You can have both installed. Just make sure to:
- Use the full path to the 64-bit Python when creating venv
- Or use `py -3.11` (Python Launcher) to specify version

## Troubleshooting
- If `python` still points to 32-bit: Restart your terminal/PowerShell
- If still issues: Use full path: `C:\Users\james\AppData\Local\Programs\Python\Python311\python.exe -m venv venv`

