#!/bin/bash
# Simple bash script to run the fixed game launcher

# Make sure the current directory is used
cd "$(dirname "$0")"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON="python3"
elif command -v python &>/dev/null; then
    PYTHON="python"
else
    echo "Error: Python is not installed or not in PATH."
    echo "Please install Python 3 to run this game."
    exit 1
fi

# Make sure the launcher is executable
chmod +x fixed_game_launcher.py

# Run the fixed game launcher
$PYTHON fixed_game_launcher.py

# Exit with the same status as the Python script
exit $?
