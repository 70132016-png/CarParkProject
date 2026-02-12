@echo off
echo ============================================================
echo    Adding Firewall Rule for Flask Port 5000
echo ============================================================
echo.
echo This will allow your phone/other devices to connect...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - Good!
    echo.
    echo Adding firewall rule...
    netsh advfirewall firewall add rule name="Flask Port 5000" dir=in action=allow protocol=TCP localport=5000
    echo.
    echo ============================================================
    echo    SUCCESS! Firewall rule added.
    echo ============================================================
    echo.
    echo Now try accessing from your phone:
    echo http://192.168.100.174:5000
    echo.
    pause
) else (
    echo ERROR: Not running as Administrator!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
)
