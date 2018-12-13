$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\algo.exe"

Start-Process $algoPath -NoNewWindow -Wait