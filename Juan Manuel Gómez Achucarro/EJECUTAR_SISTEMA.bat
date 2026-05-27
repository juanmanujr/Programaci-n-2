@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║     SISTEMA DE GESTIÓN - EJECUCIÓN INTELIGENTE   ║  
echo ╚══════════════════════════════════════════════════╝
echo.
echo 👨‍🎓 ALUMNO: Juan Manuel Gómez Achucarro
echo 📚 MATERIA: Programacion 2
echo.
echo 🔍 Sistema con 44 TABLAS - Modo automático
echo.

cd sistema_ventas1.1

echo ====================================================
echo    DETECTANDO CONFIGURACIÓN...
echo ====================================================

REM OPCIÓN 1: Probar .venv original
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe -c "import django" >nul 2>&1
    if not errorlevel 1 (
        echo ✅ .venv original FUNCIONA
        goto :iniciar_con_original
    )
    echo ⚠️  .venv existe pero Django no funciona
)

REM OPCIÓN 2: Crear .venv_nuevo
echo.
echo 🔧 Creando entorno virtual NUEVO...
python -m venv .venv_nuevo

echo 📦 Instalando Django y dependencias...
.venv_nuevo\Scripts\pip.exe install django pillow django-extensions django-crispy-forms django-widget-tweaks

echo ✅ Entorno virtual NUEVO listo
goto :iniciar_con_nuevo

:iniciar_con_original
echo.
echo 💡 Usando: .venv ORIGINAL
set PYTHON_PATH=.venv\Scripts\python.exe
goto :mostrar_instrucciones

:iniciar_con_nuevo
echo.
echo 💡 Usando: .venv NUEVO (reparado)
set PYTHON_PATH=.venv_nuevo\Scripts\python.exe

:mostrar_instrucciones
echo ====================================================
echo    INICIANDO SERVIDOR...
echo ====================================================
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
echo ====================================================
echo 🚀 SERVIDOR INICIADO - Ctrl+C para detener
echo ====================================================
echo.

%PYTHON_PATH% manage.py runserver

echo.
echo ====================================================
echo    Servidor detenido
echo ====================================================
echo.
pause