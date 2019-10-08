
/// Rust representation of messages passed between the game and this algo.

use serde::{Deserialize, Deserializer};
use serde::de::{Visitor, Error};
use std::fmt::Formatter;
use std::fmt;

/// The config file received at the beginning of the game.
#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Config {
    pub debug: config::Debug,
    pub unit_information: [config::UnitInformation; 7],
    pub resources: config::Resources,
    pub mechanics: config::Mechanics,
}

pub mod config {
    #[derive(Debug, Deserialize, Clone)]
    #[serde(rename_all = "camelCase")]
    pub struct Debug {
        pub print_map_string: bool,
        pub print_t_strings: bool,
        pub print_act_strings: bool,
        pub print_hit_strings: bool,
        pub print_player_input_strings: bool,
        pub print_bot_errors: bool,
        pub print_player_get_hit_strings: bool,
    }

    #[derive(Debug, Deserialize, Clone)]
    #[serde(untagged)]
    pub enum UnitInformation {
        #[serde(rename_all = "camelCase")]
        Wall {
            damage: f32,
            cost: f32,
            get_hit_radius: f32,
            display: String,
            range: f32,
            shorthand: String,
            stability: f32,
            shield_amount: f32,
        },
        #[serde(rename_all = "camelCase")]
        Data {
            damage_i: f32,
            damage_to_player: f32,
            cost: f32,
            get_hit_radius: f32,
            damage_f: f32,
            display: String,
            range: f32,
            shorthand: String,
            stability: f32,
            speed: f32,
        },
        #[serde(rename_all = "camelCase")]
        Remove {
            display: String,
            shorthand: String,
        },
    }
    impl UnitInformation {
        pub fn shorthand(&self) -> &String {
            match self {
                &UnitInformation::Wall {
                    ref shorthand,
                    ..
                } => &shorthand,
                &UnitInformation::Data {
                    ref shorthand,
                    ..
                } => &shorthand,
                &UnitInformation::Remove {
                    ref shorthand,
                    ..
                } => &shorthand,
            }
        }

        pub fn cost(&self) -> Option<f32> {
            match self {
                &UnitInformation::Wall {
                    cost,
                    ..
                } => Some(cost),
                &UnitInformation::Data {
                    cost,
                    ..
                } => Some(cost),
                &UnitInformation::Remove { .. } => None,
            }
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    #[serde(rename_all = "camelCase")]
    pub struct Resources {
        turn_interval_for_bit_cap_schedule: f32,
        turn_interval_for_bit_schedule: f32,
        bit_ramp_bit_cap_growth_rate: f32,
        round_start_bit_ramp: f32,
        bit_growth_rate: f32,
        #[serde(rename = "startingHP")]
        starting_hp: f32,
        max_bits: f32,
        bits_per_round: f32,
        cores_per_round: f32,
        cores_for_player_damage: f32,
        starting_bits: f32,
        bit_decay_per_round: f32,
        starting_cores: f32
    }

    #[derive(Debug, Deserialize, Clone)]
    #[serde(rename_all = "camelCase")]
    pub struct Mechanics {
        base_player_health_damage: f32,
        damage_growth_based_on_y: f32,
        bits_can_stack_on_deployment: bool,
        destroy_own_unit_refund: f32,
        destroy_own_units_enabled: bool,
        steps_required_self_destruct: f32,
        self_destruct_radius: f32,
        shield_decay_per_frame: f32,
        melee_multiplier: f32,
        destroy_own_unit_delay: f32,
        reroute_mid_round: bool,
        firewall_build_time: f32
    }
}

/// Player 1 or player 2.
#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum PlayerId {
    Player1,
    Player2
}
impl PlayerId {
    pub fn all() -> &'static [PlayerId] {
        &[
            PlayerId::Player1,
            PlayerId::Player2,
        ]
    }
}
impl<'de> Deserialize<'de> for PlayerId {
    fn deserialize<D>(deserializer: D) -> Result<Self, <D as Deserializer<'de>>::Error> where
        D: Deserializer<'de> {

        struct PlayerIdVisitor;
        impl<'de> Visitor<'de> for PlayerIdVisitor {
            type Value = PlayerId;

            fn expecting(&self, formatter: &mut Formatter) -> Result<(), fmt::Error> {
                formatter.write_str("integer 0..3")
            }

            fn visit_u64<E: Error>(self, n: u64) -> Result<PlayerId, E> {
                match n {
                    1 => Ok(PlayerId::Player1),
                    2 => Ok(PlayerId::Player2),
                    n => Err(E::custom(format!("invalid player id number {}", n)))
                }
            }
        }

        deserializer.deserialize_u64(PlayerIdVisitor)
    }
}

/// The frame data, received every game frame.
#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct FrameData {
    pub turn_info: frame::TurnInfo,
    pub p1_stats: frame::PlayerStats,
    pub p2_stats: frame::PlayerStats,
    pub p1_units: frame::PlayerUnits,
    pub p2_units: frame::PlayerUnits,
    pub end_stats: Option<frame::EndStats>,
    pub events: frame::Events,
}

pub mod frame {
    use coords::*;
    use super::PlayerId;
    use serde::{Deserialize, Deserializer};
    use serde::de::{Visitor, Error};
    use std::fmt::Formatter;
    use std::fmt;

    #[derive(Debug, Deserialize, Clone)]
    pub struct TurnInfo(pub Phase, pub f32, pub f32);
    impl TurnInfo {
        pub fn phase(&self) -> Phase {
            self.0
        }

        pub fn turn_number(&self) -> f32 {
            self.1
        }

        pub fn action_phase_frame_number(&self) -> f32 {
            self.2
        }
    }

    #[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
    pub enum Phase {
        Deploy,
        Action,
        EndGame
    }
    impl<'de> Deserialize<'de> for Phase {
        fn deserialize<D>(deserializer: D) -> Result<Self, <D as Deserializer<'de>>::Error> where
            D: Deserializer<'de> {

            struct PhaseVisitor;
            impl<'de> Visitor<'de> for PhaseVisitor {
                type Value = Phase;

                fn expecting(&self, formatter: &mut Formatter) -> Result<(), fmt::Error> {
                    formatter.write_str("integer 0..3")
                }

                fn visit_u64<E: Error>(self, n: u64) -> Result<Phase, E> {
                    match n {
                        0 => Ok(Phase::Deploy),
                        1 => Ok(Phase::Action),
                        2 => Ok(Phase::EndGame),
                        n => Err(E::custom(format!("invalid phase number {}", n)))
                    }
                }
            }

            deserializer.deserialize_u64(PhaseVisitor)
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct PlayerStats(pub f32, pub f32, pub f32, pub f32);
    impl PlayerStats {
        pub fn integrity(&self) -> f32 {
            self.0
        }

        pub fn cores(&self) -> f32 {
            self.1
        }

        pub fn cores_mut(&mut self) -> &mut f32 {
            &mut self.1
        }

        pub fn bits(&self) -> f32 {
            self.2
        }

        pub fn bits_mut(&mut self) -> &mut f32 {
            &mut self.2
        }

        pub fn time_taken_last_turn_millis(&self) -> f32 {
            self.3
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct PlayerUnit(pub i32, pub i32, pub f32, pub String);
    impl PlayerUnit {
        pub fn x(&self) -> i32 {
            self.0
        }

        pub fn y(&self) -> i32 {
            self.1
        }

        pub fn coords(&self) -> Coords {
            xy(self.x(), self.y())
        }

        pub fn stability(&self) -> f32 {
            self.2
        }

        pub fn unit_id(&self) -> &String {
            &self.3
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct PlayerUnits(
        // TODO: make this an array
        pub Vec<PlayerUnit>,
        pub Vec<PlayerUnit>,
        pub Vec<PlayerUnit>,
        pub Vec<PlayerUnit>,
        pub Vec<PlayerUnit>,
        pub Vec<PlayerUnit>,
        pub Vec<PlayerUnit>,
    );
    impl PlayerUnits {
        pub fn filter(&self) -> &Vec<PlayerUnit> {
            &self.0
        }

        pub fn encryptor(&self) -> &Vec<PlayerUnit> {
            &self.1
        }

        pub fn destructor(&self) -> &Vec<PlayerUnit> {
            &self.2
        }

        pub fn ping(&self) -> &Vec<PlayerUnit> {
            &self.3
        }

        pub fn emp(&self) -> &Vec<PlayerUnit> {
            &self.4
        }

        pub fn scrambler(&self) -> &Vec<PlayerUnit> {
            &self.5
        }

        pub fn remove(&self) -> &Vec<PlayerUnit> {
            &self.6
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    #[serde(rename_all = "camelCase")]
    pub struct EndStats {
        player1: PlayerEndStats,
        player2: PlayerEndStats,
        duration: f32,
        turns: i32,
        frames: i32,
        winner: Winner,

    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct PlayerEndStats {
        pub dynamic_resource_spent: f32,
        pub dynamic_resource_destroyed: f32,
        pub dynamic_resource_spoiled: f32,
        pub stationary_resource_spent: f32,
        pub stationary_resource_left_on_board: f32,
        pub points_scored: f32,
        pub crashed: bool,
        pub total_computation_time: f32,
    }

    #[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
    pub enum Winner {
        Tie,
        Player1,
        Player2
    }
    impl<'de> Deserialize<'de> for Winner {
        fn deserialize<D>(deserializer: D) -> Result<Self, <D as Deserializer<'de>>::Error> where
            D: Deserializer<'de> {

            struct WinnerVisitor;
            impl<'de> Visitor<'de> for WinnerVisitor {
                type Value = Winner;

                fn expecting(&self, formatter: &mut Formatter) -> Result<(), fmt::Error> {
                    formatter.write_str("integer 0..3")
                }

                fn visit_u64<E: Error>(self, n: u64) -> Result<Winner, E> {
                    match n {
                        0 => Ok(Winner::Tie),
                        1 => Ok(Winner::Player1),
                        2 => Ok(Winner::Player2),
                        n => Err(E::custom(format!("invalid winner number {}", n)))
                    }
                }
            }

            deserializer.deserialize_u64(WinnerVisitor)
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    #[serde(rename_all = "camelCase")]
    pub struct Events {
        pub attack: Vec<AttackEvent>,
        pub breach: Vec<BreachEvent>,
        pub damage: Vec<DamageEvent>,
        pub death: Vec<DeathEvent>,
        pub melee: Vec<MeleeEvent>,
        #[serde(rename = "move")]
        pub moves: Vec<MoveEvent>,
        pub self_destruct: Vec<SelfDestructEvent>,
        pub shield: Vec<ShieldEvent>,
        pub spawn: Vec<SpawnEvent>,
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct AttackEvent(
        pub Coords,
        pub Coords,
        pub f32,
        pub u8,
        pub String,
        pub String,
        pub PlayerId,
    );
    impl AttackEvent {
        pub fn source(&self) -> Coords {
            self.0
        }

        pub fn target(&self) -> Coords {
            self.1
        }

        pub fn damage(&self) -> f32 {
            self.2
        }

        pub fn attacker_type(&self) -> u8 {
            self.3
        }

        pub fn source_unit_id(&self) -> &String {
            &self.4
        }

        pub fn target_unit_id(&self) -> &String {
            &self.5
        }

        pub fn source_player(&self) -> PlayerId {
            self.6
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct BreachEvent(
        pub Coords,
        pub f32,
        pub u8,
        pub String,
        pub PlayerId,
    );
    impl BreachEvent {
        pub fn coords(&self) -> Coords {
            self.0
        }

        pub fn damage(&self) -> f32 {
            self.1
        }

        pub fn breacher_type(&self) -> u8 {
            self.2
        }

        pub fn breacher_id(&self) -> &String {
            &self.3
        }

        pub fn unit_owner(&self) -> PlayerId {
            self.4
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct DamageEvent(
        pub Coords,
        pub f32,
        pub u8,
        pub String,
        pub PlayerId
    );
    impl DamageEvent {
        pub fn coords(&self) -> Coords {
            self.0
        }

        pub fn damage(&self) -> f32 {
            self.1
        }

        pub fn damager_type(&self) -> u8 {
            self.2
        }

        pub fn damager_id(&self) -> &String {
            &self.3
        }

        pub fn unit_owner(&self) -> PlayerId {
            self.4
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct DeathEvent(
        pub Coords,
        pub u8,
        pub String,
        pub PlayerId,
        pub bool,
    );
    impl DeathEvent {
        pub fn coords(&self) -> Coords {
            self.0
        }

        pub fn destroyed_unit_type(&self) -> u8 {
            self.1
        }

        pub fn destroyed_unit_id(&self) -> &String {
            &self.2
        }

        pub fn unit_owner(&self) -> PlayerId {
            self.3
        }

        pub fn is_self_removal(&self) -> bool {
            self.4
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct MeleeEvent(
        pub Coords,
        pub Coords,
        pub f32,
        pub u8,
        pub String,
        pub PlayerId,
    );
    impl MeleeEvent {
        pub fn attacker_location(&self) -> Coords {
            self.0
        }

        pub fn victim_location(&self) -> Coords {
            self.1
        }

        pub fn damage_dealt(&self) -> f32 {
            self.2
        }

        pub fn attacker_unit_type(&self) -> u8 {
            self.3
        }

        pub fn attacker_unit_id(&self) -> &String {
            &self.4
        }

        pub fn attacker_player_id(&self) -> PlayerId {
            self.5
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct MoveEvent(
        pub Coords,
        pub Coords,
        pub Coords,
        pub u8,
        pub String,
        pub PlayerId
    );
    impl MoveEvent {
        pub fn old_location(&self) -> Coords {
            self.0
        }

        pub fn new_location(&self) -> Coords {
            self.1
        }

        pub fn desired_next_location(&self) -> Coords {
            self.2
        }

        pub fn unit_type(&self) -> u8 {
            self.3
        }

        pub fn unit_id(&self) -> &String {
            &self.4
        }

        pub fn owner(&self) -> PlayerId {
            self.5
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct SelfDestructEvent(
        pub Coords,
        pub Vec<Coords>,
        pub f32,
        pub u8,
        pub String,
        pub PlayerId
    );
    impl SelfDestructEvent {
        pub fn source(&self) -> Coords {
            self.0
        }

        pub fn targets(&self) -> &Vec<Coords> {
            &self.1
        }

        pub fn damage(&self) -> f32 {
            self.2
        }

        pub fn exploding_unit_type(&self) -> u8 {
            self.3
        }

        pub fn exploding_unit_id(&self) -> &String {
            &self.4
        }

        pub fn exploding_unit_owner(&self) -> PlayerId {
            self.5
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct ShieldEvent(
        pub Coords,
        pub Coords,
        pub f32,
        pub u8,
        pub String,
        pub String,
        pub PlayerId
    );
    impl ShieldEvent {
        pub fn encryptor_coords(&self) -> Coords {
            self.0
        }

        pub fn info_coords(&self) -> Coords {
            self.1
        }

        pub fn shield_amount(&self) -> f32 {
            self.2
        }

        pub fn encryptor_type(&self) -> u8 {
            self.3
        }

        pub fn encryptor_unit_id(&self) -> &String {
            &self.4
        }

        pub fn info_unit_id(&self) -> &String {
            &self.5
        }

        pub fn encryptor_owner(&self) -> PlayerId {
            self.6
        }
    }

    #[derive(Debug, Deserialize, Clone)]
    pub struct SpawnEvent(
        pub Coords,
        pub u8,
        pub String,
        pub PlayerId
    );
    impl SpawnEvent {
        pub fn spawn_location(&self) -> Coords {
            self.0
        }

        pub fn spawning_unit_type(&self) -> u8 {
            self.1
        }

        pub fn spawning_unit_id(&self) -> &String {
            &self.2
        }

        pub fn owner(&self) -> PlayerId {
            self.3
        }
    }

}