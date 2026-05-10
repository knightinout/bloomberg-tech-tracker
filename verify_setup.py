#!/usr/bin/env python3
"""
Setup Verification Script
Checks that all components are properly configured.
"""

import os
import sys
import json
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass

def print_status(message, status):
    """Print a status message with emoji."""
    emoji = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{emoji}{reset} {message}")

def check_python_version():
    """Check Python version is 3.8+"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 8
    print_status(f"Python {version.major}.{version.minor}.{version.micro}", is_valid)
    return is_valid

def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'google.genai',
        'yt_dlp',
        'youtube_transcript_api',
        'requests',
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package)
            print_status(f"Package: {package}", True)
        except ImportError:
            print_status(f"Package: {package}", False)
            all_installed = False

    return all_installed

def check_config():
    """Check configuration file."""
    config_path = Path(__file__).parent / "config" / "config.json"

    if not config_path.exists():
        print_status("config.json exists", False)
        return False

    print_status("config.json exists", True)

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Check API key
        env_key = os.environ.get('GEMINI_API_KEY', '').strip()
        config_key = config.get('api_keys', {}).get('gemini_api_key', '')
        has_key = bool(env_key) or (config_key and config_key != 'YOUR_GEMINI_API_KEY_HERE')
        print_status("Gemini API key configured (via .env or config.json)", has_key)

        return has_key

    except Exception as e:
        print_status(f"Config validation: {str(e)}", False)
        return False

def check_directories():
    """Check required directories exist."""
    base_path = Path(__file__).parent
    dirs = [
        "scripts",
        "config",
        "reports",
        "reports/daily",
        "logs"
    ]

    all_exist = True
    for dir_name in dirs:
        dir_path = base_path / dir_name
        exists = dir_path.exists()
        print_status(f"Directory: {dir_name}", exists)
        all_exist = all_exist and exists

    return all_exist

def check_scripts():
    """Check all scripts exist."""
    base_path = Path(__file__).parent / "scripts"
    scripts = [
        "main.py",
        "youtube_fetcher.py",
        "gemini_analyzer.py",
        "markdown_generator.py",
        "setup_scheduler.py"
    ]

    all_exist = True
    for script in scripts:
        script_path = base_path / script
        exists = script_path.exists()
        print_status(f"Script: {script}", exists)
        all_exist = all_exist and exists

    return all_exist

def main():
    """Run all verification checks."""
    print("="*60)
    print("Bloomberg Technology Automation - Setup Verification")
    print("="*60)
    print()

    checks = {
        "Python Version": check_python_version,
        "Required Packages": check_dependencies,
        "Configuration": check_config,
        "Directories": check_directories,
        "Scripts": check_scripts,
    }

    results = {}

    for name, check_func in checks.items():
        print(f"\n{name}:")
        print("-" * 40)
        results[name] = check_func()

    print()
    print("="*60)

    if all(results.values()):
        print("✓ All checks passed! System is ready to use.")
        print()
        print("Next steps:")
        print("1. cd scripts")
        print("2. python main.py --test  # Test components")
        print("3. python main.py         # Run full workflow")
        print("4. python setup_scheduler.py  # Set up automation")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set GEMINI_API_KEY=your_key in .env (or config/config.json)")
        print("3. Make sure you're in the project directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())
