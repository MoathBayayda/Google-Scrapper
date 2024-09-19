@echo off
:: Check if the script is run as administrator
openfiles >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Call the installation steps
call :install_software
goto :eof

:install_software
echo Installing Chocolatey...
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
echo Installing ffmpeg...
choco install ffmpeg -y
echo ffmpeg installation complete.
echo.

echo Downloading Visual C++ Redistributable...
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://aka.ms/vs/16/release/vc_redist.x64.exe', 'vc_redist.x64.exe')"
echo Download complete.

echo Installing Visual C++ Redistributable...
powershell -Command "Start-Process 'vc_redist.x64.exe' -ArgumentList '/install /quiet /norestart' -Wait"
echo Visual C++ Redistributable installation complete.

echo.
echo Press Enter to exit...
pause
