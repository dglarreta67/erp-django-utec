@echo off
TITLE ERP Django - Guardando Sesion
COLOR 0E

SET PC_WORK=C:\Temp_Workspace_ERP
SET USB_PATH=%~dp0

echo ======================================================
echo  ERP DJANGO :: PC ^-^> USB (RESPALDO)
echo ======================================================

if not exist "%PC_WORK%" (
    echo [ERROR] No existe %PC_WORK%
    echo Ejecuta primero iniciar_sesion.bat
    pause & exit /b 1
)

echo Guardando cambios en la USB...
xcopy /s /e /y /d "%PC_WORK%" "%USB_PATH%WorkSpace_ERP" >nul 2>&1

echo.
echo ======================================================
echo  RESPALDO COMPLETADO.
echo  Guardado en: %USB_PATH%WorkSpace_ERP
echo ======================================================
pause
