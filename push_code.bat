set GIT_BIN=C:\Program Files\Git\cmd\git.exe

cd /d D:\IT\github\futures_order

set MESSAGE=auto commit %date% %time%

"%GIT_BIN%" add .
"%GIT_BIN%" commit -m "%MESSAGE%"
"%GIT_BIN%" push origin

