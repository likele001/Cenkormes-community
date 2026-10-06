@echo off
setlocal

set ROOT=%~dp0
set MODE=%1
set START_ADMIN=0
set START_H5=0

if /I "%MODE%"=="all" set START_ADMIN=1& set START_H5=1
if /I "%MODE%"=="--all" set START_ADMIN=1& set START_H5=1
if /I "%MODE%"=="admin" set START_ADMIN=1
if /I "%MODE%"=="--admin" set START_ADMIN=1
if /I "%MODE%"=="h5" set START_H5=1
if /I "%MODE%"=="--h5" set START_H5=1

if /I "%MODE%"=="-h" goto :help
if /I "%MODE%"=="--help" goto :help

if not "%MODE%"=="" if "%START_ADMIN%%START_H5%"=="00" goto :unknown

if "%START_ADMIN%"=="1" start "frontend-admin-pro" cmd /k "cd /d %ROOT%frontend-admin-pro && npm install && npm run dev -- --host 0.0.0.0 --port 5173"
if "%START_H5%"=="1" start "frontend-h5" cmd /k "cd /d %ROOT%frontend-h5 && npm install && npm run dev -- --host 0.0.0.0 --port 5174"

cd /d %ROOT%backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
exit /b 0

:help
echo 用法: run.bat [all^|admin^|h5]
exit /b 0

:unknown
echo 未知参数: %MODE%
echo 用法: run.bat [all^|admin^|h5]
exit /b 1
