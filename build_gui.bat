@echo off
echo Building Finance Tracker GUI...
pyinstaller --onefile --windowed --name FinanceTrackerGUI gui_finance_tracker.py
echo Build completed!
echo Copying essential files...
copy credentials.json dist\ >nul 2>&1
copy user_settings.json dist\ >nul 2>&1
copy env.example dist\ >nul 2>&1
xcopy /E /I config dist\config >nul 2>&1
xcopy /E /I data dist\data >nul 2>&1
echo Done!
pause 