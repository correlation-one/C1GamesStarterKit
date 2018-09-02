# C1 CLI Commands

## Forking a Local Algo

Copy the `starter-algo` to start your own bot, or duplicate a local algo to pursue an alternative
line of development:

    $ scripts/fork_algo.sh <path/to/algo1> <path/to/algo2>

### Concrete Examples

    $ scripts/fork_algo.sh algos/starter-algo algos/renamed-algo

## Run Match

Play a match between two local algos, the replay from Player One's perspective will be saved in
`replays/`:

    $ scripts/run_match.sh <path/to/algo1> <path/to/algo2>

### Concrete Examples

    $ scripts/run_match.sh algos/starter-algo algos/renamed-algo

## Archive Algo

Run the archive script to prepare an algo for upload:

    $ scripts/archive_algo.sh <input/path/algo> <output/path/algo.zip>

### Concrete Examples

    $ scripts/archive_algo.sh algos/renamed-algo dist/renamed-algo.zip

