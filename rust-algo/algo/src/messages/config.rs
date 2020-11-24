
use serde::{Deserialize};
use enum_iterator::IntoEnumIterator;

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
#[serde(rename_all = "camelCase")]
pub struct UnitInformation {
    pub unit_category: Option<UnitCategory>,
    pub attack_damage_tower: Option<f32>,
    pub attack_damage_walker: Option<f32>,
    pub attack_range: Option<f32>,
    pub get_hit_radius: Option<f32>,
    pub shield_per_unit: Option<f32>,
    pub shield_range: Option<f32>,
    pub shield_bonus_per_y: Option<f32>,
    pub shield_decay: Option<f32>,
    pub start_health: Option<f32>,
    pub speed: Option<f32>,
    pub cost1: Option<f32>,
    pub cost2: Option<f32>,
    pub upgrade: Option<Box<UnitInformation>>,
    pub display: Option<String>,
    pub shorthand: Option<String>,
}

#[derive(Debug, Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, IntoEnumIterator)]
pub enum UnitCategory {
    Structure,
    Mobile,
}

serde_enum_from_int!(UnitCategory, {
    0 => UnitCategory::Structure,
    1 => UnitCategory::Mobile,
});

#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Resources {
    pub turn_interval_for_bit_cap_schedule: f32,
    pub turn_interval_for_bit_schedule: f32,
    pub bit_ramp_bit_cap_growth_rate: f32,
    pub round_start_bit_ramp: f32,
    pub bit_growth_rate: f32,
    #[serde(rename = "startingHP")]
    pub starting_hp: f32,
    pub max_bits: f32,
    pub bits_per_round: f32,
    pub cores_per_round: f32,
    pub starting_bits: f32,
    pub bit_decay_per_round: f32,
    pub starting_cores: f32
}
