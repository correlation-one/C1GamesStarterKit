$defaultAlgo="$pwd\python-algo"
if (!$args[0]) { $algo1="$defaultAlgo\run.ps1" } else { $algo1="$($args[0])\run.ps1"}
if (!$args[1]) { $algo2="$defaultAlgo\run.ps1" } else { $algo2="$($args[1])\run.ps1"}

echo p1: $algo1
echo p2: $algo2

java -jar engine.jar work $algo1 $algo2