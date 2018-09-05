# C1GamesStarterKit

Welcome to the C1 Starter Kit! This collection of scripts and an example `starter-algo` should help
you start on your journey to developing the ultimate algo.

For more details about competitions and the game itself please check out our
[main site](https://terminal.c1games.com/rules).

## First Time Walkthrough

1. We recommend familiarizing yourself with the game and creating a strategy through playing by
hand before starting your algo.
2. Once you are ready, open algo-strategy in starter-algo using the editor of your choice and
create your strategy using the functions provided in gamelib. The provided strategy has examples
with explanations on how to do this.
3. Explore changes to your algo by running matches using our Command Line Interface, detailed below.
4. When you are ready to test your algo, you can use the CLI to archive the algo, saving it as a zip
with the desired algo name that is visible to other users.
5. You can upload it on the "My Algos" page of the terminal site, then that’s it! Your zipped algo
will automatically begin playing in matches.

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

Check out all of the [C1 CLI Commands](https://github.com/correlation-one/C1GamesStarterKit/blob/master/docs/C1_CLI_COMMANDS.md) to learn how to create, run and upload your algos!
