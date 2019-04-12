# Starter Algo C++

#### NOTE: This project is currently being developed, and is NOT supported by C1's servers yet.
This means you currently cannot upload this algo to their servers, it will not work.
However, if you have a linux OS it is possible compile and upload your compiled version and have it run.
This compilation will not work in the playground.

### Directory Overview

```
community/c++-algo
│
├───algo-target
│       run.ps1
│       run.sh
│
├───build
│
├───include
│   ├───GameLib
│   │   │
│   │   └───src
│   │           algoCore.cpp
│   │           algoCore.h
│   │           customExceptions.h
│   │           enums.h
│   │           gameMap.cpp
│   │           gameMap.h
│   │           gameState.cpp
│   │           gameState.h
│   │           navigation.cpp
│   │           navigation.h
│   │           structs.h
│   │           unit.cpp
│   │           unit.h
│   │           util.cpp
│   │           util.h
│   │
│   └───json11
│
└───src
        algoStrategy.cpp
        algoStrategy.h
        source.cpp
```


### Creating an algo

For starters, simply modify the `src/algoStrategy.cpp` files. You will be mostly using functions in the `GameState` class.

The `GameState` provides fast and convenient access to the game board, and the ability to perform actions, such as placing a 
unit, which will mutate the `GameState` game state, as well as record that action. The GameState can then be used to submit your changes to the engine.

**The standard output is used to communicate with the game engine, and must not be printed to.**
For this reason, debugging must be done with the standard error. The standard error messages are 
available on the playground. As an abstraction over this logic, the `Util` method `debugWrite()` prints to the standard error stream.

This project is intentionally modeled after the python-algo to make it familiar to those who are either new to programming in C++ or have been coding with terminal for a while.

### Build script

Since compiling will be different for every user, this is a CMake project to build for multiple enviornments.
This means for whatever enviornemnt you are using, you will need to install CMake (found [here](https://cmake.org/download/)).
In order to compile your algo, create a `build` directory under the `C1GamesStarterKit` directory and then run `cmake`.
Thus, the steps to setup a completely new enviornment would be (in terminal or cmd):
```
C1GamesStarterKit\community\c++-algo> mkdir build
C1GamesStarterKit\community\c++-algo> cd build
C1GamesStarterKit\community\c++-algo\build> cmake ..
```
(the commands are only after the `>`).

This will create a project depending on what system you have avalible.
For example, if you have Visual Studio, it will generate a .sln project inside of `build` and you can then open
the project and build it.
If you are running linux, or something that supports makefiles, then while in the `build` directory you simply run:
```
make
```

In all cases, the target for your executable is inside `c++-algo\algo-target`.

Thus, to run a local game, you would give it the directory `community\c++-algo\algo-target`.

### Contributing

This is a community made and supported algo. If you'd like to contribute a new feature
just reach out to me (@Isaac) on the [C1 forums](https://forum.c1games.com/) or submit a pull request with your changes.

Feel free to submit a Pull Request for any bugs or new features, but please try and follow the style of the rest of the project.
