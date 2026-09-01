@echo off

setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

set PGHOST=localhost
set PGPORT=5432
set PGUSER=postgres
set PGDATABASE_DESTINO=red_goat_eyes
set PGCLIENTENCODING=UTF8

set "PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin"

echo.
echo ============================================================
echo   RED GOAT EYES - Instalacion de la base de datos
echo ============================================================
echo.

where psql >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro psql en el PATH del sistema.
    echo.
    echo Agrega la carpeta bin de PostgreSQL al PATH, por ejemplo:
    echo    C:\Program Files\PostgreSQL\18\bin
    echo.
    pause
    exit /b 1
)

if not exist "07_credenciales.sql" (
    echo [AVISO] No existe 07_credenciales.sql
    echo.
    echo    Los roles se crearan SIN contrasena y no podran conectarse.
    echo    Para completarlo despues:
    echo      1. Copiar 07_credenciales.sql.example como 07_credenciales.sql
    echo      2. Escribir dentro las contrasenas elegidas
    echo      3. Volver a ejecutar este script
    echo.
)

echo Servidor : %PGHOST%:%PGPORT%
echo Usuario  : %PGUSER%
echo Base     : %PGDATABASE_DESTINO%
echo.

set /p PGPASSWORD=Contrasena de PostgreSQL para %PGUSER%: 
echo.

echo [1/10] Creando la base de datos...
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d postgres -f "00_create_database.sql"
echo        Si aparecio el error 42P04, la base ya existia. Continuamos.
echo.

call :ejecutar "01_schema.sql"              "2/10"  "Creando las 21 tablas"
call :ejecutar "02_seed.sql"                "3/10"  "Cargando catalogos y productos"
call :ejecutar "03_functions_triggers.sql"  "4/10"  "Creando funciones y triggers"
call :ejecutar "04_procedures.sql"          "5/10"  "Creando procedimientos almacenados"
call :ejecutar "05_views_reportes.sql"      "6/10"  "Creando vistas y reportes"
call :ejecutar "06_roles_permisos.sql"      "7/10"  "Configurando roles y permisos"
call :ejecutar "07_credenciales.sql"        "8/10"  "Asignando contrasenas a los roles"
call :ejecutar "08_security_definer.sql"    "9/10"  "Elevando privilegios de triggers y procedimientos"
call :ejecutar "09_datos_demo.sql"          "10/10" "Preparando el catalogo por tallas"

echo.
echo ============================================================
echo   Instalacion terminada
echo ============================================================
echo.
echo Verifica en pgAdmin que existe la base %PGDATABASE_DESTINO%
echo con sus 21 tablas dentro de Schemas ^> public ^> Tables
echo.
echo Comprueba tambien:
echo    SELECT COUNT(*) FROM v_catalogo_publico;   -- deben ser 24
echo    SELECT COUNT(*) FROM producto_talla;       -- deben ser 72
echo.
echo Cuenta de administrador:  fc762798@gmail.com  /  1234
echo.
echo No olvides crear backend\.env con las mismas contrasenas
echo que pusiste en 07_credenciales.sql
echo.

set PGPASSWORD=
pause
exit /b 0


:ejecutar
if not exist "%~1" (
    echo [%~2] %~1 no existe. Se omite.
    exit /b 0
)

echo [%~2] %~3...
psql -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE_DESTINO% -v ON_ERROR_STOP=1 -f "%~1"

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo al ejecutar %~1
    echo Revisa el mensaje de error de arriba antes de continuar.
    echo.
    set PGPASSWORD=
    pause
    exit /b 1
)

echo       OK
exit /b 0