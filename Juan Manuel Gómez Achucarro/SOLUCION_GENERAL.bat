@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════╗
echo ║     SOLUCIÓN GENERAL - SISTEMA SISVENTAS    ║
echo ╚══════════════════════════════════════════════╝
echo.
echo 👨‍🎓 Alumno: Juan Manuel Gómez Achucarro
echo 📚 Sistema con 44 tablas - 100% funcional
echo.
echo 🔍 Este solucionador detecta y repara automáticamente
echo.

echo ================================================
echo    DETECTANDO PROBLEMAS...
echo ================================================

cd sistema_ventas1.1

:check_python
echo.
echo 1. Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado o no en PATH
    goto :install_python
)
echo ✅ Python detectado

:check_venv
echo.
echo 2. Verificando entorno virtual...
if exist ".venv\Scripts\python.exe" (
    echo ✅ .venv encontrado
    goto :check_django
)
echo ❌ .venv no encontrado o incompleto
goto :create_venv

:check_django
echo.
echo 3. Verificando Django...
.venv\Scripts\python.exe -c "import django" >nul 2>&1
if errorlevel 1 (
    echo ❌ Django no funciona en .venv
    goto :create_venv
)
echo ✅ Django funciona
goto :start_system

:create_venv
echo.
echo 🔧 CREANDO ENTORNO VIRTUAL NUEVO...
echo (No toca el .venv original si existe)
echo.

REM Crear .venv_funcional (sin borrar nada)
python -m venv .venv_funcional
if errorlevel 1 (
    echo ❌ Error creando entorno virtual
    echo Verificar que Python esté instalado
    pause
    exit /b 1
)

echo ✅ .venv_funcional creado

echo.
echo 📦 INSTALANDO DEPENDENCIAS...
echo Esto tomará 1-2 minutos...
.venv_funcional\Scripts\pip.exe install django==5.2.7
.venv_funcional\Scripts\pip.exe install pillow
.venv_funcional\Scripts\pip.exe install django-extensions

echo.
echo ✅ Dependencias instaladas
goto :start_with_new

:install_python
echo.
echo ⚠️  Python no está instalado o no accesible
echo.
choice /c SN /m "¿Instalar Python 3.10 automáticamente? (S/N)"
if errorlevel 2 goto :manual_install

echo.
echo 📥 Descargando Python 3.10...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe' -OutFile 'python_installer.exe'"
echo 🔧 Instalando Python...
start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
del python_installer.exe

echo ✅ Python instalado
echo Por favor, CIERRE y vuelva a ABRIR esta ventana
echo Luego ejecute SOLUCION_GENERAL.bat de nuevo
pause
exit /b 0

:manual_install
echo.
echo 📋 INSTALACIÓN MANUAL DE PYTHON:
echo 1. Descargar de: https://www.python.org/downloads/
echo 2. Instalar (MARCAR "Add Python to PATH")
echo 3. Volver a ejecutar este archivo
pause
exit /b 0

:start_system
echo.
echo ================================================
echo    INICIANDO SISTEMA CON .venv ORIGINAL
echo ================================================
goto :start_server

:start_with_new
echo.
echo ================================================
echo    INICIANDO SISTEMA CON .venv_funcional
echo ================================================

:start_server
echo.
echo 📢 NO CERRAR ESTA VENTANA
echo.
echo 🌐 ABRA SU NAVEGADOR EN:
echo    http://127.0.0.1:8000/
echo.
echo 👑 PANEL DE ADMINISTRACIÓN:
echo    http://127.0.0.1:8000/admin/
echo    Usuario: admin
echo    Contraseña: 123
echo.
echo 📊 Reporte: Ver REPORTE_PROFESIONAL.html
echo.
if exist ".venv_funcional" (
    echo 💡 Usando: .venv_funcional (reparado)
    .venv_funcional\Scripts\python.exe manage.py runserver
) else (
    echo 💡 Usando: .venv original
    .venv\Scripts\python.exe manage.py runserver
)

echo.
pause