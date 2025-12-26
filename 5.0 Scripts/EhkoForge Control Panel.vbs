' EhkoLabs Control Panel Launcher v5.1
' Runs the control panel without a visible command prompt
' Double-click this file to launch

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Set working directory
ScriptDir = "C:\EhkoVaults\EhkoForge\5.0 Scripts"
WshShell.CurrentDirectory = ScriptDir

' Use pythonw to avoid console window
' If pythonw doesn't work, fall back to python with hidden window
PythonScript = ScriptDir & "\ehko_control.py"

If FSO.FileExists(PythonScript) Then
    ' Try pythonw first (no console)
    WshShell.Run "pythonw """ & PythonScript & """", 0, False
Else
    MsgBox "Control panel script not found:" & vbCrLf & PythonScript, vbCritical, "EhkoLabs"
End If

Set FSO = Nothing
Set WshShell = Nothing
