$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\algo_strategy.py"

java -jar $algoPath