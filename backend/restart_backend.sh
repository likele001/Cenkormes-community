#!/usr/bin/env bash
cd /www/wwwroot/lightmes/backend
PID=$(ss -lntp 2>/dev/null | grep ':8000 ' | grep -oE 'pid=[0-9]+' | grep -oE '[0-9]+' | head -1 || true)
echo "killing listener pid=${PID:-none}"
if [ -n "$PID" ]; then kill "$PID" 2>/dev/null || true; fi
sleep 3
echo "port after kill:"; ss -lntp 2>/dev/null | grep ':8000 ' || echo "  free"
nohup /www/server/pyporject_evn/lightmes/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >> /www/wwwroot/lightmes/backend/uvicorn_restart.log 2>&1 &
sleep 12
echo "listener now:"; ss -lntp 2>/dev/null | grep ':8000 '
echo "health=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/api/health)"