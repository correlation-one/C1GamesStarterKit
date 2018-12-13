$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\algo.jar"

java -jar $algoPath