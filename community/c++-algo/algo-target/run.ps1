$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\StarterAlgo.exe"

Invoke-Expression $algoPath
