#!/bin/bash

# Activate the virtual environment if it isn't already active
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

echo "Installing PyInstaller..."
pip install pyinstaller

echo "Building SVGFontBuilder executable..."
# --noconfirm: Clean and overwrite the output directory if it already exists
# --windowed: Run the app without opening a separate console/terminal window
# --name: The name of the output executable
# --onefile: Bundle the application into a single executable file
pyinstaller --noconfirm --windowed --name "SVGFontBuilder" --onefile main.py

echo "========================================================="
echo "Build complete! "
echo "- Your Mac app bundle is located at: dist/SVGFontBuilder.app"
echo "- Your standalone executable is located at: dist/SVGFontBuilder"
echo "========================================================="
