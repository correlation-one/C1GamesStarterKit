# AIGamesStarterKit

# Step-by-step Startup:
1. We reccomend familiarizing yourself with the game and creating a strategy by playing by hand before starting your bot
2. Once you are ready, open algo-strategy in starter-algo using an editor of your choice, and create your strategy using the functions provided in gamelib (The provided strategy has examples with explinations on how to do this)
3. When you are ready, you can test your bot using our Command Line Interface, detailed below
4. Once you are finished, you can zip starter-algo and rename the zip (This name will be the name of your algo, and is visable to other users)
5. That’s it! Your zipped algo is ready to compete in the arena! You can upload it on the "My Algos" page on the terminal site

# Detailed Documentation for Creators

## Some of the common parameters taken or returned by functions

### Location:
A list with two integers corresponding to the x, y coordinate of a tile in the grid
- Example: [9,13]

### player_index:
0 indicates you, 1 indicates your opponent

## GameState
This class is a representation of the current game state, and contains many helper methods to simplify placing units, determining paths, and other common actions.
The starting strategy many algos are based off of creates 'game_state', which can be used to access these methods. Examples of using game_map to use these methods can be seen within the starter strategy.

##GameMap
This class holds information about the current location of units on the game map, and has functions to help you interact with the map

## GameUnit
The GameUnit class represents one unit. You will most often access it by getting the list of units on a given tile via game_map.map[x,y] then getting a unit from this list.

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
 │       ├──README.md                           // detailed starter-algo and gammelib documentation
 │       └──run.sh                              // entry point for algo (required)
 │ 
 ├──dist                                        // directory where archived algos get saved 
 │   ├──renamed-algo.zip                        // archived algo (ready to upload)
 │   └──starter-algo.zip                        
 │ 
 ├──docs                                        // more detailed guides/documentation
 │   ├──ALGO_CREATION_GUIDE.md
 │   └──C1_CLI_COMMANDS.md
 │ 
 ├──replays                                     // where match replay files get saved
 │   ├──p1-DD-MM-YYYY-HH-MM-SS-UUID.replay      // replay file (ready to upload/watch on terminal.c1games.com)
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

## Using the C1 CLI
In the below examples, we assume your working directory is AIGamesStarterKit and you are storing your algos in the algos/ directory

### Running matches locally between algos
Easily run a match between two local algos using the `run_match.sh` script. The resulting replay file
will be saved in the replays/ directory and can be uploaded and watched on terminal.c1games.com/play.

For example, if you wanted to run starter_algo against a renamed_algo of your own creation in the command line,
you can cd into the AIGamesStarterKit and run the following command:

    $ scripts/run_match.sh algos/starter_algo algos/renamed_algo

This will also save a replay file in replays/, which you can upload on our site to watch your game

### Uploading your algo
Zip the entire algo directory or run the `archive_algo.sh` script to zip an algo. It will be saved in
the /dist directory and can then be uploaded on terminal.c1games.com/myalgos to compete in ranked matches.

While using AIGamesStarterKit as your working directory, to zip an algo in the algos folder, you can use

    $ scripts/archive_algo.sh dist/renamed-algo.zip algos/renamed-algo

Check out all the [C1 CLI Commands](https://github.com/correlation-one/AIGamesStarterKit/blob/dev/docs/C1_CLI_COMMANDS.md) for more information.

## Custom Config

Customize the "debug" values in game-configs.json to control the level of error/debug information printed during a match.
