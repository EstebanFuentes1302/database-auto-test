@echo off
rem Ruta al intérprete de Python
set PYTHON_EXECUTABLE=python

rem Ruta al script de Python
set PYTHON_SCRIPT=C:\env\DB_TEST\py\db_test_csv.py

rem Ejecutar el script de Python
%PYTHON_EXECUTABLE% %PYTHON_SCRIPT%

rem Espera a que el usuario presione una tecla para salir
pause