$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path -Path $DesktopPath -ChildPath "Zeni Translate.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "d:\translate language\start_zeni_translate.vbs"
$Shortcut.WorkingDirectory = "d:\translate language"
$Shortcut.Description = "Launch Zeni Translate Web Application"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $ShortcutPath"
