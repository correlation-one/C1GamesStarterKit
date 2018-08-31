# Python Starter Algo

You should only need to modify `algo_strategy.py` to implement your strategy,
however looking at other files may help you understand the game structure,
and create more complex and efficient algos

## Submitting your bot

Run the `archive_algo.sh` script while your working directory is inside the git
repository:

    cd path/to/repos/starter-algo
    ./archive_algo.sh

The script will generate a file at `~/my-algo-archive.zip` which you can
upload through the web interface.

## File Overview

### `algo_strategy.py`

This file contains the `AlgoStrategy` class which you should modify to implement
your strategy.

At a minimum you must implement the `step` method which handles responding to
the game state for each turn since the default implementation simply ends the
turn without doing anything. Refer to the included starter strategy for
inspiration.

If your algo requires initialization then you should also implement the
`process_config` method an do any inital setup there.

### `run.sh`

A script that contains logic to invoke your code. You shouldn't need to change
this unless you change file structure or require a more customized process
startup.

### `gamelib/__init__.py`

This file tells python to treat `gamelib` as a bundled python module. This
library of functions and classes is intended to simplify development by
handling tedious tasks such as communication with the game engine, summarizing
the latest turn, and estimating paths based on the latest board state.

### `gamelib/algocore.py`

This file contains code implementing the communication between the algo and the
core game logic module so that your algo doesn't need to implement it. You
shouldn't need to change this directly, just overwrite the core methods that you
would like to behave differently. 

### `gamelib/game.py`

This module contains the `GameMap` class which is used to parse the game state
and provide functions for querying it. It also contains the `GameUnit` class as
well as several helper functions for game logic.

### `gamelib/navigation.py`

Functions and classes used to implement pathfinding.

### `gamelib/tests.py`

Unit tests. You can write your own if you would like, and can run them using
the following command:

    python3 -m unittest discover

### `gamelib/util.py`

Helper functions and values that do not yet have a better place to live.

## Strategy Overview

The starter strategy is designed to highlight a few common game_map functions
and give the user a functioning example to work with. It's gameplan is to 
draw the C1 logo using firewalls on its first turn, then make random moves
on later turns. To show more game_map functions in a non-arbitrary way, 
the strategy takes information about the game state into account, and 
uses it to adjust the probability that it will randomly spawn a given unit.
