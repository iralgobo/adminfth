@echo off
chcp 65001 > nul
echo ========================================
echo    INICIANDO SERVICIOS PARA DJANGO CELERY
echo ========================================
echo.

REM Verificar si Redis está en el PATH
where redis-server >nul 2>nul
if errorlevel 1 (
    echo ERROR: Redis no encontrado en el PATH
    echo Por favor, instala Redis o ajusta el PATH
    pause
    exit /b 1
)

REM Configurar título de ventanas
title Servicios Django Celery - %~n0

REM Ruta a tu entorno virtual (AJUSTA ESTA RUTA)
set VENV_PATH=D:\Trading\adminfth\.venv

REM Ruta a tu proyecto Django (AJUSTA ESTA RUTA)
set PROJECT_PATH=D:\Trading\adminfth

REM Verificar si existe el entorno virtual
if not exist "%VENV_PATH%" (
    echo ERROR: No se encuentra el entorno virtual en %VENV_PATH%
    pause
    exit /b 1
)

REM Verificar si existe el proyecto
if not exist "%PROJECT_PATH%" (
    echo ERROR: No se encuentra el proyecto en %PROJECT_PATH%
    pause
    exit /b 1
)

echo 1. Iniciando Redis...
start "Redis Server" cmd /k "echo Iniciando Redis... && redis-server && echo Redis cerrado. && pause"

echo Esperando 3 segundos para que Redis inicie...
timeout /t 3 /nobreak >nul

echo 2. Iniciando Celery Worker...
start "Celery Worker" cmd /k "echo Iniciando Celery Worker... && cd /d "%PROJECT_PATH%" && "%VENV_PATH%\Scripts\activate" && celery -A config worker --loglevel=info --pool=solo && echo Celery Worker cerrado. && pause"

echo 3. Iniciando Celery Beat...
start "Celery Beat" cmd /k "echo Iniciando Celery Beat... && cd /d "%PROJECT_PATH%" && "%VENV_PATH%\Scripts\activate" && celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler && echo Celery Beat cerrado. && pause"

echo.
echo ========================================
echo    Todos los servicios se estan iniciando
echo ========================================
echo.
echo Redis: Puerto 6379
echo Celery Worker: Procesando tareas
echo Celery Beat: Programando tareas cada 5 minutos
echo.
echo Presiona cualquier tecla para cerrar este mensaje...
pause >nul