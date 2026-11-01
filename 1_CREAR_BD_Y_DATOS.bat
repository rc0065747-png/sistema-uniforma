@echo off
cd /d "%~dp0"
chcp 65001 >nul
echo ============================================================================
echo   SISTEMA UNIFORMA (EQUIPO 16) - INSTALACION Y CREACION DE BD (U3-E1)
echo   Directorio activo: %CD%
echo ============================================================================
if not exist .env (
    copy .env.example .env >nul
    echo [OK] Archivo .env creado a partir de .env.example
)
echo.
echo [1/2] Instalando dependencias en Python (python-dotenv, Jinja2, pg8000)...
python -m pip install -r requirements.txt
echo.
echo [2/2] Creando las 7 tablas en 3FN (UniformaDB) y cargando datos ficticios...
python database/init_db.py
echo.
echo ============================================================================
echo   PROCESO COMPLETADO. Ahora haga doble clic en 2_INICIAR_SISTEMA_UNIFORMA.bat
echo ============================================================================
pause
