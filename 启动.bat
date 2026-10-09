@echo off
cd /d "%~dp0"
echo [1/2] 同步BOSS客户数据...
python scripts\sync_boss.py
echo.
echo [2/2] 启动中台（http://127.0.0.1:8001）...
python serve.py