
#[macro_use]
extern crate algo;
extern crate rand;

use algo::prelude::*;
use rand::prelude::*;

const FIREWALL_LOCATIONS_C: &[Coords] = &[
   xy!(8, 11),
   xy!(9, 11),
   xy!(7, 10),
   xy!(7, 9),
   xy!(7, 8),
   xy!(8, 7),
   xy!(9, 7),
];

const FIREWALL_LOCATIONS_1: &[Coords] = &[
   xy!(17, 11),
   xy!(18, 11),
   xy!(18, 10),
   xy!(18, 9),
   xy!(18, 8),
   xy!(17, 7),
   xy!(18, 7),
   xy!(19, 7),
];

const FIREWALL_LOCATIONS_DOTS: &[Coords] = &[
   xy!(11, 7),
   xy!(13, 9),
   xy!(15, 11),
];

const DEFENSIVE_DESTRUCTOR_LOCATIONS: &[Coords] = &[
   xy!(0, 13),
   xy!(27, 13),
];

const DEFENSIVE_ENCRYPTOR_LOCATIONS: &[Coords] = &[
   xy!(3, 11),
   xy!(4, 11),
   xy!(5, 11),
];

/// Rust implementation of the standard starter algo.
struct StarterAlgo;
impl GameLoop for StarterAlgo {
    fn initialize(&mut self, _: Arc<Config>) {
        eprintln!("Configuring your custom rust algo strategy...");
    }

    fn on_action_frame(&mut self, _: Arc<Config>, _: Map) {}

    fn make_move(&mut self, _: Arc<Config>, move_builder: &mut MoveBuilder) {
        build_c1_logo(move_builder);
        build_defenses(move_builder);
        deploy_attackers(move_builder);
    }
}

/// Make the C1 logo.
fn build_c1_logo(move_builder: &mut MoveBuilder) {
    for &coord in FIREWALL_LOCATIONS_C {
        move_builder.tile(coord).unwrap().attempt_spawn(FirewallUnitType::Filter);
    }
    for &coord in FIREWALL_LOCATIONS_1 {
        move_builder.tile(coord).unwrap().attempt_spawn(FirewallUnitType::Filter);
    }
    for &coord in FIREWALL_LOCATIONS_DOTS {
        move_builder.tile(coord).unwrap().attempt_spawn(FirewallUnitType::Destructor);
    }
}

/// Once the C1 logo is made, attempt to build some defenses.
fn build_defenses(move_builder: &mut MoveBuilder) {
    /*
    First lets protect ourselves a little with destructors.
     */
    move_builder.attempt_spawn_multiple(DEFENSIVE_DESTRUCTOR_LOCATIONS,
                                        FirewallUnitType::Destructor).unwrap();

    /*
    Then lets boost our offense by building some encryptors to shield
    our information units. Lets put them near the front because the
    shields decay over time, so shields closer to the action
    are more effective.
     */
    move_builder.attempt_spawn_multiple(DEFENSIVE_ENCRYPTOR_LOCATIONS,
                                        FirewallUnitType::Encryptor).unwrap();

    /*
    Lastly lets build encryptors in random locations. Normally building
    randomly is a bad idea but we'll leave it to you to figure out better
    strategies.

    First we get all locations on the bottom half of the map
    that are in the arena bounds.
     */
    let mut possible_spawn_points = Vec::new();
    for x in 0..BOARD_SIZE {
        for y in 0..BOARD_SIZE {
            let coords = Coords::from([x, y]);
            if let Some(cell) = move_builder.tile(coords) {
                if cell.can_spawn(FirewallUnitType::Encryptor, 1).affirmative() {
                    possible_spawn_points.push(coords);
                }
            }
        }
    }
    thread_rng().shuffle(&mut possible_spawn_points);
    while move_builder.map().number_affordable(FirewallUnitType::Encryptor) > 0 &&
        possible_spawn_points.len() > 0 {

        let coords = possible_spawn_points.pop().unwrap();
        move_builder.tile(coords).unwrap().attempt_spawn(FirewallUnitType::Encryptor);
    }
}

/// Deploy offensive units.
fn deploy_attackers(move_builder: &mut MoveBuilder) {
    /*
    First lets check if we have 10 bits, if we don't we lets wait for
    a turn where we do.
     */
    if move_builder.map().data().p1_stats.bits() < 10.0 {
        return;
    }

    /*
    Then lets deploy an EMP long range unit to destroy firewalls for us.
     */
    move_builder.tile(xy(3, 10)).unwrap().attempt_spawn(InfoUnitType::Emp);

    /*
    Now lets send out 3 Pings to hopefully score, we can spawn multiple
    information units in the same location.
    */
    for _ in 0..3 {
        move_builder.tile(xy(14, 0)).unwrap().attempt_spawn(InfoUnitType::Ping);
    }

    /*
    NOTE: the locations we used above to spawn information units may become
    blocked by our own firewalls. We'll leave it to you to fix that issue
    yourselves.

    Lastly lets send out Scramblers to help destroy enemy information units.
    A complex algo would predict where the enemy is going to send units and
    develop its strategy around that. But this algo is simple so lets just
    send out scramblers in random locations and hope for the best.

    Firstly information units can only deploy on our edges. So lets get a
    list of those locations.
     */
    let mut friendly_edges = Vec::new();
    friendly_edges.extend(MAP_BOUNDS.edge(MapEdge::BottomLeft).iter().cloned());
    friendly_edges.extend(MAP_BOUNDS.edge(MapEdge::BottomRight).iter().cloned());

    /*
    While we have remaining bits to spend lets send out scramblers randomly.
    */
    while {
        let affordable = move_builder.map().number_affordable(InfoUnitType::Scrambler);
        affordable >= 1
    } {
        let coords = friendly_edges[thread_rng().gen::<usize>() % friendly_edges.len()];
        move_builder.tile(coords).unwrap().attempt_spawn(InfoUnitType::Scrambler);
    }
}

fn main() {
    run_game_loop(StarterAlgo);
}