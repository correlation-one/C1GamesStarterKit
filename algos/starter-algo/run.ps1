$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\algo_strategy.py"

py -3 $algoPath

while ($true) {
	Start-Sleep -Seconds 5
}