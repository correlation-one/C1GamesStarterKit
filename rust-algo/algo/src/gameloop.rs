
use crate::{
    messages::Config,
    messages::frame::Phase,
    io::GameDataReader,
    map::{
        MapState,
        parse::parse_frame,
    },
};

use std::{
    process,
    sync::Arc,
};

/// A trait for a simple, single-threaded game loop, which the user can implement and then plug into a
/// game loop driver to create a working algo.
pub trait GameLoop {
    /// The `initialize` callback is called once, at the beginning of the game, with the `Config` data
    /// that this algo has received and deserialized from the game engine.
    fn initialize(&mut self, config: Arc<Config>) {
        let _ = config;
    }

    /// The `on_action_frame` callback is called every action frame, and is given a `Map`, an immutable
    /// and random-access representation of the state of the game that frame. The `Map` also contains
    /// the deserialized frame data for this frame, including player stats.
    fn on_action_frame(&mut self, config: Arc<Config>, map: &MapState) {
        let _ = (config, map);
    }

    /// The `make_move` callback is called every turn frame, and is given mutable access to a
    /// `MoveBuilder`. The `MoveBuilder` contains a `Map`, and is able to mutate the `Map` by making valid
    /// moves, such as spawning and removing units. The `MoveBuilder` records each spawn command that is
    /// used to mutate it, and when `make_move` returns, those spawn commands will be submitted to the engine.
    fn on_turn(&mut self, config: Arc<Config>, state: &MapState);
}


/// Run a game loop until the game ends and the process exits.
pub fn run_game_loop(mut game_loop: impl GameLoop) -> ! {
    let mut io = GameDataReader::new();
    let (config, atlas) = io.config().expect("Config error");
    game_loop.initialize(config.clone());
    loop {
        let frame = io.next_frame_any_type().expect("Frame error");
        match frame.turn_info.phase {
            Phase::Deploy => {
                let map =
                    parse_frame(config.clone(), frame, atlas.clone())
                        .expect("Frame error");

                game_loop.on_turn(config.clone(), &map);
                map.submit();
            },
            Phase::Action => {
                let map =
                    parse_frame(config.clone(), frame, atlas.clone())
                        .expect("Frame error");

                game_loop.on_action_frame(config.clone(), &map);
            },
            Phase::EndGame => {
                process::exit(0);
            }
        }
    }
}