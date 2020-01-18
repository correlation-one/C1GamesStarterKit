
//! Rust model of data passed between the game and this algo.

/// Utilities for serializing and deserializing.
#[macro_use]
pub mod serde_util;

use serde::Deserialize;
use enum_iterator::IntoEnumIterator;

/// Model of config data.
pub mod config;

/// Model of game frame data;
pub mod frame;

/// Config file received at the beginning of the game.
#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Config {
    pub debug: config::Debug,
    pub unit_information: [config::UnitInformation; 8],
    pub resources: config::Resources,
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


/// Player 1 or player 2.
#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, IntoEnumIterator)]
pub enum PlayerId {
    Player1,
    Player2,
}

serde_enum_from_int!(PlayerId, {
    1 => PlayerId::Player1,
    2 => PlayerId::Player2,
});

