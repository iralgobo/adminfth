@echo off
echo Deteniendo servicios Celery...
taskkill /f /im celery.exe 2>nul
taskkill /f /im python.exe 2>nul

echo Deteniendo Redis...
redis-cli shutdown 2>nul
taskkill /f /im redis-server.exe 2>nul

echo Todos los servicios detenidos
pause