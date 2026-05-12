@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building SVGFontBuilder executable for Windows...
:: --noconfirm: Clean and overwrite the output directory if it already exists
:: --windowed: Run the app without opening a separate console/terminal window
:: --name: The name of the output executable
:: --onefile: Bundle the application into a single executable file
pyinstaller --noconfirm --windowed --name "SVGFontBuilder" --onefile main.py

echo =========================================================
echo Build complete! 
echo - Your Windows executable is located at: dist\SVGFontBuilder.exe
echo =========================================================
pause
