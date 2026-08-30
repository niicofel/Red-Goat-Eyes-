@echo off

setlocal
chcp 65001 >nul
cd /d "%~dp0"

set PGHOST=localhost
set PGPORT=5432
set PGUSER=postgres
set PGDATABASE=red_goat_eyes
set PGCLIENTENCODING=UTF8

set "PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin"

if "%~1"=="" (
    echo.
    echo Uso: restaurar.bat ARCHIVO.dump
    echo.
    echo Respaldos disponibles en esta carpeta:
    dir /b *.dump 2>nul
    echo.
    pause
    exit /b 1
)

if not exist "%~1" (
    echo [ERROR] No se encontro el archivo %~1
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   ATENCION - OPERACION DESTRUCTIVA
echo ============================================================
echo.
echo Se va a ELIMINAR la base %PGDATABASE% y reconstruirla
echo desde el archivo:  %~1
echo.
echo TODOS los datos actuales se perderan.
echo.

set /p CONFIRMA=Escribe RESTAURAR en mayusculas para continuar: 
if not "%CONFIRMA%"=="RESTAURAR" (
    echo.
    echo Operacion cancelada. No se modifico nada.
    pause
    exit /b 0
)

echo.
set /p PGPASSWORD=Contrasena del usuario %PGUSER%: 
echo.

echo [1/3] Cerrando conexiones y eliminando la base...
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d postgres -c "DROP DATABASE IF EXISTS %PGDATABASE% WITH (FORCE);"
if errorlevel 1 goto error

echo [2/3] Creando la base vacia...
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d postgres -c "CREATE DATABASE %PGDATABASE% WITH ENCODING='UTF8' TEMPLATE=template0;"
if errorlevel 1 goto error

echo [3/3] Restaurando el contenido...
pg_restore -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -v "%~1"
if errorlevel 1 (
    echo.
    echo [AVISO] pg_restore reporto advertencias.
    echo Algunas son normales si los roles ya existian en el servidor.
)

echo.
echo ============================================================
echo   Restauracion terminada
echo ============================================================
echo.
echo Verifica el contenido en pgAdmin con:
echo    SELECT COUNT(*) FROM producto;   -- deben ser 24
echo.

set PGPASSWORD=
pause
exit /b 0

:error
echo.
echo [ERROR] Fallo la restauracion. Revisa el mensaje anterior.
set PGPASSWORD=
pause
exit /b 1