@echo off
setlocal

set "APP_NAME=Gestor de Correlatividades"
set "SOURCE_FILE=main.py"
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo =============================================
echo   Compilador de %APP_NAME%
echo =============================================

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta disponible en PATH.
    echo Instala Python 3.12 o superior y activa "Add Python to PATH".
    pause
    exit /b 1
)

if not exist "%SOURCE_FILE%" (
    echo [ERROR] No se encontro %SOURCE_FILE% en %SCRIPT_DIR%
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias...
python -m pip install --disable-pip-version-check -r requirements.txt pyinstaller
if errorlevel 1 goto :error

echo [2/3] Generando ejecutable...
python -m PyInstaller --noconfirm --onefile --windowed --clean --collect-all customtkinter --name "%APP_NAME%" "%SOURCE_FILE%"
if errorlevel 1 goto :error

echo [3/3] Copiando resultado...
copy /Y "dist\%APP_NAME%.exe" "%APP_NAME%.exe" >nul
if errorlevel 1 goto :error

rd /s /q build 2>nul
rd /s /q dist 2>nul
del /q "%APP_NAME%.spec" 2>nul

echo.
echo Listo. Ejecutable creado en:
echo %SCRIPT_DIR%%APP_NAME%.exe
pause
exit /b 0

:error
echo.
echo [ERROR] La compilacion no se pudo completar.
pause
exit /b 1
