#!/bin/bash

# Music Bingo Setup Script for macOS

echo "Setting up Music Bingo application..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing required packages..."
pip install --upgrade pip
pip install pygame mutagen

# Create launch script
cat > run_music_bingo.command << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 music_bingo.py
EOF

# Make launch script executable
chmod +x run_music_bingo.command

echo "Setup complete!"
echo "To run the application, double-click 'run_music_bingo.command'"
echo "Or run: ./run_music_bingo.command from the terminal"