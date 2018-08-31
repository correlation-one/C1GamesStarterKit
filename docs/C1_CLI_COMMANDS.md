## C1 CLI Commands

#### Run Match

`$ scripts/run_match.sh`   

`$ scripts/run_match.sh <path/to/algo1> <path/to/algo2>`

`$ scripts/run_match.sh algos/starter-algo algos/renamed-algo`


#### Archive Algo

`$ scripts/archive_algo.sh`

`$ scripts/archive_algo.sh <output/path/algo.zip> <input/path/algo>`

`$ scripts/archive_algo.sh dist/renamed-algo.zip algos/renamed-algo`


## TODO

#### Pre-Upload Test for an algo (final check to make sure everything looks good)

#### Boss Gauntlet (Run an algo agianst bosses in order until a loss)

#### Round Robin (Run all algos agianst eachother and output rank order)

#### Hide ugly shell scripts behind a sexy c1 namespace like:  

```
$ c1 match algo1 algo2
$ c1 hot-zip -watch
$ c1 test algo1

etc.
```