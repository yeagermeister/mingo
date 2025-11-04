#!/bin/bash
# save as setup_tkinter.sh

echo "Checking Python and Tkinter setup..."

# Check if Tkinter is available
python3 -c "import tkinter" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Tkinter is already installed and working!"
    echo "You can run: python3 music_bingo.py"
else
    echo "✗ Tkinter not found. Installing..."
    
    # Check if using Homebrew Python
    if command -v brew &> /dev/null; then
        echo "Installing python-tk via Homebrew..."
        brew install python-tk
        
        # Get Python version
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        echo "Installing python-tk for Python ${PYTHON_VERSION}..."
        brew install python-tk@${PYTHON_VERSION}
        
        echo "Reinstalling Python to ensure proper linking..."
        brew reinstall python@${PYTHON_VERSION}
    else
        echo "Homebrew not found. Please install Python from python.org"
        echo "Visit: https://www.python.org/downloads/"
    fi
fi

# Test again
python3 -c "import tkinter" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Setup complete! Tkinter is working."
    
    # Install other requirements
    echo "Installing other requirements..."
    pip3 install pygame mutagen
    
    echo ""
    echo "✓ All done! You can now run:"
    echo "  python3 music_bingo.py"
else
    echo "✗ Tkinter still not working."
    echo "Please try:"
    echo "1. Download Python from python.org"
    echo "2. Or use system Python: /usr/bin/python3 music_bingo.py"
fi