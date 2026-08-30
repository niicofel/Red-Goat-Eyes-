@echo off

setlocal
chcp 65001 >nul
cd /d "%~dp0"

set PGHOST=localhost
set PGPORT=5432
set PGUSER=rge_respaldo
set PGDATABASE=red_goat_eyes
set PGCLIENTENCODING=UTF8

set "PATH=%PATH%;C:\Program Files\PostgreSQL\18\bin"

for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"') do set FECHA=%%a
for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format HHmm"') do set HORA=%%a

set ARCHIVO=red_goat_eyes_%FECHA%_%HORA%.dump
set ROLES=roles_%FECHA%_%HORA%.sql

echo.
echo ============================================================
echo   RED GOAT EYES - Respaldo de la base de datos
echo ============================================================
echo.

where pg_dump >nul 2>nul
if errorlevel 1 (
    echo [ERROR] No se encontro pg_dump.
    echo Revisa la ruta de PostgreSQL en la linea del PATH de este script.
    pause
    exit /b 1
)

set /p PGPASSWORD=Contrasena del rol %PGUSER%: 
echo.

echo [1/3] Respaldando la base %PGDATABASE%...
pg_dump -h %PGHOST% -p %PGPORT% -U %PGUSER% -d %PGDATABASE% -F c -b -v -f "%ARCHIVO%"
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo el respaldo de la base.
    set PGPASSWORD=
    pause
    exit /b 1
)
echo       OK  %ARCHIVO%
echo.

echo [2/3] Respaldando roles y permisos...
pg_dumpall -h %PGHOST% -p %PGPORT% -U %PGUSER% --roles-only -f "%ROLES%"
if errorlevel 1 (
    echo [AVISO] No se pudieron respaldar los roles.
    echo         pg_dumpall --roles-only requiere un rol superusuario.
) else (
    echo       OK  %ROLES%
)
echo.

echo [3/3] Eliminando respaldos con mas de 7 dias...
forfiles /P "%~dp0" /M *.dump /D -7 /C "cmd /c del @path" 2>nul
forfiles /P "%~dp0" /M roles_*.sql /D -7 /C "cmd /c del @path" 2>nul
echo       OK
echo.

echo ============================================================
echo   Respaldo terminado
echo ============================================================
echo.
dir /b *.dump 2>nul
echo.
echo RECUERDA: copia el archivo a la nube. Un respaldo guardado
echo solo en el mismo equipo no protege ante un fallo de disco.
echo.

set PGPASSWORD=
pause