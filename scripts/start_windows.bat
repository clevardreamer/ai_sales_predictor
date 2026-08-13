@echo off
setlocal

set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE="
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "FRONTEND_HOST=127.0.0.1"
set "FRONTEND_PORT=8501"
set "BACKEND_URL=http://%BACKEND_HOST%:%BACKEND_PORT%/predict"

echo Starting backend on http://%BACKEND_HOST%:%BACKEND_PORT%
start "Sales Backend" cmd /k "cd /d "%PROJECT_ROOT%" && %PYTHON_EXE% app.py"

echo Starting frontend on http://%FRONTEND_HOST%:%FRONTEND_PORT%
start "Sales Frontend" cmd /k "cd /d "%PROJECT_ROOT%" && set BACKEND_URL=%BACKEND_URL% && %PYTHON_EXE% -m streamlit run streamlit_app.py --server.address %FRONTEND_HOST% --server.port %FRONTEND_PORT%"

timeout /t 5 /nobreak >nul
start "" "http://%FRONTEND_HOST%:%FRONTEND_PORT%"

echo.
echo App launch requested.
echo - Backend:  http://%BACKEND_HOST%:%BACKEND_PORT%
echo - Frontend: http://%FRONTEND_HOST%:%FRONTEND_PORT%
echo.
echo Close each terminal window to stop the app.
endlocal
