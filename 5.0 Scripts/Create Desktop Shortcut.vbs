' Create Desktop Shortcut for Ehko Control Panel
' This script creates a proper .lnk shortcut with an icon

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' Get desktop path
Desktop = WshShell.SpecialFolders("Desktop")

' Create the shortcut
Set Shortcut = WshShell.CreateShortcut(Desktop & "\Ehko Control Panel.lnk")

' Set shortcut properties
LauncherPath = "C:\EhkoVaults\EhkoForge\5.0 Scripts\Ehko Control Panel.vbs"

If FSO.FileExists(LauncherPath) Then
    Shortcut.TargetPath = LauncherPath
    Shortcut.WorkingDirectory = "C:\EhkoVaults\EhkoForge\5.0 Scripts"
    Shortcut.Description = "Ehko Control Panel v5.1 - Unified EhkoForge, ReCog, Website Control"
    ' Use terminal/command prompt icon from shell32.dll (icon 24)
    Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,24"
    Shortcut.Save
    
    MsgBox "Desktop shortcut created successfully!", 64, "Success"
Else
    MsgBox "Launcher not found at: " & LauncherPath & vbCrLf & vbCrLf & "Creating it now...", 48, "Notice"
    
    ' Create the launcher
    Set LauncherFile = FSO.CreateTextFile(LauncherPath, True)
    LauncherFile.WriteLine "' Ehko Control Panel Launcher"
    LauncherFile.WriteLine "' Launches the Ehko Control Panel (Python GUI) with no console window"
    LauncherFile.WriteLine ""
    LauncherFile.WriteLine "Set WshShell = CreateObject(""WScript.Shell"")"
    LauncherFile.WriteLine "Set FSO = CreateObject(""Scripting.FileSystemObject"")"
    LauncherFile.WriteLine ""
    LauncherFile.WriteLine "ScriptDir = ""C:\EhkoVaults\EhkoForge\5.0 Scripts"""
    LauncherFile.WriteLine "PythonScript = ScriptDir & ""\ehko_control.py"""
    LauncherFile.WriteLine ""
    LauncherFile.WriteLine "If FSO.FileExists(PythonScript) Then"
    LauncherFile.WriteLine "    WshShell.CurrentDirectory = ScriptDir"
    LauncherFile.WriteLine "    ' Run with window style 0 (hidden) to prevent any console windows"
    LauncherFile.WriteLine "    WshShell.Run ""pythonw.exe """" & PythonScript & """""", 0, False"
    LauncherFile.WriteLine "Else"
    LauncherFile.WriteLine "    MsgBox ""Control panel script not found at: "" & PythonScript, 16, ""Error"""
    LauncherFile.WriteLine "End If"
    LauncherFile.Close
    
    ' Now create shortcut
    Shortcut.TargetPath = LauncherPath
    Shortcut.WorkingDirectory = "C:\EhkoVaults\EhkoForge\5.0 Scripts"
    Shortcut.Description = "Ehko Control Panel v5.1 - Unified EhkoForge, ReCog, Website Control"
    Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,24"
    Shortcut.Save
    
    MsgBox "Launcher created and desktop shortcut added!", 64, "Success"
End If
