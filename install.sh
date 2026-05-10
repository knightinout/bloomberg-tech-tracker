#!/bin/bash
# Bloomberg Tech Tracker - Quick Installation Script

set -e  # Exit on error

echo "=========================================="
echo "Bloomberg Technology Automation Installer"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Get your Gemini API key from: https://makersuite.google.com/app/apikey"
echo "2. Edit config/config.json and add your API key"
echo "3. Activate the virtual environment: source venv/bin/activate"
echo "4. Test the setup: cd scripts && python main.py --test"
echo "5. Set up daily automation: python setup_scheduler.py"
echo ""
echo "For detailed instructions, see README.md or QUICKSTART.md"
echo ""
