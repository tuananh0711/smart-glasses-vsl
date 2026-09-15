@echo off
title TEST AI KINH THONG MINH
cd /d D:\do_an_tot_nghiep
echo ========================================================
echo DANG KHOI DONG HE THONG NHAN DIEN KINH THONG MINH (WEBCAM)
echo ========================================================
echo Dang nap mo hinh AI va khoi dong camera...
.\.venv\Scripts\python.exe src\inference_webcam.py
pause

