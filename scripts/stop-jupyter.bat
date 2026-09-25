@echo off
echo Dang tat tien trinh JupyterLab MCP (Port 3001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3001" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a
)
echo Hoan tat! JupyterLab da dung.
timeout /t 3
