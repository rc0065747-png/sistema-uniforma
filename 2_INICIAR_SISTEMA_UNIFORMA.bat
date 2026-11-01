@echo off
cd /d "%~dp0"
chcp 65001 >nul
echo ============================================================================
echo   INICIANDO SERVIDOR WEB - SISTEMA UNIFORMA (4 PANTALLAS PROTOTIPO U2-E3)
echo   URL Inicial: http://127.0.0.1:8000/login
echo ============================================================================
start http://127.0.0.1:8000/login
python run_server.py
pause
