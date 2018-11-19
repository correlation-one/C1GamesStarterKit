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

The simplest way to create an algo is to create a data type which stores your algo state, 
implement `GameLoop` on it, and create a main function which calls `run_game_loop` on that 
type.

The are three callbacks for `GameLoop` which you must implement:
```rust
    fn initialize(&mut self, config: Arc<Config>);

    fn on_action_frame(&mut self, config: Arc<Config>, map: Map);

    fn make_move(&mut self, config: Arc<Config>, move_builder: &mut MoveBuilder);
```
The `initialize` callback is called once, at the beginning of the game, with the `Config` data 
that this algo has received and deserialized from the game engine.

The `on_action_frame` callback is called every action frame, and is given a `Map`, an immutable 
and random-access representation of the state of the game that frame. The `Map` also contains
the deserialized frame data for this frame, including player stats.

The `make_move` callback is called every turn frame, and is given mutable access to a 
`MoveBuilder`. The `MoveBuilder` contains a `Map`, and is able to mutate the `Map` by making valid
moves, such as spawning and removing units. The `MoveBuilder` records each spawn command that is
used to mutate it, and when `make_move` returns, those spawn commands will be submitted to the engine.

**The standard output is used to communicate with the game engine, and must not be printed to.**
For this reason, debugging must be done through `eprintln!`, and never `println!`. The standard
error messages are available on the playground.

### Example algo
```rust
    #[macro_use]
    extern crate algo;
    
    use algo::prelude::*;
    
    fn main() {
        // entry point to the algo
        run_game_loop(ExampleAlgo);
    }
    
    // an example algo which showcases the key features provided in this repository
    struct ExampleAlgo;
    impl GameLoop for ExampleAlgo {
        fn initialize(&mut self, _: Arc<Config>) {}
    
        fn on_action_frame(&mut self, _: Arc<Config>, _: Map) {}
    
        // callback to make a move in the game
        fn make_move(&mut self, _: Arc<Config>, move_builder: &mut MoveBuilder) {
            // try to place as many of four filters as possible
            let wall_locations = [xy(12, 5), xy(13, 5), xy(14, 5), xy(15, 5)];
            move_builder.attempt_spawn_multiple(&wall_locations, FirewallUnitType::Filter).unwrap();
    
            // try to atomically place four pings in two locations
            {
                let [mut cell1, mut cell2] = all_builder_cells!(move_builder, xy(6, 7), xy(21, 7)).unwrap();
                if cell1.can_spawn(InfoUnitType::Ping, 2).affirmative() &&
                    cell2.can_spawn(InfoUnitType::Ping, 2).affirmative() {
                    for _ in 0..2 {
                        cell1.spawn(InfoUnitType::Ping)
                            .expect("Unexpected spawn failure");
                        cell2.spawn(InfoUnitType::Ping)
                            .expect("Unexpected spawn failure");
                    }
                }
            }
    
            // if our cores are low, try to delete a firewall
            {
                if move_builder.map().data().p1_stats.cores() < 5.0 &&
                    move_builder.cell(xy(5, 5)).unwrap().can_remove_firewall().affirmative() {
                    move_builder.cell(xy(5, 5)).unwrap().remove_firewall().unwrap();
                }
            }
    
            // print the path that an enemy unit would take if spawned at a particular location
            {
                let move_from = move_builder.cell(xy(13, 27)).unwrap();
                if move_from.get_wall().is_none() {
                    let path = move_from.pathfind(MapEdge::BottomRight).unwrap();
                    eprintln!("Path from [13, 27] = {:?}", path);
                } else {
                    eprintln!("Enemy slot [13, 27] is blocked");
                }
            }
        }
    }
```

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
  "release": false,
  "package": "starter-algo",
  "toolchain": "stable"
}
```

- release: whether to run the build in release mode (enable optimizations)
    - this will make your code run faster, but it will take longer to compile
- package: this is the executable package that will be built
    - change this if you implement your strategy in a new package
- toolchain: which rust toolchain to compile with
    - can be stable, beta, or nightly
    
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
- `FirewallUnitType`: an enum over all firewall unit types
- `InfoUnitType`: an enum over all info unit types
- `RemoveUnitType`: a unit-like struct denoting the remove unit type
- `SpawnableUnitType`: a union of `FirewallUnitType` and `InfoUnitType`

These types are convertible into each other, both fallibly and infallibly, through the `Into` trait. For example, 
All unit types implement `Into<UnitType>`. Both `FirewallUnitType`, `InfoUnitType`, and `SpawnableUnitType` implement 
`Into<SpawnableUnitType>`, but `RemoveUnitType` does not. 

This type system allows code which deals with units to be restrictive at compile-time over which unit types are allowed.
For example, the `Map`'s `cost_of` function accepts an `impl Into<SpawnableUnitType>`, allowing it to be called with 
any `InfoUnitType` or `FirewallUnitType`, but never a `RemoveUnitType`.

#### Tile

Any operation on a specific tile of a `Map` or `MoveBuilder` could potentially fail if the tile coordinates were invalid.
This failure isolated and handled up-front through use of the `MapTile` trait.

```rust
    trait MapTile
    ├--struct MapReadTile<'a>
    └--struct BuilderTile<'a>
```

The `MapReadTile` and `BuilderTile` borrow from a `Map` and `MoveBuilder`, and also contain a valid coordinate. These structs 
are borrowed out from the underlying structure, and the underlying structure will refuse to borrow out invalid tiles, by
returning, for example, an `Option<BuilderTile<>`. Both tile types can be used to perform queries on the game state at that 
tile, and the `BuilderTile` can additionally be used to place and remove units at that tile.

An example use case:

```rust
move_builder.tile(xy(14, 0)).unwrap().attempt_spawn(InfoUnitType::Ping);
```

The `MoveBuilder` is asked to borrow out a `BuilderTile` at the coordinate `14, 0`, which is constructed through the `xy` function.
The `Option<BuilderTile>` is unwrapped, explicitly and quickly panicking if that tile is not valid. Then, the `BuilderTile` 
is used to attempt to spawn a ping, given a paramter of the type `impl Into<SpawnableUnitType>`. The `attempt_spawn` function 
is okay with failing, so it returns a `bool`, unlike the `spawn` function, which returns a `Result<(), CanSpawn>`.

### Convenience functions

Because this tile pattern can be verbose, there are convenience functions for spawning, or attempting to spawn, multiple units.
These functions live in the `MoveBuilder` itself, not in a borrowed-out tile. For example, the `MoveBuilder` function:

```rust
pub fn attempt_spawn_multiple(&mut self, coords: &[Coords],
                              unit_type: impl Into<SpawnableUnitType>) -> Result<u32, InvalidTile>
```

### Simultaneous `BuilderTile` borrowing

A `BuilderTile` mutably borrows from a `MoveBuilder`. As such, Rust will try to prevent you from simultaneously borrowing out
multiple `BuilderTile`s at a time, for fear of borrowing the same tile simultaneously, and causing a concurrent modification
bug or a race condition.

The `algo` package does have code which allows for the simultaneous borrowing of multiple `BuilderTile`s from a single `MoveBuilder`,
using a runtime check to prevent borrowing out the same tile twice simultaneously. The easiest way to access this API is through 
two macros.

The `multiple_builder_tiles!` macro accepts a move builder, then several coordinates, and expresses an
array of `Option<BuilderTile>`. The array is fixed-size, and equal in length to the number of coordinates given to the macro.
A particular tile will be `None` if it is an invalid tile, or borrowed twice.

```rust
macro_rules! multiple_builder_tiles {
    ($builder:expr, $( $coord:expr ),* ) => ...
}
```

The `all_builder_tiles!` macro works similarly, and accepts the same types of parameters. However, it will fail if any of the 
tile acquisitions fail. It expresses a `Result<[BuilderTile; N], GetMultipleBuilderTilesError>`.

```rust
macro_rules! all_builder_tiles {
    ($builder:expr, $( $coord:expr ),* ) => ...
}
```

An example use case:
```rust
let [mut cell1, mut cell2] = all_builder_tiles!(move_builder, xy(6, 7), xy(21, 7)).unwrap();
```

The `MoveBuilder` is asked to borrow out two coordinates. The `Result` is unwrapped, explicitly and quickly panicking if 
any tile is not valid. Then, the array of `BuilderTile`s is bound to an fixed size array pattern with a let binding.
As such, the two `BuilderCell`s are bound to the variables `cell1` and `cell2`. Further code can perform operations on these
`BuilderCells`.