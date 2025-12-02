Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts"
WshShell.Run "pythonw ehko_control.py", 0, False
