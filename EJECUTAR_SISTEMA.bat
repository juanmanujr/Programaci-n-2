@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║     SISTEMA DE GESTIÓN - EJECUCIÓN DIRECTA       ║  
echo ╚══════════════════════════════════════════════════╝
echo.
echo 👨‍🎓 ALUMNO: Juan Manuel Gómez Achucarro
echo 📚 MATERIA: Programacion 2
echo.
echo 🔍 Sistema con 43 TABLAS - Modo directo
echo.

cd sistema_ventas1.1

echo ====================================================
echo    Verificando Python y Django...
echo ====================================================

REM Verificar si Django está instalado globalmente
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo ❌ Django no encontrado
    echo.
    echo ⚠️  Django no está instalado en el sistema
    echo.
    echo SOLUCIÓN RÁPIDA:
    echo 1. Abra PowerShell como Administrador
    echo 2. Ejecute: pip install django
    echo 3. Vuelva a ejecutar este archivo
    echo.
    pause
    exit /b 1
)

echo ✅ Django encontrado
echo.
echo ====================================================
echo    Iniciando servidor...
echo ====================================================
echo.
echo 📢 IMPORTANTE: NO CERRAR ESTA VENTANA
echo.
echo 🌐 ABRA SU NAVEGADOR EN:
echo    http://127.0.0.1:8000/
echo.
echo 👑 PANEL DE ADMINISTRACIÓN:
echo    http://127.0.0.1:8000/admin/
echo    Usuario: admin
echo    Contraseña: 123
echo.
echo 📊 Diagrama de tablas en: ..\base_de_datos\
echo.
echo ====================================================
echo 🚀 SERVIDOR INICIADO - Ctrl+C para detener
echo ====================================================
echo.

python manage.py runserver

echo.
echo ====================================================
echo    Servidor detenido
echo ====================================================
echo.
pause