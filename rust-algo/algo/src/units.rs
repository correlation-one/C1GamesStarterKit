//! Unit types in the game.

use crate::messages::config::UnitInformation;
use std::collections::HashMap;
use enum_iterator::IntoEnumIterator;


/// Any unit type, including the remove type.
#[derive(Debug, Copy, Clone, Eq, PartialEq, PartialOrd, Ord, Hash, IntoEnumIterator)]
#[repr(u32)]
pub enum UnitType {
    Wall,
    Support,
    Turret,
    Scout,
    Demolisher,
    Interceptor,
    Remove,
    Upgrade,
}
impl UnitType {
    /// Attempt to convert to a StructureUnitType.
    pub fn as_structure(self) -> Option<StructureUnitType> {
        match self {
            UnitType::Wall => Some(StructureUnitType::Wall),
            UnitType::Support => Some(StructureUnitType::Support),
            UnitType::Turret => Some(StructureUnitType::Turret),
            _ => None
        }
    }

    /// Whether self is a StructureUnitType.
    pub fn is_structure(self) -> bool {
        match self {
            UnitType::Wall | UnitType::Support | UnitType::Turret => true,
            _ => false
        }
    }

    /// Attempt to convert to an MobileUnitType.
    pub fn as_mobile(self) -> Option<MobileUnitType> {
        match self {
            UnitType::Scout => Some(MobileUnitType::Scout),
            UnitType::Demolisher => Some(MobileUnitType::Demolisher),
            UnitType::Interceptor => Some(MobileUnitType::Interceptor),
            _ => None
        }
    }

    /// Whether self is an MobileUnitType.
    pub fn is_mobile(self) -> bool {
        match self {
            UnitType::Scout | UnitType::Demolisher | UnitType::Interceptor => true,
            _ => false
        }
    }

    /// Whether self is a unit type which can be spawned.
    pub fn is_spawnable(self) -> bool {
        self.is_structure() || self.is_mobile()
    }

    /// Attempt to convert to a SpawnableUnitType.
    pub fn as_spawnable(self) -> Option<SpawnableUnitType> {
        if let Some(mobile) = self.as_mobile() {
            Some(SpawnableUnitType::Mobile(mobile))
        } else if let Some(wall) = self.as_structure() {
            Some(SpawnableUnitType::Structure(wall))
        } else {
            None
        }
    }
}

/// A type of structure unit.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, IntoEnumIterator)]
pub enum StructureUnitType {
    Wall,
    Support,
    Turret,
}

impl Into<UnitType> for StructureUnitType {
    fn into(self) -> UnitType {
        match self {
            StructureUnitType::Wall => UnitType::Wall,
            StructureUnitType::Support => UnitType::Support,
            StructureUnitType::Turret => UnitType::Turret,
        }
    }
}

impl Into<SpawnableUnitType> for StructureUnitType {
    fn into(self) -> SpawnableUnitType {
        SpawnableUnitType::Structure(self)
    }
}

/// A type of mobile unit.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash, IntoEnumIterator)]
pub enum MobileUnitType {
    Scout,
    Demolisher,
    Interceptor,
}

impl Into<UnitType> for MobileUnitType {
    fn into(self) -> UnitType {
        match self {
            MobileUnitType::Scout => UnitType::Scout,
            MobileUnitType::Demolisher => UnitType::Demolisher,
            MobileUnitType::Interceptor => UnitType::Interceptor,
        }
    }
}

impl Into<SpawnableUnitType> for MobileUnitType {
    fn into(self) -> SpawnableUnitType {
        SpawnableUnitType::Mobile(self)
    }
}

/// A unit-like struct which represents the remove unit type.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
pub struct RemoveUnitType;
impl Into<UnitType> for RemoveUnitType {
    fn into(self) -> UnitType {
        UnitType::Remove
    }
}

/// A unit-like struct which represents the upgrade unit type.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
pub struct UpgradeUnitType;
impl Into<UnitType> for UpgradeUnitType {
    fn into(self) -> UnitType {
        UnitType::Upgrade
    }
}

/// The unit types which can be spawned; a union if MobileUnitType and StructureUnitType.
#[derive(Debug, Copy, Clone, Eq, PartialEq, Hash)]
pub enum SpawnableUnitType {
    Mobile(MobileUnitType),
    Structure(StructureUnitType),
}
impl SpawnableUnitType {
    /// Is this an MobileUnitType?
    pub fn is_mobile(&self) -> bool {
        match self {
            &SpawnableUnitType::Mobile(_) => true,
            &SpawnableUnitType::Structure(_) => false,
        }
    }

    /// Is this a StructureUnitType?
    pub fn is_structure(&self) -> bool {
        match self {
            &SpawnableUnitType::Mobile(_) => false,
            &SpawnableUnitType::Structure(_) => true,
        }
    }

    pub fn into_mobile(self) -> Option<MobileUnitType> {
        match self {
            SpawnableUnitType::Mobile(inner) => Some(inner),
            SpawnableUnitType::Structure(_) => None,
        }
    }

    pub fn into_structure(self) -> Option<StructureUnitType> {
        match self {
            SpawnableUnitType::Structure(inner) => Some(inner),
            SpawnableUnitType::Mobile(_) => None,
        }
    }
}
impl Into<UnitType> for SpawnableUnitType {
    fn into(self) -> UnitType {
        match self {
            SpawnableUnitType::Mobile(unit_type) => unit_type.into(),
            SpawnableUnitType::Structure(unit_type) => unit_type.into(),
        }
    }
}

/// Translations between unit types, integers, and shorthand strings.
pub struct UnitTypeAtlas {
    unit_information: [UnitInformation; 8],
    unit_type_lookup: HashMap<String, UnitType>,
}

impl UnitTypeAtlas {
    /// Construct a UnitTypeAtlas from the array of 7 UnitInformation found in the Config.
    pub fn new(unit_information: [UnitInformation; 8]) -> Self {
        let mut lookup = HashMap::new();
        for unit_type in UnitType::into_enum_iter() {
            lookup.insert(
                unit_information[unit_type as usize].shorthand.clone().unwrap(),
                unit_type,
            );
        }
        UnitTypeAtlas {
            unit_information,
            unit_type_lookup: lookup
        }
    }

    /// Get the UnitInformation from a unit type
    pub fn type_mobile(&self, unit_type: UnitType) -> &UnitInformation {
        &self.unit_information[unit_type as u32 as usize]
    }

    /// Convert a unit type integer into a UnitType.
    pub fn type_from_u32(&self, n: u32) -> Option<UnitType> {
        UnitType::into_enum_iter().nth(n as usize)
    }

    /// Convert a unit type shorthand into a UnitType.
    pub fn type_from_shorthand(&self, shorthand: &String) -> Option<UnitType> {
        self.unit_type_lookup.get(shorthand).cloned()
    }

    /// Convert a unit type into its shorthand.
    pub fn type_into_shorthand(&self, unit_type: UnitType) -> &str {
        self.unit_information[unit_type as usize].shorthand.as_ref().unwrap()
    }
}

