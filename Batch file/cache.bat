@echo off
echo Clearing cache and temporary files...
timeout /t 2 /nobreak >nul

:: Clear Windows Temp folder
echo Deleting system temporary files...
del /s /q "%SystemRoot%\Temp\*.*"
for /d %%x in ("%SystemRoot%\Temp\*") do rd /s /q "%%x"

:: Clear User Temp folder
echo Deleting user temporary files...
del /s /q "%Temp%\*.*"
for /d %%x in ("%Temp%\*") do rd /s /q "%%x"

:: Clear Windows Prefetch
echo Deleting prefetch files...
del /s /q "%SystemRoot%\Prefetch\*.*"

:: Clear DNS cache
echo Flushing DNS cache...
ipconfig /flushdns

:: Clear Windows Explorer recent files
echo Clearing Explorer recent files...
del /f /q "%AppData%\Microsoft\Windows\Recent\*"

:: Clear Windows Update cache (optional)
echo Deleting Windows Update cache...
net stop wuauserv >nul 2>&1
del /s /q "%SystemRoot%\SoftwareDistribution\Download\*.*"
net start wuauserv >nul 2>&1

echo Cache cleared successfully! ✅
pause
