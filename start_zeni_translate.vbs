Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Run python server in background without console window
WshShell.Run "cmd /c cd /d """ & strPath & """ && python app.py", 0, False

' Wait 2 seconds for server to start, then open website in browser
WScript.Sleep 2000
WshShell.Run "http://127.0.0.1:5050"
