@echo off
REM Bloomberg Tech Tracker - Quick Installation Script for Windows

echo ==========================================
echo Bloomberg Technology Automation Installer
echo ==========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

python --version

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Get your Gemini API key from: https://makersuite.google.com/app/apikey
echo 2. Edit config\config.json and add your API key
echo 3. Activate the virtual environment: venv\Scripts\activate
echo 4. Test the setup: cd scripts ^&^& python main.py --test
echo 5. Set up daily automation: python setup_scheduler.py
echo.
echo For detailed instructions, see README.md or QUICKSTART.md
echo.
pause
