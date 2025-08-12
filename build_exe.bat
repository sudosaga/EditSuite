@echo off
echo Building EditSuite executable...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    echo.
)

REM Create the executable
echo Creating executable...
pyinstaller --onefile --windowed --name "EditSuite" --icon=icon.ico EditSuite.py

REM Check if build was successful
if exist "dist\EditSuite.exe" (
    echo.
    echo ✅ Build successful!
    echo Executable created: dist\EditSuite.exe
    echo.
    echo 📋 Important Notes:
    echo - Users need FFmpeg installed on their system
    echo - Executable size: ~15-20MB
    echo - Works on Windows 10+
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed!
    echo Please check the output above for errors.
    echo.
    pause
)
