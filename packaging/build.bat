@echo off
echo Building VoxType...
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name VoxType --add-data "ui/frontend;ui/frontend" --add-data "assets;assets" main.py
echo Build complete! Output in dist/VoxType/
pause
