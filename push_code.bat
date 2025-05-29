@echo off
REM 設定 portable git 路徑（你解壓的位置）
set GIT_BIN=C:\Program Files\Git\cmd\git.exe

REM 設定你的專案資料夾（你 clone 下來的 GitHub 專案）
cd /d D:\IT\github\futures_order

REM 設定 commit 訊息（可自動或手動）
set MESSAGE=auto commit %date% %time%

REM 加入 & commit & push
"%GIT_BIN%" add .
"%GIT_BIN%" commit -m "%MESSAGE%"
"%GIT_BIN%" push origin

echo.
echo ✅ Push 成功！
pause
