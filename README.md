# AIGamesStarterKit

## StarterKit Files

```
AIGamesStarterKit
 │
 ├──algos                                       // src directory for your algos
 │   ├──renamed-algo                            // a renamed starter-algo for you to customize
 │   └──starter-algo                            // basic starter-algo
 │       │          
 │       ├──gamelib                             // core api, classes, and methods for starter-algo
 │       │    ├──__init__.py
 │       │    ├──advanced.py
 │       │    ├──algocore.py
 │       │    ├──game.py
 │       │    ├──map.py
 │       │    ├──navigation.py                 
 │       │    ├──tests.py
 │       │    ├──unit.py
 │       │    └──util.py
 │       │ 
 │       ├──algo_strategy.py                    // basic strategy for starter-algo 
 │       ├──README.md                           // detailed starter-algo documentation
 │       └──run.sh                              // entry point for starter-algo (required)
 │ 
 ├──dist                                        // directory where archived algos get saved 
 │   ├──renamed-algo.zip                        // archived renamed-algo (ready to upload)
 │   └──starter-algo.zip                        
 │ 
 ├──docs                                        // more detailed guides/documentation
 │   ├──ALGO_CREATION_GUIDE.md
 │   └──C1_CLI_COMMANDS.md
 │ 
 ├──replays                                     // where match replay files get saved
 │   ├──p1-DD-MM-YYYY-HH-MM-SS-UUID.replay      // replay file (ready to upload/watch on c1games.com)
 │   └──p1-DD-MM-YYYY-HH-MM-SS-UUID.replay      
 │ 
 ├──scripts                                     // Helpful commands/scripts
 │   ├──archive_algo.sh
 │   └──run_match.sh
 │ 
 ├──engine.jar                                  // Game Engine Executable
 ├──game-configs.json                           // Game Configs
 └──README.md                                   // General StarterKit Overview
```

## Getting started

Start implementing your own strategy by modifying `algo_strategy.py` inside of algos/renamed-algo. 
Check out the [Algo Creation Guide](https://github.com/correlation-one/AIGamesStarterKit/blob/dev/docs/ALGO_CREATION_GUIDE.md) for more information.


## Using the C1 CLI

### Running matches locally between algos

Easily run a match between two local algos using the `run_match.sh` script. The resulting replay file
will be saved in the /replays directory and can be uploaded and watched on terminal.c1games.com/play.

`$ scripts/run_match.sh path/to/algo1 path/to/algo2`

### Uploading your algo

Zip the entire algo directory or run the `archive_algo.sh` script to zip an algo. It will be saved in 
the /dist directory and can then be uploaded on terminal.c1games.com/myalgos to compete in ranked matches.

`$ scripts/archive_algo.sh dist/renamed-algo.zip algos/renamed-algo`

Check out all the [C1 CLI Commands](https://github.com/correlation-one/AIGamesStarterKit/blob/dev/docs/C1_CLI_COMMANDS.md) for more information.


## Custom Config

Customize the "debug" values in game-configs.json to control 
the level of error/debug information printed during a match.


