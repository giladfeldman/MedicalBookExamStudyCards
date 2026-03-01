@echo off
chcp 65001 >nul 2>&1
setlocal

echo ============================================
echo   Nelson Pediatrics - Anki Import
echo ============================================
echo.

REM Check if the merged complete deck exists
if exist "%~dp0output\nelson_complete.apkg" (
    echo Found: nelson_complete.apkg (all 4,400+ notes in one file^)
    echo.
    echo Opening in Anki...
    start "" "%~dp0output\nelson_complete.apkg"
    echo.
    echo Done! Anki should open and import all cards.
    echo If Anki doesn't open, make sure Anki is installed and
    echo .apkg files are associated with it.
) else (
    echo nelson_complete.apkg not found.
    echo.
    echo Checking for Python to build it...
    where python >nul 2>&1
    if %errorlevel%==0 (
        echo Python found. Merging all APKG files...
        echo.
        python "%~dp0scripts\merge_apkg.py"
        echo.
        if exist "%~dp0output\nelson_complete.apkg" (
            echo Opening merged deck in Anki...
            start "" "%~dp0output\nelson_complete.apkg"
        ) else (
            echo ERROR: Merge failed. Please run manually:
            echo   python scripts\merge_apkg.py
        )
    ) else (
        echo Python not found. Importing files one by one...
        echo Close each Anki import dialog to proceed to the next file.
        echo.
        for %%f in ("%~dp0output\batch*.apkg") do (
            echo   Importing: %%~nxf
            start /wait "" "%%f"
        )
        echo.
        echo All files imported!
    )
)

echo.
pause
