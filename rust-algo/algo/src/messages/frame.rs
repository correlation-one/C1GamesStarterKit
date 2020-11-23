use crate::coords::*;
use super::PlayerId;
use serde::Deserialize;
use enum_iterator::IntoEnumIterator;


use super::serde_util::{DeserializeAs, RoundNumber};

#[derive(Copy, Debug, Clone, PartialEq)]
pub struct TurnInfo {
    pub phase: Phase,
    pub turn_number: i64,
    pub action_phase_frame_number: i64,
    pub total_number_frames: i64,
}

impl DeserializeAs for TurnInfo {
    type Model = (Phase, RoundNumber, RoundNumber, RoundNumber);

    fn from_model((
                      phase,
                      turn_number,
                      action_phase_frame_number,
                      total_number_frames,
                  ): Self::Model) -> Self {
        TurnInfo {
            phase,
            turn_number: turn_number.int(),
            action_phase_frame_number: action_phase_frame_number.int(),
            total_number_frames: total_number_frames.int(),
        }
    }
}

deser_as!(TurnInfo);


#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, IntoEnumIterator)]
pub enum Phase {
    Deploy,
    Action,
    EndGame
}

serde_enum_from_int!(Phase, {
    0 => Phase::Deploy,
    1 => Phase::Action,
    2 => Phase::EndGame,
});

#[derive(Copy, Debug, Clone, PartialEq)]
pub struct PlayerStats {
    pub integrity: f64,
    pub cores: f32,
    pub bits: f32,
    pub time_taken_last_turn_millis: f32,
}

deser_as_tuple!(PlayerStats, (
    integrity: f64,
    cores: f32,
    bits: f32,
    time_taken_last_turn_millis: f32,
));

#[derive(Debug, Clone, PartialEq)]
pub struct PlayerUnit {
    pub coords: Coords,
    pub stability: f32,
    pub unit_id: String,
}


impl DeserializeAs for PlayerUnit {
    type Model = (i32, i32, f32, String);

    fn from_model((x, y, stability, unit_id): Self::Model) -> Self {
        PlayerUnit {
            coords: Coords::xy(x, y),
            stability,
            unit_id,
        }
    }
}

deser_as!(PlayerUnit);


#[derive(Debug, Clone, PartialEq)]
pub struct PlayerUnits {
    pub wall: Vec<PlayerUnit>,
    pub support: Vec<PlayerUnit>,
    pub turret: Vec<PlayerUnit>,
    pub scout: Vec<PlayerUnit>,
    pub demolisher: Vec<PlayerUnit>,
    pub interceptor: Vec<PlayerUnit>,
    pub remove: Vec<PlayerUnit>,
    pub upgrade: Vec<PlayerUnit>,
}

deser_as_tuple!(PlayerUnits, (
    wall: Vec<PlayerUnit>,
    support: Vec<PlayerUnit>,
    turret: Vec<PlayerUnit>,
    scout: Vec<PlayerUnit>,
    demolisher: Vec<PlayerUnit>,
    interceptor: Vec<PlayerUnit>,
    remove: Vec<PlayerUnit>,
    upgrade: Vec<PlayerUnit>,
));


#[derive(Debug, Deserialize, Clone, PartialEq)]
#[serde(rename_all = "camelCase")]
pub struct EndStats {
    pub player1: PlayerEndStats,
    pub player2: PlayerEndStats,
    pub duration: f32,
    pub turns: i32,
    pub frames: i32,
    pub winner: Winner,
}


#[derive(Copy, Deserialize, Debug, Clone, PartialEq)]
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


#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, IntoEnumIterator)]
pub enum Winner {
    Tie,
    Player1,
    Player2
}

serde_enum_from_int!(Winner, {
    0 => Winner::Tie,
    1 => Winner::Player1,
    2 => Winner::Player2,
});


#[derive(Debug, Deserialize, Clone, PartialEq)]
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


#[derive(Debug, Clone, PartialEq)]
pub struct AttackEvent {
    pub source: Coords,
    pub target: Coords,
    pub damage: f32,
    pub attacker_type: u8,
    pub source_unit_id: String,
    pub target_unit_id: String,
    pub source_player: PlayerId,
}

deser_as_tuple!(AttackEvent, (
    source: Coords,
    target: Coords,
    damage: f32,
    attacker_type: u8,
    source_unit_id: String,
    target_unit_id: String,
    source_player: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct BreachEvent {
    pub coords: Coords,
    pub damage: f32,
    pub breacher_type: u8,
    pub breacher_id: String,
    pub unit_owner: PlayerId,
}

deser_as_tuple!(BreachEvent, (
    coords: Coords,
    damage: f32,
    breacher_type: u8,
    breacher_id: String,
    unit_owner: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct DamageEvent {
    pub coords: Coords,
    pub damage: f32,
    pub damager_type: u8,
    pub damager_id: String,
    pub unit_owner: PlayerId,
}

deser_as_tuple!(DamageEvent, (
    coords: Coords,
    damage: f32,
    damager_type: u8,
    damager_id: String,
    unit_owner: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct DeathEvent {
    pub coords: Coords,
    pub destroyed_unit_type: u8,
    pub destroyed_unit_id: String,
    pub unit_owner: PlayerId,
    pub is_self_removal: bool,
}

deser_as_tuple!(DeathEvent, (
    coords: Coords,
    destroyed_unit_type: u8,
    destroyed_unit_id: String,
    unit_owner: PlayerId,
    is_self_removal: bool,
));


#[derive(Debug, Clone, PartialEq)]
pub struct MeleeEvent {
    pub attacker_location: Coords,
    pub target_location: Coords,
    pub damage_dealt: f32,
    pub attacker_unit_type: u8,
    pub attacker_unit_id: String,
    pub attacker_player_id: PlayerId,
}

deser_as_tuple!(MeleeEvent, (
    attacker_location: Coords,
    target_location: Coords,
    damage_dealt: f32,
    attacker_unit_type: u8,
    attacker_unit_id: String,
    attacker_player_id: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct MoveEvent {
    pub old_location: Coords,
    pub new_location: Coords,
    pub desired_next_lcoation: Coords,
    pub unit_type: u8,
    pub unit_id: String,
    pub owner: PlayerId,
}

deser_as_tuple!(MoveEvent, (
    old_location: Coords,
    new_location: Coords,
    desired_next_lcoation: Coords,
    unit_type: u8,
    unit_id: String,
    owner: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct SelfDestructEvent {
    pub source: Coords,
    pub targets: Vec<Coords>,
    pub damage: f32,
    pub exploding_unit_type: u8,
    pub exploding_unit_id: String,
    pub exploding_unit_owner: PlayerId,
}

deser_as_tuple!(SelfDestructEvent, (
    source: Coords,
    targets: Vec<Coords>,
    damage: f32,
    exploding_unit_type: u8,
    exploding_unit_id: String,
    exploding_unit_owner: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct ShieldEvent {
    pub support_coords: Coords,
    pub mobile_coords: Coords,
    pub shield_amount: f32,
    pub support_type: u8,
    pub support_unit_id: String,
    pub mobile_unit_id: String,
    pub support_owner: PlayerId,
}

deser_as_tuple!(ShieldEvent, (
    support_coords: Coords,
    mobile_coords: Coords,
    shield_amount: f32,
    support_type: u8,
    support_unit_id: String,
    mobile_unit_id: String,
    support_owner: PlayerId,
));


#[derive(Debug, Clone, PartialEq)]
pub struct SpawnEvent {
    pub spawn_location: Coords,
    pub spawning_unit_type: u8,
    pub spawning_unit_id: String,
    pub owner: PlayerId,
}

deser_as_tuple!(SpawnEvent, (
    spawn_location: Coords,
    spawning_unit_type: u8,
    spawning_unit_id: String,
    owner: PlayerId,
));
