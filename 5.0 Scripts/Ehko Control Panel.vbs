' Ehko Control Panel Launcher
' Launches the Ehko Control Panel (Python GUI) with no console window

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

ScriptDir = "C:\EhkoVaults\EhkoForge\5.0 Scripts"
PythonScript = ScriptDir & "\ehko_control.py"

If FSO.FileExists(PythonScript) Then
    WshShell.CurrentDirectory = ScriptDir
    ' Run with window style 0 (hidden) to prevent any console windows
    WshShell.Run "pythonw.exe """ & PythonScript & """", 0, False
Else
    MsgBox "Control panel script not found at: " & PythonScript, 16, "Error"
End If
