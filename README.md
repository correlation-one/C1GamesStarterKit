# C1GamesStarterKit

Welcome to the C1 Starter Kit! This collection of scripts and an example `starter-algo` should help
you start on your journey to developing the ultimate algo.

For more details about competitions and the game itself please check out our
[main site](https://terminal.c1games.com/rules).

## First Time Walkthrough

1. We recommend familiarizing yourself with the game and creating a strategy through playing by
hand before starting your algo.

1. In order to run the the game locally [java jdk](http://www.oracle.com/technetwork/java/javase/downloads/jdk10-downloads-4416644.html) version 10 or above must be installed. You may need to restart your shell after installing or updating dependencies. If using the python starter-algo Python3 must be installed and the command `python3` for unix or `py -3` for windows must work. If you are on windows `powershell` is required but should come pre-installed on your windows OS. All commands on windows should be run using the `powershell`. Additionally, some windows users might need to run the following powershell command in adminstrator mode (simply right click powershell and hit run as adminstrator):
    ```
    Set-ExecutionPolicy Unrestricted
    ```
    If this doesn't work try:
    ```
    Set-ExecutionPolicy Unrestricted CurrentUser
    ```

1. First try running a match with the default starter-algo using our CLI. You can also leave arguments blank and it will default to the starter-algo.

You can use the new run_match.py script to run on any OS that is more robust than the other run_match scripts.

    ```
    Windows:
    py run_match.py 
    or
    py run_match.py C:\Users\Junaid\Downloads\starterKitClone\C1GamesStarterKit\algos\starter-algo
    or
    py run_match.py C:\Users\Junaid\Downloads\starterKitClone\C1GamesStarterKit\algos\starter-algo C:\Users\Junaid\Downloads\starterKitClone\C1GamesStarterKit\algos\starter-algo

    Unix:
    python3 run_match.py
    or
    python3 run_match.py /Users/junaid/Documents/C1GamesStarterKit/algos/starter-algo
    or
    python3 run_match.py /Users/junaid/Documents/C1GamesStarterKit/algos/starter-algo /Users/junaid/Documents/C1GamesStarterKit/algos/starter-algo

    scripts/run_match.sh
    or
    scripts/run_match.sh algos/starter-algo algos/my-algo

    Windows:
    scripts\run_match.ps1
    or
    scripts\run_match.ps1 algos\starter-algo algos\starter-algo
    ```
   
1. Once you are ready, create your own Algo by forking the example `starter-algo` to serve as a base
for you to develop your own strategy in. You can use the below script if on unix or simply copy paste the folder.

    `scripts/fork_algo.sh algos/starter-algo algos/my-algo`

1. Open `algo_strategy.py` in your new algo using the editor of your choice and create your strategy
using the functions provided in gamelib. The provided strategy has examples with explanations on how
to do this.

1. When you are ready to post your algo, you can use the CLI to archive it if in unix. Or simply right click it and use built in compression methods for your OS. Save it as a zip with a filename
that matches how you want your algo to be identified to other users on the site.

    `scripts/archive_algo.sh algos/my-algo dist/my-algo.zip`

1. You can upload the zipped algo on the "My Algos" page of the terminal site, then that’s it! Your
zipped algo will automatically begin playing in matches and can be selected as your entry in any
competitions you are eligible for. You can also play with or against it in Play mode.

Check out all of the [C1 CLI Commands][C1 CLI Commands] to learn how to create, run and upload your
algos!

## Documentation for Creators

### Concepts and Data Structures

#### `location`

A list with two integers corresponding to the x, y coordinate of a tile in the grid
- Example: [9,13]

#### `player_index`

0 indicates you, 1 indicates your opponent

#### GameState

This class is a representation of the current game state, and contains many helper methods to
simplify placing units, determining paths, and other common actions. The starting strategy many
algos are based off of creates `game_state`, which can be used to access these methods. Examples
of using `game_map` to use these methods can be seen within the starter strategy.

#### GameMap

This class holds information about the current location of units on the game map, and has functions to help you interact with the map

#### GameUnit

The GameUnit class represents one unit. You will most often access it by getting the list of units on a given tile via game_map.map[x,y] then getting a unit from this list.

### StarterKit Files

```
C1GamesStarterKit
│
├── README.md                                   // General StarterKit Overview
├── engine.jar                                  // Game Engine Executable
├── game-configs.json                           // Game Configs
│
├── algos                                       // src directory for your algos
│   │
│   └── starter-algo                            // basic starter-algo
│       ├── gamelib                             // core api, classes, and methods for starter-algo
│       │   ├── __init__.py
│       │   ├── advanced.py
│       │   ├── algocore.py
│       │   ├── game.py
│       │   ├── map.py
│       │   ├── navigation.py
│       │   ├── tests.py
│       │   ├── unit.py
│       │   └── util.py
│       │
│       ├── README.md                           // detailed starter-algo and gammelib documentation
│       ├── algo_strategy.py                    // basic strategy for starter-algo (required)
│       └── run.sh                              // entry point for algo (required)
│
├── dist                                        // directory where archived algos get saved
│   └── starter-algo.zip
│
├── docs                                        // more detailed guides/documentation
│   └── C1_CLI_COMMANDS.md
│
├── replays                                     // where match replay files from player one's perspective get saved
│   ├── p1-DD-MM-YYYY-HH-MM-SS-UUID.replay      // replay file, ready to watch at https://terminal.c1games.com/playground
│   └── p1-DD-MM-YYYY-HH-MM-SS-UUID.replay      
│
└── scripts                                     // Helpful commands/scripts
    ├── archive_algo.sh
    ├── fork_algo.sh
    └── run_match.sh
```

[C1 CLI Commands]: https://github.com/correlation-one/C1GamesStarterKit/blob/master/docs/C1_CLI_COMMANDS.md
