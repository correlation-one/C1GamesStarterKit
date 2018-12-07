
extern crate algo;
extern crate serde_json;

use algo::prelude::*;
use algo::enum_iterator::IntoEnumIterator;

use std::io::stdin;
use std::io::BufRead;

fn main() {
    let mut reader = GameDataReader::new();
    let (config, _) = reader.config().unwrap();
    loop {
        let frame = reader.next_turn_frame().unwrap();
        let map = Map::new(config.clone(), frame).unwrap();
        let start: [f32; 2] = {
            let stdin = stdin();
            let line = stdin.lock().lines().next().unwrap().unwrap();
            serde_json::from_str(line.as_ref()).unwrap()
        };
        let start = xy(start[0] as i32, start[1] as i32);
        let target: MapEdge = {
            let stdin = stdin();
            let line = stdin.lock().lines().next().unwrap().unwrap();
            let i: f32 = line.parse().unwrap();
            MapEdge::into_enum_iter().nth(i as usize).unwrap()
        };
        let path = map
            .tile(start).unwrap()
            .pathfind(target).unwrap();
        println!("{}", serde_json::to_string(&path).unwrap());
    }
}