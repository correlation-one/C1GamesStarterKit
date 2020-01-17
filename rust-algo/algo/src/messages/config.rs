
use serde::{Deserialize};

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
        shield_amount: Option<f32>,
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
    pub fn shorthand(&self) -> &str {
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
    pub cores_for_player_damage: f32,
    pub starting_bits: f32,
    pub bit_decay_per_round: f32,
    pub starting_cores: f32
}

#[derive(Debug, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Mechanics {
    pub base_player_health_damage: f32,
    pub damage_growth_based_on_y: f32,
    pub bits_can_stack_on_deployment: bool,
    pub destroy_own_unit_refund: f32,
    pub destroy_own_units_enabled: bool,
    pub steps_required_self_destruct: f32,
    pub self_destruct_radius: f32,
    pub shield_decay_per_frame: f32,
    pub melee_multiplier: f32,
    pub destroy_own_unit_delay: f32,
    pub reroute_mid_round: bool,
    pub firewall_build_time: f32
}