@echo off
echo The Program is started
setlocal enabledelayedexpansion
set FunctionName=%1
if "%FunctionName%" == "actionRule" (
    start ms-settings:network-wifi
) else if "%FunctionName%" == "commandRule" (
    :: Initialize signal variable
    set "signal="
    :: Extract Wi-Fi signal strength
    for /f "tokens=2 delims=:" %%A in ('netsh wlan show interfaces ^| findstr /C:"Signal"') do (
        set "signal=%%A"
    )
    :: Trim spaces and remove % symbol
    set "signal=!signal: =!"
    set "signal=!signal:~0,-1!"

    :: Ensure signal is numeric before comparison
    if "!signal!"=="" (
        pause
        exit /b
    )
    :: Check if signal is less than 100%%
    if !signal! LSS 100 (
        echo true
    ) else (
        echo false
    )
)