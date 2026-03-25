@echo off
REM Daily auto-push script for C:\Users\kita\.claude repository
REM Runs at midnight via Task Scheduler

set REPO_DIR=C:\Users\kita\.claude
set LOG_FILE=%REPO_DIR%\scripts\daily-git-push.log
set GIT_EXE=C:\Program Files\Git\cmd\git.exe

echo ========================================>> "%LOG_FILE%"
echo %date% %time% - Start>> "%LOG_FILE%"
echo ========================================>> "%LOG_FILE%"

cd /d "%REPO_DIR%"
if errorlevel 1 (
    echo %date% %time% - ERROR: Failed to cd to %REPO_DIR%>> "%LOG_FILE%"
    exit /b 1
)

REM Check for changes
"%GIT_EXE%" status --porcelain > "%TEMP%\gitstatus.tmp" 2>&1
set /p STATUS=<"%TEMP%\gitstatus.tmp"
del "%TEMP%\gitstatus.tmp"

if "%STATUS%"=="" (
    echo %date% %time% - No changes to commit>> "%LOG_FILE%"
    exit /b 0
)

REM Stage all changes
"%GIT_EXE%" add -A >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo %date% %time% - ERROR: git add failed>> "%LOG_FILE%"
    exit /b 1
)

REM Get date string for commit message
for /f "tokens=1-3 delims=/" %%a in ("%date%") do set DATESTR=%%a-%%b-%%c
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do set DATESTR=%%a/%%b/%%c

REM Commit with auto-generated message
"%GIT_EXE%" diff --cached --name-only > "%TEMP%\gitfiles.tmp" 2>&1
set /p CHANGED_FILES=<"%TEMP%\gitfiles.tmp"
del "%TEMP%\gitfiles.tmp"

"%GIT_EXE%" commit -m "Auto-update: %CHANGED_FILES%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo %date% %time% - ERROR: git commit failed>> "%LOG_FILE%"
    exit /b 1
)

REM Push to remote
"%GIT_EXE%" push origin main >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo %date% %time% - ERROR: git push failed>> "%LOG_FILE%"
    exit /b 1
)

echo %date% %time% - Successfully pushed to GitHub>> "%LOG_FILE%"
exit /b 0
