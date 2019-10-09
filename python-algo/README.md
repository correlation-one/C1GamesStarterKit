# Starter Algo

## File Overview

```
starter-algo
 │
 ├──gamelib
 │   ├──__init__.py
 │   ├──algocore.py
 │   ├──game_map.py
 │   ├──game_state.py
 │   ├──navigation.py
 │   ├──tests.py
 │   ├──unit.py
 │   └──util.py
 │
 ├──algo_strategy.py
 ├──documentation
 ├──README.md
 ├──run.ps1
 └──run.sh
```

### Creating an Algo

To create an algo, simply modify the `algo_strategy.py` file.

### `algo_strategy.py`

This file contains the `AlgoStrategy` class which you should modify to implement
your strategy.

At a minimum you must implement the `on_turn` method which handles responding to
the game state for each turn. Refer to the `starter_strategy` method for inspiration.

If your algo requires initialization then you should also implement the
`on_game_start` method and do any inital setup there.

### `documentation`

A directory containing the sphinx generated documentation, as well as the files required
to build it. You can view the docs at https://docs.c1games.com, or by opening index.html
in documents/_build. You can remake the documentation by running 'make html' in the documentation folder.

### `run.sh`

A script that contains logic to invoke your code. You do not need to run this directly.
See the 'scripts' folder in the Starterkit for information about testing locally. 

### `run.ps1`

A script that contains logic to invoke your code. You shouldn't need to change
this unless you change file structure or require a more customized process
startup. 

### `gamelib/__init__.py`

This file tells python to treat `gamelib` as a bundled python module. This
library of functions and classes is intended to simplify development by
handling tedious tasks such as communication with the game engine, summarizing
the latest turn, and estimating paths based on the latest board state.

### `gamelib/algocore.py`

This file contains code that handles the communication between your algo and the
core game logic module. You shouldn't need to change this directly. Feel free to 
just overwrite the core methods that you would like to behave differently. 

### `gamelib/game_map.py`

This module contains the `GameMap` class which is used to parse the game state
and provide functions for querying it. 

### `gamelib/navigation.py`

Functions and classes used to implement pathfinding.

### `gamelib/tests.py`

Unit tests. You can write your own if you would like, and can run them using
the following command:

    python3 -m unittest discover

### `gamelib/unit.py`

This module contains the `GameUnit` class which holds information about a Unit.

### `gamelib/util.py`

Helper functions and values that do not yet have a better place to live.

## Strategy Overview

The starter strategy is designed to highlight a few common `GameMap` functions
and give the user a functioning example to work with. It's gameplan is to 
draw the C1 logo, place destructors in its corners, and randomly spawn encryptors
and units.
