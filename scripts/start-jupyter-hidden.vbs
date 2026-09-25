Set WshShell = CreateObject("WScript.Shell")
' Set working directory to project
WshShell.CurrentDirectory = "D:\do_an_tot_nghiep"
' Start JupyterLab in hidden window with no browser popup
WshShell.Run "cmd.exe /c python -m jupyterlab --no-browser", 0, False
