
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

        // try to place as many of four filters as possible
        for &wall_coord in &[
            xy(12, 5),
            xy(13, 5),
            xy(14, 5),
            xy(15, 5),
        ] {
            map[wall_coord].try_spawn(FirewallUnitType::Filter);
        }

        // try to atomically place four pings in two locations
        let ping_coord_1 = xy(6, 7);
        let ping_coord_2 = xy(21, 7);

        if map[ping_coord_1].can_spawn(InfoUnitType::Ping, 2).yes() &&
            map[ping_coord_2].can_spawn(InfoUnitType::Ping, 2).yes()
        {
            for _ in 0..2 {
                map[ping_coord_1].spawn(InfoUnitType::Ping)
                    .expect("Unexpected spawn failure");
                map[ping_coord_2].spawn(InfoUnitType::Ping)
                    .expect("Unexpected spawn failure");
            }
        }

        // if our cores are low, try to delete a firewall
        if map.frame_data().p1_stats.cores < 5.0 &&
            map[xy(5, 5)].can_remove_firewall().yes()
        {
            map[xy(5, 5)].remove_firewall().unwrap();
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