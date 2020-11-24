
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

        // try to atomically place four Scouts in two locations
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

        // if our cores are low, try to delete a Structure
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