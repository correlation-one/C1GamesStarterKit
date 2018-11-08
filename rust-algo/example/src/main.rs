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
            let [mut cell1, mut cell2] = all_builder_tiles!(move_builder, xy(6, 7), xy(21, 7)).unwrap();
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
                move_builder.tile(xy(5, 5)).unwrap().can_remove_firewall().affirmative() {
                move_builder.tile(xy(5, 5)).unwrap().remove_firewall().unwrap();
            }
        }

        // print the path that an enemy unit would take if spawned at a particular location
        {
            let move_from = move_builder.tile(xy(13, 27)).unwrap();
            if move_from.get_wall().is_none() {
                let path = move_from.pathfind(MapEdge::BottomRight).unwrap();
                eprintln!("Path from [13, 27] = {:?}", path);
            } else {
                eprintln!("Enemy slot [13, 27] is blocked");
            }
        }
    }
}