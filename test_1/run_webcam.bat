@echo off
title VSL Live Sign Language Camera Inference
cd /d "D:\do_an_tot_nghiep"
echo =======================================================
echo   KHOI DONG HE THONG NHAN DIEN CU CHI VSL QUA WEBCAM
echo =======================================================
echo Dang nap moi truong Python .venv va bo nao AI...
echo Nhan 'q' tren cua so camera de thoat.
echo Nhan 'c' de xoa cau hien tai.
echo Nhan '[' hoac ']' de tang/giam nguong nhan dien.
echo =======================================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { & '.\.venv\Scripts\python.exe' src/inference_webcam.py | Tee-Object -FilePath 'webcam_live.log' }"
if errorlevel 1 (
    echo.
    echo [ERROR] Co loi phat sinh khi chay camera inference.
    pause
)
