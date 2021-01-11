# Starter Algo Rust

### File overview

    starter-algo-rust
    |
    ├--algo/src
    |  |
    |  ├--lib.rs
    |  ├--bounds.rs
    |  ├--gameloop.rs
    |  ├--grid.rs
    |  ├--io.rs
    |  ├--map.rs
    |  ├--messages.rs
    |  └--units.rs
    |
    └--starter-algo/src
       |
       └main.rs
       
### Creating an algo

For starters, simply modify the `starter-algo/src/main.rs` file. You will mostly be using
methods of `GameState` and `FrameData`.

The easiest way to test your algo locally is to run the `build_local.py` script with a Python
interpreter, then run the engine with the path `rust-algo/algo-target`. The `build_local.py`
script will build your algo based on the content in `algo.json`, then move the resultant
binary to the algo target directory. 

Our servers will essentially do the same thing when you upload your algo.
To upload your algo, upload the entire rust-algo folder on the myalgos page of the terminal site.
Note that the max upload size is limited, be carful not to include large build artifacts.

The simplest way to create an algo is to create a data type which stores your algo state,
implement `GameLoop` on it, and create a main function which calls `run_game_loop` on that
type.

The are three callbacks for `GameLoop` which you must implement:
```rust
    fn initialize(&mut self, config: Arc<Config>);

    fn on_action_frame(&mut self, config: Arc<Config>, map: &GameState);

    fn make_move(&mut self, config: Arc<Config>, map: &GameState);
```
The `initialize` callback is called once, at the beginning of the game, with the `Config` data 
that this algo has received and deserialized from the game engine.

The `on_action_frame` callback is called every action frame, and is given a `MapState`, an immutable 
and random-access representation of the state of the game that frame. The `MapState` also contains
the deserialized frame data for this frame, including player stats.

The `make_move` callback is called every turn frame, and is given mutable access to a 
`MapState`. Here, the algo should mutate the `MapState` by making valid
moves, such as spawning and removing units. The `MapState` records each spawn command that is
used to mutate it, and when `make_move` returns, those spawn commands will be submitted to the engine.

To generate programming documentation, run cargo doc in rust-algo. Then open index.html in rust-algo/target/doc/starter_algo

**The standard output is used to communicate with the game engine, and must not be printed to.**
For this reason, debugging must be done through `eprintln!`, and never `println!`. The standard
error messages are available on the playground.

Some people may find the `stderrlog` logging backend crate useful for this purpose.

### Example algo
```rust
extern crate algo;

use algo::{
    prelude::*,
    pathfinding::StartedAtWall,
};

fn main() {
    run_game_loop(ExampleAlgo);
}

/// An example algo which showcases the key features provided in this repository
struct ExampleAlgo;

impl GameLoop for ExampleAlgo {
    fn on_turn(&mut self, _: Arc<Config>, map: &MapState) {
        // callback to make a move in the game

        // try to place as many of four walls as possible
        for &wall_coord in &[
            xy(12, 5),
            xy(13, 5),
            xy(14, 5),
            xy(15, 5),
        ] {
            map[wall_coord].try_spawn(StructureUnitType::Wall);
        }

        // try to atomically place four scouts in two locations
        let scout_coord_1 = xy(6, 7);
        let scout_coord_2 = xy(21, 7);

        if map[scout_coord_1].can_spawn(MobileUnitType::Scout, 2).yes() &&
            map[scout_coord_2].can_spawn(MobileUnitType::Scout, 2).yes()
        {
            for _ in 0..2 {
                map[scout_coord_1].spawn(MobileUnitType::Scout)
                    .expect("Unexpected spawn failure");
                map[scout_coord_2].spawn(MobileUnitType::Scout)
                    .expect("Unexpected spawn failure");
            }
        }

        // if our cores are low, try to delete a structure
        if map.frame_data().p1_stats.cores < 5.0 &&
            map[xy(5, 5)].can_remove_structure().yes()
        {
            map[xy(5, 5)].remove_structure().unwrap();
        }

        // print the path that an enemy unit would take if spawned at a particular location
        let move_from = xy(13, 27);
        match map.pathfind(move_from, MapEdge::BottomRight) {
            Ok(path) => {
                eprintln!("Path from [13, 27] = {:?}", path)
            },
            Err(StartedAtWall(_, unit)) => {
                eprintln!("Enemy slot [13, 27] is blocked by {:?}", unit);
            }

        }
    }
}
```

### Running locally basics

1. Install rust. You can use this [link](https://www.rust-lang.org/tools/install) or search 'Install rust' on a search engine like google and follow the most up to date instructions to install rust on your machine.
2. Compile your algo. Move to the rust-algo working directory, run cargo build. Note that you need to repeat this step to recompile after making changes.
3. Run ```python ../scripts/run_match.py rust-algo/algo-target```

See the README in the scripts folder for more detailed information on running locally.

### Project structure

Rust starter algo is organized as a [Cargo workspace](https://doc.rust-lang.org/book/second-edition/ch14-03-cargo-workspaces.html).
This workspace starts with 4 packages:

- `algo`: a library that contains everything you need to create an algo, in terms of interacting with the game engine.
- `starter-algo`: the rust implementation of the starter algo
- `example`: the algo code in the readme
- `pathtest`: an executable that we use to verify that algos' pathfinding matches the engine pathfinding when we develop new algos

To create your own algo, you can either create your own package, or modify the starter-algo code. If you create your own package,
you will have to point to it in your `algo.json` metadata file. 

Rust's `algo.json` file can have these fields:

```rust
{
  "language": "rust",
  "rust-specific": {
    "release": false,
    "package": "starter-algo",
    "toolchain": "stable",
    "compile-target": "algo-target"
  }
}
```

- release: whether to run the build in release mode (enable optimizations)
    - this will make your code run faster, but it will take longer to compile
- package: this is the executable package that will be built
    - change this if you implement your strategy in a new package
- toolchain: which rust toolchain to compile with
    - can be stable, beta, or nightly
- compile-target: the directory which will be compiled to, then bundled
    
When you upload your algo to our servers, they will compile your code, and move the binary into the `algo-target` directory with 
the name `algo`. Any file in the `algo-target` directory at that point, will be accessible when your algo runs. `algo-target`
comes with a `run.sh` script, the entry point to all algos. You probably don't need to modify that.

If you ever change your build process such that you wish to build to some other directory than `algo-target`, you can simply 
change the target path in the `compile-target` field of `algo.json`.

### Code Patterns

Idiomatic Rust code is often able to use the type system and borrow checker to minimize points of runtime failure, and then use 
the type system to explicitly denote where these points of failure are. This presents a challenge with creating a terminal
algo, since essentially any operation performed in a move can fail for many reasons, including:

- An operation was performed on a tile which does not exist
- An operation was performed with a unit type which does not make sense
    - For example, asking how much is costs to spawn the "remove" unit type
- Attempting to spawn a unit on a tile which is blocked
- Attempting to spawn a unit without sufficient resources

The `algo` packages attacks the first two of these problems using the type and borrowing system.

#### Unit type

The `units` module contains several different types, each of which has variants for a subset of unit types.

- `UnitType`: an enum over all unit types, including remove
- `StructureUnitType`: an enum over all structure unit types
- `MobileUnitType`: an enum over all mobile unit types
- `RemoveUnitType`: a `()`-like struct denoting the remove unit type
- `SpawnableUnitType`: a union of `StructureUnitType` and `MobileUnitType`

These types are convertible into each other, both fallibly and infallibly, through the `Into` trait. For example, 
All unit types implement `Into<UnitType>`. Both `StructureUnitType`, `MobileUnitType`, and `SpawnableUnitType` implement 
`Into<SpawnableUnitType>`, but `RemoveUnitType` does not. 

This type system allows code which deals with units to be restrictive at compile-time over which unit types are allowed.
For example, the `Map`'s `cost_of` function accepts an `impl Into<SpawnableUnitType>`, allowing it to be called with 
any `MobileUnitType` or `StructureUnitType`, but never a `RemoveUnitType`.
