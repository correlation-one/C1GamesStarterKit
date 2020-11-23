# Starter Algo Java

### Directory Overview

    starter-algo-java
    |
    ├--algo
    |
    ├--src
    |   |
    |   ├--main/java/com/c1games/terminal
    |   |   |
    |   |   ├--algo
    |   |   |   |
    |   |   |   ├--io
    |   |   |   ├--map
    |   |   |   ├--pathfinding
    |   |   |   ├--serialization
    |   |   |   └--units
    |   |   |
    |   |   ├--pathtest
    |   |   └--starteralgo
    |   |
    |   └--test/java
    |
    └--gradle build files

### Creating an algo

For starters, simply modify the `starteralgo/StarterAlgo.java` file. You will be mostly using functions in the `GameState`
and `FrameData` classes. To build locally simple run `./gradlew build` (use gradlew.bat for windows) in this directory.
Your algo will build to the folder `algo-target`. Use the run scripts in `C1GamesStarterKit/scripts` and point to the 
`algo-target` folder.
To submit to terminal.c1games.com upload the entire java-algo folder.

All that is necessary to create an algo is to implement `GameLoop`, and create a main method 
which wraps your `GameLoop` in a `GameLoopDriver` and `.run()`s it.

There are three callbacks for `GameLoop` which you can implement

    void initialize(GameIO io, Config config)
    
    void onActionFrame(GameIO io, GameState move)
    
    void onTurn(GameIO io, GameState move)

However, it is only essential to implement `onTurn`. The `GameState` provides fast and 
convenient access to the game board, and the ability to perform actions, such as placing a 
unit, which will mutate the `GameState` game state, as well as record that action. When 
`onTurn` returns, the recorded actions will be submitted to the game.

To generate programming documentation, run gradle javadoc in java-algo. Then open index.html in java-algo/build/docs/javadoc

**The standard output is used to communicate with the game engine, and must not be printed to.**
For this reason, debugging must be done with the standard error. The standard error messages are 
available on the playground. As an abstraction over this logic, the `GameIO` method `debug()` 
returns a `PrintStream` which can be safely used for logging.

### Example Algo

    // an example algo which showcases the key features provided in this repository
    public class ExampleAlgo implements GameLoop {
        public static void main(String[] args) {
            // entry point to the algo
            new GameLoopDriver(new ExampleAlgo()).run();
        }
    
        // callback to make a move in the game
        @Override
        public void onTurn(GameIO io, GameState move) {
            // try to place as many of four walls as possible
            List<Coords> wallLocations = List.of(new Coords(12, 5), new Coords(13, 5),
                    new Coords(14, 5), new Coords(15, 5));
            int wallsPlaced = move.attemptSpawnMultiple(wallLocations, UnitType.Wall);
            io.debug().println("Placed " + wallsPlaced + " walls");
    
            // try to atomically place four scouts in two locations
            if (
                    move.canSpawn(new Coords(6, 7), UnitType.Scout, 2).affirmative() &&
                            move.canSpawn(new Coords(21, 7), UnitType.Scout, 2).affirmative()
            ) {
                try {
                    for (int i = 0; i < 2; i++) {
                        move.spawn(new Coords(6, 7), UnitType.Scout);
                        move.spawn(new Coords(21, 7), UnitType.Scout);
                    }
                } catch (CannotSpawnException e) {
                    // debug on failure
                    io.debug().println("Unexpected CannotSpawnException");
                    e.printStackTrace(io.debug());
                }
            }
    
            // if our cores are low, try to delete a Structure
            if (move.data.p1Stats.cores < 5 && move.canRemoveStructure(new Coords(5, 5)).affirmative()) {
                move.removeStructure(new Coords(5, 5));
            }
    
            // print the path that an enemy unit would take if spawned at a particular location
            if (move.getWallAt(new Coords(13, 27)) == null) {
                List<Coords> path = move.pathfind(new Coords(13, 27), MapBounds.EDGE_BOTTOM_RIGHT);
                io.debug().println("Path from (13, 27) = " + path);
            } else {
                io.debug().println("Enemy slot (13, 27) is blocked");
            }
        }
    }

### Map Bounds

The `MapBounds` class contains statically initialized data pertaining to the structure of the 
map, including the board size, which cells are on which edges, which cells are in the arena, and 
the four integer edge direction constants, `EDGE_TOP_LEFT`, `EDGE_BOTTOM_RIGHT`, etc.

### Path Finding

The `GameState` method `pathfind(Coords start, int targetEdge)` returns the path that a particular 
mobile unit will take through the current configuration of the board, where `targetEdge` is one 
direction constant from `MapBounds`. This is guaranteed to produce accurate results, but is intentionally 
left less than maximally optimized.

### Build script

Java algos use gradle build scripts for compilation. Gradle is already set up in the starter algo, but 
the scripts can be modified if necessary, such as to add dependencies. When your algo is compiled on 
our servers, the command `./gradlew build` will be executed, which will build `algo-target/algo.jar`. Next to 
`algo-target/algo.jar` is `algo-target/run.sh`. Any algo from any language uses a `run.sh` script as an entry point, 
and this `run.sh` simply starts `algo.jar`. After this command finishes, the entire `algo-target` directory will 
be zipped, and this will be distributed to playground and ranked matches.

If you create your algo by modifying `src/main/java/com/c1games/terminal/starteralgo/StarterAlgo.java`, 
then you can simply upload or compile. **If you create a new main method, in a new class file, for 
your algo, you will have to modify the `mainClassName` in the `build.gradle` file.** It is currently set to:

    // Define the main class for the application
    mainClassName = 'com.c1games.terminal.starteralgo.StarterAlgo'

If you change your build process such that you are no longer building to the directory `algo-target`, you can
configure the path which will be packaged with the `compile-target` field in `algo.json`.

To build the doc strings: `./gradlew javadoc`

### Unit tests

The gradle build script is set up to perform `JUnit` unit tests. These test are in the `src/test/java` directory. 
To run unit tests, simple call `./gradlew test`.
